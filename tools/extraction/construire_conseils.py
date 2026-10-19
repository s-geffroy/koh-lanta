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
import re
import sys
from collections import defaultdict

# Le module qui ecrit et relit _data/ (virgule decimale), dans tools/.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import donnees  # noqa: E402

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


# LES COQUILLES DES MATRICES DE VOTES, chacune verifiee contre la source. Le
# nom du fichier photo de la meme case dit le vrai nom, ou la fiche du
# candidat le dit : « [[Fichier:Irya_Koh_Lanta_Caramoan.png]]<br />Iria ».
# Une coquille non corrigee laisse le bulletin sans personne -- et quand elle
# touche l'elimine, le conseil entier perd son decompte (0 voix lue contre
# lui). Cle : (saison, libelle fautif). Le libelle fautif peut ouvrir un
# libelle double, « Maire Parmentier Marie » : il est remplace en tete.
COQUILLES_VOTES = {
    ("s07", "Marylise"): "Maryline",      # Maryline Hemelsdael
    ("s07", "Pascal"): "Pascale",          # Pascale Bodin, seule « Pasc… » de la saison
    ("s08", "Iria"): "Irya",               # photo « Irya_Koh_Lanta_Caramoan »
    ("s09", "Rodolhphe"): "Rodolphe",      # photo « Rodolphe_Koh_Lanta_Palau »
    ("s12", "Maire Parmentier"): "Marie Parmentier",  # « link=Maire Parmentier »
}

# Ce qu'une case de matrice ecrit quand il n'y a PAS de bulletin : la colonne
# ou un votant a ete evacue, un tiret egare. Lu comme un nom, cela fabriquait
# des bulletins visant « Evacuee ».
NON_BULLETINS = {"evacuee", "evacue", "-"}

# Ce que la ligne « Elimine » ecrit quand personne ne sort ce soir-la : un
# conseil fini sur une egalite, tranchee plus tard par un duel ; une colonne
# barree. Lu comme un nom, cela donnait un conseil dont l'elimine s'appelait
# « Egalite ».
SANS_ELIMINE = {"egalite", "/"}

# Deux voix sur la meme cible dans UNE case, et la source dit pourquoi :
# « Brice/Brice » -- « Le vote noir de Thierry est comptabilise au conseil, il
# a donc deux votes. » Le bulletin de Thierry, plus une voix de mecanique.
DOUBLES = {
    ("s12", "Brice/Brice"): "Vote noir",
}


# LE VOTE NOIR DE L'ELIMINE : de 2011 a 2016, celui qui sort au conseil laisse
# une derniere voix, qui compte au conseil suivant (s14 : « Apres son
# elimination, le candidat elimine doit voter pour un candidat restant »). La
# matrice la range dans la ligne de l'elimine, dans une case PEINTE EN NOIR --
# barree quand elle n'a pas ete comptee. Lue comme un vote ordinaire, elle
# faisait voter des gens deja partis. Voir `parse_votes.RE_CASE_NOIRE`.


# LES COLONNES QUE LA SOURCE REND INCOHERENTES, et qu'aucune seconde source ni
# aucune note ne permet de reconcilier. Leurs cases contredisent l'elimine
# qu'elles annoncent : on ne devine pas lequel des deux a raison. Les bulletins
# restent, le conseil sort des mesures au bulletin pres (`complet: false`), et
# la raison est ecrite dans la donnee. Cle : (saison, numero de colonne).
COLONNES_INCOHERENTES = {
    ("s03", 10): "cases Richard 3, Alexandra 2, Alexandre 1 ; la source fait sortir "
                 "Alexandre et annonce 4/6 — aucune seconde source ni note pour trancher",
    ("s10", 6): "cases Jean-Pierre 3, Marine 2, Aurelie 1 ; la source fait sortir "
                "Marine et annonce 3/6 — aucune seconde source ni note pour trancher",
}


