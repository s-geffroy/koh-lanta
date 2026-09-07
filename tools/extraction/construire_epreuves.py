#!/usr/bin/env python3
"""Ecrit _data/epreuves.yml : qui remporte quelle epreuve, episode par episode.

Une cellule de tableau ne dit qu'un nom. Tout le travail consiste a savoir ce
qu'il designe :

  * un nom de TRIBU declaree pour la saison  -> epreuve collective ;
  * un prenom present dans les participations -> epreuve individuelle ;
  * autre chose -> non resolu, et signale comme tel.

Rien n'est devine : un nom qui ne correspond ni a une tribu ni a une
participation reste tel quel, avec `resolu: false`.

    tools/atelier python3 tools/extraction/construire_epreuves.py --ecrire
"""
import os
import re
import sys
from collections import Counter, defaultdict

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
WIKI = os.environ.get("KL_WIKI", os.path.join(RACINE, "specs", "sources", "wiki"))

from parse_fandom import slug            # noqa: E402
from parse_epreuves import parse_page    # noqa: E402

SUFFIXES = (".wiki", ".fandom.wiki", ".en.wiki")

# De combien un bilan d'epreuves peut legitimement depasser le dernier conseil
# NUMEROTE. Le dernier conseil d'elimination precede la finale d'un episode ou
# deux -- poteaux, orientation, jury -- et une epreuve peut s'y tenir encore.
# Au-dela, ce n'est plus un decalage de fin de saison : c'est une autre
# numerotation d'episodes, et elle rend fausse toute comparaison a une date de
# sortie.
TOLERANCE_EPISODES = 2

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Vainqueurs des epreuves de confort et d'immunite, episode par episode.
# Produit par tools/extraction/construire_epreuves.py depuis les bilans par
# episode de Wikipedia (fr et en) et du wiki Fandom francophone.
#
# `forme` vaut `collective` quand l'epreuve est remportee par une tribu,
# `individuelle` quand elle l'est par une personne. Les identifiants renvoient
# a participations.yml ; un nom non rattache est conserve en clair avec
# `resolu: false`.
#
#     tools/atelier python3 tools/extraction/construire_epreuves.py --ecrire
#
"""


# « Equipe de X », « Team de X » : le groupe mene par X. La source designe
# ainsi le vainqueur d'un confort par equipes, sans lister ses membres.
RE_EQUIPE = re.compile(r"^(?:[ÉEée]quipe|Team)\s+d[eu'’]\s*(.+)$", re.I)


def index_saison(saison, parts):
    tribus = {}
    for t in saison.get("tribus") or []:
        tribus[slug(t["nom"])] = t["nom"]
    personnes = defaultdict(list)
    for p in parts:
        if p["saison"] == saison["id"]:
            personnes[slug(p["nom"])].append(p)
    return tribus, personnes


def dernier_episode_des_conseils(conseils):
    """(saison) -> numero du dernier conseil numerote.

    C'est la reference de numerotation du depot : tout ce qui se compare a une
    date de sortie passe par elle. Les scrutins de jury portent un en-tete
    (« Gagnant », « Finaliste ») au lieu d'un numero et n'entrent pas ici.
    """
    dernier = {}
    for c in conseils or []:
        try:
            n = int(c.get("episode"))
        except (TypeError, ValueError):
            continue
        sid = c["saison"]
        dernier[sid] = max(dernier.get(sid, 0), n)
    return dernier


def _max_episode(lot):
    nums = [e["episode"] for e in lot if isinstance(e.get("episode"), int)]
    return max(nums) if nums else 0


def construire(saisons, parts, rapport, dernier_conseil=None, elimines_du_soir=None):
    par_saison = {s["id"]: s for s in saisons}
    dernier_conseil = dernier_conseil or {}
    elimines_du_soir = elimines_du_soir or {}
    epreuves = []

    for s in saisons:
        if s.get("annulee"):
            continue
        sid = s["id"]
        # Le surlignage d'un nom suit la tribu du MOMENT : apres la
        # reunification, ce n'est plus la tribu de depart. On ne lit donc que
        # les couleurs de depart de la saison.
        couleurs_depart = {t.get("couleur") for t in (s.get("tribus") or [])
                           if not t.get("apres_fusion") and t.get("couleur")}
        # Deux pages peuvent decrire les MEMES epreuves avec deux
        # numerotations d'episodes : Wikipedia en anglais compte dix-sept
        # episodes au Totem maudit la ou le tableau des votes en compte
        # quatorze. Prendre la page la plus fournie choisirait alors une
        # numerotation etrangere a celle des conseils, et « l'epreuve
        # a-t-elle eu lieu avant sa sortie ? » n'aurait plus de reponse juste.
        # On prefere donc la page qui s'accorde avec les conseils, et le
        # volume ne departage qu'a accord egal.
        attendu = dernier_conseil.get(sid)
        candidats = []
        for suf in SUFFIXES:
            chemin = os.path.join(WIKI, sid + suf)
            if not os.path.exists(chemin):
                continue
            try:
                lot = parse_page(open(chemin, encoding="utf-8").read(), sid,
                                 couleurs_depart)
            except Exception as e:
                rapport.append(f"{sid} : lecture des epreuves impossible ({suf}) — {e}")
                continue
            if lot:
                candidats.append((suf, lot))
        meilleur = []
        if candidats:
            def rang(c):
                # Un bilan peut s'arreter avant le dernier conseil -- les
                # colonnes d'orientation et de poteaux ferment le tableau. Il
                # ne peut pas aller AU-DELA : c'est le signe d'une autre
                # numerotation, et cet ecart-la seul est penalise.
                trop = _max_episode(c[1]) - attendu - TOLERANCE_EPISODES
                return (max(0, trop) if attendu else 0, -len(c[1]))
            candidats.sort(key=rang)
            meilleur = candidats[0][1]
            if attendu and len(candidats) > 1:
                plafond = attendu + TOLERANCE_EPISODES
                ecarte = [c for c in candidats[1:]
                          if _max_episode(c[1]) > plafond >= _max_episode(candidats[0][1])]
                for suf, lot in ecarte:
                    rapport.append(
                        f"{sid} : {suf} ecarte — {_max_episode(lot)} episodes "
                        f"contre {attendu} conseils numerotes")
        if not meilleur:
            rapport.append(f"{sid} : aucun bilan d'epreuves exploitable")
            continue

        tribus, personnes = index_saison(s, parts)

        def eclater(libelle):
            """« Claude Laurent » : deux vainqueurs, pas un aventurier inconnu.

            Quelques cellules citent plusieurs gagnants sans separateur. On ne
            les coupe que si CHAQUE mot designe un aventurier de la saison et
            que l'ensemble n'en designe pas un -- sinon « Jean Charles » ou
            « Marie France » seraient coupes en deux.
            """
            mots = libelle.split()
            if len(mots) < 2 or slug(libelle) in personnes or slug(libelle) in tribus:
                return [libelle]
            if all(slug(m) in personnes for m in mots):
                return mots
            return [libelle]

        for e in meilleur:
            vainqueurs, formes = [], set()
            libelles = [x for l in e["libelles"] for x in eclater(l)]
            for libelle in libelles:
                cle = slug(libelle)
                if cle in tribus:
                    vainqueurs.append({"libelle": tribus[cle], "type": "tribu",
                                       "id": None, "resolu": True})
                    formes.add("collective")
                elif cle in personnes and len(personnes[cle]) == 1:
                    vainqueurs.append({"libelle": libelle, "type": "personne",
                                       "id": personnes[cle][0]["id"], "resolu": True})
                    formes.add("individuelle")
                elif cle in personnes:
                    # Deux aventuriers du meme prenom. La source le sait et
                    # accroche au nom une note « De la tribu jaune » : on la
                    # lit, on ne devine pas. Sans note, le nom reste non
                    # rattache.
                    couleur = (e.get("indices") or {}).get(cle)
                    lot = [p_ for p_ in personnes[cle] if p_.get("couleur") == couleur]
                    if couleur and len(lot) == 1:
                        vainqueurs.append({"libelle": libelle, "type": "personne",
                                           "id": lot[0]["id"], "resolu": True})
                        rapport.append(f"{sid} ep.{e['episode']} : « {libelle} » "
                                       f"homonyme, tranche par la note de la source "
                                       f"(tribu {couleur}) → {lot[0]['id']}")
                    else:
                        vainqueurs.append({"libelle": libelle, "type": "personne",
                                           "id": None, "resolu": False})
                        rapport.append(f"{sid} ep.{e['episode']} : « {libelle} » est un "
                                       f"homonyme, vainqueur non rattache")
                    formes.add("individuelle")
                elif RE_EQUIPE.match(libelle):
                    # « Equipe de Guillaume » : une recompense de confort
                    # partagee, dont la source ne nomme que le capitaine. Ce
                    # n'est ni une tribu ni une personne, mais ce n'est pas non
                    # plus un libelle incompris : c'est un GROUPE, et l'epreuve
                    # est donc collective.
                    chef = slug(RE_EQUIPE.match(libelle).group(1))
                    pid = (personnes[chef][0]["id"]
                           if chef in personnes and len(personnes[chef]) == 1 else None)
                    vainqueurs.append({"libelle": libelle, "type": "equipe",
                                       "id": pid, "resolu": True})
                    formes.add("collective")
                else:
                    vainqueurs.append({"libelle": libelle, "type": None,
                                       "id": None, "resolu": False})
                    rapport.append(f"{sid} ep.{e['episode']} : « {libelle} » ne "
                                   f"correspond ni a une tribu ni a un aventurier")
            if not vainqueurs:
                continue
            forme = formes.pop() if len(formes) == 1 else (
                "mixte" if len(formes) > 1 else None)
            epreuves.append({
                "saison": sid,
                "episode": e["episode"],
                "type": e["type"],
                "forme": forme,
                "vainqueurs": vainqueurs,
                "source": e["source"],
            })
    return _oter_les_immunites_dementies(epreuves, elimines_du_soir, rapport)


def elimines_par_episode(conseils):
    """(saison, episode) -> l'elimine, quand le soir n'a tenu qu'UN conseil.

    Un soir a plusieurs conseils ne permet pas de rattacher une immunite a
    l'un d'eux : on ne rend que les soirs sans ambiguite.
    """
    par_soir = defaultdict(list)
    for c in conseils or []:
        if c.get("type") == "jury" or not c.get("elimine_rattache"):
            continue
        try:
            par_soir[(c["saison"], int(c["episode"]))].append(c["elimine"])
        except (TypeError, ValueError, KeyError):
            continue
    return {k: v[0] for k, v in par_soir.items() if len(v) == 1}


def _oter_les_immunites_dementies(epreuves, elimines, rapport):
    """Une immunite individuelle gagnee par celui qui part le soir meme n'existe pas.

    Les deux faits ne peuvent pas tenir ensemble : l'immunite protege du
    conseil. Quand ils se contredisent, c'est le conseil qui gagne -- il est
    atteste par ses bulletins, quand l'immunite ne l'est que par un nom dans
    une cellule.

    Le cas connu est la Revanche des 4 Terres, episode 13 : la colonne
    « Immunite » y porte trois noms, qui sont les rescapes d'une EPREUVE
    ELIMINATOIRE et non les vainqueurs d'une immunite. Maxime y figure, et il
    part au conseil du soir. On retire la seule attribution qui se contredit,
    et on garde les autres.
    """
    for e in epreuves:
        if e.get("type") != "immunite" or e.get("forme") != "individuelle":
            continue
        try:
            cle = (e["saison"], int(e["episode"]))
        except (TypeError, ValueError, KeyError):
            continue
        sortant = elimines.get(cle)
        if not sortant:
            continue
        garde = [v for v in e["vainqueurs"] if v.get("id") != sortant]
        if len(garde) != len(e["vainqueurs"]):
            rapport.append(
                f"{e['saison']} ep.{e['episode']} : immunite individuelle "
                f"attribuee a {sortant}, qui part au conseil du meme soir — "
                f"attribution ecartee, le conseil fait foi")
            e["vainqueurs"] = garde
    return [e for e in epreuves if e["vainqueurs"]]


def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    chemin_conseils = os.path.join(RACINE, "_data", "conseils.yml")
    conseils = (yaml.safe_load(open(chemin_conseils))
                if os.path.exists(chemin_conseils) else [])
    rapport = []
    epreuves = construire(saisons, parts, rapport,
                          dernier_episode_des_conseils(conseils),
                          elimines_par_episode(conseils))

    total = sum(len(e["vainqueurs"]) for e in epreuves)
    resolus = sum(1 for e in epreuves for v in e["vainqueurs"] if v["resolu"])
    formes = Counter(e["forme"] for e in epreuves)
    types = Counter(e["type"] for e in epreuves)
    saisons_couvertes = len({e["saison"] for e in epreuves})

    print(f"epreuves          : {len(epreuves)}")
    print(f"saisons couvertes : {saisons_couvertes} / "
          f"{sum(1 for s in saisons if not s.get('annulee'))}")
    print(f"types             : {dict(types)}")
    print(f"formes            : {dict(formes)}")
    print(f"vainqueurs cites  : {total}, dont {resolus} rattaches "
          f"({100*resolus/total:.1f} %)")

    dementies = [r for r in rapport if "fait foi" in r]
    if dementies:
        print(f"\nimmunites dementies par le conseil ({len(dementies)}) :")
        for r in dementies:
            print("  " + r)

    ecartes = [r for r in rapport if "ecarte —" in r]
    if ecartes:
        print(f"\nsources ecartees pour numerotation ({len(ecartes)}) :")
        for r in ecartes:
            print("  " + r)

    manques = [r for r in rapport if "aucun bilan" in r]
    if manques:
        print(f"\nsaisons sans bilan ({len(manques)}) :")
        for r in manques:
            print("  " + r)
    autres = Counter(r.split("«")[-1].split("»")[0].strip()
                     for r in rapport if "ne correspond" in r)
    if autres:
        print(f"\nlibelles non rattaches ({sum(autres.values())} citations, "
              f"{len(autres)} distincts) :")
        for nom, n in autres.most_common(14):
            print(f"  {n:4d}  {nom!r}")

    if "--ecrire" in sys.argv:
        chemin = os.path.join(RACINE, "_data", "epreuves.yml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE)
            yaml.safe_dump(epreuves, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
