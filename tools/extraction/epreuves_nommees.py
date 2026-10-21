#!/usr/bin/env python3
"""Le catalogue des epreuves recurrentes de Koh-Lanta, et sa limite.

Le site ecrivait que la nature d'une epreuve -- endurance, equilibre,
precision -- n'etait donnee nulle part de facon exploitable. C'est faux pour
la premiere moitie de la phrase : le wiki Fandom tient une page par epreuve
recurrente, avec son type et la liste des saisons ou elle a ete disputee.

C'est vrai pour la seconde. Ce catalogue ne dit pas dans QUEL EPISODE chaque
epreuve a eu lieu ; il ne donne que la saison, le vainqueur et le gain. Or un
aventurier gagne souvent plusieurs epreuves du meme type dans une saison :
l'appariement avec `_data/epreuves.yml`, qui est episode par episode, reste
alors indecidable. Ce script mesure ce taux de raccord au lieu de l'affirmer,
et il est bas.

    tools/atelier python3 tools/extraction/epreuves_nommees.py --ecrire
"""
import argparse
import collections
import json
import os
import re
import sys
import unicodedata

# Le module qui ecrit et relit _data/ (virgule decimale), dans tools/.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import donnees  # noqa: E402
from coquilles import corriger  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
PAGES = os.path.join(RACINE, "specs", "sources", "epreuves")
SORTIE = os.path.join(RACINE, "_data", "epreuves_nommees.yml")

from parse_fandom import slug          # noqa: E402

RE_TABLE = re.compile(r"\{\|[^\n]*article-table.*?\n\|\}", re.S)
RE_LIEN = re.compile(r"\[\[\s*([^\]|]+?)\s*(?:\|\s*([^\]]*?)\s*)?\]\]")
RE_CHAMP = lambda nom: re.compile(r"\|\s*" + nom + r"\s*=\s*([^\n|]*)")

# Les mots que le wiki emploie pour qualifier une epreuve. Une page en porte
# souvent deux (« Rapidite, force ») : on les garde toutes les deux.
# La cle est sans accents -- elle sert a chercher dans un texte normalise ;
# le libelle, lui, est publie et prend les siens.
NATURES = {"statique": "Statique", "force": "Force", "precision": "Précision",
           "rapidite": "Rapidité", "equilibre": "Équilibre", "logique": "Logique",
           "reflexion": "Réflexion", "aquatique": "Aquatique",
           "endurance": "Endurance", "adresse": "Adresse"}


def sansaccents(t):
    t = unicodedata.normalize("NFD", t or "")
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


def propre(cellule):
    """Le texte d'une cellule : liens deroules, gras retire, modeles ecartes."""
    c = re.sub(r"<[^>]*>", "", cellule or "")
    c = RE_LIEN.sub(lambda m: m.group(2) or m.group(1), c)
    c = c.replace("'''", "").replace("''", "")
    c = re.sub(r"\{\{[^}]*\}\}", "", c)
    return re.sub(r"\s+", " ", c).strip(" .:-|")


def liens_ou_texte(cellule):
    """Les noms cites dans une cellule : les liens s'il y en a, sinon le texte."""
    liens = [(m.group(2) or m.group(1)).strip() for m in RE_LIEN.finditer(cellule or "")]
    if liens:
        return liens
    v = propre(cellule)
    return [x.strip() for x in re.split(r"\bet\b|,|&|/", v) if x.strip()] if v else []


