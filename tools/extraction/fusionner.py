#!/usr/bin/env python3
"""Croise les deux sources et ecrit _data/participations.yml et personnes.yml.

Aucune des deux sources ne suffit seule :

  * le wiki Fandom couvre les 34 saisons et donne le nom complet, l'age, la
    profession et le total des voix recues, mais sa table est incomplete sur
    six saisons et il ne dit le sexe que par l'accord du participe ;
  * Wikipedia en francais ne couvre que quinze saisons, mais sa table est
    complete, donne le sexe en clair et borne l'appartenance aux tribus en
    jours -- donc la trajectoire.

Pour chaque saison, la source de reference est celle dont l'effectif tombe
juste ; l'autre vient completer, champ par champ. Chaque valeur retenue garde
la trace de sa provenance dans `sources`.
"""
import os
import re
import sys
import unicodedata

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))

import parse_fandom as F
import parse_wikipedia_fr as W
import lieux

# Wikitexte brut des pages sources, tel que recupere par specs/sources/fetch*.py.
# Hors du site publie : `specs/` est dans la liste `exclude:` de _config.yml.
WIKI = os.environ.get("KL_WIKI", os.path.join(RACINE, "specs", "sources", "wiki"))

# Ordre de preference par champ. « w » = Wikipedia fr, « f » = Fandom.
PREFERENCE = {
    "genre":         ["w", "f"],
    "age":           ["w", "f"],
    "profession":    ["w", "f"],
    "localisation":  ["w", "f"],
    "tribu":         ["w", "f"],
    "couleur":       ["w"],
    "parcours":      ["w"],
    # Le jour lu chez Wikipedia est celui de la derniere bascule de tribu, pas
    # celui du depart : sur une saison entiere il vaut le jour de reunification
    # pour tout le monde. Fandom donne le jour de sortie en clair.
    "jour_sortie":   ["f", "w"],
    # Wikipedia dit « Éliminé » tout court ; Fandom precise « aux poteaux »,
    # « a l'orientation », « aux ambassadeurs ». La nuance porte des statistiques
    # entieres, elle prime.
    "sort":          ["f", "w"],
    "motif":         ["f", "w"],
    "nom_complet":   ["f"],
    "votes_recus":   ["f"],
    "edition_origine": ["f"],
}

LIBELLE = {
    "w": "wikipedia-fr",
    "f": "fandom",
}

def cle(nom):
    return F.slug(nom or "")

def indexer(rows):
    """Index par prenom. Les homonymes d'une meme saison sont conserves."""
    idx = {}
    for r in rows:
        idx.setdefault(cle(r.get("nom")), []).append(r)
    return idx


def mots(texte):
    return {m for m in re.split(r"\W+", (texte or "").lower()) if len(m) > 3}


def apparier(r, candidats):
    """Choisit, parmi des homonymes, celui qui est la meme personne.

    Deux Lea en saison 25, deux Cecile en 26, deux Jerome en 27 : ce sont bien
    des personnes differentes, pas des doublons. Le prenom ne suffit donc pas.
    L'age les separe sans ambiguite dans tous les cas rencontres ; le metier
    sert de second recours.
    """
    if len(candidats) == 1:
        return candidats[0]

    def score(c):
        s = 0
        if r.get("age") and c.get("age"):
            s += 100 if r["age"] == c["age"] else -abs(r["age"] - c["age"])
        communs = mots(r.get("profession")) & mots(c.get("profession"))
        s += 10 * len(communs)
        if r.get("jour_sortie") and c.get("jour_sortie") and r["jour_sortie"] == c["jour_sortie"]:
            s += 5
        return s

    classes = sorted(candidats, key=score, reverse=True)
    if len(classes) > 1 and score(classes[0]) == score(classes[1]):
        return None          # indepartageable : on prefere ne rien croiser
    return classes[0]

