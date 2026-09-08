#!/usr/bin/env python3
"""Recupere sur Wikidata les comptes publics et les portraits libres.

    tools/atelier python3 tools/extraction/wikidata.py

DEUX CHOSES, UNE SEULE SOURCE. Les comptes de reseaux sociaux et la photo d'un
aventurier sont deux proprietes du meme element Wikidata. C'est aussi la seule
source ou l'attribution NE SE DEVINE PAS : un compte y est rattache a une
personne identifiee, avec sa reference, et une image y porte sa licence et son
auteur. Chercher « instagram + prenom » aurait donne des liens vers la mauvaise
personne, et une photo sans droits clairs.

LA REGLE D'APPARIEMENT, ET POURQUOI ELLE EST STRICTE. Un nom ne suffit pas :
« Alain Garcia » designe plusieurs personnes. Un element n'est retenu que s'il
est un etre humain ET qu'un lien vers Koh-Lanta y est ecrit -- dans sa
description, ou dans l'une de ses declarations. Sans cette preuve, on ne
retient rien : une fiche sans photo vaut mieux qu'une fiche qui montre
quelqu'un d'autre.

LES IMAGES : LIBRES SEULEMENT. Seules sont telechargees celles dont la licence
Commons est dans LICENCES_LIBRES -- domaine public, CC0, CC BY, CC BY-SA. Tout
ce qui porte une restriction, une clause non commerciale ou sans derive est
laisse. L'auteur et la licence sont enregistres AVEC l'image : le gabarit les
affiche sous la photo, ce n'est pas optionnel.

Le brut est cache dans specs/sources/wikidata/ : c'est la preuve de provenance,
et une deuxieme execution ne redemande rien.
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import yaml

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(RACINE, "_data")
CACHE = os.path.join(RACINE, "specs", "sources", "wikidata")
PORTRAITS = os.path.join(RACINE, "assets", "portraits")
UA = {"User-Agent": "koh-lanta-dataset/1.0 (personal research)"}

# Les proprietes retenues. L'ordre est celui de l'affichage sur la fiche.
RESEAUX = [
    ("P2003", "Instagram", "https://www.instagram.com/{}/"),
    ("P2013", "Facebook", "https://www.facebook.com/{}"),
    ("P6634", "LinkedIn", "https://www.linkedin.com/in/{}"),
    ("P2002", "X", "https://x.com/{}"),
    ("P7085", "TikTok", "https://www.tiktok.com/@{}"),
    ("P856", "Site officiel", "{}"),
]

# Ce qui est reutilisable sans condition autre que le credit. La liste est
# FERMEE : une licence inconnue n'est pas presumee libre.
LICENCES_LIBRES = re.compile(
    r"^(cc0|cc-by-\d|cc-by-sa-\d|pd-|public.?domain|attribution$)", re.I)

LARGEUR_PORTRAIT = 480


# Wikimedia repond 429 des qu'on enchaine sans respirer. La premiere version
# s'est arretee au treizieme aventurier sur 531. On tient donc un rythme --
# PAUSE entre deux requetes -- et on obeit a l'en-tete `Retry-After` quand le
# service le pose, plutot que de deviner un delai.
PAUSE = 0.4
_derniere = [0.0]


def api(url, essais=8):
    for essai in range(essais):
        attente = PAUSE - (time.monotonic() - _derniere[0])
        if attente > 0:
            time.sleep(attente)
        _derniere[0] = time.monotonic()
        try:
            requete = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(requete, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or essai == essais - 1:
                raise
            dit = e.headers.get("Retry-After") if e.headers else None
            repos = int(dit) if (dit or "").isdigit() else 5 * 2 ** essai
            time.sleep(min(repos, 120))
        except urllib.error.URLError:
            if essai == essais - 1:
                raise
            time.sleep(4 * (essai + 1))


def en_cache(nom, fabrique):
    os.makedirs(CACHE, exist_ok=True)
    chemin = os.path.join(CACHE, nom + ".json")
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    valeur = fabrique()
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(valeur, f, ensure_ascii=False, indent=1, sort_keys=True)
    return valeur


def par_article(noms):
    """Resout des noms en elements Wikidata via leur article Wikipedia francais.

    POURQUOI PAS LA RECHERCHE PAR NOM. La premiere version interrogeait
    `wbsearchentities` une fois par aventurier : 531 requetes, que Wikimedia
    limite en debit -- cinquante personnes en onze minutes, et un 429 au bout.
    L'API accepte au contraire CINQUANTE titres d'un coup quand on lui donne un
    site et des titres : onze requetes au lieu de 531.

    Le gain n'est pas que de vitesse. Un titre d'article est un appariement
    EXACT, la ou une recherche floue rapporte des homonymes qu'il faut ensuite
    ecarter. Le prix a payer est connu et assume : un aventurier dont l'article
    porte un titre desambiguise -- « Machin (aventurier) » -- n'est pas trouve.
    Mieux vaut le manquer que de publier la photo de quelqu'un d'autre.
    """
    out = {}
    for debut in range(0, len(noms), 50):
        lot = noms[debut:debut + 50]
        url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
               "&props=claims|descriptions|labels|sitelinks&sites=frwiki&titles="
               + urllib.parse.quote("|".join(lot)))
        d = en_cache(f"lot_{debut // 50:03d}", lambda: api(url))
        for qid, e in (d.get("entities") or {}).items():
            if not qid.startswith("-"):
                titre = ((e.get("sitelinks") or {}).get("frwiki") or {}).get("title")
                if titre:
                    out[titre] = e
    return out


def valeurs(element, propriete):
    out = []
    for c in (element.get("claims") or {}).get(propriete, []):
        v = (c.get("mainsnak") or {}).get("datavalue", {}).get("value")
        if v is not None:
            out.append(v)
    return out


def parle_de_koh_lanta(element):
    """La preuve qu'on tient la bonne personne, et non un homonyme."""
    for d in (element.get("descriptions") or {}).values():
        if "koh-lanta" in (d.get("value") or "").lower():
            return True
    for declarations in (element.get("claims") or {}).values():
        for c in declarations:
            v = (c.get("mainsnak") or {}).get("datavalue", {}).get("value")
            if isinstance(v, dict) and v.get("id") in ELEMENTS_KOH_LANTA:
                return True
    return False


