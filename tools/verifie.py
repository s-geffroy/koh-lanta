#!/usr/bin/env python3
"""Controle de coherence du jeu de donnees.

A lancer apres toute regeneration :

    tools/atelier python3 tools/verifie.py

Sort en 1 des qu'une erreur est trouvee. Les avertissements, eux, n'arretent
rien : ils signalent des trous connus et assumes (une saison en cours n'a pas
de jour de sortie pour ses candidats encore en jeu).

Ce fichier est la contrepartie de l'exhaustivite : plus le jeu de donnees
grossit, moins on peut le relire a l'oeil, et plus il faut que les invariants
soient verifies par une machine.
"""
import hashlib
import os
import re
import sys
from collections import Counter, defaultdict

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "extraction"))
import lieux  # noqa: E402
# Les en-tetes de colonne du scrutin final, definis la ou l'extraction les lit :
# une seule liste, pour que le controle et la generation ne divergent jamais.
from construire_conseils import EN_TETES_JURY, entete_de_colonne  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(RACINE, "_data")

SORTS_VALIDES = {
    "vainqueur", "finaliste", "elimine_poteaux", "elimine_orientation",
    "elimine_conseil", "elimine_ambassadeurs", "elimine_duel", "elimine_exil",
    "abandon_medical", "abandon_volontaire", "disqualifie",
}
COULEURS_VALIDES = {"jaune", "rouge", "bleu", "vert", "orange", "violet", "noir", "blanc"}
GENRES_VALIDES = {"h", "f"}
AGE_MIN, AGE_MAX = 15, 75
# Le palmares le plus lourd du jeu de donnees tient sous les vingt-cinq
# victoires sur une edition. Au-dela, c'est une faute de saisie.
VICTOIRES_MAX = 40


class Controle:
    """Trois registres, et la difference compte.

    ERREUR    : les donnees se contredisent. Le script sort en 1.
    AVERTIR   : quelque chose ressemble a un defaut de lecture. A regarder.
    CONSTAT   : une limite CONNUE et assumee, dont on publie le compte plutot
                que de la repeter en avertissement a chaque passage. « Brassac »
                designe deux communes et le restera ; deux Jerome jouent la
                meme saison et la source n'en distingue qu'un. Ce ne sont pas
                des defauts a corriger, ce sont des choses que ces donnees ne
                savent pas -- et les taire serait pire que les compter.
    """

    def __init__(self):
        self.erreurs = []
        self.avertissements = []
        self.constats = []

    def erreur(self, message):
        self.erreurs.append(message)

    def avertir(self, message):
        self.avertissements.append(message)

    def constater(self, message):
        self.constats.append(message)

    def exiger(self, condition, message):
        if not condition:
            self.erreur(message)
        return condition


def charger(nom):
    chemin = os.path.join(DATA, nom)
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8") as f:
        return yaml.safe_load(f)


# Ce qu'une page de Wikipedia en FRANCAIS porte et qu'une anglaise n'a jamais.
# Sert a demasquer un fichier `.en.wiki` qui n'est pas anglais.
MARQUEURS_FRANCAIS = ("Infobox Émission de télévision", "Sources secondaires",
                      "Travail inédit", "Palette Koh-Lanta")


def verifier_sources(c):
    """La provenance des wikitextes : pas de doublon, pas d'etiquette menteuse.

    Le wikitexte brut est versionne parce qu'il est la PREUVE de provenance :
    il permet de refaire tout le chemin sans redemander les pages. Une preuve
    qui ment est pire que pas de preuve.

    Deux fautes se sont produites. Un fichier `sp8.en.wiki` etait la copie
    octet pour octet de la page FRANCAISE -- les lecteurs d'epreuves et de
    colliers, qui lisent ce suffixe comme une troisieme source, croyaient donc
    lire l'anglais. Et le fichier ne se rafraichissant jamais, la copie a
    survecu a la mise a jour de l'original : elle etait devenue perimee EN PLUS
    d'etre mal etiquetee.
    """
    dossier = os.path.join(RACINE, "specs", "sources", "wiki")
    if not os.path.isdir(dossier):
        return
    empreintes = defaultdict(list)
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".wiki"):
            continue
        chemin = os.path.join(dossier, nom)
        with open(chemin, "rb") as f:
            contenu = f.read()
        empreintes[hashlib.sha256(contenu).hexdigest()].append(nom)
        if nom.endswith(".en.wiki"):
            texte = contenu.decode("utf-8", "replace")
            trouves = [m for m in MARQUEURS_FRANCAIS if m in texte]
            if trouves:
                c.erreur(f"specs/sources/wiki/{nom} : etiquete anglais mais porte "
                         f"« {trouves[0]} » — provenance fausse")
    for noms in empreintes.values():
        if len(noms) > 1:
            c.erreur(f"specs/sources/wiki : {' et '.join(noms)} sont identiques "
                     f"octet pour octet — deux etiquettes, une seule source")


def verifier_saisons(saisons, c):
    vus = set()
    for s in saisons:
        sid = s.get("id")
        if not sid:
            c.erreur("une saison n'a pas d'identifiant")
            continue
        if sid in vus:
            c.erreur(f"{sid} : identifiant de saison en double")
        vus.add(sid)

        if s.get("annulee"):
            continue

        for champ in ("titre", "annee", "pays", "lieu"):
            if not s.get(champ):
                c.erreur(f"{sid} : champ obligatoire « {champ} » vide")

        if not (2000 <= (s.get("annee") or 0) <= 2030):
            c.erreur(f"{sid} : annee hors plage ({s.get('annee')})")

        for t in s.get("tribus") or []:
            if t.get("couleur") not in COULEURS_VALIDES:
                c.erreur(f"{sid} : couleur de tribu inconnue « {t.get('couleur')} » "
                         f"pour « {t.get('nom')} »")

        if not s.get("en_cours") and not s.get("vainqueurs"):
            c.erreur(f"{sid} : aucun vainqueur declare")

        d = s.get("diffusion")
        if isinstance(d, dict) and d.get("debut") and d.get("fin"):
            if d["fin"] < d["debut"]:
                c.erreur(f"{sid} : la diffusion se termine avant de commencer")