def fusionner_saison(saison, rows_f, rows_w, rapport, saisons_connues=()):
    sid = saison["id"]
    attendu = saison.get("nb_candidats") or 0

    # source de reference : celle dont l'effectif tombe juste
    if len(rows_w) == attendu and rows_w:
        base_code, base, autre_code, autre = "w", rows_w, "f", rows_f
    elif len(rows_f) == attendu and rows_f:
        base_code, base, autre_code, autre = "f", rows_f, "w", rows_w
    else:
        if len(rows_w) >= len(rows_f):
            base_code, base, autre_code, autre = "w", rows_w, "f", rows_f
        else:
            base_code, base, autre_code, autre = "f", rows_f, "w", rows_w
        rapport.append(
            f"{sid} : aucune source ne donne l'effectif attendu ({attendu}) — "
            f"fandom={len(rows_f)}, wikipedia={len(rows_w)} ; "
            f"reference = {LIBELLE[base_code]}")

    idx_autre = indexer(autre)
    couleurs = {F.slug(t["nom"]): t.get("couleur") for t in saison.get("tribus", [])}

    out = []
    for r in base:
        k = cle(r.get("nom"))
        jumeau = None
        if k in idx_autre:
            jumeau = apparier(r, idx_autre[k])
            if jumeau is None:
                rapport.append(f"{sid} : « {r.get('nom')} » a un homonyme dans la "
                               f"saison et rien ne les departage")

        dispo = {base_code: r}
        if jumeau:
            dispo[autre_code] = jumeau

        fiche = {champ: None for champ in PREFERENCE}
        provenance = {}
        for champ, ordre in PREFERENCE.items():
            for code in ordre:
                src = dispo.get(code)
                if src and src.get(champ) not in (None, "", []):
                    fiche[champ] = src[champ]
                    provenance[champ] = LIBELLE[code]
                    break

        # Sur les editions de retour, la colonne « profession » porte parfois
        # l'edition d'origine (« Palawan », « Pacifique ») ou un palmares.
        # Ce ne sont pas des metiers : les y laisser polluerait la taxonomie.
        titres = {F.slug(x.get("titre") or "") for x in saisons_connues}
        pr = fiche.get("profession")
        if pr and (F.slug(pr) in titres
                   or "\u2020" in pr or re.search(r"d[ée]c[ée]d", pr, re.I)
                   or re.search(r"\b([ée]limin|vainqueur|finaliste|gagnant)", pr, re.I)):
            if not fiche.get("edition_origine"):
                fiche["edition_origine"] = pr
                provenance["edition_origine"] = provenance.get("profession", "?")
            fiche["profession"] = None
            provenance.pop("profession", None)

        # La profession porte parfois le departement colle devant ou derriere.
        # On l'en detache pour que la taxonomie des metiers reste propre.
        if fiche.get("profession"):
            lieu, metier = lieux.separer(fiche["profession"])
            if lieu:
                fiche["profession"] = metier
                if not fiche.get("localisation"):
                    fiche["localisation"] = lieu
                    provenance["localisation"] = provenance.get("profession", "?")

        nom = r.get("nom")
        fiche["nom"] = nom
        if not fiche.get("nom_complet"):
            fiche["nom_complet"] = nom
        fiche["saison"] = sid
        fiche["id"] = F.slug(fiche["nom_complet"])

        if not fiche.get("couleur") and fiche.get("tribu"):
            c = couleurs.get(F.slug(fiche["tribu"]))
            if c:
                fiche["couleur"] = c
                provenance["couleur"] = "saisons.yml"

        # Signaler les vrais desaccords, pas les ecarts structurels connus.
        # L'ecart sur le jour entre les deux sources est attendu (Wikipedia
        # borne a la derniere bascule de tribu) : il n'est signale que s'il va
        # dans le sens inverse, c'est-a-dire si Fandom sort quelqu'un plus tot
        # que sa derniere tribu connue.
        if jumeau:
            src = {base_code: r, autre_code: jumeau}
            w, f = src.get("w", {}), src.get("f", {})
            if w.get("age") is not None and f.get("age") is not None and w["age"] != f["age"]:
                rapport.append(f"{sid} / {nom} : age diverge — "
                               f"wikipedia-fr={w['age']}, fandom={f['age']} "
                               f"(retenu : {fiche.get('age')})")
            jw, jf = w.get("jour_sortie"), f.get("jour_sortie")
            if jw is not None and jf is not None and jf < jw:
                rapport.append(f"{sid} / {nom} : jour de sortie incoherent — "
                               f"fandom={jf} anterieur a la derniere tribu connue "
                               f"chez wikipedia-fr ({jw})")
            sw, sf = w.get("sort"), f.get("sort")
            if sw and sf and sw != sf and sw != "elimine_conseil":
                rapport.append(f"{sid} / {nom} : sort diverge — "
                               f"wikipedia-fr={sw}, fandom={sf} "
                               f"(retenu : {fiche.get('sort')})")

        fiche["sources"] = provenance
        out.append(fiche)
    return out