def lire_liste(texte, saison_de):
    """Les pages sans tableau : une puce par saison.

    Quatre pages du wiki, dont l'ORIENTATION, n'ont ni fiche d'identite ni
    tableau « Apparitions et vainqueurs ». Elles listent, une puce par saison :

      * [[Koh-Lanta : Palawan]] : [[Jade Handi|'''Jade''']], '''[[Kévin]]''' ...

    Sous un titre « Candidats », les VAINQUEURS sont les noms en gras ; sous un
    titre « Vainqueurs », tous les noms le sont, et la parenthese finale dit le
    gain. Le gras est pose n'importe ou -- autour du lien, dans son libelle, sur
    plusieurs noms a la fois -- : on le suit comme un interrupteur, chaque
    « ''''' » le basculant, au lieu de chercher des motifs fixes. Un lien vers
    une saison au milieu des noms n'est pas un nom.
    """
    apparitions, section = [], ""
    for ligne in texte.split("\n"):
        titre = re.match(r"^=+\s*(.*?)\s*=+\s*$", ligne)
        if titre:
            section = sansaccents(titre.group(1))
            continue
        if not ligne.startswith("*") or not ("candidat" in section or "vainqueur" in section):
            continue
        liens = list(RE_LIEN.finditer(ligne))
        if not liens:
            continue
        sid = saison_de(liens[0].group(1)) or saison_de(liens[0].group(2) or "")
        if not sid:
            continue
        gras = ligne[:liens[0].end()].count("'''") % 2 == 1
        pos, noms, gagnants = liens[0].end(), [], []
        for m in liens[1:]:
            gras ^= ligne[pos:m.start()].count("'''") % 2 == 1
            pos = m.end()
            etiquette = m.group(2) or m.group(1)
            bascules = etiquette.count("'''")
            nom = re.sub(r"'{2,}", "", etiquette).strip(" ,.;:")
            nom_gras = gras or bascules > 0
            gras ^= bascules % 2 == 1
            if not nom or saison_de(m.group(1)):
                continue
            noms.append(nom)
            if nom_gras:
                gagnants.append(nom)
        if "vainqueur" in section:
            gagnants = noms
        gain = re.search(r"\(([^()]*)\)\s*$", propre(ligne[pos:]) and ligne[pos:].strip() or "")
        apparitions.append({
            "saison": sid,
            "vainqueurs": gagnants,
            "participants": noms if "candidat" in section else None,
            "gain": gain.group(1).strip() if gain else None,
            "genre": genre_du_gain(gain.group(1)) if gain else None,
        })
    return apparitions


def lignes_de_table(bloc):
    """Les lignes d'une table wiki, chacune rendue comme une liste de cellules."""
    sortie = []
    for morceau in re.split(r"\n\|-+[^\n]*", bloc):
        cellules = []
        for m in re.finditer(r"^\|(?!\})(.*)$", morceau, re.M):
            c = m.group(1)
            c = re.sub(r"^[^|\[\{]*\|(?!\|)", "", c)   # attributs de cellule
            cellules.append(c.strip())
        if cellules:
            sortie.append(cellules)
    return sortie


def natures(libelle):
    """Les mots-cles de nature contenus dans le champ « Type d'epreuve »."""
    t = sansaccents(libelle)
    return [n for n in NATURES if n in t]


def genre_du_gain(gain):
    """Confort ou immunite, deduit de ce qui a ete remporte."""
    if not gain:
        return None
    t = sansaccents(gain)
    return "immunite" if ("immunit" in t or "totem" in t or "collier" in t) else "confort"


def lire(saisons):
    par_titre = {}
    for s in saisons:
        if s.get("titre"):
            par_titre[re.sub(r"[^a-z0-9]", "", sansaccents(s["titre"]))] = s["id"]

    def saison_de(cellule):
        t = re.sub(r"^koh[- ]?lanta\s*:?\s*", "", sansaccents(propre(cellule)))
        return par_titre.get(re.sub(r"[^a-z0-9]", "", t))

    catalogue, rapport = [], []
    if not os.path.isdir(PAGES):
        return [], ["specs/sources/epreuves/ absent : lancer fetch_epreuves.py"]
    index = os.path.join(PAGES, "_titres.json")
    titres = json.load(open(index, encoding="utf-8")) if os.path.exists(index) else {}
    for fichier in sorted(os.listdir(PAGES)):
        if not fichier.endswith(".wiki"):
            continue
        texte = open(os.path.join(PAGES, fichier), encoding="utf-8").read()
        champ = RE_CHAMP("Nom de l'épreuve").search(texte)
        # Deux fiches ne remplissent pas le champ ; le titre de la page, lui,
        # est toujours la. On le garde en second recours plutot que de perdre
        # l'epreuve.
        nom = (champ.group(1).strip() if champ and champ.group(1).strip()
               else re.sub(r"^Épreuve (?:de |du |des |d')?", "",
                           titres.get(fichier, "")).strip())
        if not nom:
            rapport.append(f"{fichier} : pas de nom d'epreuve")
            continue
        typ = RE_CHAMP("Type d'épreuve").search(texte)
        apparitions = []
        for table in RE_TABLE.findall(texte):
            for cellules in lignes_de_table(table):
                if len(cellules) < 2:
                    continue
                sid = saison_de(cellules[0])
                if not sid:
                    continue
                gain = propre(cellules[2]) if len(cellules) > 2 else None
                apparitions.append({
                    "saison": sid,
                    "vainqueurs": liens_ou_texte(cellules[1]),
                    "gain": gain or None,
                    "genre": genre_du_gain(gain),
                })
        if not apparitions:
            apparitions = lire_liste(texte, saison_de)
        catalogue.append({
            "nom": nom[:1].upper() + nom[1:],
            "type": (typ.group(1).strip() if typ else None),
            "natures": natures(typ.group(1) if typ else ""),
            "apparitions": len(apparitions),
            "saisons": sorted({a["saison"] for a in apparitions}),
            "detail": apparitions,
        })
    catalogue.sort(key=lambda x: (-x["apparitions"], x["nom"]))
    return catalogue, rapport