def verifier_matrices_de_votes(conseils, c):
    """Une saison entiere sans un seul bulletin est une panne, pas une absence.

    La matrice « Detail des votes » existe pour presque toutes les saisons. Si
    on n'en tire aucun bulletin alors qu'elle annonce des decomptes, c'est que
    la lecture a echoue -- et elle echoue en silence. Deux saisons entieres
    (Les 4 Terres, Le Totem maudit) sont restees vides des mois pour cette
    raison : les noms y etaient enveloppes dans un modele que le nettoyage du
    wikitexte effacait.
    """
    par_saison = defaultdict(lambda: [0, 0, 0])
    for x in conseils:
        etat = par_saison[x.get("saison")]
        etat[0] += len(x.get("votes") or [])
        if x.get("votes_exprimes"):
            etat[1] += 1
        etat[2] += 1
    for sid, (bulletins, annonces, total) in sorted(par_saison.items()):
        if annonces and not bulletins:
            c.erreur(f"{sid} : {total} conseils, {annonces} decomptes annonces, "
                     f"et AUCUN bulletin lu — la matrice des votes n'a pas ete "
                     f"comprise")


def verifier_bulletins_sans_votant(conseils, c):
    """Un bulletin sans votant doit dire POURQUOI il n'en a pas.

    Depuis 2017, le jeu impose des voix que personne n'ecrit : vote noir,
    penalite, malediction. Elles comptent dans le total annonce par la source,
    et sans elles cinquante-huit conseils restaient « incomplets » -- donc
    absents de toute analyse au bulletin, en silence.

    Deux fautes se ressemblent et n'ont pas le meme sens. Un bulletin sans
    votant ET sans motif est un votant qu'on a perdu ; un bulletin qui porte un
    motif ET un votant est un votant qu'on a invente. Les deux sont des
    erreurs, et aucune ne produirait le moindre message sans ce controle.
    """
    orphelins = motives = 0
    for x in conseils:
        for b in x.get("votes") or []:
            a_votant = bool(b.get("votant"))
            motif = b.get("mecanique")
            if not a_votant and not motif:
                orphelins += 1
            if a_votant and motif:
                motives += 1
                c.erreur(f"{x.get('saison')} conseil {x.get('numero')} : le "
                         f"bulletin « {b.get('votant')} » porte le motif "
                         f"« {motif} » — un bulletin de mecanique n'a pas de "
                         f"votant, par definition")
    if orphelins:
        c.erreur(f"{orphelins} bulletin(s) sans votant et sans motif : un "
                 f"votant perdu ne se distingue plus d'une voix imposee par "
                 f"le jeu")


# Ce que la colonne « tribu » dit parfois a la place d'une tribu : une
# situation. Banni sur une ile, absent d'un episode -- la personne n'est alors
# dans aucun campement, et la saison n'a aucune raison de declarer ces mots.
SITUATIONS_HORS_TRIBU = {"banni", "bannie", "absent", "absente",
                         "exile", "exilee", "en-attente"}