# Prenoms que le recoupement ne tranche pas : ni l'accord du participe, ni le
# modele {{♀}}/{{♂}} ne les couvrent, et ils n'apparaissent nulle part ailleurs
# dans le jeu de donnees. Tranches a la main, un par un.
GENRE_MANUEL = {
    "videli": "h",        # Vidéli Dittmar, saison 4, décorateur-sculpteur
    "mama": "f",          # Mama Diarra, saison 6
    "cega": "h",          # Céga, saison 8, magasinier
    "charlie": "f",       # Charlie, saison 15, restauratrice de meubles
    "brahma": "h",        # Brahma, saison 17, éducateur spécialisé
    "jesta": "f",         # Jesta Hillmann, finaliste de la saison 16
    "ines": "f",          # Inès Loucif, finaliste de L'Île des héros
    "kaouther": "f",
    "naouel": "f",
    "alisea": "f",
    "carinne": "f",
    "manuella": "f",
    # Prenoms sans ambiguite, restes sans accord parce que la personne a
    # abandonne (« Abandon medical » ne s'accorde pas) ou a ete finaliste.
    "richard": "h", "odile": "f", "aude": "f", "jean-claude": "h", "ali": "h",
    "kevin": "h", "christopher": "h", "jennifer": "f", "valentin": "h",
    "gerard": "h", "manon": "f", "margot": "f", "corinne": "f", "marc": "h",
    "marius": "h", "bastien": "h", "jean-philippe": "h", "adrien": "h",
    "jade": "f", "sara": "f", "coumba": "f", "karima": "f", "cindy": "f",
    "patrick": "h", "freddy": "h", "ugo": "h", "teheiura": "h",
}

def completer_genre(participations, rapport):
    """Comble le sexe manquant par recoupement sur le prenom.

    L'accord du participe (« Éliminée ») et le modele {{♀}} couvrent la grande
    majorite des lignes. Pour le reste, un prenom deja tranche ailleurs dans le
    jeu de donnees fait foi -- a condition qu'il n'ait jamais ete vu des deux
    genres, auquel cas on prefere ne rien dire.
    """
    par_prenom = {}
    for p in participations:
        if p.get("genre"):
            par_prenom.setdefault(F.slug(p["nom"]), set()).add(p["genre"])
    ambigus = {k for k, v in par_prenom.items() if len(v) > 1}

    residuel = []
    for p in participations:
        if p.get("genre"):
            continue
        k = F.slug(p["nom"])
        if k in GENRE_MANUEL:
            p["genre"] = GENRE_MANUEL[k]
            p.setdefault("sources", {})["genre"] = "arbitrage manuel"
        elif k in par_prenom and k not in ambigus:
            p["genre"] = next(iter(par_prenom[k]))
            p.setdefault("sources", {})["genre"] = "recoupement sur le prenom"
        else:
            residuel.append(f"{p['saison']}/{p['nom']}")
    if residuel:
        rapport.append(f"sexe non tranche pour {len(residuel)} participations : "
                       + ", ".join(residuel))

def rattacher_prenoms_nus(participations, rapport):
    """Rend son nom de famille a une participation qui n'a qu'un prenom.

    Les editions de retour presentent parfois les revenants par leur seul
    prenom. Sans nom de famille, la meme personne compte pour deux : le
    palmares des multi-participants s'en trouve fausse, et l'age ne peut plus
    se deduire d'une autre annee.

    Le rattachement n'est fait que si UN SEUL nom complet du jeu de donnees
    porte ce prenom. Des qu'il y a deux porteurs, on s'abstient.
    """
    complets = {}
    for p in participations:
        if p["nom_complet"] != p["nom"]:
            complets.setdefault(F.slug(p["nom"]), set()).add(p["nom_complet"])

    rattaches = 0
    for p in participations:
        if p["nom_complet"] != p["nom"]:
            continue
        candidats = complets.get(F.slug(p["nom"]))
        if candidats and len(candidats) == 1:
            p["nom_complet"] = next(iter(candidats))
            p["id"] = F.slug(p["nom_complet"])
            p.setdefault("sources", {})["nom_complet"] = (
                "rattache a son autre participation")
            rattaches += 1
    if rattaches:
        rapport.append(f"{rattaches} participation(s) rattachee(s) a leur nom "
                       f"complet vu sur une autre saison")