def corriger_libelle(sid, libelle):
    if not isinstance(libelle, str):
        return libelle
    # « Clemence Clemence » : le meme prenom ecrit deux fois, nom de lien puis
    # texte affiche, quand le lien ne porte pas le nom de famille.
    mots = libelle.split()
    if len(mots) == 2 and mots[0] == mots[1]:
        libelle = mots[0]
    for (s_, faux), vrai in COQUILLES_VOTES.items():
        if s_ == sid and (libelle == faux or libelle.startswith(faux + " ")):
            return vrai + libelle[len(faux):]
    return libelle


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
# `mecanique: Vote noir` avec `auteur` : de 2011 a 2016, la derniere voix que
# l'elimine laisse au conseil suivant. Son auteur est connu, mais il n'est plus
# en jeu : il n'est donc pas `votant`.
#
# `votant: null` avec un champ `mecanique` : une voix que PERSONNE n'a ecrite.
# Depuis 2017 le jeu en impose -- vote noir, penalite, malediction -- et la
# source les compte dans son total. Elles comptent donc au-dessus de la cible,
# jamais au-dessous d'un votant : `votant_rattache` est faux, ce qui les ecarte
# d'office de toute mesure cote emetteur.
#
# `cible_source` : sur un bulletin, la cible que la case ecrivait quand elle
# designait quelqu'un deja sorti du jeu, et que le total annonce a permis de
# rendre a l'elimine.
#
# `votes_contre_annonce` : le total que la source ecrivait, quand ses propres
# bulletins -- tous lus -- en portent un autre. `votes_contre` dit alors ce que
# disent les bulletins. `incoherence_source` : une colonne dont les cases
# contredisent l'elimine, sortie des mesures au bulletin pres.
#
# `voix_annulees` : les voix qu'un objet d'immunite a annulees -- bulletins
# ecrits, plus les voix de mecanique visant la meme personne protegee.
# `voix_mecanique_non_comptees` : les voix de mecanique barrees pour une autre
# raison, le plus souvent une cible deja sortie du jeu.
# `bulletins_ecartes` (sur une sortie) : une case egaree dans une colonne
# d'abandon annoncee a zero voix, gardee pour la tracabilite.
#
# `type: sortie` : une sortie OU PERSONNE NE VOTE -- abandon, orientation,
# poteaux, duel, ambassadeurs. La ligne est gardee parce qu'elle date la
# sortie ; elle porte `nature`, et elle n'est pas un conseil.
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
        # `nom_source` : la forme que la SOURCE ecrit, quand le site publie le
        # titre canonique du wiki a la place. Les tableaux de votes, eux, n'ont
        # pas suivi le renommage -- sans cet alias, un bulletin cesse de se
        # rattacher le jour ou une fiche change de nom.
        if p.get("nom_source"):
            complets[p["saison"]][slug(p["nom_source"])].append(p)
    for sid, table in complets.items():
        idx[sid]["_complets"] = table
    # Le PRENOM tire du nom complet, quand le champ `nom` porte deja le nom
    # entier. Sur les editions de celebrites, la table de saison donne « Frank
    # Lebœuf » la ou la matrice de votes ecrit « Frank » : sans cette cle, une
    # saison ENTIERE restait sans un bulletin rattache. Elle ne sert qu'en
    # dernier recours, et `resoudre` y applique la meme regle qu'ailleurs : un
    # prenom porte par deux personnes ne designe personne.
    prenoms = defaultdict(lambda: defaultdict(list))
    for p in parts:
        mots = (p.get("nom_complet") or "").split()
        if len(mots) > 1:
            prenoms[p["saison"]][slug(mots[0])].append(p)
    for sid, table in prenoms.items():
        idx[sid]["_prenoms"] = table
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
    prenoms = index_saison.get("_prenoms") or {}
    for table in (index_saison, complets, prenoms):
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


def recoller_le_scrutin_final(lignes, rapport):
    """Remet chaque bulletin de jury dans la colonne de celui qu'il nomme.

    Le scrutin final tient une colonne par finaliste, et un bulletin appartient
    a la colonne de la personne dont il porte le nom : c'est la definition meme
    du scrutin. Une matrice le respecte presque toujours -- mais celle du
    Totem maudit etale le jury sur trois colonnes et y range chaque jure selon
    la ligne qu'il occupe, pas selon le nom qu'il ecrit. Trois bulletins s'y
    retrouvaient dans la mauvaise colonne, et le vote a egalite qui a fait deux
    vainqueurs devenait invisible.

    Une fois recolle, le decompte de chaque colonne EST le nombre de ses
    bulletins. On s'en sert pour corriger le total annonce, mais seulement
    quand le scrutin est complet -- la somme des bulletins atteignant le nombre
    de voix que la source annonce. Sans cette garantie, un total lu vaut mieux
    qu'un total recalcule sur un relevé partiel.
    """
    jurys = [x for x in lignes if x["type"] == "jury"]
    if len(jurys) < 2:
        jurys = [x for x in jurys if x.get("votes")]
    if not jurys:
        return
    place = {}
    for x in jurys:
        pid = x.get("laureat") if "laureat" in x else x.get("finaliste")
        if x.get("laureat_rattache") or x.get("finaliste_rattache"):
            place[pid] = x
    if len(place) < 2:
        return

    tous = [b for x in jurys for b in x.get("votes") or []]
    deplaces = 0
    for x in jurys:
        x["votes"] = []
    for b in tous:
        destination = place.get(b["cible"]) if b.get("cible_rattachee") else None
        if destination is None:
            destination = jurys[-1]          # on ne perd aucun bulletin
        destination["votes"].append(b)
    for x in jurys:
        pid = x.get("laureat") if "laureat" in x else x.get("finaliste")
        deplaces += sum(1 for b in x["votes"]
                        if b.get("cible_rattachee") and b["cible"] != pid)

    exprimes = max((x.get("votes_exprimes") or 0 for x in jurys), default=0)
    complet = exprimes and len(tous) == exprimes
    for x in jurys:
        lus = len(x["votes"])
        if complet and x.get("votes_pour") is not None and x["votes_pour"] != lus:
            sid = x["saison"]
            pid = x.get("laureat") if "laureat" in x else x.get("finaliste")
            rapport.append(f"{sid} conseil {x['numero']} : la source annonce "
                           f"{x['votes_pour']} voix pour « {pid} » et en fait lire "
                           f"{lus} ; le scrutin etant complet, ce sont les "
                           f"bulletins qui font foi")
        if complet:
            x["votes_pour"] = lus


