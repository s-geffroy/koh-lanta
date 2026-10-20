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

# Le module qui ecrit et relit _data/ (virgule decimale), dans tools/.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import donnees  # noqa: E402

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

# Les attributions qu'une source donne et qu'une autre DEMENT, preuve a
# l'appui. C'est une TABLE, pas une regle : chaque ligne cite ce qui la fonde,
# et rien n'y entre sans cela. (saison, episode, type, libelle) -> preuve.
ATTRIBUTIONS_REFUTEES = {
    ("sp5", 4, "confort", "Yassin"):
        "Wikipedia, resume de l'episode 4 : Dylan gagne, Yassin finit deuxieme "
        "et devient chef de la seconde equipe ; Fandom le range dans la colonne "
        "du confort, il n'a pas gagne l'epreuve.",
    **{("s23", 10, "confort", nom):
        "Wikipedia anglais : « François [Fouzi, Louana, Ambre, Bastien] » -- "
        "François gagne et emmene quatre invites. Fandom cite les cinq ; les "
        "deux sources ne s'accordent que sur François, et c'est lui seul "
        "qu'on retient. Convention des crochets verifiee a Panama et Vanuatu."
       for nom in ("Fouzi", "Louana", "Ambre", "Bastien")},
    ("s04", 9, "immunite", "Linda"):
        "Wikipedia anglais, note de la case : « As part of Linda's return to "
        "the game, she was given immunity at the next Tribal Council. » "
        "L'immunite lui est DONNEE a son retour, elle ne la gagne pas.",
    ("s04", 13, "immunite", "Linda"):
        "Fandom : « 13ème épisode (finale) », Linda gagne l'epreuve des poteaux. "
        "Le resume anglais l'ecrit dans la colonne Immunity, sans le trio qui "
        "signale ailleurs la finale.",
}


def index_saison(saison, parts):
    tribus = {}
    for t in saison.get("tribus") or []:
        tribus[slug(t["nom"])] = t["nom"]
    personnes = defaultdict(list)
    for p in parts:
        if p["saison"] == saison["id"]:
            personnes[slug(p["nom"])].append(p)
    return tribus, personnes


# Les tableaux qui numerotent leurs LIGNES et non les episodes. Fandom ecrit
# « 7ème épisode » pour la septieme ligne de son bilan de la Legende, qui en
# saute quatre ; les conseils, eux, suivent les quinze episodes diffuses. La
# correspondance se lit aux dates et aux jours que donnent les resumes de
# Wikipedia, et c'est une TABLE : chaque ligne a ete verifiee a la main.
#   ligne 7  (12 oct., jour 18) -> ep. 7 (confort, jour 17) et 8 (immunite, jour 19)
#   ligne 8  (26 oct.)          -> ep. 9
#   ligne 9  (2 nov.)           -> ep. 10
#   ligne 10 (9 nov., jour 29)  -> ep. 11 (bambous, jour 26) et 12 (confort
#                                  eliminatoire, jour 28 ; immunite, jour 29)
#   ligne 11 (30 nov.)          -> ep. 13
# Sur deux episodes, le confort va au premier et l'immunite au dernier ; deux
# conforts sur la meme ligne vont chacun a son soir, dans l'ordre.
RENUMEROTATION = {
    ("sp7", ".fandom.wiki"): {7: [7, 8], 8: [9], 9: [10], 10: [11, 12], 11: [13]},
}


def _renumeroter(sid, suf, lot, rapport):
    table = RENUMEROTATION.get((sid, suf))
    if not table:
        return lot
    vus = defaultdict(int)
    for e in lot:
        cible = table.get(e["episode"])
        if not cible:
            continue
        if e["type"] == "immunite":
            nouveau = cible[-1]
        else:
            rang = vus[(e["episode"], e["type"])]
            vus[(e["episode"], e["type"])] += 1
            nouveau = cible[min(rang, len(cible) - 1)]
        if nouveau != e["episode"]:
            rapport.append(f"{sid} : {e['type']} de la ligne {e['episode']} "
                           f"renumerote en episode {nouveau} (RENUMEROTATION)")
        e["episode"] = nouveau
    return lot