def appliquer_vainqueurs(participations, saisons, rapport):
    """Cale le sort et le jour des finalistes sur ce que la saison declare.

    Les tables sources sont irregulieres sur leurs dernieres lignes : la
    cellule de depart du gagnant est tantot vide, tantot remplie par le nom de
    la tribu reunifiee, et le jour lu chez Wikipedia est celui de la derniere
    bascule de tribu, pas celui de la finale.

    Deux regles remettent tout d'aplomb :
      * la liste des vainqueurs de saisons.yml, tiree du tableau recapitulatif
        de Wikipedia, fait foi sur QUI a gagne ;
      * un vainqueur ou un finaliste quitte le jeu le dernier jour, par
        definition de la finale.

    La premiere sert aussi de controle : une saison ou l'on ne retrouve pas
    tous les vainqueurs declares remonte dans le rapport.
    """
    par_saison = {}
    for p in participations:
        par_saison.setdefault(p["saison"], []).append(p)

    for s in saisons:
        if s.get("annulee") or s.get("en_cours"):
            continue
        lignes = par_saison.get(s["id"], [])
        attendus = {F.slug(x) for x in (s.get("vainqueurs") or [])}
        if not attendus:
            continue

        trouves = []
        for p in lignes:
            noms = {F.slug(p["nom"]), F.slug(p.get("nom_complet") or "")}
            if noms & attendus:
                trouves.append(p)
                if p.get("sort") != "vainqueur":
                    p["sort"] = "vainqueur"
                    p.setdefault("sources", {})["sort"] = "saisons.yml"
            elif p.get("sort") == "vainqueur":
                rapport.append(f"{s['id']} / {p['nom']} : donne vainqueur par la "
                               f"source mais absent de la liste declaree "
                               f"({', '.join(s['vainqueurs'])})")

        if len(trouves) != len(attendus):
            rapport.append(f"{s['id']} : {len(trouves)} vainqueur(s) retrouve(s) "
                           f"sur {len(attendus)} declare(s) "
                           f"({', '.join(s['vainqueurs'])})")

        duree = s.get("duree_jours")
        if not duree:
            continue
        for p in lignes:
            if p.get("sort") in ("vainqueur", "finaliste") and p.get("jour_sortie") != duree:
                p["jour_sortie"] = duree
                p.setdefault("sources", {})["jour_sortie"] = (
                    "dernier jour de la saison (finale)")


def completer_depuis_autres_participations(participations, saisons, rapport):
    """Comble l'age et le metier des joueurs de retour.

    Les editions de heros et les All Stars ne redonnent ni l'age ni la
    profession des revenants : la source suppose qu'on les connait deja. Or on
    les connait : la meme personne a une autre participation, datee. L'age s'en
    deduit par difference d'annees, le metier se reprend tel quel.

    La deduction est datee et tracee : elle n'invente pas une valeur, elle
    reporte une valeur connue d'une annee sur une autre.
    """
    annees = {s["id"]: s.get("annee") for s in saisons}
    par_personne = {}
    for p in participations:
        par_personne.setdefault(p["id"], []).append(p)

    for pid, lignes in par_personne.items():
        if len(lignes) < 2:
            continue
        avec_age = [x for x in lignes if x.get("age") and annees.get(x["saison"])]
        avec_metier = [x for x in lignes if x.get("profession")]
        for p in lignes:
            an = annees.get(p["saison"])
            if p.get("age") is None and avec_age and an:
                ref = min(avec_age, key=lambda x: abs(annees[x["saison"]] - an))
                p["age"] = ref["age"] + (an - annees[ref["saison"]])
                p.setdefault("sources", {})["age"] = (
                    f"deduit de sa participation de {annees[ref['saison']]}")
            if p.get("profession") is None and avec_metier:
                ref = min(avec_metier,
                          key=lambda x: abs((annees.get(x["saison"]) or 0) - (an or 0)))
                p["profession"] = ref["profession"]
                p.setdefault("sources", {})["profession"] = (
                    f"reprise de sa participation de {annees.get(ref['saison'])}")