def verifier_participations(parts, saisons, c):
    par_id = {s["id"]: s for s in saisons}
    par_saison = defaultdict(list)
    effectifs = Counter(p.get("saison") for p in parts)
    ambigus = []

    for p in parts:
        sid = p.get("saison")
        if sid not in par_id:
            c.erreur(f"participation « {p.get('nom')} » : saison inconnue « {sid} »")
            continue
        par_saison[sid].append(p)
        s = par_id[sid]

        if p.get("genre") not in GENRES_VALIDES:
            c.erreur(f"{sid} / {p.get('nom')} : sexe invalide « {p.get('genre')} »")

        if p.get("sort") is not None and p["sort"] not in SORTS_VALIDES:
            c.erreur(f"{sid} / {p.get('nom')} : sort inconnu « {p['sort']} »")

        age = p.get("age")
        if age is not None and not (AGE_MIN <= age <= AGE_MAX):
            c.erreur(f"{sid} / {p.get('nom')} : age hors plage ({age})")

        jour = p.get("jour_sortie")
        duree = s.get("duree_jours")
        if jour is not None:
            if jour < 1:
                c.erreur(f"{sid} / {p.get('nom')} : jour de sortie invalide ({jour})")
            elif duree and jour > duree:
                c.erreur(f"{sid} / {p.get('nom')} : sorti au jour {jour}, "
                         f"or la saison dure {duree} jours")

        couleur = p.get("couleur")
        if couleur is not None and couleur not in COULEURS_VALIDES:
            c.erreur(f"{sid} / {p.get('nom')} : couleur inconnue « {couleur} »")

        # Les champs apportes par les fiches individuelles Fandom. Ils sont
        # saisis a la main par des lecteurs : un rang au-dela de l'effectif ou
        # un palmares invraisemblable est une faute de saisie, pas un record.
        rang = p.get("classement")
        if rang is not None:
            if rang < 1:
                c.erreur(f"{sid} / {p.get('nom')} : rang final invalide ({rang})")
            elif rang > effectifs.get(sid, 0):
                c.erreur(f"{sid} / {p.get('nom')} : rang final {rang} au-dela "
                         f"de l'effectif de la saison ({effectifs.get(sid, 0)})")
        for champ in ("victoires_collectives", "victoires_individuelles"):
            v = p.get(champ)
            if v is not None and not (0 <= v <= VICTOIRES_MAX):
                c.erreur(f"{sid} / {p.get('nom')} : {champ} hors plage ({v})")

        lieu = p.get("localisation")
        if lieu and lieux.normaliser(lieu) is None:
            if lieux.est_ambigu(lieu):
                ambigus.append(f"{sid}/{p.get('nom')} « {lieu} »")
            else:
                c.avertir(f"{sid} / {p.get('nom')} : localisation « {lieu} » hors "
                          f"de la liste des lieux connus")

        tribu = p.get("tribu")
        # « Bannie », « Absente » : la case dit ou la personne se trouvait, pas
        # de quelle tribu elle etait. Ce sont des situations, pas des campements,
        # et aucune saison ne les declare.
        if tribu and s.get("tribus") and lieux._norm(tribu) not in SITUATIONS_HORS_TRIBU:
            connues = {t["nom"].lower() for t in s["tribus"]}
            if tribu.lower() not in connues:
                c.avertir(f"{sid} / {p.get('nom')} : tribu « {tribu} » absente "
                          f"des tribus declarees de la saison")

        if not p.get("nom"):
            c.erreur(f"{sid} : une participation sans nom")

    # effectifs, vainqueurs, doublons
    for sid, s in par_id.items():
        if s.get("annulee"):
            if par_saison.get(sid):
                c.erreur(f"{sid} : saison annulee mais des participations existent")
            continue

        lignes = par_saison.get(sid, [])
        attendu = s.get("nb_candidats")
        if attendu and len(lignes) != attendu:
            c.erreur(f"{sid} : {len(lignes)} participations pour {attendu} candidats annonces")

        doublons = [n for n, k in Counter(p.get("id") for p in lignes).items() if k > 1]
        if doublons:
            c.erreur(f"{sid} : meme personne comptee deux fois — {', '.join(map(str, doublons))}")

        vainqueurs = [p for p in lignes if p.get("sort") == "vainqueur"]
        declares = s.get("vainqueurs") or []
        if s.get("en_cours"):
            # Le point aveugle repare : jusqu'ici, une saison EN COURS
            # echappait a tout controle de sort, et All Stars 2026 y a porte
            # trois vainqueurs et quatre finalistes pour quatre conseils
            # joues. Ils venaient de la colonne « Saisons precedentes » du
            # tableau des candidats, prise pour la colonne de depart -- vide,
            # puisque la saison n'est pas finie.
            #
            # Une saison qui n'est pas terminee n'a ni vainqueur ni finaliste.
            # Elle n'a que des elimines, et ceux-la sont attestes.
            au_bout = [p for p in lignes
                       if p.get("sort") in ("vainqueur", "finaliste")]
            if au_bout:
                c.erreur(f"{sid} : saison en cours, mais "
                         f"{len(au_bout)} aventurier(s) portent deja un sort de "
                         f"fin d'aventure — "
                         f"{', '.join(sorted(p['id'] for p in au_bout))}")
        # Un sort ne peut pas contredire une source qui dit « encore en jeu ».
        for p in lignes:
            if p.get("sort") and re.search(r"encore en jeu|toujours en jeu",
                                           p.get("motif") or "", re.I):
                c.erreur(f"{sid} / {p['nom']} : sort « {p['sort']} » alors que la "
                         f"source ecrit « {p['motif']} »")
        if not s.get("en_cours"):
            if len(vainqueurs) != len(declares):
                c.erreur(f"{sid} : {len(vainqueurs)} vainqueur(s) dans les donnees "
                         f"pour {len(declares)} declare(s)")
            for v in vainqueurs:
                if v.get("jour_sortie") and s.get("duree_jours") \
                        and v["jour_sortie"] < s["duree_jours"] - 4:
                    c.avertir(f"{sid} / {v['nom']} : vainqueur sorti au jour "
                              f"{v['jour_sortie']} alors que la saison dure "
                              f"{s['duree_jours']} jours")

        # personne ne peut sortir avant le premier conseil
        for p in lignes:
            if p.get("sort") == "finaliste" and p.get("jour_sortie") \
                    and s.get("duree_jours") and p["jour_sortie"] < s["duree_jours"] - 4:
                c.avertir(f"{sid} / {p['nom']} : finaliste sorti au jour "
                          f"{p['jour_sortie']} pour une saison de {s['duree_jours']} jours")

    _constater_lieux(ambigus, c)