def palmares_par_personne(catalogue, saisons, parts):
    """Qui a gagne quelles epreuves nommees, et de quelle nature.

    Le raccord a l'EPISODE est presque toujours indecidable : le catalogue ne
    dit pas dans quel episode une epreuve a eu lieu, et un aventurier gagne
    souvent plusieurs epreuves du meme type dans une saison. C'est mesure plus
    haut, et c'est bas -- 10,7 %.

    Mais l'episode n'est pas necessaire pour tout. Le catalogue nomme la SAISON
    et le VAINQUEUR, et cela suffit a dire « Claude a gagne telle epreuve, de
    nature force ». Ce raccord-la, au niveau de la personne, aboutit dans plus
    de neuf cas sur dix -- et c'est lui qui porte la seule chose que le site ne
    savait pas dire : quel profil gagne quelle NATURE d'epreuve.

    Une reserve, et elle compte : on compte des CITATIONS, pas des victoires
    distinctes. Une epreuve porte souvent deux natures -- le parcours du
    combattant est force ET rapidite -- et une meme victoire alimente alors
    deux compteurs.
    """
    par_prenom = collections.defaultdict(list)
    for p in parts:
        par_prenom[(p["saison"], slug(p["nom"]))].append(p)
    tribus = {(s["id"], slug(t["nom"])) for s in saisons for t in (s.get("tribus") or [])}

    lignes = collections.defaultdict(lambda: {"epreuves": [], "natures": collections.Counter()})
    motifs = collections.Counter()
    for entree in catalogue:
        for a in entree["detail"]:
            for nom in a["vainqueurs"]:
                cle = (a["saison"], slug(nom))
                if cle in tribus:
                    motifs["gagnee par une tribu"] += 1
                    continue
                candidats = par_prenom.get(cle)
                if not candidats:
                    motifs["nom introuvable dans la saison"] += 1
                    continue
                if len(candidats) > 1:
                    motifs["homonyme, non tranche"] += 1
                    continue
                motifs["attribuee"] += 1
                fiche = lignes[(a["saison"], candidats[0]["id"])]
                fiche["epreuves"].append(entree["nom"])
                for n in entree["natures"]:
                    fiche["natures"][n] += 1

    sortie = [{"saison": sid, "id": pid,
               "epreuves": sorted(v["epreuves"]),
               "natures": dict(sorted(v["natures"].items()))}
              for (sid, pid), v in sorted(lignes.items())]
    total = sum(motifs.values())
    return sortie, {
        "citations": total,
        "attribuees": motifs["attribuee"],
        "part": round(100.0 * motifs["attribuee"] / total, 1) if total else None,
        "personnes": len(sortie),
        "motifs": [{"motif": m, "effectif": n} for m, n in motifs.most_common()],
    }


