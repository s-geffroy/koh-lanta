#!/usr/bin/env python3
"""Ecrit _data/conseils.yml a partir des matrices de votes des pages sources.

Les tables de votes ne designent les gens que par leur prenom. Ce script les
rattache aux participations deja constituees, pour que chaque bulletin porte un
identifiant utilisable et non une chaine de caracteres.

Un prenom porte par deux personnes d'une meme saison (deux Lea en 25, deux
Cecile en 26, deux Jerome en 27) n'est PAS devine : le bulletin garde le prenom
et signale que le rattachement a echoue.
"""
import os
import sys
from collections import defaultdict

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
WIKI = os.environ.get("KL_WIKI", os.path.join(RACINE, "specs", "sources", "wiki"))

from parse_fandom import slug
from parse_votes import parse_page

# La matrice titre elle-meme la colonne du scrutin final. Ces en-tetes viennent
# de la source : ils ne sont pas devines, et ils rattrapent les deux cas que la
# detection par le nom du vainqueur laissait passer -- la ligne du FINALISTE
# battu, qui ne porte jamais le nom d'un vainqueur, et celle du gagnant dont le
# nom ne se resout pas (« Ugo Lartiche Ugo »).
EN_TETES_LAUREAT = {"gagnant", "gagnante", "gagnants", "gagnantes",
                    "vainqueur", "vainqueure", "vainqueurs"}
EN_TETES_FINALISTE = {"finaliste", "finalistes"}
EN_TETES_JURY = EN_TETES_LAUREAT | EN_TETES_FINALISTE