def verifier_epreuves(epreuves, saisons, parts, c):
    par_id = {s["id"]: s for s in saisons}
    ids = {(p["saison"], p["id"]) for p in parts}
    tribus = {s["id"]: {t["nom"].lower() for t in (s.get("tribus") or [])}
              for s in saisons}
    homonymes = prenoms_en_double(parts)
    groupe_final = groupes_de_fin(parts)
    par_saison = defaultdict(list)

    for e in epreuves:
        sid = e.get("saison")
        if sid not in par_id:
            c.erreur(f"epreuve : saison inconnue « {sid} »")
            continue
        par_saison[sid].append(e)

        if e.get("type") not in ("confort", "immunite", "epreuve"):
            c.erreur(f"{sid} ep.{e.get('episode')} : type d'epreuve inconnu "
                     f"« {e.get('type')} »")
        if e.get("forme") not in ("collective", "individuelle", "mixte", None):
            c.erreur(f"{sid} ep.{e.get('episode')} : forme inconnue « {e.get('forme')} »")
        if not e.get("episode") or e["episode"] < 1:
            c.erreur(f"{sid} : epreuve sans numero d'episode valide")
        if not e.get("vainqueurs"):
            c.erreur(f"{sid} ep.{e.get('episode')} : epreuve sans vainqueur")

        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                if (sid, v["id"]) not in ids:
                    c.erreur(f"{sid} ep.{e['episode']} : vainqueur « {v['id']} » "
                             f"absent des participations de la saison")
            elif v.get("type") == "tribu":
                if v["libelle"].lower() not in tribus.get(sid, set()):
                    c.erreur(f"{sid} ep.{e['episode']} : tribu « {v['libelle']} » "
                             f"absente des tribus declarees")

    for sid, lot in par_saison.items():
        s = par_id[sid]
        if s.get("annulee"):
            c.erreur(f"{sid} : saison annulee mais des epreuves existent")
        # Plusieurs noms sur une meme epreuve n'est pas toujours une cellule
        # mal lue. Deux familles sont legitimes, et il a fallu les regarder une
        # a une pour s'en assurer :
        #
        #   * un CONFORT se partage. Le vainqueur invite qui il veut, ou c'est
        #     une equipe entiere qui gagne : citer quatre noms est exact.
        #   * la DERNIERE epreuve d'une saison ne designe pas un vainqueur mais
        #     les qualifies pour les poteaux. Les trois noms sont alors les
        #     trois qui iront au bout -- verifiable, puisque ce sont exactement
        #     les finalistes et l'elimine des poteaux.
        #
        # Ce qui reste suspect : trois noms sur une immunite individuelle qui
        # ne sont pas ce trio-la.
        for e in lot:
            noms = [v["libelle"] for v in e["vainqueurs"]]
            if len(noms) <= 2 or e.get("forme") == "collective":
                continue
            if e.get("type") == "confort":
                continue
            cites = {v.get("id") for v in e["vainqueurs"]}
            if cites and None not in cites and cites <= groupe_final.get(sid, set()):
                continue
            c.avertir(f"{sid} ep.{e['episode']} ({e['type']}) : "
                      f"{len(noms)} vainqueurs cites — {', '.join(noms)}")

    non_resolus = [(e["saison"], v) for e in epreuves for v in e["vainqueurs"]
                   if not v.get("resolu")]
    _rendre_compte_des_noms(non_resolus, "vainqueur d'epreuve", homonymes, c)

    couvertes = len(par_saison)
    diffusees = sum(1 for s in saisons if not s.get("annulee"))
    if couvertes < diffusees:
        absentes = [s["id"] for s in saisons
                    if not s.get("annulee") and s["id"] not in par_saison]
        c.constater(f"epreuves absentes pour {len(absentes)} saison(s) sur "
                  f"{diffusees} : {', '.join(absentes)}")


def constater_epreuves_apres_la_sortie(conseils, epreuves, parts, c):
    """Une victoire posterieure a la colonne qui elimine son vainqueur.

    Ce n'est pas une incoherence de la source : l'episode de sortie se lit
    dans la matrice des votes, dont le dernier conseil NUMEROTE precede d'un
    episode ou deux les epreuves de la finale. Celui qui sort aux poteaux ou a
    l'orientation dispute donc des epreuves apres la colonne qui l'elimine.

    C'est rattrape la ou il faut -- `indicateurs.py` prend pour denominateur au
    moins le nombre d'epreuves gagnees -- mais le fait merite d'etre compte :
    sans lui, treize victoires tombaient hors de leur propre denominateur.
    """
    sortie = {}
    finissent = {(p["saison"], p["id"]) for p in parts
                 if p.get("sort") in ("vainqueur", "finaliste")}
    for x in conseils:
        if x.get("type") == "jury" or not x.get("elimine_rattache"):
            continue
        if (x["saison"], x["elimine"]) in finissent:
            continue
        try:
            sortie[(x["saison"], x["elimine"])] = int(x["episode"])
        except (TypeError, ValueError, KeyError):
            pass
    tardives = []
    for e in epreuves:
        try:
            ep = int(e["episode"])
        except (TypeError, ValueError, KeyError):
            continue
        for v in e.get("vainqueurs") or []:
            if v.get("type") != "personne" or not v.get("id"):
                continue
            depart = sortie.get((e["saison"], v["id"]))
            if depart is not None and ep > depart:
                tardives.append(f"{e['saison']} ep.{ep} {v['id']}")
    if tardives:
        c.constater(f"{len(tardives)} victoire(s) d'epreuve posterieure(s) a la "
                    f"colonne d'elimination de leur vainqueur — sortie aux "
                    f"poteaux ou a l'orientation, denominateur rattrape "
                    f"({', '.join(tardives[:4])}...)")


def constater_victoires_impossibles(conseils, epreuves, parts, c):
    """Une victoire individuelle datee d'apres le depart de son vainqueur.

    Les fiches individuelles du wiki donnent un total de victoires PAR SAISON,
    mais leur infobox n'a pas toujours de champ « Saison » : `fusionner`
    rattache alors les rangs par ordre chronologique, et le rattachement peut
    se tromper de saison. On le voit quand une fiche credite quelqu'un d'une
    victoire individuelle dans une saison ou il est parti AVANT la premiere
    epreuve individuelle -- Julie Navarro, sortie le premier jour du Combat des
    heros, y compte une victoire ; Raphaele, sortie au sixieme, en compte trois.

    Ce n'est pas rattrapable : on sait que la valeur est fausse pour CETTE
    saison, on ne sait pas a laquelle elle appartient. Elle reste donc en
    place, comptee et signalee -- et le classement des joueurs, lui, ne s'en
    sert pas : il ne lit que le tableau date.
    """
    par_saison = defaultdict(list)
    for e in epreuves:
        if e.get("forme") == "individuelle":
            try:
                par_saison[e["saison"]].append(int(e["episode"]))
            except (TypeError, ValueError, KeyError):
                pass
    premiere = {sid: min(eps) for sid, eps in par_saison.items() if eps}
    sortie = {}
    finissent = {(p["saison"], p["id"]) for p in parts
                 if p.get("sort") in ("vainqueur", "finaliste")}
    for x in conseils:
        if x.get("type") == "jury" or not x.get("elimine_rattache"):
            continue
        if (x["saison"], x["elimine"]) in finissent:
            continue
        try:
            sortie[(x["saison"], x["elimine"])] = int(x["episode"])
        except (TypeError, ValueError, KeyError):
            pass
    fautives = []
    for p in parts:
        vi = p.get("victoires_individuelles")
        cle = (p["saison"], p["id"])
        if not vi or p["saison"] not in premiere or cle not in sortie:
            continue
        if sortie[cle] < premiere[p["saison"]]:
            fautives.append(f"{p['saison']}/{p['nom']} ({vi})")
    if fautives:
        c.constater(f"{len(fautives)} fiche(s) creditent une victoire individuelle "
                    f"a quelqu'un parti avant la premiere epreuve individuelle de "
                    f"sa saison — rattachement de saison fautif dans l'infobox "
                    f"({', '.join(fautives[:4])}...)")