RE_INITIALE = re.compile(r"^(\S+)\s+\(?([A-ZÀ-Ý])\.?\)?$")


def trancher_homonyme(nom, idx, presents, sorts_admis=None, sorts=None):
    """Un prenom porte par deux personnes, tranche par une PREUVE -- ou pas.

    Trois preuves, dans cet ordre, et aucune n'est une devinette :

    1. l'INITIALE que la source ecrit : « Cecile B » ne peut etre que celle des
       deux Cecile dont le nom commence par B ;
    2. la PRESENCE : une Cecile sortie au premier conseil n'ecrit plus rien au
       cinquieme. Si une seule des homonymes est encore en jeu, c'est elle ;
    3. pour l'ELIMINE d'un conseil, le TYPE de sortie : des deux Cecile, une
       seule est sortie au conseil -- l'autre a l'orientation.

    Si aucune ne suffit -- deux Jerome tous deux en jeu jusqu'a la fin --, le
    bulletin garde le prenom et reste non rattache. C'est voulu.
    """
    if not isinstance(nom, str) or not nom.strip():
        return None
    m = RE_INITIALE.match(nom.strip())
    tete = slug(m.group(1) if m else nom.split()[0])
    cands = list({p["id"]: p for p in (idx.get(tete) or [])}.values())
    if len(cands) < 2:
        return None
    if m:
        lettre = slug(m.group(2))
        par_initiale = [p for p in cands
                        if slug(" ".join((p.get("nom_complet") or "").split()[1:]))[:1] == lettre]
        if len(par_initiale) == 1:
            return par_initiale[0]["id"]
    restants = [p for p in cands if p["id"] in presents]
    if len(restants) == 1:
        return restants[0]["id"]
    if sorts_admis is not None and sorts is not None:
        pool = restants or cands
        par_sort = [p for p in pool if sorts.get(p["id"]) in sorts_admis]
        if len(par_sort) == 1:
            return par_sort[0]["id"]
    return None


def trancher_par_ligne(lot, idx, sid, rapport):
    """Une ligne de matrice est une personne : on la rend a celle qui sort la.

    Deux Lea jouent les Chasseurs d'immunite, et la matrice les ecrit « Lea »
    l'une comme l'autre. Le libelle ne prouve rien ; la LIGNE, si : chaque
    votant y tient la sienne d'un bout a l'autre, et cesse d'y voter le soir ou
    il quitte le jeu. On compare donc le DERNIER conseil d'elimination ou vote
    chaque ligne -- en la prenant entiere, bulletins deja rattaches compris --
    au conseil ou sort chacun des homonymes.

    Deux regles, et une verification :
      * une ligne qui s'arrete au conseil ou sort un seul des homonymes est la
        sienne ;
      * s'il ne reste alors qu'une ligne et qu'un homonyme, ils vont ensemble
        (celle qui va au bout est celle du vainqueur) ;
      * une ligne dont un bulletin est DEJA rattache a quelqu'un d'autre
        contredit l'attribution : on s'abstient.

    Deux Jerome sortis les deux derniers soirs, a l'orientation et aux poteaux,
    votent ensemble jusqu'au bout : aucune ligne ne se distingue, rien n'est
    attribue. C'est voulu.

    Les cles `_ligne` et `_libelle` ne servent qu'ici : retirees avant ecriture.
    """
    sortie = {}
    for c in lot:
        if c["type"] == "elimination" and c.get("elimine_rattache"):
            sortie[c["elimine"]] = max(sortie.get(c["elimine"], 0), c["numero"])
    lignes = defaultdict(lambda: defaultdict(list))   # prenom -> ligne -> bulletins
    derniers = defaultdict(dict)                      # prenom -> ligne -> dernier conseil
    for c in lot:
        if c["type"] != "elimination":
            continue
        for b in c["votes"]:
            lib, lg = b.get("_libelle"), b.get("_ligne")
            if not lib or lg is None:
                continue
            tete = slug(lib.split()[0])
            lignes[tete][lg].append(b)
            derniers[tete][lg] = max(derniers[tete].get(lg, 0), c["numero"])
    for tete, par_ligne in lignes.items():
        cands = {p["id"] for p in (idx.get(tete) or [])}
        if len(cands) < 2 or not any(not b["votant_rattache"]
                                     for bs in par_ligne.values() for b in bs):
            continue
        attribue = {}
        for lg in par_ligne:
            qui = [pid for pid in cands if sortie.get(pid) == derniers[tete][lg]]
            if len(qui) == 1:
                attribue[lg] = qui[0]
        restes_l = [lg for lg in par_ligne if lg not in attribue]
        restes_p = cands - set(attribue.values())
        if len(restes_l) == 1 and len(restes_p) == 1:
            attribue[restes_l[0]] = next(iter(restes_p))
        if len(set(attribue.values())) != len(attribue):
            continue
        contradiction = any(b["votant_rattache"] and b["votant"] != attribue[lg]
                            for lg, bs in par_ligne.items() if lg in attribue for b in bs)
        if contradiction:
            rapport.append(f"{sid} : lignes « {tete} » non attribuees — un bulletin deja "
                           f"rattache contredit l'attribution")
            continue
        n = 0
        for lg, pid in attribue.items():
            for b in par_ligne[lg]:
                if not b["votant_rattache"]:
                    b["votant"], b["votant_rattache"] = pid, True
                    n += 1
        if n:
            rapport.append(f"{sid} : {n} bulletins « {tete} » rendus par ligne de matrice "
                           f"-> {sorted(set(attribue.values()))}")
    for c in lot:
        for b in c["votes"]:
            b.pop("_ligne", None)
            b.pop("_libelle", None)
            b.pop("_noir", None)