# L'emission et ses saisons, telles que Wikidata les nomme. Sert de preuve
# d'appariement : un element qui pointe vers l'un d'eux parle bien du jeu.
ELEMENTS_KOH_LANTA = set()


def charger_elements_koh_lanta():
    requete = ("SELECT ?s WHERE { { BIND(wd:Q1707097 AS ?s) } UNION "
               "{ ?s wdt:P179 wd:Q1707097 } }")
    url = ("https://query.wikidata.org/sparql?format=json&query="
           + urllib.parse.quote(requete))
    d = en_cache("_saisons_koh_lanta", lambda: api(url))
    for b in d["results"]["bindings"]:
        ELEMENTS_KOH_LANTA.add(b["s"]["value"].rsplit("/", 1)[-1])
    ELEMENTS_KOH_LANTA.add("Q1707097")


def extraits(titres):
    """Le texte des articles francais, pour PROUVER l'appariement.

    Le nom ne suffit pas, et la description Wikidata non plus. Sur les trente
    et un articles dont le titre est exactement celui d'un aventurier, il y a
    « Olga Khokhlova, danseuse ukrainienne » et « Alexandre Berard, avocat et
    homme politique » -- des homonymes -- a cote de Claude Dartois et de
    Teheiura Teahui. Aucune de ces deux categories ne se distingue par son
    nom.

    Ce qui les separe : l'article parle du jeu, ou il n'en parle pas. On lit
    donc le texte, et c'est lui qui tranche.
    """
    # UN SEUL TITRE PAR REQUETE, et ce n'est pas un oubli : demander vingt
    # articles entiers fait repondre a l'API « "exlimit" was too large for a
    # whole article extracts request, lowered to 1 ». Elle rend alors dix-neuf
    # extraits VIDES, sans erreur -- et vingt articles paraissent ne pas parler
    # de Koh-Lanta. La quantite de titres restant petite, on paie la requete.
    out = {}
    for titre in titres:
        url = ("https://fr.wikipedia.org/w/api.php?action=query&format=json"
               "&prop=extracts&explaintext=1&redirects=1&titles="
               + urllib.parse.quote(titre))
        cle = "texte_" + re.sub(r"[^A-Za-z0-9]+", "_", titre)[:70]
        d = en_cache(cle, lambda: api(url))
        for page in ((d.get("query") or {}).get("pages") or {}).values():
            if page.get("title"):
                out[page["title"]] = page.get("extract") or ""
    return out


# Le passe-partout que Commons pose quand le champ auteur n'est pas structure :
# « No machine-readable author provided. Untel assumed (based on copyright
# claims). » Affiche tel quel sous une photo, il donne une legende en anglais
# qui noie le seul mot utile -- le nom. On garde le nom.
RE_AUTEUR_PASSE_PARTOUT = re.compile(
    r"^No machine-readable author provided\.\s*(.*?)\s*"
    r"assumed \(based on copyright claims\)\.?$", re.I | re.S)


def sans_balises(texte):
    plat = html.unescape(re.sub(r"<[^>]+>", " ", texte or ""))
    plat = re.sub(r"\s+", " ", plat).strip()
    trouve = RE_AUTEUR_PASSE_PARTOUT.match(plat)
    return trouve.group(1).strip() if trouve else plat