def entete_de_colonne(episode):
    """Le libelle de la colonne, normalise -- ou "" si c'est un numero."""
    return episode.strip().lower() if isinstance(episode, str) else ""

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Detail des conseils : qui part, avec combien de voix, et le bulletin de
# chacun. Produit par tools/extraction/construire_conseils.py depuis les
# matrices « Detail des votes » du wiki Fandom francophone et de Wikipedia.
#
# `annule: true` sur un bulletin signale une voix rendue nulle par un collier
# d'immunite : c'est ce qui permet de mesurer l'effet reel des colliers.
#
# `type` vaut `elimination` ou `jury`. Le dernier scrutin d'une saison n'est
# pas un conseil : c'est le vote du jury final, et le sens du bulletin y est
# INVERSE -- ecrire un nom veut dire « qu'il gagne », pas « qu'il parte ». Une
# ligne `jury` porte donc `votes_pour`, jamais `elimine` ni `votes_contre`,
# pour qu'aucun calcul ne puisse les confondre.
#
# Ce scrutin tient UNE LIGNE PAR FINALISTE : la colonne du gagnant porte
# `laureat`, celle du finaliste battu porte `finaliste`. Les deux comptent des
# bulletins de jury ; ne lire que la premiere ne montrerait qu'un cote du
# choix.
#
#     tools/atelier python3 tools/extraction/construire_conseils.py --ecrire
#
"""


def index_participations(parts):
    """prenom normalise -> liste de participations, par saison.

    Le nom COMPLET entre dans le meme index, sous sa propre cle. Il ne sert
    qu'a rattraper les libelles ou la source donne les deux formes a la suite :
    la cellule « [[Fichier:Ugo.png|75px|link=Ugo Lartiche]]<br />Ugo » sort de
    l'extraction en « Ugo Lartiche Ugo », et aucune des deux moities seules
    n'est ce qui est ecrit.
    """
    idx = defaultdict(lambda: defaultdict(list))
    complets = defaultdict(lambda: defaultdict(list))
    for p in parts:
        idx[p["saison"]][slug(p["nom"])].append(p)
        if p.get("nom_complet"):
            complets[p["saison"]][slug(p["nom_complet"])].append(p)
    for sid, table in complets.items():
        idx[sid]["_complets"] = table
    return idx


def _un_seul(cands):
    ids = {p["id"] for p in cands}
    return cands[0]["id"] if len(ids) == 1 else None


def resoudre(nom, index_saison):
    """Rend (identifiant, motif_d_echec).

    Deux passes, toutes deux par egalite EXACTE -- on ne devine jamais.

    1. le libelle entier, contre les prenoms de la saison ;
    2. son plus long prefixe qui soit exactement un NOM COMPLET de la saison.

    La seconde passe n'existe que pour les libelles doubles decrits plus haut.
    Elle ne s'applique qu'a un nom complet, jamais a un prenom nu : « Marie
    Laure » ne doit pas devenir « Marie » parce qu'une Marie joue cette
    saison-la.
    """
    complets = index_saison.get("_complets") or {}
    for table in (index_saison, complets):
        cands = table.get(slug(nom or ""))
        if not cands:
            continue
        if len({p["id"] for p in cands}) > 1:
            return None, "homonyme"
        return cands[0]["id"], None

    mots = (nom or "").split()
    for k in range(len(mots) - 1, 1, -1):
        lot = complets.get(slug(" ".join(mots[:k])))
        if not lot:
            continue
        if len({p["id"] for p in lot}) > 1:
            return None, "homonyme"
        return lot[0]["id"], None
    return None, "inconnu"


def resoudre_parmi(nom, idx, autorises):
    """Resout un prenom en le restreignant a un ensemble d'identifiants.

    Sert la ou la STRUCTURE du scrutin leve l'ambiguite sans qu'on ait rien a
    deviner : sur un vote de jury, la cible est forcement un finaliste, et le
    votant forcement quelqu'un qui ne l'est pas -- un finaliste ne siege pas a
    son propre jury. Quand deux Lea jouent la meme saison et qu'une seule est
    finaliste, « Lea » dans la colonne du jury ne peut designer qu'elle.
    """
    cands = idx.get(slug(nom or ""))
    if not cands:
        return None
    ids = {p["id"] for p in cands} & set(autorises)
    return ids.pop() if len(ids) == 1 else None


def laureat_declare(libelle, saison, idx):
    """Rattrape la colonne du laureat quand son libelle ne se resout pas.

    `saisons.yml` est tenu a la main et tranche les homonymes la ou ils
    existent : « Lea Sahin » plutot que « Lea », parce que deux Lea jouent
    cette saison-la. Ce n'est donc pas une devinette, c'est la seule source du
    depot qui sache repondre -- et on ne s'en sert qu'a deux conditions : le
    conseil doit etre une colonne du scrutin FINAL, et le prenom du vainqueur
    declare doit etre exactement celui que la colonne porte en tete.
    """
    tete = slug((libelle or "").split()[0]) if (libelle or "").split() else ""
    if not tete:
        return None
    trouves = set()
    for declare in saison.get("vainqueurs") or []:
        pid, _ = resoudre(declare, idx)
        if not pid:
            continue
        for cands in idx.values():
            if not isinstance(cands, list):
                continue
            for p in cands:
                if p["id"] == pid and slug(p["nom"]) == tete:
                    trouves.add(pid)
    return trouves.pop() if len(trouves) == 1 else None


def completer_par_seconde_source(base, autre, sid, rapport):
    """Ajoute a `base` les bulletins que seule `autre` connait.

    L'appariement se fait par EPISODE, et seulement quand chaque source n'y
    tient qu'un conseil. Sinon on s'abstient : un episode a deux conseils --
    une egalite suivie d'un second vote -- se decoupe differemment d'une source
    a l'autre, et apparier au nom de l'elimine y confondrait le premier tour
    avec le second. C'est ce qui produisait sept faux desaccords.

    Rend (bulletins vus des deux cotes, accords, ajouts, desaccords). On ne
    remplace jamais : un desaccord laisse la valeur de la source de reference
    et remonte au rapport.
    """
    par_episode_autre = {}
    for c in autre:
        par_episode_autre.setdefault(str(c.get("episode")), []).append(c)
    par_episode_base = {}
    for c in base:
        par_episode_base.setdefault(str(c.get("episode")), []).append(c)

    communs = accords = ajouts = desaccords = 0
    for episode, lot in par_episode_base.items():
        jumeaux = par_episode_autre.get(episode) or []
        if len(lot) != 1 or len(jumeaux) != 1:
            continue
        c, jumeau = lot[0], jumeaux[0]
        # Meme episode, mais est-ce le meme conseil ? Le nom de l'elimine doit
        # au moins commencer pareil : une source ecrit « Thierry Villette », la
        # seconde « Thierry ».
        a, b_ = slug(c.get("elimine") or ""), slug(jumeau.get("elimine") or "")
        if not a or not b_ or a.split("-")[0] != b_.split("-")[0]:
            continue
        connus = {x["votant"]: x for x in c["votes"]}
        for x in jumeau["votes"]:
            if x["votant"] in connus:
                communs += 1
                # On compare les noms normalises : « Eric » et « Éric » sont la
                # meme personne, et leur difference n'est pas un desaccord.
                if slug(connus[x["votant"]]["cible"]) == slug(x["cible"]):
                    accords += 1
                else:
                    desaccords += 1
                    rapport.append(
                        f"{sid} ep.{c['episode']} : « {x['votant']} » vise "
                        f"« {connus[x['votant']]['cible']} » chez l'une des sources "
                        f"et « {x['cible']} » chez l'autre — la reference est gardee")
            else:
                c["votes"].append(dict(x, complement=True))
                ajouts += 1
    return communs, accords, ajouts, desaccords


def construire(saisons, parts, rapport):
    index = index_participations(parts)
    # Le vainqueur d'une saison ne peut pas avoir ete elimine au conseil : si
    # une matrice le donne « sortant », c'est qu'on lit le vote du jury final.
    # La cle porte la saison : l'identifiant seul est celui de la PERSONNE, et
    # un vainqueur qui rejoue une autre saison n'y est pas vainqueur pour
    # autant. Sans la saison, on classerait « jury » des conseils ordinaires.
    vainqueurs = {(p["saison"], p["id"]) for p in parts if p.get("sort") == "vainqueur"}
    # Le FINALISTE battu non plus n'a pas ete elimine au conseil : il a perdu
    # au vote du jury. Sa colonne est la seconde moitie du scrutin final, et
    # les matrices ne la titrent pas toujours « Finaliste » -- souvent, elles
    # lui donnent simplement le numero de l'episode, comme a un conseil
    # ordinaire. Le titre ne suffit donc pas : il faut aussi la PLACE.
    finalistes = {(p["saison"], p["id"]) for p in parts if p.get("sort") == "finaliste"}
    places_finales = defaultdict(int)
    for p in parts:
        if p.get("sort") in ("vainqueur", "finaliste"):
            places_finales[p["saison"]] += 1
    # Les prenoms portes par deux aventuriers d'une meme saison. Ils servent au
    # lecteur de matrice, qui sans eux confondrait « Lea vote pour Lea » avec la
    # diagonale du tableau.
    compte_prenoms = defaultdict(lambda: defaultdict(int))
    for p in parts:
        compte_prenoms[p["saison"]][slug(p["nom"])] += 1
    homonymes = {sid: {n for n, k in table.items() if k > 1}
                 for sid, table in compte_prenoms.items()}
    conseils = []
    accord = {"communs": 0, "accord": 0, "ajoutes": 0, "desaccords": 0}

    for s in saisons:
        if s.get("annulee"):
            continue
        sid = s["id"]
        # La source de reference est la lecture la plus riche des deux ; l'autre
        # est gardee pour completer et pour verifier.
        lectures = []
        for suffixe in (".fandom.wiki", ".wiki"):
            chemin = os.path.join(WIKI, sid + suffixe)
            if not os.path.exists(chemin):
                continue
            try:
                lus = parse_page(open(chemin, encoding="utf-8").read(), sid,
                                 homonymes=homonymes.get(sid) or set())
            except Exception as e:
                rapport.append(f"{sid} : lecture des votes impossible ({suffixe}) — {e}")
                continue
            lectures.append((sum(len(c["votes"]) for c in lus), suffixe, lus))
        lectures.sort(key=lambda x: -x[0])
        meilleure = lectures[0][2] if lectures else []
        seconde = lectures[1][2] if len(lectures) > 1 else None

        if not meilleure:
            rapport.append(f"{sid} : aucune matrice de votes exploitable")
            continue

        # La seconde source complete la premiere, conseil par conseil : chacune
        # a des trous, et ce ne sont pas les memes. On n'ajoute qu'un bulletin
        # dont le VOTANT est absent de la source de reference -- jamais on ne
        # remplace une valeur. Les bulletins presents des deux cotes servent
        # d'epreuve croisee : leur taux d'accord mesure la fiabilite du releve,
        # et il est publie.
        if seconde:
            croisement = completer_par_seconde_source(meilleure, seconde, sid, rapport)
            accord["communs"] += croisement[0]
            accord["accord"] += croisement[1]
            accord["ajoutes"] += croisement[2]
            accord["desaccords"] += croisement[3]

        idx = index.get(sid, {})
        au_bout_ids = {pid for (s2, pid) in vainqueurs | finalistes if s2 == sid}
        jures_possibles = {p["id"] for p in parts
                           if p["saison"] == sid and p["id"] not in au_bout_ids}
        # Bornes du vote de jury, calculees avant la boucle : le dernier numero
        # de conseil de la saison, et le nombre de gens arrives au bout. Le
        # scrutin final tient UNE COLONNE PAR PERSONNE qui l'a atteint -- deux
        # d'ordinaire, trois quand le jury a sacre deux laureats -- et ce sont
        # les dernieres colonnes de la matrice.
        #
        # Sur une saison EN COURS, les sorts ne sont pas encore joues : la
        # fenetre serait grande ouverte et avalerait de vrais conseils. On s'en
        # tient alors au titre de colonne, qui ne se trompe pas.
        dernier_conseil = max((c["numero"] for c in meilleure), default=0)
        nb_places = (0 if s.get("en_cours")
                     else max(1, places_finales.get(sid) or len(s.get("vainqueurs") or [])))
        for c in meilleure:
            elimine_id, echec = resoudre(c["elimine"], idx)
            if echec:
                rapport.append(f"{sid} conseil {c['numero']} : elimine « {c['elimine']} » "
                               f"non rattache ({echec})")
            bulletins = []
            for b in c["votes"]:
                vid, e1 = resoudre(b["votant"], idx)
                cid, e2 = resoudre(b["cible"], idx)
                if e1 or e2:
                    rapport.append(f"{sid} conseil {c['numero']} : bulletin "
                                   f"« {b['votant']} » -> « {b['cible']} » non rattache "
                                   f"({e1 or ''}{'/' if e1 and e2 else ''}{e2 or ''})")
                bulletins.append({
                    "votant": vid or b["votant"],
                    "votant_rattache": bool(vid),
                    "cible": cid or b["cible"],
                    "cible_rattachee": bool(cid),
                    "annule": b["annule"],
                })
            # Nommer le vainqueur ne suffit pas a faire un vote de jury : il
            # faut aussi que le conseil soit a sa place. Une saison a k
            # vainqueurs declares tient k scrutins de jury -- un par laureat
            # quand le jury s'est partage -- et ce sont les k derniers. Un
            # conseil de milieu de saison qui donne le vainqueur « sortant »
            # n'est pas un vote de jury : c'est une extraction fautive, et on
            # prefere ne rien affirmer plutot que d'affirmer faux.
            final = nb_places > 0 and c["numero"] > dernier_conseil - nb_places
            entete = entete_de_colonne(c["episode"])
            if not elimine_id and (final or entete in EN_TETES_JURY):
                repeche = laureat_declare(c["elimine"], s, idx)
                if repeche:
                    rapport.append(f"{sid} conseil {c['numero']} : colonne du "
                                   f"scrutin final rattachee au vainqueur declare "
                                   f"dans saisons.yml (« {c['elimine']} » → {repeche})")
                    elimine_id = repeche
            gagnant = bool(elimine_id) and (sid, elimine_id) in vainqueurs
            battu = bool(elimine_id) and (sid, elimine_id) in finalistes
            jury = ((gagnant or battu) and final) or entete in EN_TETES_JURY
            if gagnant and not final and entete not in EN_TETES_JURY:
                rapport.append(f"{sid} conseil {c['numero']} : ABERRANT — "
                               f"« {c['elimine']} » gagne la saison mais serait "
                               f"sortant au conseil {c['numero']}/{dernier_conseil} ; "
                               f"elimine laisse non rattache")
                elimine_id = None
            # Le scrutin final tient UNE LIGNE PAR FINALISTE : celle du gagnant
            # et celle du battu. Les deux sont des bulletins de jury ; seule
            # change la personne au sommet de la colonne.
            laureat = gagnant or (entete in EN_TETES_LAUREAT and not battu)
            if jury:
                rapport.append(
                    f"{sid} conseil {c['numero']} : vote du JURY FINAL, colonne "
                    f"{'du laureat' if laureat else 'du finaliste battu'} "
                    f"(« {c['elimine']} » n'est pas sortant)")
            commun = {
                "saison": sid,
                "numero": c["numero"],
                "type": "jury" if jury else "elimination",
                "complet": c.get("complet", False),
                "episode": c["episode"],
            }
            if jury:
                champ = "laureat" if laureat else "finaliste"
                commun.update({
                    champ: elimine_id or c["elimine"],
                    champ + "_rattache": bool(elimine_id),
                    "votes_pour": c["votes_contre"],
                })
            else:
                commun.update({
                    "elimine": elimine_id or c["elimine"],
                    "elimine_rattache": bool(elimine_id),
                    "votes_contre": c["votes_contre"],
                })
            commun["votes_exprimes"] = c["votes_exprimes"]
            # Une voix barree dans la matrice n'a pas toujours la meme cause.
            # Si SEULE une partie des bulletins est barree, c'est qu'un objet
            # d'immunite a protege quelqu'un : les autres voix comptent, et
            # quelqu'un sort. Si TOUS le sont, c'est le tour entier qui est
            # nul -- egalite suivie d'un second vote, le plus souvent. Les
            # confondre, c'est attribuer aux colliers des annulations qui ne
            # leur doivent rien.
            barres = [b for b in bulletins if b["annule"]]
            if barres:
                commun["annulation"] = ("totale" if len(barres) == len(bulletins)
                                        else "partielle")
                commun["voix_annulees"] = len(barres)
                if commun["annulation"] == "partielle":
                    proteges = sorted({b["cible"] for b in barres})
                    commun["proteges"] = proteges
            if jury:
                # Les homonymes que la structure du scrutin suffit a trancher.
                for b_ in bulletins:
                    if not b_["cible_rattachee"]:
                        pid = resoudre_parmi(b_["cible"], idx, au_bout_ids)
                        if pid:
                            b_["cible"], b_["cible_rattachee"] = pid, True
                    if not b_["votant_rattache"]:
                        pid = resoudre_parmi(b_["votant"], idx, jures_possibles)
                        if pid:
                            b_["votant"], b_["votant_rattache"] = pid, True
            commun["votes"] = bulletins
            conseils.append(commun)

    if accord["communs"]:
        rapport.append(
            f"epreuve croisee des deux sources : {accord['communs']} bulletins "
            f"presents des deux cotes, {accord['accord']} identiques "
            f"({100.0 * accord['accord'] / accord['communs']:.1f} %), "
            f"{accord['desaccords']} divergents ; "
            f"{accord['ajoutes']} bulletins ajoutes par la seconde source")
    return conseils, accord


def main():
    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    rapport = []
    conseils, accord = construire(saisons, parts, rapport)

    bulletins = sum(len(c["votes"]) for c in conseils)
    rattaches = sum(1 for c in conseils for b in c["votes"]
                    if b["votant_rattache"] and b["cible_rattachee"])
    jurys = [c for c in conseils if c["type"] == "jury"]
    print(f"conseils   : {len(conseils)} dont {len(jurys)} votes de jury final")
    print(f"bulletins  : {bulletins}")
    print(f"rattaches  : {rattaches}  ({100*rattaches/bulletins:.1f} %)")
    if accord["communs"]:
        print(f"epreuve croisee : {accord['accord']}/{accord['communs']} bulletins "
              f"identiques dans les deux sources "
              f"({100.0 * accord['accord'] / accord['communs']:.1f} %), "
              f"{accord['ajoutes']} ajoutes, {accord['desaccords']} divergents")

    from collections import Counter
    motifs = Counter(r.split("(")[-1].rstrip(")") for r in rapport if "non rattache" in r)
    if motifs:
        print("\nechecs de rattachement :", dict(motifs))
    autres = [r for r in rapport if "non rattache" not in r]
    if autres:
        print(f"\nautres remarques ({len(autres)}) :")
        for r in autres[:12]:
            print("  " + r)

    if "--ecrire" in sys.argv:
        chemin = os.path.join(RACINE, "_data", "conseils.yml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE)
            yaml.safe_dump(conseils, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
        # L'epreuve croisee est un resultat, pas un message : elle est publiee.
        croise = os.path.join(RACINE, "_data", "croisement_votes.yml")
        with open(croise, "w", encoding="utf-8") as f:
            f.write("# Fichier genere par tools/extraction/construire_conseils.py.\n"
                    "# Ne pas editer a la main : toute modification sera ecrasee.\n")
            yaml.safe_dump({
                "bulletins_communs": accord["communs"],
                "identiques": accord["accord"],
                "divergents": accord["desaccords"],
                "part_identiques": (round(100.0 * accord["accord"] / accord["communs"], 1)
                                    if accord["communs"] else None),
                "ajoutes_par_seconde_source": accord["ajoutes"],
            }, f, allow_unicode=True, sort_keys=False)
        print(f"ecrit : {croise}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