def _par_initiale(libelle, personnes):
    """« Cécile B » -> la seule Cecile de la saison dont le nom commence par B."""
    m = re.fullmatch(r"(.+?)\s+([A-ZÉÈ])\.?", libelle.strip())
    if not m:
        return None
    lot = [p for p in personnes.get(slug(m.group(1)), [])
           if (p.get("nom_complet") or "").split(" ", 1)[-1][:1].upper() == m.group(2)]
    return lot[0] if len(lot) == 1 else None


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
                candidats.append((suf, _renumeroter(sid, suf, lot, rapport)))
        meilleur = []
        if candidats:
            def rang(c):
                # Un bilan peut s'arreter avant le dernier conseil -- les
                # colonnes d'orientation et de poteaux ferment le tableau. Il
                # ne peut pas aller AU-DELA : c'est le signe d'une autre
                # numerotation, et cet ecart-la seul est penalise.
                # Dans la tolerance, la page la plus PROCHE des conseils passe
                # encore avant la plus fournie : a l'Ile des heros, Wikipedia
                # compte chaque diffusion (13) quand Fandom et le tableau des
                # votes regroupent les soirs coupes par le confinement (11).
                # A volume egal, l'ordre des fichiers choisissait Wikipedia, et
                # les immunites tombaient deux episodes a cote de leur conseil.
                # A egalite stricte, la page francaise passe avant la page
                # anglaise, qui la traduit : au Cambodge, l'anglaise donne
                # l'immunite de l'episode 10 a Vincent, Fandom a Claire -- et
                # la page de Claire compte ses quatre victoires avec celle-la.
                anglaise = c[1][0]["source"] in ("season summary", "challenges")
                trop = _max_episode(c[1]) - attendu - TOLERANCE_EPISODES
                if not attendu:
                    return (0, 0, -len(c[1]), anglaise)
                return (max(0, trop), abs(_max_episode(c[1]) - attendu),
                        -len(c[1]), anglaise)
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
        # (episode, chef) des conforts qu'une source ecrit « Équipe de X ». Le
        # rapprochement se fait par le CHEF, a deux episodes pres : les deux
        # pages ne numerotent pas toujours de meme (Ile des heros).
        equipes_ailleurs = [(x["episode"], slug(RE_EQUIPE.match(l).group(1)))
                            for _, lot in candidats for x in lot
                            if x["type"] == "confort"
                            for l in x["libelles"] if RE_EQUIPE.match(l)]

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
            refutes = [l for l in libelles
                       if (sid, e["episode"], e["type"], l) in ATTRIBUTIONS_REFUTEES]
            for l in refutes:
                rapport.append(f"{sid} ep.{e['episode']} : {e['type']} attribue a "
                               f"« {l} » — refute, voir ATTRIBUTIONS_REFUTEES")
            libelles = [l for l in libelles if l not in refutes]
            if not libelles:
                continue
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
                elif _par_initiale(libelle, personnes):
                    # « Cécile B » : Fandom separe ses deux Cecile par
                    # l'initiale du nom. On ne rattache que si UNE seule
                    # personne du prenom a un nom qui commence par la lettre.
                    p_ = _par_initiale(libelle, personnes)
                    vainqueurs.append({"libelle": libelle, "type": "personne",
                                       "id": p_["id"], "resolu": True})
                    rapport.append(f"{sid} ep.{e['episode']} : « {libelle} » "
                                   f"rattache par l'initiale du nom → {p_['id']}")
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
            # Un confort d'EQUIPE ne donne de victoire individuelle a personne
            # (regle arretee avec l'utilisateur le 20 octobre 2026). Wikipedia
            # l'ecrit « Équipe de Vincent », Fandom nomme les cinq membres :
            # c'est la meme epreuve, et sans cette regle la forme dependait de
            # la page retenue. On ne le declare que si une source l'ECRIT --
            # compter les noms ne suffit pas : deux duos gagnants (Armes
            # secretes, ep. 1) ou trois recompenses individuelles (4 Terres,
            # ep. 9) ne sont pas une equipe.
            personnes_citees = sum(1 for v in vainqueurs if v["type"] == "personne")
            if (e["type"] == "confort" and forme == "individuelle"
                    and personnes_citees >= 3
                    and any(abs(ep - e["episode"]) <= 2
                            and chef in {slug(v["libelle"]) for v in vainqueurs}
                            for ep, chef in equipes_ailleurs)):
                forme = "collective"
                rapport.append(f"{sid} ep.{e['episode']} : confort a "
                               f"{personnes_citees} noms, « équipe » pour l'autre "
                               f"source — confort d'equipe, collectif")
            epreuves.append({
                "saison": sid,
                "episode": e["episode"],
                "type": e["type"],
                "forme": forme,
                "vainqueurs": vainqueurs,
                "source": e["source"],
            })
    epreuves = _fondre_les_immunites_de_tribus(epreuves, rapport)
    epreuves = _oter_les_trios_de_finale(epreuves, rapport)
    return _oter_les_immunites_dementies(epreuves, elimines_du_soir, rapport)