def charger(sid):
    f_path = os.path.join(WIKI, f"{sid}.fandom.wiki")
    w_path = os.path.join(WIKI, f"{sid}.wiki")
    rows_f = F.parse_page(open(f_path, encoding="utf-8").read(), sid) if os.path.exists(f_path) else []
    rows_w = W.parse_page(open(w_path, encoding="utf-8").read(), sid) if os.path.exists(w_path) else []
    return rows_f, rows_w

def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    rapport, participations = [], []
    for s in saisons:
        if s.get("annulee"):
            continue
        rows_f, rows_w = charger(s["id"])
        if not rows_f and not rows_w:
            rapport.append(f"{s['id']} : aucune source")
            continue
        participations.extend(fusionner_saison(s, rows_f, rows_w, rapport, saisons))

    rattacher_prenoms_nus(participations, rapport)
    appliquer_vainqueurs(participations, saisons, rapport)
    completer_genre(participations, rapport)
    completer_depuis_autres_participations(participations, saisons, rapport)

    # champs encore vides
    manques = {}
    for p in participations:
        for champ in ("age", "profession", "genre", "tribu", "jour_sortie", "sort"):
            if p.get(champ) in (None, "", []):
                manques.setdefault(champ, []).append(f"{p['saison']}/{p['nom']}")

    return participations, rapport, manques

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Produit par tools/extraction/fusionner.py, qui croise deux sources :
#   - le wiki Fandom francophone   https://kohlanta.fandom.com/fr/
#   - Wikipedia en francais        https://fr.wikipedia.org/
#
# Chaque enregistrement porte un bloc `sources` qui dit, champ par champ, d'ou
# vient la valeur retenue. Regenerer avec :
#
#     tools/atelier python3 tools/extraction/fusionner.py --ecrire
#
"""

ORDRE = ["id", "nom", "nom_complet", "saison", "genre", "age", "profession",
         "localisation", "edition_origine", "tribu", "couleur", "parcours",
         "jour_sortie", "sort", "motif", "votes_recus", "sources"]

def ordonner(p):
    return {k: p[k] for k in ORDRE if k in p}

def ecrire(participations, saisons):
    """Ecrit _data/participations.yml et _data/personnes.yml."""
    import collections
    chemin_p = os.path.join(RACINE, "_data", "participations.yml")
    with open(chemin_p, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump([ordonner(p) for p in participations], f,
                       allow_unicode=True, sort_keys=False, width=100)

    annees = {s["id"]: s.get("annee") for s in saisons}
    gens = collections.OrderedDict()
    for p in participations:
        e = gens.setdefault(p["id"], {
            "id": p["id"], "nom": p["nom_complet"], "prenom": p["nom"],
            "genre": p.get("genre"), "participations": [],
        })
        if not e["genre"]:
            e["genre"] = p.get("genre")
        e["participations"].append(p["saison"])
    for e in gens.values():
        e["nb_participations"] = len(e["participations"])

    chemin_g = os.path.join(RACINE, "_data", "personnes.yml")
    with open(chemin_g, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump(list(gens.values()), f,
                       allow_unicode=True, sort_keys=False, width=100)
    return chemin_p, chemin_g, len(gens)


if __name__ == "__main__":
    parts, rapport, manques = main()
    print(f"participations fusionnees : {len(parts)}")
    print(f"\n--- champs encore vides ---")
    for champ, qui in sorted(manques.items()):
        print(f"  {champ:12s} {len(qui):4d}   {', '.join(qui[:8])}{' …' if len(qui) > 8 else ''}")
    print(f"\n--- rapport ({len(rapport)} entrées) ---")
    for r in rapport[:40]:
        print("  " + r)
    if len(rapport) > 40:
        print(f"  … et {len(rapport)-40} autres")

    if "--ecrire" in sys.argv:
        saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
        cp, cg, n = ecrire(parts, saisons)
        print(f"\necrit : {cp} ({len(parts)} participations)")
        print(f"ecrit : {cg} ({n} personnes)")