def mesurer_raccord(catalogue, saisons, parts, epreuves):
    """Combien d'epreuves relevees peuvent recevoir une nature, et pourquoi si peu."""
    par_prenom = collections.defaultdict(list)
    for p in parts:
        par_prenom[(p["saison"], slug(p["nom"]))].append(p)
    tribus = {(s["id"], slug(t["nom"])) for s in saisons for t in (s.get("tribus") or [])}

    personnes, collectives = collections.defaultdict(list), collections.defaultdict(list)
    for e in epreuves:
        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                personnes[(e["saison"], v["id"], e.get("type"))].append(e)
            elif v.get("type") == "tribu" and v.get("libelle"):
                collectives[(e["saison"], slug(v["libelle"]), e.get("type"))].append(e)

    # L'ENSEMBLE des vainqueurs, pas un nom a la fois. Une epreuve du catalogue
    # cite souvent deux gagnants -- le meilleur homme et la meilleure femme du
    # parcours du combattant. Cherchee nom par nom, elle rencontre toutes les
    # epreuves de la saison que l'un OU l'autre a gagnees, et l'ambiguite ne se
    # leve jamais ; cherchee par son ensemble complet, elle n'en rencontre le
    # plus souvent qu'une. C'est un appariement plus STRICT, pas une devinette
    # de plus : il exige que les deux listes coincident exactement.
    par_ensemble = collections.defaultdict(list)
    for e in epreuves:
        vus = set()
        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                vus.add(("p", v["id"]))
            elif v.get("type") == "tribu" and v.get("libelle"):
                vus.add(("t", slug(v["libelle"])))
        if vus:
            par_ensemble[(e["saison"], e.get("type"), frozenset(vus))].append(e)

    motifs = collections.Counter()
    raccordees = {}
    for entree in catalogue:
        for a in entree["detail"]:
            attendu, incertain = set(), False
            for nom in a["vainqueurs"]:
                cle = (a["saison"], slug(nom))
                if cle in tribus:
                    attendu.add(("t", slug(nom)))
                    continue
                candidats = par_prenom.get(cle)
                if not candidats or len(candidats) > 1:
                    incertain = True
                    continue
                attendu.add(("p", candidats[0]["id"]))
            if attendu and not incertain:
                lot = par_ensemble.get((a["saison"], a["genre"], frozenset(attendu))) or []
                if len(lot) == 1:
                    motifs["raccordee sur l'ensemble des vainqueurs"] += 1
                    raccordees[id(lot[0])] = entree["natures"]
                    continue

            for nom in a["vainqueurs"]:
                cle = (a["saison"], slug(nom))
                if cle in tribus:
                    lots = collectives.get((a["saison"], slug(nom), a["genre"])) or []
                else:
                    candidats = par_prenom.get(cle)
                    if not candidats:
                        motifs["nom introuvable dans la saison"] += 1
                        continue
                    if len(candidats) > 1:
                        motifs["homonyme"] += 1
                        continue
                    lots = personnes.get((a["saison"], candidats[0]["id"], a["genre"])) or []
                if not lots:
                    motifs["aucune epreuve relevee qui corresponde"] += 1
                elif len(lots) > 1:
                    motifs["plusieurs epreuves possibles, sans episode pour trancher"] += 1
                else:
                    motifs["raccordee"] += 1
                    raccordees[id(lots[0])] = entree["natures"]
    individuelles = [e for e in epreuves if e.get("forme") == "individuelle"]
    return {
        "citations": sum(motifs.values()),
        "motifs": [{"motif": m, "effectif": n} for m, n in motifs.most_common()],
        "epreuves_relevees": len(epreuves),
        "epreuves_raccordees": len(raccordees),
        "part_raccordee": round(100.0 * len(raccordees) / len(epreuves), 1) if epreuves else None,
        "individuelles_relevees": len(individuelles),
        "individuelles_raccordees": sum(1 for e in individuelles if id(e) in raccordees),
    }


FINALE = os.path.join(RACINE, "_data", "finale.yml")


