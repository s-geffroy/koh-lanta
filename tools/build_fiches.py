#!/usr/bin/env python3
"""Fabrique une page par aventurier et une page par saison.

POURQUOI CE SCRIPT EXISTE. Le site est une suite d'essais ; ses 531 personnes
et ses 34 saisons n'y existaient que comme LIGNES de deux grands tableaux.
Aucun nom n'etait cliquable nulle part. Chercher « Teheiura » demandait de
trier une table de 531 lignes -- et repondre a « il est ou au classement ? »
demandait de le faire a la main, une personne a la fois.

COMMENT, EN SAFE MODE. Jekyll ne peut pas engendrer des pages depuis `_data/` :
le greffon qui le ferait n'est pas dans la liste blanche de GitHub Pages, et
`_plugins/` est ignore sans le moindre avertissement. La seule voie propre est
donc celle-ci : Python ecrit des pages COMMITEES, minuscules, qui ne portent
qu'un identifiant, et un gabarit les remplit depuis `_data/fiches.yml`.

    tools/atelier python3 tools/build_fiches.py

Le gabarit lit `site.data.fiches.aventuriers[page.aventurier]` : un acces par
cle, en temps constant. La tentation etait de faire chercher au gabarit sa
propre ligne dans une liste de 531 -- 531 pages parcourant 531 entrees font
282 000 iterations Liquid a chaque construction, pour un resultat identique.

Les fichiers produits sont regeneres a l'identique a chaque execution : ils
sont commites parce que GitHub Pages n'a pas le droit de les fabriquer, pas
parce qu'ils seraient tenus a la main.
"""
import argparse
import collections
import json
import os
import re
import sys
import unicodedata

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(ICI, "extraction"))
RACINE = os.path.dirname(ICI)
DATA = os.path.join(RACINE, "_data")

import indicateurs                                            # noqa: E402

# LES CHAINES QUE LE YAML DE RUBY LIT COMME DES NOMBRES, ET QUE PYYAML ECRIT
# NUES. Le piege a ete paye en ligne. YAML 1.1 -- la version que Psych
# implemente, donc celle de Jekyll -- accepte la VIRGULE comme separateur de
# milliers dans un entier : « 39,9 » y vaut trois cent quatre-vingt-dix-neuf.
# PyYAML ne connait pas cette forme : il n'y voit qu'une chaine et l'ecrit sans
# guillemets. Les deux bibliotheques ne sont pas d'accord, et c'est le site qui
# tranche -- la part de marche s'est publiee « 395 % » au lieu de « 39,5 % ».
# Rien n'avait echoue : ni la construction, ni le controle, ni l'affichage.
#
# On force donc les guillemets des que la chaine ressemble a un nombre pour
# Ruby. Une chaine entre guillemets est une chaine dans les deux versions de
# YAML, et c'est la seule facon de ne pas dependre de celle qui relit.
RE_NOMBRE_RUBY = re.compile(r"^[-+]?[0-9][0-9_,]*(\.[0-9_]*)?$")


def _chaine_yaml(dumper, valeur):
    style = '"' if RE_NOMBRE_RUBY.match(valeur) else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", valeur, style=style)


yaml.SafeDumper.add_representer(str, _chaine_yaml)
from build_stats import LIBELLE_SORT, arrondi                 # noqa: E402

DOSSIER_AVENTURIERS = os.path.join(RACINE, "aventuriers")
DOSSIER_SAISONS = os.path.join(RACINE, "saisons")
SORTIE_DATA = os.path.join(DATA, "fiches.yml")
SORTIE_URLS = os.path.join(DATA, "saisons_urls.yml")

ENTETE = ("# ATTENTION : fichier genere par tools/build_fiches.py.\n"
          "# Ne pas editer a la main : toute modification sera ecrasee.\n"
          "#\n"
          "# Une entree par aventurier et une par saison, indexees par leur\n"
          "# identifiant. Les gabarits `fiche-aventurier` et `fiche-saison` y\n"
          "# accedent par cle -- jamais en parcourant la liste entiere.\n"
          "#\n"
          "#     tools/atelier python3 tools/build_fiches.py\n"
          "#\n")