def _fondre_les_immunites_de_tribus(epreuves, rapport):
    """Deux tribus immunisees le meme soir : UNE epreuve, deux gagnantes.

    Avec trois ou quatre tribus, seule la derniere va au conseil. Fandom
    ecrit les protegees dans deux colonnes, la page anglaise du Cambodge dans
    deux lignes : lues telles quelles, elles faisaient deux epreuves la ou il
    n'y en a qu'une, et le compte des immunites gonflait d'une par soir. On ne
    fond que des immunites COLLECTIVES -- les deux immunites individuelles,
    hommes puis femmes, du premier soir de la Legende restent deux epreuves.
    """
    gardees, par_soir = [], {}
    for e in epreuves:
        de_tribus = (e["type"] == "immunite" and e.get("forme") == "collective"
                     and all(v["type"] == "tribu" for v in e["vainqueurs"]))
        cle = (e["saison"], e["episode"])
        if de_tribus and cle in par_soir:
            deja = par_soir[cle]
            noms = {v["libelle"] for v in deja["vainqueurs"]}
            deja["vainqueurs"] += [v for v in e["vainqueurs"] if v["libelle"] not in noms]
            rapport.append(f"{e['saison']} ep.{e['episode']} : immunite de "
                           f"{', '.join(v['libelle'] for v in deja['vainqueurs'])} "
                           f"— une epreuve, plusieurs tribus protegees")
            continue
        if de_tribus:
            par_soir[cle] = e
        gardees.append(e)
    return gardees


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


def _oter_les_trios_de_finale(epreuves, rapport):
    """Une « immunite » individuelle a trois noms, au dernier episode, n'en est pas une.

    Les resumes de saison (Nicoya, Vanuatu, Palawan, Caramoan) et le tableau
    « Challenges » de Raja Ampat ecrivent, dans la colonne de l'immunite du
    dernier episode, les TROIS qualifies pour les poteaux : ce sont les
    rescapes d'une epreuve eliminatoire, pas les vainqueurs d'une immunite.
    Les lire comme tels donnait trois victoires de plus par saison, et trois
    « immunises » dont l'un partait le soir meme -- la probabilite de partir
    sous immunite, qui doit valoir zero, valait 3 sur 130.

    La regle est etroite a dessein : trois noms ou plus, immunite
    individuelle, dernier episode de la saison. Une immunite a deux noms (un
    homme et une femme, un duo) reste une immunite. Les epreuves de finale
    sont deja exclues ailleurs ; celle-ci passait parce que la source la
    range sous « Immunite ».
    """
    dernier = defaultdict(int)
    for e in epreuves:
        if isinstance(e.get("episode"), int):
            dernier[e["saison"]] = max(dernier[e["saison"]], e["episode"])

    def trio(e):
        return (e.get("type") == "immunite" and e.get("forme") == "individuelle"
                and len(e.get("vainqueurs") or []) >= 3
                and e.get("episode") == dernier.get(e["saison"]))

    # Le trio signe la finale, et TOUTE l'immunite de ce soir-la en releve :
    # les resumes anglais l'ecrivent sur deux lignes sans en-tete, le trio
    # qualifie puis le gagnant des poteaux (Amel, Linda, Emilie, Jade,
    # Christelle). Ecarter le seul trio laissait ce dernier compte comme une
    # immunite, quand les tableaux francais s'arretent avant les poteaux.
    finales = {(e["saison"], e["episode"]) for e in epreuves if trio(e)}
    gardees = []
    for e in epreuves:
        if e.get("type") == "immunite" and (e["saison"], e.get("episode")) in finales:
            noms = ", ".join(v.get("libelle") or "?" for v in e["vainqueurs"])
            quoi = "trio des poteaux" if trio(e) else "gagnant des poteaux"
            rapport.append(f"{e['saison']} ep.{e['episode']} : « immunite » de "
                           f"finale ({noms}) — {quoi}, pas une immunite : ecartee")
            continue
        gardees.append(e)
    return gardees


def _oter_les_immunites_dementies(epreuves, elimines, rapport):
    """Une immunite individuelle gagnee par celui qui part le soir meme n'existe pas.

    Les deux faits ne peuvent pas tenir ensemble : l'immunite protege du
    conseil. Quand ils se contredisent, c'est le conseil qui gagne -- il est
    atteste par ses bulletins, quand l'immunite ne l'est que par un nom dans
    une cellule.

    Le seul cas rencontre -- Maxime, Revanche des 4 Terres -- n'etait pas une
    immunite mal lue mais un tableau mal NUMEROTE : les epreuves y etaient
    rangees un episode trop loin, et l'immunite de l'episode 12 tombait sur
    le soir de son elimination. Depuis que les numeros se lisent dans le
    modele « {{13e|épisode}} », plus rien ne se contredit. Le garde-fou reste :
    on retire la seule attribution qui se contredit, et on garde les autres.
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
    saisons = donnees.charger(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = donnees.charger(open(os.path.join(RACINE, "_data", "participations.yml")))
    chemin_conseils = os.path.join(RACINE, "_data", "conseils.yml")
    conseils = (donnees.charger(open(chemin_conseils))
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

    refutees = [r for r in rapport if "ATTRIBUTIONS_REFUTEES" in r]
    if refutees:
        print(f"\nattributions refutees par une autre source ({len(refutees)}) :")
        for r in refutees:
            print("  " + r)

    trios = [r for r in rapport if "pas une immunite : ecartee" in r]
    if trios:
        print(f"\n« immunites » de finale ecartees ({len(trios)}) :")
        for r in trios:
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
            donnees.ecrire(epreuves, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