# Les sorties qui ne sont PAS un conseil : personne n'y vote. Elles occupent
# pourtant une colonne de la matrice, et c'est voulu -- la colonne date la
# sortie, et `indicateurs._episode_de_sortie` en a besoin.
SORTIES_SANS_VOTE = {"abandon_medical", "abandon_volontaire", "elimine_orientation",
                     "elimine_poteaux", "elimine_duel", "elimine_ambassadeurs"}


def etiqueter_les_sorties(conseils, debut, sorts, rapport):
    """Separe les SORTIES sans vote des conseils, sans les effacer.

    Un abandon sur blessure, une defaite a l'orientation ou aux poteaux ont
    chacun leur colonne dans la matrice des votes, et la chaine en faisait
    autant de « conseils d'elimination » : 112 sorties ou personne n'a vote
    comptaient dans les « 628 conseils » du site, et dans tous les calculs qui
    enchainent les conseils. Le test « elimine-t-on le faible avant la fusion
    et le fort apres ? » y lisait des blesses comme des elimines.

    La ligne reste, parce qu'elle DATE la sortie ; elle prend `type: sortie` et
    `nature`, le sort de la personne. Trois conditions, toutes necessaires :
      * aucun bulletin dans la colonne ;
      * un elimine rattache, dont le sort final est une sortie sans vote ;
      * c'est sa DERNIERE colonne de la saison -- un revenant a pu sortir une
        premiere fois au conseil, et cette colonne-la reste un conseil.

    Les colonnes vides et sans elimine (« / » dans la ligne des elimines) ne
    portent ni personne ni bulletin : elles sont retirees.
    """
    lot = conseils[debut:]
    derniere = {}
    for c in lot:
        if c["type"] != "jury" and c.get("elimine_rattache"):
            derniere[c["elimine"]] = max(derniere.get(c["elimine"], 0), c["numero"])
    garde = []
    for c in lot:
        if c["type"] == "jury":
            garde.append(c)
            continue
        if not c["votes"] and c.get("sans_elimination"):
            rapport.append(f"{c['saison']} conseil {c['numero']} : colonne vide, sans elimine "
                           f"ni bulletin — retiree")
            continue
        nature = sorts.get(c.get("elimine")) if c.get("elimine_rattache") else None
        # Une colonne d'abandon dont la source ANNONCE zero voix, mais qui porte
        # un bulletin egare -- un seul, visant quelqu'un d'autre (Alain au
        # Vietnam, Loic et Margot a Johor). Il n'appartient a aucun conseil : on
        # l'ecarte de la ligne, sans l'effacer, et la colonne est une sortie.
        # Un bulletin qui vise L'ELIMINE lui-meme n'est pas egare : c'est une
        # decision -- le choix du vainqueur des poteaux, celui de deux
        # ambassadeurs. Seuls ceux qui visent quelqu'un d'autre sont ecartes.
        if (c["votes"] and c.get("votes_contre") == 0 and not c.get("votes_exprimes")
                and nature in SORTIES_SANS_VOTE and derniere.get(c["elimine"]) == c["numero"]
                and all(b_["cible"] != c["elimine"] for b_ in c["votes"])):
            c["bulletins_ecartes"] = c["votes"]
            c["votes"] = []
            c.pop("annulation", None); c.pop("voix_annulees", None); c.pop("proteges", None)
            rapport.append(f"{c['saison']} conseil {c['numero']} : colonne d'abandon annoncee a "
                           f"0 voix, {len(c['bulletins_ecartes'])} bulletin(s) egare(s) ecarte(s)")
        if (not c["votes"] and nature in SORTIES_SANS_VOTE
                and derniere.get(c["elimine"]) == c["numero"]):
            c["type"] = "sortie"
            c["nature"] = nature
            for cle in ("votes_contre", "votes_exprimes"):
                if c.get(cle) is None:
                    c.pop(cle, None)
        garde.append(c)
    conseils[debut:] = garde


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