def charger(nom):
    with open(os.path.join(DATA, nom + ".yml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def liste(d, cle):
    """Un fichier de donnees est tantot une liste, tantot un dict qui en porte une."""
    return d[cle] if isinstance(d, dict) else d


def fiches_des_aventuriers(parts, personnes, saisons, indiv, classement, natures, colliers):
    par_saison = {s["id"]: s for s in saisons}
    par_pid = collections.defaultdict(list)
    for p in parts:
        par_pid[p["id"]].append(p)

    ind = {(x["saison"], x["id"]): x for x in indiv}
    rang = {x["id"]: x for x in classement.get("tous") or []}
    perso = {p["id"]: p for p in personnes}

    # Un collier peut passer de main en main : `detenteurs` porte celles qui
    # l'ont eu, chacune avec son identifiant quand il a pu etre resolu.
    cols = collections.Counter()
    joues = collections.Counter()
    for c in colliers:
        vus = set()
        for d in (c.get("detenteurs") or []) + (c.get("detenteurs_suivants") or []):
            if d.get("resolu") and d.get("id"):
                vus.add(d["id"])
        for pid in vus:
            cols[(c.get("saison"), pid)] += 1
            if c.get("statut") == "utilise":
                joues[(c.get("saison"), pid)] += 1

    nat = {(x["saison"], x["id"]): x for x in natures}

    out = {}
    for pid, lot in par_pid.items():
        lot = sorted(lot, key=lambda p: (par_saison.get(p["saison"], {}).get("annee") or 0,
                                         p["saison"]))
        base = lot[-1]
        r = rang.get(pid) or {}
        participations = []
        for p in lot:
            s = par_saison.get(p["saison"], {})
            i = ind.get((p["saison"], pid)) or {}
            n = nat.get((p["saison"], pid)) or {}
            participations.append({
                "saison": p["saison"],
                "titre": s.get("titre"),
                "annee": s.get("annee"),
                "numero": s.get("numero"),
                "speciale": bool(s.get("speciale")),
                "en_cours": bool(s.get("en_cours")),
                "lieu": s.get("lieu"),
                "effectif": sum(1 for x in parts if x["saison"] == p["saison"]),
                "age": p.get("age"),
                "profession": p.get("profession"),
                "localisation": p.get("localisation"),
                "tribu": p.get("tribu"),
                "couleur": p.get("couleur"),
                "sort": p.get("sort"),
                "libelle_sort": LIBELLE_SORT.get(p.get("sort"), p.get("motif")),
                "jour_sortie": p.get("jour_sortie"),
                "classement": p.get("classement"),
                "voix_recues": p.get("votes_recus"),
                "conseils_assistes": i.get("conseils_assistes"),
                "menace": i.get("menace"),
                # Les COMPTEURS valent 0, jamais nil : le gabarit doit pouvoir
                # ecrire `{% if x > 0 %}` sans risquer une comparaison avec
                # nil, que Liquid ne sait pas faire. Les MESURES, elles,
                # restent nil quand elles n'existent pas -- « 0 % de justesse »
                # et « justesse inconnue » ne sont pas la meme phrase.
                "bulletins_emis": i.get("bulletins_emis") or 0,
                "justesse_vote": i.get("justesse_vote"),
                "conseils_vise": i.get("conseils_vise") or 0,
                "evasion": i.get("evasion"),
                "epreuves_gagnees": i.get("epreuves_gagnees") or 0,
                "epreuves_disputees": i.get("epreuves_disputees") or 0,
                "ratio_epreuves": i.get("ratio_epreuves"),
                "colliers": cols.get((p["saison"], pid)) or 0,
                "colliers_joues": joues.get((p["saison"], pid)) or 0,
                "epreuves_nommees": [{"nom": affichable(x),
                                      "id": identifiant(x)}
                                     for x in (n.get("epreuves") or [])],
                "natures": [{"nature": k, "effectif": v}
                            for k, v in sorted((n.get("natures") or {}).items(),
                                               key=lambda x: (-x[1], x[0]))],
            })

        titres = sum(1 for p in lot if p.get("sort") == "vainqueur")
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        voix = [p.get("votes_recus") for p in lot if p.get("votes_recus") is not None]
        jours = [p.get("jour_sortie") for p in lot if p.get("jour_sortie")]
        out[pid] = {
            "id": pid,
            "nom": base.get("nom_complet") or base.get("nom"),
            "prenom": base.get("nom"),
            "genre": base.get("genre"),
            "profession": base.get("profession"),
            "localisation": base.get("localisation"),
            "naissance": (perso.get(pid) or {}).get("naissance"),
            "participations": participations,
            "nb_participations": len(lot),
            "titres": titres,
            "finales": finales,
            "voix_recues": sum(voix) if voix else None,
            "jours_total": sum(jours) if jours else None,
            "jour_max": max(jours) if jours else None,
            # Le rang n'existe que pour les saisons achevees : une saison en
            # cours n'a pas de sort, donc pas de parcours mesurable.
            "rang": r.get("rang"),
            "score": r.get("score"),
            "part_top": r.get("part_top"),
            "rang_p05": r.get("rang_p05"),
            "rang_p95": r.get("rang_p95"),
            "rangs": r.get("rangs") or {},
        }
    return out


def fiches_des_saisons(parts, saisons, conseils, epreuves, audiences, classement, resume):
    par_pid_rang = {x["id"]: x for x in classement.get("tous") or []}
    aud = {a["saison"]: a for a in (audiences.get("saisons") or [])}
    res = {x["id"]: x for x in resume}
    par_saison = collections.defaultdict(list)
    for p in parts:
        par_saison[p["saison"]].append(p)

    cons = collections.defaultdict(list)
    for c in conseils:
        cons[c.get("saison")].append(c)
    epr = collections.defaultdict(list)
    for e in epreuves:
        epr[e.get("saison")].append(e)

    ordre = {"vainqueur": 0, "finaliste": 1}
    out = {}
    for s in saisons:
        sid = s["id"]
        # Deux saisons ont ete ANNULEES avant tournage : elles n'ont ni titre,
        # ni casting, ni un seul conseil. Leur donner une page servirait une
        # fiche vide sous une URL qui semble promettre autre chose ; elles
        # restent listees sur /saisons/, ou leur ligne dit ce qu'elles sont.
        if s.get("annulee"):
            continue
        lot = par_saison.get(sid) or []
        casting = []
        for p in sorted(lot, key=lambda p: (ordre.get(p.get("sort"), 2),
                                            -(p.get("jour_sortie") or 0),
                                            p.get("nom") or "")):
            r = par_pid_rang.get(p["id"]) or {}
            casting.append({
                "id": p["id"],
                "nom": p.get("nom_complet") or p.get("nom"),
                "age": p.get("age"),
                "genre": p.get("genre"),
                "profession": p.get("profession"),
                "tribu": p.get("tribu"),
                "couleur": p.get("couleur"),
                "sort": p.get("sort"),
                "libelle_sort": LIBELLE_SORT.get(p.get("sort"), p.get("motif")),
                "jour_sortie": p.get("jour_sortie"),
                "classement": p.get("classement"),
                "voix_recues": p.get("votes_recus"),
                "rang": r.get("rang"),
            })
        el = [c for c in cons.get(sid) or [] if c.get("type") == "elimination"]
        a = aud.get(sid) or {}
        r = res.get(sid) or {}
        out[sid] = {
            "id": sid,
            "numero": s.get("numero"),
            "titre": s.get("titre"),
            "annee": s.get("annee"),
            "lieu": s.get("lieu"),
            "pays": s.get("pays"),
            "speciale": bool(s.get("speciale")),
            "en_cours": bool(s.get("en_cours")),
            "duree_jours": s.get("duree_jours"),
            "effectif": len(lot),
            "tribus": s.get("tribus") or [],
            "vainqueurs": [c for c in casting if c["sort"] == "vainqueur"],
            "finalistes": [c for c in casting if c["sort"] == "finaliste"],
            "casting": casting,
            "conseils": len(el),
            "conseils_complets": sum(1 for c in el if c.get("complet")),
            "bulletins": sum(len(c.get("votes") or []) for c in el),
            "epreuves": len(epr.get(sid) or []),
            "epreuves_individuelles": sum(1 for e in epr.get(sid) or []
                                          if e.get("forme") == "individuelle"),
            "age_moyen": r.get("age_moyen"),
            "survie_moyenne": r.get("survie_moyenne"),
            "abandons": r.get("abandons"),
            "audience_lancement": a.get("lancement"),
            "audience_finale": a.get("finale"),
            "audience_moyenne": a.get("moyenne"),
            "audience_pdm": a.get("moyenne_pdm"),
        }
    return out


# --------------------------------------------------------------------------
# LE FRONT MATTER QUE SEUL UN MOTEUR DE RECHERCHE LIT.
#
# `jekyll-seo-tag` fabrique le <title> et la <meta name="description"> a partir
# de `title:` et de `description:`. Faute de `description:`, il retombe sur
# celle du SITE : les 565 fiches servaient donc, mot pour mot, la meme phrase.
# Un moteur lit cela comme 565 pages interchangeables et n'en indexe qu'une
# partie. C'est le defaut que ces fonctions corrigent.
#
# CE QUI REND LA MANOEUVRE SANS RISQUE VISUEL : sur ces deux gabarits, le H1 ne
# vient PAS de `page.title`. `_layouts/fiche-aventurier.html` affiche
# `{{ a.nom }}`, `_layouts/fiche-saison.html` affiche `{{ s.titre }}`, tous
# deux lus dans `_data/fiches.yml`. Ici `page.title` n'est lu que par le
# greffon : on peut l'enrichir sans qu'un caractere bouge a l'ecran.
#
# LA LONGUEUR QU'ON OUBLIE. Le greffon ajoute « | Koh-Lanta en chiffres » a
# tout titre : 24 caracteres qui comptent dans ce que le moteur affiche. Un
# titre de fiche est donc plafonne a TITRE_MAX, et non a la soixantaine
# habituelle. C'est aussi pourquoi ces titres ne repetent pas « Koh-Lanta » :
# le suffixe le porte deja.
SUFFIXE_TITRE = " | Koh-Lanta en chiffres"
TITRE_MAX = 62 - len(SUFFIXE_TITRE)
DESCRIPTION_MAX = 155

# Le sort, dit au present et sans accord. Les libelles de `LIBELLE_SORT` sont
# au masculin (« Elimine au conseil ») : les reprendre imposerait d'accorder
# 531 fiches sur un champ `genre` a deux valeurs, et de trancher les cas ou il
# manque. Un verbe n'a pas ce probleme.
VERBE_SORT = {
    "vainqueur": "gagne la saison",
    "finaliste": "va en finale",
    "elimine_conseil": "sort au conseil",
    "elimine_poteaux": "sort aux poteaux",
    "elimine_orientation": "sort à l'orientation",
    "elimine_ambassadeurs": "sort aux ambassadeurs",
    "elimine_duel": "sort en duel",
    "elimine_exil": "sort sur l'île",
    "abandon_medical": "abandonne sur blessure",
    "abandon_volontaire": "abandonne",
    "disqualifie": "quitte le jeu sur disqualification",
}


def ordinal(n):
    return "1er" if n == 1 else f"{n}e"


def compte(n, singulier, pluriel):
    return f"{n} {singulier}" if abs(n) < 2 else f"{n} {pluriel}"


def premier_qui_tient(candidats, maximum=TITRE_MAX):
    """Rend le premier libelle qui tient, sinon le plus court, tronque.

    Tronquer au caractere pres donne « Clarisse Cresseveur — Les Reliqu ».
    On prefere une formule plus pauvre mais entiere, d'ou cette echelle de
    repli ecrite d'avance, du plus informatif au plus sobre.
    """
    for c in candidats:
        if len(c) <= maximum:
            return c
    court = min(candidats, key=len)
    return court[:maximum].rstrip(" -—,:") if len(court) > maximum else court


def assembler(tete, clauses, chute, maximum=DESCRIPTION_MAX):
    """Ajoute les clauses tant que la phrase tient, et jette le reste.

    Le budget est calcule chute comprise : une description coupee par le moteur
    perd sa fin, or c'est la fin qui dit ce que la page apporte.
    """
    fin = f" {chute}" if chute else ""
    texte = tete
    for c in clauses:
        if not c:
            continue
        essai = f"{texte}, {c}"
        if len(essai) + 1 + len(fin) <= maximum:
            texte = essai
    if len(texte) + 1 + len(fin) <= maximum:
        return f"{texte}.{fin}"
    return f"{texte}."


def avec_marque(titre):
    """Prefixe « Koh-Lanta » -- sauf quand le titre le porte deja.

    La saison 1 s'appelle « Les Aventuriers de Koh-Lanta » : sans ce garde-fou,
    sa description commence par « Koh-Lanta Les Aventuriers de Koh-Lanta ».
    """
    return titre if "Koh-Lanta" in titre else f"Koh-Lanta {titre}"


def titre_seo_aventurier(e):
    p = e["participations"]
    if len(p) == 1:
        u = p[0]
        return premier_qui_tient([
            f"{e['nom']} — {u['titre']} ({u['annee']})",
            f"{e['nom']} ({u['annee']})",
            e["nom"],
        ])
    return premier_qui_tient([
        f"{e['nom']} — {len(p)} saisons jouées",
        f"{e['nom']} — {len(p)} saisons",
        e["nom"],
    ])


def description_seo_aventurier(e, joueurs_classes):
    p = e["participations"]
    rang = (f"{ordinal(e['rang'])} sur {joueurs_classes} au classement"
            if e.get("rang") and joueurs_classes else None)
    if len(p) == 1:
        u = p[0]
        verbe = VERBE_SORT.get(u.get("sort"), "est encore en jeu")
        tete = f"{e['nom']}, {avec_marque(u['titre'])} ({u['annee']}) : {verbe}"
        if u.get("jour_sortie"):
            tete += f" le {ordinal(u['jour_sortie'])} jour"
        clauses = [
            (f"{ordinal(u['classement'])} sur {u['effectif']}"
             if u.get("classement") else None),
            (compte(u["epreuves_gagnees"], "épreuve gagnée", "épreuves gagnées")
             if u.get("epreuves_disputees") else None),
            (compte(u["voix_recues"], "voix reçue", "voix reçues")
             if u.get("voix_recues") else None),
        ]
        chute = f"{rang} des aventuriers." if rang else "Son parcours en chiffres."
        return assembler(tete, clauses, chute)

    annees = sorted(u["annee"] for u in p)
    tete = (f"{e['nom']}, {len(p)} saisons de Koh-Lanta entre {annees[0]} et "
            f"{annees[-1]} : {e['jours_total']} jours de jeu")
    clauses = [
        compte(e["titres"], "victoire", "victoires") if e.get("titres") else None,
        compte(e["finales"], "finale", "finales") if e.get("finales") else None,
        compte(e["voix_recues"], "voix reçue", "voix reçues") if e.get("voix_recues") else None,
    ]
    chute = f"{rang} des aventuriers." if rang else "Son parcours en chiffres."
    return assembler(tete, clauses, chute)


def titre_seo_saison(e):
    rang = ("édition spéciale" if e.get("speciale")
            else f"saison {e['numero']}" if e.get("numero") else None)
    candidats = []
    if rang:
        candidats.append(f"{e['titre']} ({e['annee']}) — {rang}")
    candidats.append(f"{e['titre']} ({e['annee']})")
    candidats.append(e["titre"])
    return premier_qui_tient(candidats)


def description_seo_saison(e):
    quoi = ("édition spéciale" if e.get("speciale")
            else f"saison {e['numero']}" if e.get("numero") else "saison")
    tete = f"{avec_marque(e['titre'])}, {quoi} diffusée en {e['annee']}"
    if e.get("pays"):
        tete += f" ({e['pays']})"
    tete += f" : {compte(e['effectif'], 'aventurier', 'aventuriers')}"
    clauses = [
        f"{e['duree_jours']} jours" if e.get("duree_jours") else None,
        compte(e["conseils"], "conseil", "conseils") if e.get("conseils") else None,
        compte(e["bulletins"], "bulletin", "bulletins") if e.get("bulletins") else None,
    ]
    noms = [v["nom"] for v in (e.get("vainqueurs") or [])]
    if e.get("en_cours"):
        chute = "Saison en cours."
    elif len(noms) > 1:
        chute = f"Victoire de {' et '.join(noms)}."
    elif noms:
        chute = f"Victoire de {noms[0]}."
    else:
        chute = "Le casting et les chiffres de la saison."
    return assembler(tete, clauses, chute)


# --------------------------------------------------------------------------
# LES QUESTIONS QU'ON POSE VRAIMENT.
#
# « quel age avait X a koh lanta », « X a-t-il gagne koh lanta », « combien de
# fois X a participe » : ce sont des recherches, et la fiche avait la reponse
# sans jamais la formuler. Six questions par aventurier, ecrites comme on les
# tape, et repondues avec les champs deja calcules.
#
# UNE RESERVE A CONNAITRE AVANT D'EN ATTENDRE TROP : depuis 2023, Google
# reserve l'AFFICHAGE enrichi des blocs FAQ aux sites gouvernementaux et de
# sante. L'accordeon n'apparaitra donc pas dans les resultats. Ce qui travaille
# ici, c'est le texte visible sur la page -- il repond mot pour mot a la
# question tapee, et c'est cela qui se classe. Le balisage FAQPage est pose en
# plus, pour ce qu'il vaut, pas pour ce qu'il promet.


# Les lettres que NFKD NE DECOMPOSE PAS. « é » se decompose en « e » plus un
# accent, que l'encodage ASCII jette : le « e » reste. « œ » n'est pas une
# lettre accentuee, c'est une lettre a part entiere -- NFKD la laisse telle
# quelle, et l'ASCII la jette ENTIEREMENT. L'adresse de Frank Lebœuf etait donc
# /aventuriers/frank-leb-uf/ : son nom avale sa propre lettre, dans la barre
# d'adresse comme dans un resultat de recherche.
#
# Sur les 531 noms du site, « œ » est le seul caractere perdu -- verifie, pas
# suppose. Les autres sont posees pour la meme raison : le jour ou un nom en
# porte une, personne ne repassera par ici.
LIGATURES = {"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE",
             "ø": "o", "Ø": "O", "ß": "ss", "đ": "d", "Đ": "D"}

# L'ancienne adresse d'une fiche dont l'identifiant a change, gardee vivante
# par `jekyll-redirect-from`. Sans elle, tout lien pose ailleurs vers l'ancienne
# forme tomberait le jour de la bascule -- et on ne le saurait jamais.
ANCIENNES_ADRESSES = {"frank-leboeuf": "frank-leb-uf"}


def identifiant(nom):
    """Un slug d'URL, sans accent ni majuscule, stable dans le temps.

    Vit ici et non dans tools/build_epreuves.py parce que les DEUX en ont
    besoin : celui-la pour nommer la page d'une epreuve, celui-ci pour poser
    dans la fiche d'un aventurier de quoi la lier.
    """
    for lettre, remplacement in LIGATURES.items():
        nom = nom.replace(lettre, remplacement)
    plat = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    garde = [c.lower() if c.isalnum() else "-" for c in plat]
    return "-".join("".join(garde).split("-")).strip("-")


def affichable(nom):
    """La premiere lettre en capitale, et rien d'autre.

    Les noms d'epreuve viennent du wiki tels quels : « la bascule » y voisine
    avec « Parcours du combattant ». En tete d'un titre de page et d'un H1, la
    minuscule se lit comme une faute. On ne touche a rien d'autre : corriger
    silencieusement un nom de source serait pire que la minuscule.
    """
    return nom[:1].upper() + nom[1:] if nom else nom


def slug_saison(titre):
    """L'URL d'une saison : « koh-lanta-palawan » et non « s07 ».

    Un identifiant technique ne dit rien a personne, ni dans la barre
    d'adresse ni dans un resultat de recherche -- alors que le nom de la
    saison EST ce qu'on tape. Le prefixe n'est pas ajoute quand le titre porte
    deja la marque : la saison 1 s'appelle « Les Aventuriers de Koh-Lanta ».

    L'ancienne adresse ne meurt pas pour autant : `redirect_from` la garde
    vivante, sinon tout lien pose ailleurs vers /saisons/s07/ tomberait.
    """
    base = identifiant(titre)
    return base if "koh-lanta" in base else f"koh-lanta-{base}"


def accord(genre, masculin, feminin):
    """Accorde au feminin quand `genre` vaut « f ». Le champ est renseigne sur
    les 531 fiches -- verifie -- donc pas de troisieme cas a prevoir."""
    return feminin if genre == "f" else masculin


def de_(nom):
    """« de Claude » mais « d'Abdellah ». L'elision devant voyelle ou h.

    Sans elle, une question sur six s'ouvrait sur « Quel est le metier de
    Abdellah Akriche ? » -- une faute que personne n'ecrit, et que 138 des 531
    fiches auraient publiee.
    """
    return f"d’{nom}" if nom[:1].lower() in "aeiouyhàâäéèêëîïôöùûü" else f"de {nom}"


def a_designation(d):
    """« a Koh-Lanta Palawan », mais « aux Aventuriers de Koh-Lanta ».

    Meme probleme que `de_` sur un prenom, et meme cause : UNE saison porte un
    titre qui commence par un article. `avec_marque` prefixe « Koh-Lanta » a
    trente-trois titres sur trente-quatre -- ceux-la commencent donc par un nom
    propre et « a » suffit. La premiere, « Les Aventuriers de Koh-Lanta »,
    porte deja la marque : rien ne la prefixe, et « a Les Aventuriers » est
    une faute. Les autres articles sont traites aussi : ils ne se presentent
    pas aujourd'hui, mais un titre futur n'aura pas a repasser ici.
    """
    for article, contracte in (("Les ", "aux "), ("Le ", "au "), ("La ", "à la ")):
        if d.startswith(article):
            return contracte + d[len(article):]
    return f"à {d}"


def de_designation(d):
    """« de Koh-Lanta Palawan », mais « des Aventuriers de Koh-Lanta ».

    Le pendant de `a_designation`, pour les tours ou la saison est complement
    du nom : « le lieu de tournage DE Koh-Lanta Palawan ».
    """
    for article, contracte in (("Les ", "des "), ("Le ", "du "), ("La ", "de la ")):
        if d.startswith(article):
            return contracte + d[len(article):]
    return f"de {d}"


def milliers(n):
    """8127000 -> « 8 127 000 ». L'espace, jamais la virgule anglaise.

    Les audiences se comptent en millions : lues d'un bloc, elles ne se lisent
    pas. Ce qui est publie l'est pour etre lu a voix haute.
    """
    return f"{int(n):,}".replace(",", "\u00a0")


def decimal(x):
    """32.7 -> « 32,7 », et 37.0 -> « 37 ». La virgule, pas le point.

    Le point decimal est anglais. Et une moyenne qui tombe juste n'a pas
    besoin de son zero : « 37 ans », pas « 37,0 ans ».
    """
    if float(x) == int(float(x)):
        return str(int(float(x)))
    return f"{x}".replace(".", ",")


def _liste(morceaux):
    """« a, b et c » -- la virgule partout sauf devant le dernier."""
    if len(morceaux) < 2:
        return "".join(morceaux)
    return ", ".join(morceaux[:-1]) + " et " + morceaux[-1]


def _edition(p):
    """« en 2001 (Les Aventuriers de Koh-Lanta) ».

    La forme est cette annee-la, et pas « lors de {titre} », parce que la
    saison 1 s'appelle « Les Aventuriers de Koh-Lanta » : toute preposition
    donnait « lors de Les Aventuriers ». Passer par l'annee evite d'avoir a
    contracter l'article de trente-quatre titres.
    """
    return f"en {p['annee']} ({p['titre']})"


def faq_aventurier(e, joueurs_classes):
    nom, genre = e["nom"], e.get("genre")
    il = accord(genre, "il", "elle")
    a_t_il = accord(genre, "a-t-il", "a-t-elle")
    alle = accord(genre, "allé", "allée")
    parts = sorted(e["participations"], key=lambda p: p["annee"])
    q = []

    q.append((
        f"Quel âge avait {nom} à Koh-Lanta ?",
        _liste([f"{p['age']} ans {_edition(p)}" for p in parts]) + ".",
    ))

    metiers = []
    for p in parts:
        if p.get("profession") and p["profession"] not in [m[0] for m in metiers]:
            metiers.append((p["profession"], p["annee"]))
    if len(metiers) == 1:
        reponse = f"{metiers[0][0]}, profession déclarée au casting."
    else:
        reponse = _liste([f"{m} ({an})" for m, an in metiers]) + "."
    q.append((f"Quel est le métier {de_(nom)} ?", reponse))

    titres = [p for p in parts if p.get("sort") == "vainqueur"]
    if len(titres) > 1:
        reponse = (f"Oui, {compte(len(titres), 'fois', 'fois')} : "
                   f"{_liste([_edition(p) for p in titres])}.")
    elif titres:
        reponse = f"Oui, {_edition(titres[0])}."
    elif e.get("finales"):
        reponse = (f"Non. {nom} est {alle} en finale "
                   f"{compte(e['finales'], 'fois', 'fois')} sans jamais "
                   f"remporter le titre.")
    elif len(parts) == 1:
        reponse = f"Non. {nom} n’a joué qu’une saison, {_edition(parts[0])}."
    else:
        reponse = f"Non, sur ses {len(parts)} participations."
    q.append((f"{nom} {a_t_il} gagné Koh-Lanta ?", reponse))

    if len(parts) == 1:
        reponse = f"Une seule fois, {_edition(parts[0])}."
    else:
        editions = [f"{p['titre']} ({p['annee']})" for p in parts]
        reponse = f"{len(parts)} fois : {_liste(editions)}."
    q.append((f"Combien de fois {nom} {a_t_il} participé à Koh-Lanta ?", reponse))

    meilleure = min(parts, key=lambda p: (p.get("classement") or 999))
    verbe = VERBE_SORT.get(meilleure.get("sort"), "est encore en jeu")
    if meilleure.get("classement"):
        reponse = (f"Son meilleur parcours : {ordinal(meilleure['classement'])} sur "
                   f"{meilleure['effectif']} {_edition(meilleure)}, où {il} {verbe}")
    else:
        reponse = f"{_edition(meilleure).capitalize()}, où {il} {verbe}"
    if meilleure.get("jour_sortie"):
        reponse += f" le {ordinal(meilleure['jour_sortie'])} jour"
    q.append((f"Jusqu’où {nom} est-{il} {alle} à Koh-Lanta ?", reponse + "."))

    if e.get("rang") and joueurs_classes:
        q.append((
            f"Quel est le classement {de_(nom)} parmi les aventuriers de Koh-Lanta ?",
            f"{ordinal(e['rang'])} sur {joueurs_classes}. Ce classement mesure "
            f"quatre façons de bien jouer — le parcours, les épreuves, la "
            f"discrétion et la lecture du vote — sans jamais regarder qui a gagné.",
        ))

    return [{"q": question, "r": reponse} for question, reponse in q]



def faq_saison(e):
    """Les questions qu'on tape sur une saison, et leurs reponses.

    « qui a gagne koh lanta palawan », « combien de jours dure koh lanta »,
    « ou a ete tourne koh lanta » : la fiche de saison avait tous ces chiffres
    et n'en formulait aucun comme une question. Les 531 fiches d'aventurier en
    posaient six chacune ; les 34 fiches de saison, aucune.

    LA GRAMMAIRE EST LE PIEGE, et c'est le meme que sur les prenoms : un titre
    de saison ne se met pas n'importe ou dans une phrase. On ne le place donc
    jamais en SUJET d'un verbe -- « Combien de jours a dure Les Aventuriers de
    Koh-Lanta ? » demanderait un accord par titre -- mais toujours en
    complement, derriere `a_designation` ou `de_designation`, qui contractent
    l'article.

    AUCUN COMPTE DE VAINQUEURS, AUCUNE QUALIFICATION. Trois saisons portent
    deux noms au champ `vainqueurs` ; la fiche les affiche tous les deux depuis
    toujours, et la reponse dit exactement la meme chose. Ecrire « ex aequo »
    serait une these, et les donnees ne la portent pas : sur Bocas del Toro,
    les deux noms n'ont pas le meme classement. Ecrire « 1 vainqueur » n'est
    pas mieux -- on ne compte pas ce qu'on nomme.
    """
    marque = avec_marque(e["titre"])
    a_elle, d_elle = a_designation(marque), de_designation(marque)
    q = []

    noms = [v["nom"] for v in (e.get("vainqueurs") or [])]
    if noms:
        reponse = f"{_liste(noms)}. La saison a été diffusée en {e['annee']}."
        finalistes = [v["nom"] for v in (e.get("finalistes") or [])]
        if finalistes:
            mot = "Finaliste" if len(finalistes) == 1 else "Finalistes"
            reponse += f" {mot} : {_liste(finalistes)}."
    elif e.get("en_cours"):
        reponse = ("La saison est en cours de diffusion : le vainqueur n’est "
                   "pas encore connu.")
    else:
        reponse = "Aucun vainqueur n’est relevé pour cette saison."
    q.append((f"Qui a gagné {marque} ?", reponse))

    reponse = f"{compte(e['effectif'], 'aventurier', 'aventuriers')} au départ"
    if e.get("age_moyen"):
        reponse += f", {decimal(e['age_moyen'])} ans de moyenne d’âge"
    reponse += "."
    if e.get("abandons"):
        reponse += f" {compte(e['abandons'], 'abandon', 'abandons')} en cours de jeu."
    q.append((f"Combien d’aventuriers ont participé {a_elle} ?", reponse))

    if e.get("duree_jours"):
        q.append((f"Combien de jours a duré l’aventure {a_elle} ?",
                  f"{e['duree_jours']} jours."))

    if e.get("lieu"):
        reponse = e["lieu"]
        if e.get("pays") and e["pays"] not in e["lieu"]:
            reponse += f", {e['pays']}"
        q.append((f"Quel est le lieu de tournage {d_elle} ?", reponse + "."))

    reponse = f"{compte(e['conseils'], 'conseil', 'conseils')} d’élimination."
    if e.get("conseils_complets"):
        reponse += (f" Le dépouillement de {e['conseils_complets']} d’entre eux "
                    f"est connu au bulletin près, pour "
                    f"{compte(e['bulletins'], 'bulletin relevé', 'bulletins relevés')}.")
    q.append((f"Combien de conseils d’élimination {a_elle} ?", reponse))

    if e.get("epreuves"):
        reponse = compte(e["epreuves"], "épreuve relevée", "épreuves relevées")
        # La clause ne se pose que si elle apprend quelque chose : « 4 epreuves
        # relevees, dont 4 individuelles » ne dit rien de plus que la premiere
        # moitie de la phrase.
        if 0 < (e.get("epreuves_individuelles") or 0) < e["epreuves"]:
            reponse += f", dont {e['epreuves_individuelles']} individuelles"
        q.append((f"Combien d’épreuves ont été courues {a_elle} ?", reponse + "."))

    if e.get("audience_moyenne"):
        reponse = f"{milliers(e['audience_moyenne'])} téléspectateurs en moyenne"
        if e.get("audience_pdm"):
            reponse += f", {decimal(e['audience_pdm'])} % de part de marché"
        reponse += "."
        if e.get("audience_lancement") and e.get("audience_finale"):
            reponse += (f" Lancement à {milliers(e['audience_lancement'])}, "
                        f"finale à {milliers(e['audience_finale'])}.")
        q.append((f"Quelle audience a fait {marque} ?", reponse))

    return [{"q": question, "r": reponse} for question, reponse in q]



# `image` remplace, pour cette page seule, la vignette par defaut posee dans
# _config.yml. Sans cette ligne, les 621 pages partageaient le meme apercu :
# celui du site, quel que soit le lien envoye.
GABARIT = """---
layout: {layout}
title: {titre}
description: {description}
image: {image}
permalink: {permalink}
{redirect}{cle}: {valeur}
---
"""


def ecrire_pages(dossier, layout, cle, entrees, titre_de, description_de,
                 permalink_de, rapport, image_de=None, redirect_de=None):
    """Ecrit une page par entree, et RETIRE celles qui n'ont plus de donnee.

    Sans le retrait, une personne disparue des donnees laisserait derriere elle
    une page orpheline, servie indefiniment et alimentee par un `nil` : le
    gabarit n'echouerait pas, il afficherait une fiche vide.
    """
    os.makedirs(dossier, exist_ok=True)
    voulus = set()
    for cid, e in sorted(entrees.items()):
        nom = cid + ".md"
        voulus.add(nom)
        # json.dumps et non yaml.safe_dump : ce dernier termine un scalaire
        # seul par une ligne « ... », le marqueur de fin de document YAML. Pose
        # au milieu d'un front matter, il coupe la page en deux et Jekyll ne
        # voit plus ni le permalien ni l'identifiant. Une chaine JSON est un
        # scalaire YAML double-quote valide, et rien d'autre.
        contenu = GABARIT.format(
            layout=layout,
            titre=json.dumps(titre_de(e), ensure_ascii=False),
            description=json.dumps(description_de(e), ensure_ascii=False),
            image=(image_de(cid) if image_de
                   else f"/assets/partage/{os.path.basename(dossier)}/{cid}.png"),
            permalink=permalink_de(cid),
            redirect=(redirect_de(cid) if redirect_de else ""),
            cle=cle, valeur=cid)
        chemin = os.path.join(dossier, nom)
        ancien = None
        if os.path.exists(chemin):
            with open(chemin, encoding="utf-8") as f:
                ancien = f.read()
        if ancien != contenu:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(contenu)
            rapport["ecrites"] += 1
    for nom in sorted(os.listdir(dossier)):
        if nom.endswith(".md") and nom not in voulus:
            os.remove(os.path.join(dossier, nom))
            rapport["retirees"] += 1
    return len(voulus)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ecrire", action="store_true",
                    help="ecrit _data/fiches.yml et les pages (defaut : essai a blanc)")
    a = ap.parse_args()

    saisons = liste(charger("saisons"), "saisons")
    parts = charger("participations")
    personnes = liste(charger("personnes"), "personnes")
    conseils = charger("conseils")
    epreuves = charger("epreuves")
    colliers = charger("colliers")
    audiences = charger("audiences")
    stats = charger("stats")
    nommees = charger("epreuves_nommees")

    indiv = indicateurs.indicateurs_individuels(saisons, parts, conseils, epreuves)
    resume = indicateurs.indicateurs_saison(saisons, parts, conseils, epreuves, colliers)

    av = fiches_des_aventuriers(parts, personnes, saisons, indiv,
                                stats.get("classement") or {},
                                nommees.get("palmares") or [], colliers)
    sa = fiches_des_saisons(parts, saisons, conseils, epreuves, audiences,
                            stats.get("classement") or {}, resume)

    print(f"aventuriers : {len(av)}   saisons : {len(sa)}")
    classes = sum(1 for x in av.values() if x.get("rang"))
    print(f"  dont {classes} avec un rang au classement "
          f"({len(av) - classes} sans : saison en cours ou parcours non mesurable)")

    if not a.ecrire:
        print("essai a blanc : rien n'est ecrit (--ecrire pour ecrire)")
        return 0

    joueurs_classes = (stats.get("classement") or {}).get("joueurs_classes")
    for e in av.values():
        e["faq"] = faq_aventurier(e, joueurs_classes)
    for cid, e in sa.items():
        e["slug"] = slug_saison(e["titre"])
        e["faq"] = faq_saison(e)
        # Les audiences se comptent en millions. Le gabarit les affichait
        # brutes -- « 8127000 telespectateurs », « 39.5 % » -- parce que Liquid
        # n'a pas de filtre de milliers et que ce depot ne calcule pas dans un
        # gabarit. La forme lisible se fabrique donc ici, a cote du reste.
        for champ in ("audience_moyenne", "audience_lancement", "audience_finale"):
            if e.get(champ):
                e[champ + "_texte"] = milliers(e[champ])
        if e.get("audience_pdm"):
            e["audience_pdm_texte"] = decimal(e["audience_pdm"])
    doublons = len(sa) - len({e["slug"] for e in sa.values()})
    if doublons:
        print(f"ARRET : {doublons} slug(s) de saison en double")
        return 1

    with open(SORTIE_DATA, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump({"aventuriers": av, "saisons": sa}, f,
                       allow_unicode=True, sort_keys=True, default_flow_style=False)
    print(f"ecrit : {SORTIE_DATA}")

    # Une table id -> slug, lue par les gabarits qui ne connaissent qu'un `s07`
    # et doivent en faire une URL. Un acces par cle, jamais un calcul.
    with open(SORTIE_URLS, "w", encoding="utf-8") as f:
        f.write("# ATTENTION : fichier genere par tools/build_fiches.py.\n"
                "# L'identifiant d'une saison vers son adresse publique.\n")
        yaml.safe_dump({cid: e["slug"] for cid, e in sa.items()}, f,
                       allow_unicode=True, sort_keys=True, default_flow_style=False)
    print(f"ecrit : {SORTIE_URLS}")

    rapport = collections.Counter()
    # Le titre du front matter n'est PAS celui qui s'affiche : le H1 des deux
    # gabarits vient de `_data/fiches.yml`. Ce titre-ci ne sort que dans la
    # balise <title>, ou il a de la place pour dire la saison et l'annee.
    n1 = ecrire_pages(DOSSIER_AVENTURIERS, "fiche-aventurier", "aventurier", av,
                      titre_seo_aventurier,
                      lambda e: description_seo_aventurier(e, joueurs_classes),
                      lambda cid: f"/aventuriers/{cid}/", rapport,
                      redirect_de=lambda cid: (
                          f"redirect_from: /aventuriers/{ANCIENNES_ADRESSES[cid]}/\n"
                          if cid in ANCIENNES_ADRESSES else ""))
    n2 = ecrire_pages(DOSSIER_SAISONS, "fiche-saison", "saison", sa,
                      titre_seo_saison, description_seo_saison,
                      lambda cid: f"/saisons/{sa[cid]['slug']}/", rapport,
                      image_de=lambda cid: f"/assets/partage/saisons/{cid}.png",
                      redirect_de=lambda cid: f"redirect_from: /saisons/{cid}/\n")
    print(f"pages : {n1} aventuriers + {n2} saisons = {n1 + n2} "
          f"({rapport['ecrites']} ecrites, {rapport['retirees']} retirees)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