def completer_l_orientation(catalogue, parts):
    """L'orientation des saisons que la page du wiki ne liste pas encore.

    La page « Épreuve d'Orientation » s'arrete au Totem maudit (2022). Les
    saisons suivantes sont connues ailleurs : `_data/finale.yml` lit les
    qualifies et les elimines de l'orientation dans les tableaux de saison.
    Sur les saisons que les deux sources partagent, elles concordent toutes
    (confrontation du 21 octobre 2026) ; on complete donc, sans jamais
    remplacer une saison que la page donne. Chaque ajout porte sa source.

    D'ou l'ordre de la chaine : finale.py AVANT ce script (README).
    """
    if not os.path.exists(FINALE):
        return []
    o = next((e for e in catalogue if e["nom"] == "Orientation"), None)
    if o is None:
        return []
    prenom = {(p["saison"], p["id"]): p["nom"] for p in parts}
    deja = {a["saison"] for a in o["detail"]}
    ajouts = []
    for l in donnees.charger(open(FINALE, encoding="utf-8")).get("lignes") or []:
        orient = l.get("orientation") or {}
        qualifies = orient.get("qualifies") or []
        if not qualifies or l["saison"] in deja:
            continue
        noms = lambda ids: [prenom[(l["saison"], i)] for i in ids if (l["saison"], i) in prenom]
        o["detail"].append({
            "saison": l["saison"],
            "vainqueurs": noms(qualifies),
            "participants": noms(qualifies + (orient.get("elimines") or [])),
            "gain": None,
            "genre": None,
            "source": "finale.yml",
        })
        ajouts.append(l["saison"])
    o["apparitions"] = len(o["detail"])
    o["saisons"] = sorted({a["saison"] for a in o["detail"]})
    return ajouts


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ecrire", action="store_true")
    a = a.parse_args()

    lire_data = lambda n: donnees.charger(open(os.path.join(RACINE, "_data", n),
                                              encoding="utf-8"))
    saisons = lire_data("saisons.yml")
    parts = lire_data("participations.yml")
    epreuves = lire_data("epreuves.yml")

    catalogue, rapport = lire(saisons)
    ajouts = completer_l_orientation(catalogue, parts)
    if ajouts:
        rapport.append(f"orientation completee par finale.yml : {', '.join(ajouts)}")
    raccord = mesurer_raccord(catalogue, saisons, parts, epreuves)
    palmares, couverture = palmares_par_personne(catalogue, saisons, parts)

    par_nature = collections.Counter()
    for e in catalogue:
        for n in e["natures"] or ["non qualifiee"]:
            par_nature[n] += 1

    print(f"{len(catalogue)} epreuves nommees, "
          f"{sum(e['apparitions'] for e in catalogue)} apparitions")
    print("natures :", dict(par_nature.most_common()))
    print(f"raccord avec _data/epreuves.yml : {raccord['epreuves_raccordees']} sur "
          f"{raccord['epreuves_relevees']} ({raccord['part_raccordee']} %) ; "
          f"individuelles {raccord['individuelles_raccordees']}/"
          f"{raccord['individuelles_relevees']}")
    for m in raccord["motifs"]:
        print(f"    {m['motif']:52s} {m['effectif']}")
    for r in rapport:
        print("  " + r)
    print(f"raccord a la PERSONNE : {couverture['attribuees']}/{couverture['citations']} "
          f"({couverture['part']} %), {couverture['personnes']} aventuriers")
    for m in couverture["motifs"]:
        print(f"    {m['motif']:52s} {m['effectif']}")

    sortie = {
        "source": "https://kohlanta.fandom.com/fr/wiki/Catégorie:Épreuves",
        "epreuves": [{k: v for k, v in e.items() if k != "detail"} for e in catalogue],
        "nb_epreuves": len(catalogue),
        "nb_apparitions": sum(e["apparitions"] for e in catalogue),
        "par_nature": [{"nature": n, "libelle": NATURES.get(n, "Non qualifiée"),
                        "effectif": c} for n, c in par_nature.most_common()],
        "raccord": raccord,
        # Le raccord a l'episode est presque toujours indecidable ; celui a la
        # PERSONNE aboutit dans plus de neuf cas sur dix, et c'est lui qui
        # porte la nature des epreuves gagnees.
        "couverture_par_personne": couverture,
        "palmares": palmares,
    }
    if a.ecrire:
        with open(SORTIE, "w", encoding="utf-8") as f:
            f.write("# Fichier genere par tools/extraction/epreuves_nommees.py.\n"
                    "# Ne pas editer a la main : toute modification sera ecrasee.\n")
            donnees.ecrire(corriger(sortie), f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