def verifier_immunite_individuelle(conseils, epreuves, c):
    """L'immunise du soir ne peut pas etre l'elimine du soir.

    C'est une regle du jeu, donc un invariant : si les donnees la violent, c'est
    qu'un rattachement est faux -- celui du vainqueur d'epreuve, celui de
    l'elimine, ou celui de l'episode.

    Le controle ne vaut que sur les soirs a CONSEIL UNIQUE. Un episode qui en
    compte trois enchaine trois eliminations, et l'immunite gagnee avant le
    premier ne protege pas au troisieme : rapproche sur le seul numero
    d'episode, ce meme controle annoncait 19 violations, toutes fausses.
    """
    par_soir = Counter()
    scrutins = []
    for x in conseils:
        if x.get("type") == "jury":
            continue
        try:
            episode = int(x["episode"])
        except (TypeError, ValueError, KeyError):
            continue
        par_soir[(x["saison"], episode)] += 1
        if x.get("elimine_rattache"):
            scrutins.append((x, episode))

    immunises = defaultdict(set)
    for e in epreuves:
        if e.get("type") != "immunite" or e.get("forme") != "individuelle":
            continue
        try:
            episode = int(e["episode"])
        except (TypeError, ValueError, KeyError):
            continue
        for v in (e.get("vainqueurs") or []):
            if v.get("type") == "personne" and v.get("id"):
                immunises[(e["saison"], episode)].add(v["id"])

    controles = 0
    for x, episode in scrutins:
        if par_soir[(x["saison"], episode)] != 1:
            continue
        gagnants = immunises.get((x["saison"], episode))
        if not gagnants:
            continue
        controles += 1
        if x["elimine"] in gagnants:
            c.erreur(f"{x['saison']} ep.{episode} : {x['elimine']} gagne l'immunite "
                     f"individuelle ET part au conseil du meme soir — "
                     f"rattachement incoherent")
    if controles < 40:
        c.avertir(f"immunite individuelle : seulement {controles} conseils "
                  f"controlables, l'invariant ne dit plus grand-chose")


ISSUES_VALIDES = {"annulation_efficace", "joue_pour_rien", "elimine_avec_collier",
                  "garde_sans_usage", "non_decouvert"}
STATUTS_VALIDES = {"utilise", "non_utilise", "non_decouvert", "perdu"}


def verifier_colliers(colliers, saisons, parts, c):
    par_id = {s["id"]: s for s in saisons}
    ids = {(p["saison"], p["id"]) for p in parts}
    homonymes = prenoms_en_double(parts)

    for col in colliers:
        sid = col.get("saison")
        if sid not in par_id:
            c.erreur(f"collier : saison inconnue « {sid} »")
            continue
        if par_id[sid].get("annulee"):
            c.erreur(f"{sid} : saison annulee mais des colliers existent")

        if col.get("statut") is not None and col["statut"] not in STATUTS_VALIDES:
            c.erreur(f"{sid} : statut de collier inconnu « {col['statut']} »")
        if col.get("issue") is not None and col["issue"] not in ISSUES_VALIDES:
            c.erreur(f"{sid} : issue de collier inconnue « {col['issue']} »")

        for role in ("detenteurs", "detenteurs_suivants", "proteges"):
            for x in col.get(role) or []:
                if x.get("id") and (sid, x["id"]) not in ids:
                    c.erreur(f"{sid} : {role[:-1]} « {x['id']} » absent des "
                             f"participations de la saison")

        annules, exprimes = col.get("votes_annules"), col.get("votes_exprimes")
        if annules is not None and exprimes is not None and annules > exprimes:
            c.erreur(f"{sid} : collier annulant {annules} voix sur {exprimes} "
                     f"exprimees")
        if col.get("statut") == "non_decouvert" and (col.get("detenteurs") or []):
            c.erreur(f"{sid} : collier « non decouvert » mais avec un detenteur")
        if col.get("statut") == "utilise" and annules is None:
            c.avertir(f"{sid} : collier joue sans decompte de voix annulees")
        jour = col.get("jour_trouve")
        duree = par_id[sid].get("duree_jours")
        if jour and duree and jour > duree:
            c.erreur(f"{sid} : collier trouve au jour {jour}, "
                     f"or la saison dure {duree} jours")

    non_resolus = [(col["saison"], x) for col in colliers
                   for role in ("detenteurs", "proteges")
                   for x in col.get(role) or [] if not x.get("resolu")]
    _rendre_compte_des_noms(non_resolus, "detenteur de collier", homonymes, c)


# Ce qui trahit un fragment de wikitexte reste dans un nom d'aventurier :
# une taille de vignette (« 75px »), une barre verticale, un parametre de lien,
# ou un espace de noms de fichier.
RE_RESIDU_WIKI = re.compile(
    r"\b\d{2,4}px\b|\||\blink\s*=|\b(?:File|Fichier|Image|Media)\s*:|"
    r"\bvignette\b|\bthumb\b|\[\[|\]\]", re.I)


