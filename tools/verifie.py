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
import os
import re
import sys
from collections import Counter, defaultdict

import yaml

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


class Controle:
    def __init__(self):
        self.erreurs = []
        self.avertissements = []

    def erreur(self, message):
        self.erreurs.append(message)

    def avertir(self, message):
        self.avertissements.append(message)

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


def verifier_participations(parts, saisons, c):
    par_id = {s["id"]: s for s in saisons}
    par_saison = defaultdict(list)

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

        tribu = p.get("tribu")
        if tribu and s.get("tribus"):
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


def verifier_epreuves(epreuves, saisons, parts, c):
    par_id = {s["id"]: s for s in saisons}
    ids = {(p["saison"], p["id"]) for p in parts}
    tribus = {s["id"]: {t["nom"].lower() for t in (s.get("tribus") or [])}
              for s in saisons}
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
        # deux vainqueurs pour une meme epreuve, c'est possible ; trois, c'est
        # presque toujours une cellule mal lue
        for e in lot:
            noms = [v["libelle"] for v in e["vainqueurs"]]
            if len(noms) > 2 and e.get("forme") != "collective":
                c.avertir(f"{sid} ep.{e['episode']} ({e['type']}) : "
                          f"{len(noms)} vainqueurs cites — {', '.join(noms)}")

    non_resolus = [v for e in epreuves for v in e["vainqueurs"] if not v.get("resolu")]
    if non_resolus:
        libelles = sorted({v["libelle"] for v in non_resolus})
        c.avertir(f"vainqueurs d'epreuve non rattaches : {len(non_resolus)} "
                  f"citation(s) — {', '.join(libelles[:6])}"
                  + (" …" if len(libelles) > 6 else ""))

    couvertes = len(par_saison)
    diffusees = sum(1 for s in saisons if not s.get("annulee"))
    if couvertes < diffusees:
        absentes = [s["id"] for s in saisons
                    if not s.get("annulee") and s["id"] not in par_saison]
        c.avertir(f"epreuves absentes pour {len(absentes)} saison(s) sur "
                  f"{diffusees} : {', '.join(absentes)}")


ISSUES_VALIDES = {"annulation_efficace", "joue_pour_rien", "elimine_avec_collier",
                  "garde_sans_usage", "non_decouvert"}
STATUTS_VALIDES = {"utilise", "non_utilise", "non_decouvert", "perdu"}


def verifier_colliers(colliers, saisons, parts, c):
    par_id = {s["id"]: s for s in saisons}
    ids = {(p["saison"], p["id"]) for p in parts}

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

    non_resolus = [x for col in colliers
                   for role in ("detenteurs", "proteges")
                   for x in col.get(role) or [] if not x.get("resolu")]
    if non_resolus:
        libelles = sorted({x["libelle"] for x in non_resolus})
        c.avertir(f"noms de colliers non rattaches : {len(non_resolus)} citation(s) "
                  f"— {', '.join(libelles[:6])}")


# Ce qui trahit un fragment de wikitexte reste dans un nom d'aventurier :
# une taille de vignette (« 75px »), une barre verticale, un parametre de lien,
# ou un espace de noms de fichier.
RE_RESIDU_WIKI = re.compile(
    r"\b\d{2,4}px\b|\||\blink\s*=|\b(?:File|Fichier|Image|Media)\s*:|"
    r"\bvignette\b|\bthumb\b|\[\[|\]\]", re.I)


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
    ids = {(p["saison"], p["id"]) for p in parts}
    connus = {s["id"] for s in saisons}

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
            if x.get("laureat") and (x["saison"], x["laureat"]) not in vainqueurs:
                c.erreur(f"{ref} : le laureat « {x['laureat']} » n'est pas le "
                         f"vainqueur declare de la saison")
        else:
            if "laureat" in x:
                c.erreur(f"{ref} : conseil d'elimination portant `laureat`")
            if x.get("elimine_rattache") and (x["saison"], x["elimine"]) in vainqueurs:
                c.erreur(f"{ref} : le vainqueur de la saison y est donne pour "
                         f"elimine — c'est le vote du jury, pas un conseil")

        # Un libelle non rattache reste tel quel dans le fichier : il doit au
        # moins ressembler a un nom. La syntaxe de vignette MediaWiki --
        # [[Fichier:Sara.png|75px|link=Sara Tallon]] -- a longtemps traverse
        # l'extraction et laissait « 75px » en guise d'aventurier, rendant 478
        # eliminations sur 681 non rattachables. La faute est corrigee dans
        # `plain()` ; ce controle est la pour qu'elle ne revienne pas.
        for champ in ("elimine", "laureat"):
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


def main():
    c = Controle()
    saisons = charger("saisons.yml")
    parts = charger("participations.yml")
    personnes = charger("personnes.yml")
    epreuves = charger("epreuves.yml")
    conseils = charger("conseils.yml")
    colliers = charger("colliers.yml")

    if saisons is None:
        c.erreur("_data/saisons.yml est absent")
    if parts is None:
        c.erreur("_data/participations.yml est absent")
    if personnes is None:
        c.erreur("_data/personnes.yml est absent")

    if saisons:
        verifier_saisons(saisons, c)
    if saisons and parts:
        verifier_participations(parts, saisons, c)
        trous(parts, saisons, c)
    if saisons and parts and epreuves:
        verifier_epreuves(epreuves, saisons, parts, c)
    if saisons and parts and conseils:
        verifier_conseils(conseils, saisons, parts, c)
    if saisons and parts and colliers:
        verifier_colliers(colliers, saisons, parts, c)
    if parts and personnes:
        verifier_personnes(personnes, parts, c)

    print(f"saisons        : {len(saisons or [])}")
    print(f"participations : {len(parts or [])}")
    print(f"personnes      : {len(personnes or [])}")
    print(f"epreuves       : {len(epreuves or [])}")
    print(f"conseils       : {len(conseils or [])}")
    print(f"colliers       : {len(colliers or [])}")

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