def image_commons(fichier):
    """Licence, auteur et vignette d'un fichier Commons. None si non libre."""
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
           "&prop=imageinfo&iiprop=extmetadata|url&iiurlwidth="
           f"{LARGEUR_PORTRAIT}&titles=" + urllib.parse.quote("File:" + fichier))
    d = en_cache("img_" + re.sub(r"[^A-Za-z0-9]+", "_", fichier)[:80],
                 lambda: api(url))
    for page in (d.get("query") or {}).get("pages", {}).values():
        for info in page.get("imageinfo") or []:
            meta = info.get("extmetadata") or {}
            licence = (meta.get("License") or {}).get("value", "")
            if not LICENCES_LIBRES.match(licence or ""):
                return None
            if (meta.get("Restrictions") or {}).get("value"):
                return None
            return {
                "fichier": fichier,
                "vignette": info.get("thumburl") or info.get("url"),
                "licence": (meta.get("LicenseShortName") or {}).get("value") or licence,
                "licence_url": (meta.get("LicenseUrl") or {}).get("value"),
                "auteur": sans_balises((meta.get("Artist") or {}).get("value"))
                          or sans_balises((meta.get("Credit") or {}).get("value")),
                "page": info.get("descriptionurl"),
            }
    return None


def telecharger(url, chemin):
    if os.path.exists(chemin):
        return False
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    requete = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(requete, timeout=90) as r:
        octets = r.read()
    with open(chemin, "wb") as f:
        f.write(octets)
    return True


def main():
    charger_elements_koh_lanta()
    with open(os.path.join(DATA, "personnes.yml"), encoding="utf-8") as f:
        personnes = yaml.safe_load(f)

    trouves = par_article([p["nom"] for p in personnes])
    print(f"{len(trouves)} articles francais correspondent a un nom d'aventurier")
    textes = extraits(sorted(trouves))
    parle = {t for t, x in textes.items() if "koh-lanta" in (x or "").lower()}
    print(f"{len(parle)} de ces articles parlent effectivement de Koh-Lanta")

    reseaux, portraits = {}, {}
    vus = telecharges = ecartes = 0
    for p in personnes:
        element = trouves.get(p["nom"])
        if element is None:
            continue
        humain = any(isinstance(v, dict) and v.get("id") == "Q5"
                     for v in valeurs(element, "P31"))
        # Deux preuves acceptees, et il en faut une : le jeu est ecrit dans
        # l'element Wikidata, ou il est ecrit dans l'article. Sans preuve, on
        # ne retient rien -- une fiche sans photo vaut mieux qu'une fiche qui
        # montre quelqu'un d'autre.
        if not humain or not (parle_de_koh_lanta(element) or p["nom"] in parle):
            ecartes += 1
            continue
        vus += 1

        comptes = []
        for propriete, nom, motif in RESEAUX:
            for v in valeurs(element, propriete)[:1]:
                if isinstance(v, str) and v:
                    comptes.append({"reseau": nom, "compte": v,
                                    "url": motif.format(v)})
        if comptes:
            reseaux[p["id"]] = comptes

        for fichier in valeurs(element, "P18")[:1]:
            if not isinstance(fichier, str):
                continue
            info = image_commons(fichier)
            if not info or not info.get("vignette"):
                continue
            extension = os.path.splitext(info["vignette"])[1].lower() or ".jpg"
            if extension not in (".jpg", ".jpeg", ".png", ".webp"):
                extension = ".jpg"
            relatif = f"/assets/portraits/{p['id']}{extension}"
            if telecharger(info["vignette"],
                           os.path.join(PORTRAITS, p["id"] + extension)):
                telecharges += 1
            portraits[p["id"]] = {
                "fichier": relatif, "licence": info["licence"],
                "licence_url": info["licence_url"], "auteur": info["auteur"],
                "source": info["page"], "wikidata": element.get("id"),
            }

    entete = ("# ATTENTION : fichier genere par tools/extraction/wikidata.py.\n"
              "# Ne pas editer a la main : toute modification sera ecrasee.\n#\n")
    with open(os.path.join(DATA, "reseaux.yml"), "w", encoding="utf-8") as f:
        f.write(entete + "# Les comptes publics rattaches a une personne sur"
                         " Wikidata, avec sa reference.\n")
        yaml.safe_dump({"comptes": reseaux}, f, allow_unicode=True,
                       sort_keys=True, default_flow_style=False)
    with open(os.path.join(DATA, "portraits.yml"), "w", encoding="utf-8") as f:
        f.write(entete + "# Les portraits sous licence libre, AVEC leur auteur"
                         " et leur licence.\n"
                         "# Le gabarit les affiche sous la photo : ce n'est pas"
                         " optionnel.\n")
        yaml.safe_dump({"portraits": portraits}, f, allow_unicode=True,
                       sort_keys=True, default_flow_style=False)

    print(f"{len(personnes)} aventuriers, {vus} apparies sur Wikidata "
          f"({ecartes} ecartes : pas un humain, ou aucun lien ecrit vers Koh-Lanta)")
    print(f"  comptes  : {len(reseaux)} fiches, "
          f"{sum(len(v) for v in reseaux.values())} liens")
    print(f"  portraits: {len(portraits)} sous licence libre "
          f"({telecharges} telecharges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