def _constater_lieux(ambigus, c):
    if ambigus:
        c.constater(f"localisation : {len(ambigus)} valeur(s) qu'on refuse de "
                    f"trancher — le nom designe plusieurs lieux "
                    f"({', '.join(sorted(ambigus))})")


def prenoms_en_double(parts):
    """{saison: {prenom normalise}} pour les prenoms portes par deux personnes."""
    compte = defaultdict(Counter)
    for p in parts:
        compte[p["saison"]][lieux._norm(p["nom"])] += 1
    return {sid: {n for n, k in table.items() if k > 1}
            for sid, table in compte.items()}


def groupes_de_fin(parts):
    """{saison: {identifiants de ceux qui ont atteint les poteaux}}."""
    out = defaultdict(set)
    for p in parts:
        if p.get("sort") in ("vainqueur", "finaliste", "elimine_poteaux"):
            out[p["saison"]].add(p["id"])
    return out


def _rendre_compte_des_noms(non_resolus, role, homonymes, c):
    """Separe ce qui est indecidable de ce qui n'a pas ete compris.

    Un prenom porte par DEUX aventuriers de la meme saison, sans que la source
    dise lequel, ne sera jamais rattache : ce n'est pas un defaut d'extraction,
    c'est une limite de la source. On en publie le compte -- taire ce qu'on ne
    sait pas serait pire -- mais on ne le crie pas a chaque passage.

    Un libelle qui ne correspond a personne, lui, est un vrai signal.
    """
    indecidables = [(sid, x) for sid, x in non_resolus
                    if lieux._norm(x["libelle"]) in homonymes.get(sid, set())]
    incompris = [(sid, x) for sid, x in non_resolus if (sid, x) not in indecidables]
    if indecidables:
        detail = sorted({f"{sid}/{x['libelle']}" for sid, x in indecidables})
        c.constater(f"{role} : {len(indecidables)} citation(s) qu'aucune source ne "
                    f"desambigue — deux aventuriers y portent le meme prenom "
                    f"({', '.join(detail)})")
    if incompris:
        libelles = sorted({x["libelle"] for _, x in incompris})
        c.avertir(f"{role} non rattache : {len(incompris)} citation(s) — "
                  + ", ".join(libelles[:6]) + (" …" if len(libelles) > 6 else ""))