def completer_par_seconde_source(base, autre, sid, rapport, homonymes=()):
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
        connus = {x["votant"]: x for x in c["votes"] if x.get("votant")}
        # Le prenom d'un homonyme ne prouve pas qu'il s'agit d'un NOUVEAU votant.
        # Fandom ecrit « Cecile B », Wikipedia « Cecile » : c'est la meme
        # personne, et l'ajouter faisait voter Cecile Belec deux fois dans
        # trois conseils -- un bulletin de plus que le total annonce.
        tetes_connues = {slug(v.split()[0]) for v in connus if v.split()}
        for x in jumeau["votes"]:
            if not x.get("votant"):
                # Sans votant, rien a apparier : deux bulletins de mecanique
                # partageraient la meme cle et l'un effacerait l'autre.
                continue
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
                tete = slug(x["votant"].split()[0]) if x["votant"].split() else ""
                if tete in homonymes and tete in tetes_connues:
                    rapport.append(f"{sid} ep.{c['episode']} : « {x['votant']} » de la seconde "
                                   f"source non ajoute — prenom d'homonyme deja present")
                    continue
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
            croisement = completer_par_seconde_source(meilleure, seconde, sid, rapport,
                                                      homonymes.get(sid) or set())
            accord["communs"] += croisement[0]
            accord["accord"] += croisement[1]
            accord["ajoutes"] += croisement[2]
            accord["desaccords"] += croisement[3]

        idx = index.get(sid, {})
        debut_saison = len(conseils)
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
        # Ce qu'il faut pour trancher un homonyme par la presence : le sort de
        # chacun, et qui a deja quitte le jeu pour de bon a ce point de la
        # saison. On ne sort quelqu'un du jeu qu'a la sortie qui correspond a
        # son sort FINAL -- un revenant ne quitte pas le jeu a sa premiere
        # elimination.
        sorts = {p["id"]: p.get("sort") for p in parts if p["saison"] == sid}
        sorties_conseil = {"elimine_conseil", "elimine_ambassadeurs"}
        sortis = set()
        # Les libelles de votants, conseil par conseil : un vainqueur que la
        # matrice fait sortir en cours de saison et qu'on voit VOTER ensuite
        # est revenu en jeu (exil, ile, duel). Ce n'est plus une aberration.
        votants_apres = defaultdict(set)
        for c0 in meilleure:
            for b0 in c0["votes"]:
                if b0.get("votant"):
                    votants_apres[c0["numero"]].add(slug(corriger_libelle(sid, b0["votant"])))

        # La DERNIERE colonne ou chacun sort, lue avant la boucle : un revenant
        # sort deux fois, et seule la seconde le retire du jeu. Nathalie Bella,
        # eliminee au conseil 3 de Vanuatu, revient, vote au conseil 10 et y
        # est visee -- la tenir pour partie des le conseil 3 rendait ce
        # bulletin « impossible ».
        derniere_sortie = {}
        for c0 in meilleure:
            pid0, _ = resoudre(corriger_libelle(sid, c0.get("elimine")), idx)
            if pid0:
                derniere_sortie[pid0] = max(derniere_sortie.get(pid0, 0), c0["numero"])

        for c in meilleure:
            presents = set(sorts) - sortis
            c["elimine"] = corriger_libelle(sid, c["elimine"])
            libelle_elimine = (c["elimine"] or "").strip()
            sans_elimine = slug(libelle_elimine) in SANS_ELIMINE or libelle_elimine in SANS_ELIMINE
            if sans_elimine:
                elimine_id, echec = None, None
                rapport.append(f"{sid} conseil {c['numero']} : « {c['elimine']} » en ligne "
                               f"des elimines — personne ne sort ce soir-la")
            else:
                elimine_id, echec = resoudre(c["elimine"], idx)
                if echec in ("homonyme", "inconnu"):
                    elimine_id = trancher_homonyme(
                        c["elimine"], idx, presents,
                        sorts_admis=sorties_conseil if c["votes"] else None, sorts=sorts)
                    if elimine_id:
                        echec = None
                        rapport.append(f"{sid} conseil {c['numero']} : elimine « {c['elimine']} » "
                                       f"homonyme tranche -> {elimine_id}")
            if echec:
                rapport.append(f"{sid} conseil {c['numero']} : elimine « {c['elimine']} » "
                               f"non rattache ({echec})")
            bulletins = []
            votes_lus = []
            for b in c["votes"]:
                b = dict(b, votant=corriger_libelle(sid, b.get("votant")),
                         cible=corriger_libelle(sid, b.get("cible")))
                if slug(b["cible"] or "") in NON_BULLETINS or (b["cible"] or "").strip("-` ") == "":
                    rapport.append(f"{sid} conseil {c['numero']} : case « {b['cible']} » "
                                   f"ecartee — ce n'est pas un bulletin")
                    continue
                double = DOUBLES.get((sid, b["cible"]))
                if double:
                    nom_ = b["cible"].split("/")[0]
                    votes_lus.append(dict(b, cible=nom_))
                    votes_lus.append(dict(b, votant=None, mecanique=double, cible=nom_))
                    rapport.append(f"{sid} conseil {c['numero']} : « {b['cible']} » = un "
                                   f"bulletin de {b['votant']} et une voix de mecanique ({double})")
                    continue
                votes_lus.append(b)
            for b in votes_lus:
                cid, e2 = resoudre(b["cible"], idx)
                if e2 in ("homonyme", "inconnu"):
                    cid = trancher_homonyme(b["cible"], idx, presents)
                    e2 = None if cid else e2
                # Un bulletin de mecanique -- vote noir, penalite, malediction
                # -- n'a PAS de votant : le jeu l'impose, personne ne l'ecrit.
                # Il compte au dessus de la cible et jamais en dessous du
                # votant ; c'est `votant_rattache` a false qui l'ecarte de tous
                # les calculs cote emetteur, exactement comme un votant qu'on
                # n'aurait pas su nommer.
                if b.get("votant") is None:
                    if e2:
                        rapport.append(f"{sid} conseil {c['numero']} : bulletin de "
                                       f"mecanique « {b.get('mecanique')} » -> "
                                       f"« {b['cible']} » non rattache ({e2})")
                    bulletins.append({
                        "votant": None,
                        "votant_rattache": False,
                        "mecanique": b.get("mecanique"),
                        "cible": cid or b["cible"],
                        "cible_rattachee": bool(cid),
                        "annule": b["annule"],
                    })
                    continue
                vid, e1 = resoudre(b["votant"], idx)
                if e1 in ("homonyme", "inconnu"):
                    vid = trancher_homonyme(b["votant"], idx, presents)
                    e1 = None if vid else e1
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
                    "_ligne": b.get("ligne"),
                    "_libelle": b["votant"],
                    "_noir": bool(b.get("noir")),
                })
            # DEUX PREUVES QUI NE SE LISENT QU'A L'ECHELLE DU CONSEIL.
            #
            # L'arithmetique : la source annonce N voix contre l'elimine. Si
            # exactement N bulletins portent le meme libelle que lui, ce sont
            # les siens -- aucune voix n'a pu aller a son homonyme.
            if elimine_id and c.get("votes_contre"):
                meme = [b_ for b_ in bulletins if not b_["cible_rattachee"]
                        and not b_["annule"] and b_["cible"] == c["elimine"]]
                if meme and len(meme) == c["votes_contre"]:
                    for b_ in meme:
                        b_["cible"], b_["cible_rattachee"] = elimine_id, True
                    rapport.append(f"{sid} conseil {c['numero']} : {len(meme)} voix sur "
                                   f"« {c['elimine']} » = les {c['votes_contre']} annoncees "
                                   f"contre l'elimine -> {elimine_id}")
            # L'exclusion : chacun n'ecrit qu'un bulletin par tour. Si l'un des
            # deux homonymes a deja vote dans ce tour, le libelle restant
            # designe l'autre -- a condition qu'il n'en reste qu'un.
            for annule_ in (False, True):
                tour = [b_ for b_ in bulletins if b_["annule"] == annule_ and b_.get("votant")]
                deja = {b_["votant"] for b_ in tour if b_["votant_rattache"]}
                for b_ in tour:
                    if b_["votant_rattache"]:
                        continue
                    mots_ = (b_["votant"] or "").split()
                    cands_ = {p_["id"] for p_ in (idx.get(slug(mots_[0])) or [])} if mots_ else set()
                    reste = (cands_ & presents) - deja
                    libres = [x for x in tour if not x["votant_rattache"]
                              and (x["votant"] or "").split()[:1] == mots_[:1]]
                    if len(cands_) > 1 and len(reste) == 1 and len(libres) == 1:
                        b_["votant"], b_["votant_rattache"] = reste.pop(), True
                        deja.add(b_["votant"])
                        rapport.append(f"{sid} conseil {c['numero']} : votant « {mots_[0]} » "
                                       f"tranche par exclusion -> {b_['votant']}")
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
            revenu = gagnant and any(
                slug(c["elimine"] or "") in v for n, v in votants_apres.items() if n > c["numero"])
            if revenu and not final and entete not in EN_TETES_JURY:
                # Sorti ici, il VOTE plus loin dans la meme matrice : il est
                # revenu en jeu, et il a gagne ensuite. Christina Chevry a
                # Palau. Ce n'est pas le vote du jury, c'est une vraie sortie.
                rapport.append(f"{sid} conseil {c['numero']} : « {c['elimine']} » sort ici, "
                               f"vote plus loin, et gagne la saison — retour en jeu")
                gagnant = False
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
            # LE VOTE NOIR DE L'ELIMINE, lu dans la CASE : la source le peint en
            # noir dans la ligne de son auteur, et le barre quand il n'a pas ete
            # compte. Une fois qu'on sait que la colonne est un conseil et non le
            # scrutin final -- les jures sont des elimines, leur vote est un vrai
            # vote. La voix compte au-dessus de la cible, jamais du cote des
            # votants : son auteur n'est plus en jeu.
            if not jury:
                for i_, b_ in enumerate(bulletins):
                    if not b_.get("_noir"):
                        continue
                    bulletins[i_] = {
                        "votant": None,
                        "votant_rattache": False,
                        "mecanique": "Vote noir",
                        "auteur": b_.get("votant"),
                        "auteur_rattache": bool(b_.get("votant_rattache")),
                        "cible": b_["cible"],
                        "cible_rattachee": b_["cible_rattachee"],
                        "annule": b_["annule"],
                    }
            # Une voix barree dans la matrice n'a pas toujours la meme cause.
            # Si SEULE une partie des bulletins est barree, c'est qu'un objet
            # d'immunite a protege quelqu'un : les autres voix comptent, et
            # quelqu'un sort. Si TOUS le sont, c'est le tour entier qui est
            # nul -- egalite suivie d'un second vote, le plus souvent. Les
            # confondre, c'est attribuer aux colliers des annulations qui ne
            # leur doivent rien.
            #
            # Calcule APRES la lecture du vote noir, et sur les seuls bulletins
            # ECRITS. Un vote noir barre l'est le plus souvent parce que sa
            # cible a deja quitte le jeu -- « Sara ayant quitte le jeu, le vote
            # noir de Mickael n'a pas ete compte » -- et le compter parmi les
            # annulations faisait creer aux colliers des voix qu'ils n'ont pas
            # annulees. Un vote noir barre ne compte pour un objet que si sa
            # cible est AUSSI protegee dans les bulletins ecrits : c'est alors
            # le meme collier qui l'a annule.
            ecrits_ = [b_ for b_ in bulletins if b_.get("votant") is not None]
            barres = [b_ for b_ in ecrits_ if b_["annule"]]
            if barres:
                commun["annulation"] = ("totale" if len(barres) == len(ecrits_)
                                        else "partielle")
                if commun["annulation"] == "partielle":
                    commun["proteges"] = sorted({b_["cible"] for b_ in barres})
            proteges_ = set(commun.get("proteges") or [])
            meca_barres = [b_ for b_ in bulletins if b_.get("votant") is None and b_["annule"]]
            par_objet = [b_ for b_ in meca_barres if b_["cible"] in proteges_]
            if barres or par_objet:
                commun["voix_annulees"] = len(barres) + len(par_objet)
            autres = len(meca_barres) - len(par_objet)
            if autres:
                commun["voix_mecanique_non_comptees"] = autres
            # QUAND LE DEPOUILLEMENT EST COMPLET, LES BULLETINS FONT FOI -- la
            # regle que le scrutin final applique deja. La ligne des totaux de
            # la matrice est un resume saisi a la main : « 1/10 » contre Lionel
            # quand neuf cases sur dix le nomment, « 9/11 » barre au-dessus
            # d'Andrea protegee par un collier, « 6/11 » qui compte le plus vise
            # quand une relique a fait sortir l'autre. Ce total alimente la part
            # de conseils serres : il doit dire ce que disent les bulletins. La
            # valeur de la source est gardee a cote, pour la tracabilite.
            # UN BULLETIN IMPOSSIBLE : une case ecrite qui vise quelqu'un DEJA
            # sorti du jeu pour de bon. A Le Retour des heros, la case de
            # Jean-Bernard nomme Francois-David, elimine deux conseils plus tot.
            # Si le total annonce le prouve exactement -- 4 contre Catherine, 3
            # lus sur elle, 1 case impossible --, la case est la quatrieme voix
            # contre l'elimine, et le total avait raison. Sinon, on ne devine
            # pas : le conseil sort des mesures au bulletin pres.
            if not jury and elimine_id:
                impossibles = [b_ for b_ in bulletins if b_.get("votant") is not None
                               and not b_["annule"] and b_["cible_rattachee"]
                               and b_["cible"] in sortis and b_["cible"] != elimine_id]
                if impossibles:
                    lus_ = sum(1 for b_ in bulletins if not b_["annule"] and b_["cible"] == elimine_id)
                    annonce_ = commun.get("votes_contre")
                    if annonce_ is not None and lus_ + len(impossibles) == annonce_:
                        for b_ in impossibles:
                            b_["cible_source"] = b_["cible"]
                            b_["cible"] = elimine_id
                        rapport.append(f"{sid} conseil {c['numero']} : {len(impossibles)} case(s) visant "
                                       f"quelqu'un deja sorti, rendue(s) a l'elimine — le total "
                                       f"annonce ({annonce_}) le prouve")
                    else:
                        commun["complet"] = False
                        commun["incoherence_source"] = (
                            f"{len(impossibles)} case(s) visant quelqu'un deja sorti, que le total "
                            f"annonce ne permet pas d'expliquer")
            if not jury:
                raison = COLONNES_INCOHERENTES.get((sid, c["numero"]))
                if raison:
                    # Les cases de ces colonnes sont prouvees fausses -- a
                    # Bocas del Toro, deux d'entre elles visent Alexandra,
                    # sortie au premier conseil. Elles n'alimentent donc plus
                    # rien, pas meme les voix recues : elles sont ecartees,
                    # gardees pour la tracabilite. Le total de la source reste.
                    commun["complet"] = False
                    commun["incoherence_source"] = raison
                    commun["bulletins_ecartes"] = bulletins
                    bulletins = []
                elif commun.get("complet") and elimine_id and commun.get("votes_contre") is not None:
                    lus = sum(1 for b_ in bulletins
                              if not b_["annule"] and b_["cible"] == elimine_id)
                    if lus != commun["votes_contre"]:
                        commun["votes_contre_annonce"] = commun["votes_contre"]
                        commun["votes_contre"] = lus
                        rapport.append(f"{sid} conseil {c['numero']} : la source annonce "
                                       f"{commun['votes_contre_annonce']} voix contre l'elimine, "
                                       f"ses bulletins en portent {lus} — les bulletins font foi")
            if sans_elimine and not jury:
                commun["elimine"] = None
                commun["elimine_rattache"] = False
                commun["sans_elimination"] = True
            commun["votes"] = bulletins
            conseils.append(commun)
            # Qui quitte le jeu pour de bon ici : celui dont le sort FINAL est
            # exactement cette sortie-la.
            if elimine_id and not jury:
                final_ = sorts.get(elimine_id)
                derniere_ = derniere_sortie.get(elimine_id, c["numero"])
                if derniere_ == c["numero"] and (
                        (bulletins and final_ in sorties_conseil) or
                        (not bulletins and final_ not in sorties_conseil)):
                    sortis.add(elimine_id)

        trancher_par_ligne(conseils[debut_saison:], idx, sid, rapport)
        etiqueter_les_sorties(conseils, debut_saison, sorts, rapport)
        recoller_le_scrutin_final(conseils[debut_saison:], rapport)

    if accord["communs"]:
        rapport.append(
            f"epreuve croisee des deux sources : {accord['communs']} bulletins "
            f"presents des deux cotes, {accord['accord']} identiques "
            f"({100.0 * accord['accord'] / accord['communs']:.1f} %), "
            f"{accord['desaccords']} divergents ; "
            f"{accord['ajoutes']} bulletins ajoutes par la seconde source")
    return conseils, accord


def main():
    saisons = donnees.charger(open(os.path.join(RACINE, "_data", "saisons.yml")))
    parts = donnees.charger(open(os.path.join(RACINE, "_data", "participations.yml")))
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
            donnees.ecrire(conseils, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
        # L'epreuve croisee est un resultat, pas un message : elle est publiee.
        croise = os.path.join(RACINE, "_data", "croisement_votes.yml")
        with open(croise, "w", encoding="utf-8") as f:
            f.write("# Fichier genere par tools/extraction/construire_conseils.py.\n"
                    "# Ne pas editer a la main : toute modification sera ecrasee.\n")
            donnees.ecrire({
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
