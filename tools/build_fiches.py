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
import sys

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(ICI, "extraction"))
RACINE = os.path.dirname(ICI)
DATA = os.path.join(RACINE, "_data")

import indicateurs                                            # noqa: E402
from build_stats import LIBELLE_SORT, arrondi                 # noqa: E402

DOSSIER_AVENTURIERS = os.path.join(RACINE, "aventuriers")
DOSSIER_SAISONS = os.path.join(RACINE, "saisons")
SORTIE_DATA = os.path.join(DATA, "fiches.yml")

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
                "epreuves_nommees": n.get("epreuves") or [],
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


GABARIT = """---
layout: {layout}
title: {titre}
description: {description}
permalink: {permalink}
{cle}: {valeur}
---
"""


def ecrire_pages(dossier, layout, cle, entrees, titre_de, description_de,
                 permalink_de, rapport):
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
            permalink=permalink_de(cid), cle=cle, valeur=cid)
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

    with open(SORTIE_DATA, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump({"aventuriers": av, "saisons": sa}, f,
                       allow_unicode=True, sort_keys=True, default_flow_style=False)
    print(f"ecrit : {SORTIE_DATA}")

    rapport = collections.Counter()
    # Le titre du front matter n'est PAS celui qui s'affiche : le H1 des deux
    # gabarits vient de `_data/fiches.yml`. Ce titre-ci ne sort que dans la
    # balise <title>, ou il a de la place pour dire la saison et l'annee.
    joueurs_classes = (stats.get("classement") or {}).get("joueurs_classes")
    n1 = ecrire_pages(DOSSIER_AVENTURIERS, "fiche-aventurier", "aventurier", av,
                      titre_seo_aventurier,
                      lambda e: description_seo_aventurier(e, joueurs_classes),
                      lambda cid: f"/aventuriers/{cid}/", rapport)
    n2 = ecrire_pages(DOSSIER_SAISONS, "fiche-saison", "saison", sa,
                      titre_seo_saison, description_seo_saison,
                      lambda cid: f"/saisons/{cid}/", rapport)
    print(f"pages : {n1} aventuriers + {n2} saisons = {n1 + n2} "
          f"({rapport['ecrites']} ecrites, {rapport['retirees']} retirees)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