def verifier_conseils(conseils, saisons, parts, c):
    """Le scrutin final n'est pas un conseil, et rien ne doit les confondre.

    Les tableaux sources presentent le vote du jury final comme un conseil
    ordinaire, en placant le VAINQUEUR dans la colonne du sortant. Ecrire un
    nom y signifie pourtant « qu'il gagne » : compter ces bulletins comme des
    eliminations inverse le sens de chacun d'eux. La separation se fait a la
    generation ; ce controle est la pour qu'elle ne se perde pas.
    """
    vainqueurs = {(p["saison"], p["id"]) for p in parts
                  if p.get("sort") == "vainqueur"}
    finalistes = {(p["saison"], p["id"]) for p in parts
                  if p.get("sort") == "finaliste"}
    ids = {(p["saison"], p["id"]) for p in parts}
    connus = {s["id"] for s in saisons}
    revenus = []

    for x in conseils:
        ref = f'{x.get("saison")} conseil {x.get("numero")}'
        t = x.get("type")
        if t not in ("elimination", "jury"):
            c.erreur(f"{ref} : `type` absent ou inconnu ({t!r}) — "
                     f"attendu `elimination` ou `jury`")
            continue
        if x.get("saison") not in connus:
            c.erreur(f"{ref} : saison inconnue")

        if t == "jury":
            for interdit in ("elimine", "elimine_rattache", "votes_contre"):
                if interdit in x:
                    c.erreur(f"{ref} : vote de jury portant `{interdit}` — "
                             f"personne n'y est elimine")
            # Le scrutin final tient une ligne par finaliste : celle du
            # gagnant (`laureat`) et celle du battu (`finaliste`). Une ligne
            # de jury porte exactement l'une des deux.
            portes = [ch for ch in ("laureat", "finaliste") if ch in x]
            if len(portes) != 1:
                c.erreur(f"{ref} : vote de jury portant {portes or 'aucun'} — "
                         f"attendu exactement `laureat` OU `finaliste`")
            if (x.get("laureat_rattache")
                    and (x["saison"], x["laureat"]) not in vainqueurs):
                c.erreur(f"{ref} : le laureat « {x['laureat']} » n'est pas le "
                         f"vainqueur declare de la saison")
            if (x.get("finaliste_rattache")
                    and (x["saison"], x["finaliste"]) not in finalistes):
                c.erreur(f"{ref} : « {x['finaliste']} » tient la colonne du "
                         f"finaliste battu sans porter `sort: finaliste`")
            # Le total annonce par la matrice contre les bulletins qu'on y lit.
            # Un ecart n'est pas forcement une faute de lecture -- la ligne des
            # totaux est parfois decalee d'une colonne a la source -- mais il
            # doit se voir.
            lus = len(x.get("votes") or [])
            if x.get("votes_pour") is not None and x["votes_pour"] != lus:
                c.avertir(f"{ref} : le scrutin annonce {x['votes_pour']} voix et "
                          f"en fait lire {lus} — la ligne des totaux de la "
                          f"matrice est probablement decalee")
            # Un bulletin de jury appartient a la colonne de celui qu'il nomme.
            # Ailleurs, c'est que la matrice range les jures par leur ligne et
            # non par leur vote -- et le decompte des colonnes devient faux.
            titulaire = x.get("laureat") if "laureat" in x else x.get("finaliste")
            for b in x.get("votes") or []:
                if b.get("cible_rattachee") and b["cible"] != titulaire:
                    c.erreur(f"{ref} : bulletin pour « {b['cible']} » range dans "
                             f"la colonne de « {titulaire} » — le scrutin final "
                             f"n'a pas ete recolle")
        else:
            for interdit in ("laureat", "finaliste"):
                if interdit in x:
                    c.erreur(f"{ref} : conseil d'elimination portant `{interdit}`")
            # La colonne du scrutin final est titree par la source
            # (« Gagnant », « Finaliste »...). La voir ici, c'est qu'elle a ete
            # rangee du cote des eliminations : les bulletins y comptent alors
            # a l'envers, sans qu'aucun calcul ne s'en plaigne.
            if entete_de_colonne(x.get("episode")) in EN_TETES_JURY:
                c.erreur(f"{ref} : conseil d'elimination titre "
                         f"« {x.get('episode')} » — c'est une colonne du vote "
                         f"du jury final, pas un conseil")
            if x.get("elimine_rattache") and (x["saison"], x["elimine"]) in vainqueurs:
                c.erreur(f"{ref} : le vainqueur de la saison y est donne pour "
                         f"elimine — c'est le vote du jury, pas un conseil")
            if x.get("elimine_rattache") and (x["saison"], x["elimine"]) in finalistes:
                revenus.append(f"{x['saison']} ep.{x.get('episode')} {x['elimine']}")

        # Un libelle non rattache reste tel quel dans le fichier : il doit au
        # moins ressembler a un nom. La syntaxe de vignette MediaWiki --
        # [[Fichier:Sara.png|75px|link=Sara Tallon]] -- a longtemps traverse
        # l'extraction et laissait « 75px » en guise d'aventurier, rendant 478
        # eliminations sur 681 non rattachables. La faute est corrigee dans
        # `plain()` ; ce controle est la pour qu'elle ne revienne pas.
        for champ in ("elimine", "laureat", "finaliste"):
            v = x.get(champ)
            if isinstance(v, str) and RE_RESIDU_WIKI.search(v):
                c.erreur(f"{ref} : `{champ}` porte de la syntaxe MediaWiki "
                         f"(« {v} ») — l'extraction a laisse passer une vignette")
        for b in x.get("votes") or []:
            for champ in ("votant", "cible"):
                v = b.get(champ)
                if isinstance(v, str) and RE_RESIDU_WIKI.search(v):
                    c.erreur(f"{ref} : bulletin dont `{champ}` porte de la "
                             f"syntaxe MediaWiki (« {v} »)")
            if b.get("votant_rattache") and (x["saison"], b["votant"]) not in ids:
                c.erreur(f"{ref} : votant « {b['votant']} » absent des participations")
            if b.get("cible_rattachee") and (x["saison"], b["cible"]) not in ids:
                c.erreur(f"{ref} : cible « {b['cible']} » absente des participations")

    # Un finaliste donne pour elimine a un conseil n'est pas une faute : il a
    # ete elimine PUIS il est revenu. Le fait doit se voir -- c'est lui qui
    # empechait de compter ses conseils, et Francis, finaliste du Pacifique,
    # n'en comptait que trois.
    if revenus:
        c.constater(f"retour en jeu : {len(revenus)} elimination(s) au conseil "
                    f"frappant quelqu'un qui a fini la saison "
                    f"({', '.join(sorted(revenus))})")

    # Le scrutin final se lit en entier ou il ne se lit pas. Les colonnes des
    # finalistes battus ont longtemps manque, et rien ne le signalait : le
    # total annonce par la matrice donne le nombre de jures, et la somme des
    # bulletins de la saison doit l'atteindre.
    jury_lus, jury_annonces = defaultdict(int), {}
    for x in conseils:
        if x.get("type") != "jury":
            continue
        jury_lus[x["saison"]] += len(x.get("votes") or [])
        if x.get("votes_exprimes"):
            jury_annonces[x["saison"]] = max(jury_annonces.get(x["saison"], 0),
                                             x["votes_exprimes"])
    for sid, annonce in sorted(jury_annonces.items()):
        if jury_lus[sid] < annonce:
            c.avertir(f"{sid} : le vote du jury annonce {annonce} voix et n'en "
                      f"fait lire que {jury_lus[sid]} — une colonne de finaliste "
                      f"manque probablement au relevé")


def verifier_personnes(personnes, parts, c):
    ids_parts = Counter(p["id"] for p in parts)
    ids_pers = {g["id"] for g in personnes}

    for g in personnes:
        if g.get("genre") not in GENRES_VALIDES:
            c.erreur(f"personne « {g.get('nom')} » : sexe invalide « {g.get('genre')} »")
        if g.get("nb_participations") != len(g.get("participations") or []):
            c.erreur(f"personne « {g.get('nom')} » : nb_participations incoherent")
        if g["id"] not in ids_parts:
            c.erreur(f"personne « {g.get('nom')} » : aucune participation correspondante")
        elif ids_parts[g["id"]] != g["nb_participations"]:
            c.erreur(f"personne « {g.get('nom')} » : {g['nb_participations']} participations "
                     f"annoncees, {ids_parts[g['id']]} trouvees")

    for pid in ids_parts:
        if pid not in ids_pers:
            c.erreur(f"participation d'identifiant « {pid} » sans fiche dans personnes.yml")


def trous(parts, saisons, c):
    """Recense les champs vides. Tolere ceux d'une saison en cours."""
    en_cours = {s["id"] for s in saisons if s.get("en_cours")}
    manques = defaultdict(list)
    for p in parts:
        for champ in ("age", "profession", "tribu", "jour_sortie", "sort"):
            if p.get(champ) in (None, "", []):
                if champ in ("jour_sortie", "sort") and p["saison"] in en_cours:
                    continue          # encore en jeu : c'est normal
                manques[champ].append(f"{p['saison']}/{p['nom']}")
    for champ, qui in sorted(manques.items()):
        c.avertir(f"{champ} : {len(qui)} valeur(s) inconnue(s) — "
                  + ", ".join(qui[:6]) + (" …" if len(qui) > 6 else ""))


def verifier_finale(finale, saisons, parts, c):
    """Le trio des poteaux doit etre le trio des poteaux.

    Trois personnes s'y presentent : deux en sortiront finalistes, une sera
    eliminee. Si la source dit qu'un quatrieme a gagne les poteaux, ou que le
    vainqueur des poteaux est celui qui en a ete elimine, c'est la lecture qui
    est fausse -- pas l'histoire. On le dit fort plutot que de le publier.
    """
    sorts = {(p["saison"], p["id"]): p.get("sort") for p in parts}
    connus = {s["id"] for s in saisons}
    for x in finale.get("lignes") or []:
        sid = x.get("saison")
        ref = f"finale {sid}"
        if sid not in connus:
            c.erreur(f"{ref} : saison inconnue")
            continue
        pot = x.get("poteaux") or {}
        gagnant, elimine = pot.get("vainqueur"), pot.get("elimine")
        autre = pot.get("autre_finaliste")
        if sorts.get((sid, elimine)) != "elimine_poteaux":
            c.erreur(f"{ref} : « {elimine} » tient la place de l'elimine des "
                     f"poteaux sans porter `sort: elimine_poteaux`")
        for champ, pid in (("vainqueur", gagnant), ("autre_finaliste", autre)):
            if pid and sorts.get((sid, pid)) not in ("vainqueur", "finaliste"):
                c.erreur(f"{ref} : `poteaux.{champ}` = « {pid} », qui n'est ni "
                         f"vainqueur ni finaliste de la saison")
        trio = [i for i in (gagnant, autre, elimine) if i]
        if len(set(trio)) != len(trio):
            c.erreur(f"{ref} : le trio des poteaux cite deux fois la meme personne")
        if pot.get("choix_atteste") and pot.get("choisi") != autre:
            c.erreur(f"{ref} : le choix atteste designe « {pot.get('choisi')} », "
                     f"l'arithmetique designe « {autre} »")
        qualifies = (x.get("orientation") or {}).get("qualifies") or []
        if qualifies and not set(qualifies) <= set(trio):
            c.erreur(f"{ref} : la cellule d'orientation cite quelqu'un qui n'est "
                     f"pas du trio des poteaux")
        if x.get("vainqueur") and sorts.get((sid, x["vainqueur"])) != "vainqueur":
            c.erreur(f"{ref} : « {x['vainqueur']} » donne vainqueur de la saison "
                     f"sans porter `sort: vainqueur`")
    couv = finale.get("couverture") or {}
    if couv.get("rangs_dementis"):
        c.erreur(f"finale : {couv['rangs_dementis']} rang(s) d'arrivee a "
                 f"l'orientation contredisent l'ordre de la cellule — l'ordre "
                 f"publie ne serait plus l'ordre d'arrivee")


def main():
    c = Controle()
    saisons = charger("saisons.yml")
    parts = charger("participations.yml")
    personnes = charger("personnes.yml")
    epreuves = charger("epreuves.yml")
    conseils = charger("conseils.yml")
    colliers = charger("colliers.yml")
    finale = charger("finale.yml")

    if saisons is None:
        c.erreur("_data/saisons.yml est absent")
    if parts is None:
        c.erreur("_data/participations.yml est absent")
    if personnes is None:
        c.erreur("_data/personnes.yml est absent")

    if saisons:
        verifier_saisons(saisons, c)
    verifier_sources(c)
    if saisons and parts:
        verifier_participations(parts, saisons, c)
        trous(parts, saisons, c)
    if saisons and parts and epreuves:
        verifier_epreuves(epreuves, saisons, parts, c)
    if epreuves and conseils:
        verifier_immunite_individuelle(conseils, epreuves, c)
    if epreuves and conseils and parts:
        constater_epreuves_apres_la_sortie(conseils, epreuves, parts, c)
        constater_victoires_impossibles(conseils, epreuves, parts, c)
    if saisons and parts and conseils:
        verifier_conseils(conseils, saisons, parts, c)
        verifier_matrices_de_votes(conseils, c)
        verifier_bulletins_sans_votant(conseils, c)
    if saisons and parts and colliers:
        verifier_colliers(colliers, saisons, parts, c)
    if parts and personnes:
        verifier_personnes(personnes, parts, c)
    if saisons and parts and finale:
        verifier_finale(finale, saisons, parts, c)

    print(f"saisons        : {len(saisons or [])}")
    print(f"participations : {len(parts or [])}")
    print(f"personnes      : {len(personnes or [])}")
    print(f"epreuves       : {len(epreuves or [])}")
    print(f"conseils       : {len(conseils or [])}")
    print(f"colliers       : {len(colliers or [])}")
    print(f"fins de saison : {len((finale or {}).get('lignes') or [])}")

    if c.constats:
        print(f"\n{len(c.constats)} limite(s) connue(s) et assumee(s) :")
        for x in c.constats:
            print(f"  · {x}")

    if c.avertissements:
        print(f"\n{len(c.avertissements)} avertissement(s) :")
        for a in c.avertissements:
            print(f"  ~ {a}")

    if c.erreurs:
        print(f"\n{len(c.erreurs)} ERREUR(S) :")
        for e in c.erreurs:
            print(f"  ! {e}")
        return 1

    print("\nOK  aucune incoherence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
