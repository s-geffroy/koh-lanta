#!/usr/bin/env python3
"""Controle les pages du site sans construire le site.

`CLAUDE.md` interdit d'installer Ruby et Jekyll sur cet hote : le rendu ne peut
donc pas etre essaye ici. Ce script verifie a la place ce qui casse SANS BRUIT
chez Jekyll -- une page qui disparait, une figure qui ne s'affiche pas, un
chiffre qui sort vide -- et qu'on ne verrait qu'en ligne, une fois publie :

  * front matter present et complet (layout, title, permalink) ;
  * chaque {% include %} pointe sur un fichier qui existe ;
  * chaque chemin site.data.x.y.z existe vraiment dans _data/ ;
  * pas de _site/ commite, liste `exclude:` intacte.

    tools/atelier python3 tools/verifie_site.py
"""
import os
import re
import subprocess
import sys

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

RE_FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
RE_INCLUDE = re.compile(r"\{%\s*include\s+([^\s%]+)")
RE_DATA = re.compile(r"site\.data\.([A-Za-z0-9_.]+)")
RE_ASSIGN = re.compile(r"\{%\s*assign\s+(\w+)\s*=\s*site\.data\.([A-Za-z0-9_.]+)\s*%\}")
RE_VAR = re.compile(r"\{\{\s*([a-z_][A-Za-z0-9_]*)\.([A-Za-z0-9_.]+)")

EXCLUS_ATTENDUS = {"CLAUDE.md", "README.md", "app.yaml", "compose.yaml", "specs/"}


class Controle:
    def __init__(self):
        self.erreurs, self.avertissements = [], []

    def erreur(self, m):
        self.erreurs.append(m)

    def avertir(self, m):
        self.avertissements.append(m)


def pages():
    for base, dossiers, fichiers in os.walk(RACINE):
        dossiers[:] = [d for d in dossiers
                       if d not in {".git", "_site", "_data", "_includes", "specs",
                                    "tools", "atelier", "node_modules", ".jekyll-cache"}]
        for f in fichiers:
            if f.endswith((".md", ".html")) and f not in ("CLAUDE.md", "README.md"):
                yield os.path.join(base, f)


def charger_donnees():
    donnees = {}
    dossier = os.path.join(RACINE, "_data")
    for f in os.listdir(dossier):
        if f.endswith((".yml", ".yaml")):
            with open(os.path.join(dossier, f), encoding="utf-8") as fh:
                donnees[os.path.splitext(f)[0]] = yaml.safe_load(fh)
    return donnees


def resoudre(racine, chemin):
    """Suit un chemin pointe dans les donnees. Rend (trouve, valeur)."""
    courant = racine
    for morceau in chemin.split("."):
        if isinstance(courant, list):
            if not courant:
                return True, None          # liste vide : chemin plausible
            courant = courant[0]
        if isinstance(courant, dict):
            if morceau not in courant:
                return False, None
            courant = courant[morceau]
        elif morceau.isdigit():
            return True, None
        else:
            return False, None
    return True, courant


def main():
    c = Controle()
    donnees = charger_donnees()

    permaliens = {}
    for chemin in sorted(pages()):
        rel = os.path.relpath(chemin, RACINE)
        texte = open(chemin, encoding="utf-8").read()

        m = RE_FRONT.match(texte)
        if not m:
            c.erreur(f"{rel} : pas de front matter — Jekyll ne rendra pas cette page")
            continue
        try:
            entete = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            c.erreur(f"{rel} : front matter illisible — {e}")
            continue

        if not entete.get("layout"):
            c.erreur(f"{rel} : `layout` manquant")
        if not entete.get("title"):
            c.avertir(f"{rel} : `title` manquant")
        lien = entete.get("permalink")
        if lien:
            if not lien.startswith("/") or not lien.endswith("/"):
                c.avertir(f"{rel} : permalink « {lien} » sans barre oblique initiale ou finale")
            if lien in permaliens:
                c.erreur(f"{rel} : permalink « {lien} » deja pris par {permaliens[lien]}")
            permaliens[lien] = rel
        elif rel not in ("index.md", "404.html"):
            c.avertir(f"{rel} : pas de permalink explicite, l'URL suivra le chemin du fichier")

        corps = texte[m.end():]

        for inc in RE_INCLUDE.findall(corps):
            if not os.path.exists(os.path.join(RACINE, "_includes", inc)):
                c.erreur(f"{rel} : inclusion introuvable — _includes/{inc}")

        # chemins ecrits en toutes lettres
        for parcours in RE_DATA.findall(corps):
            ok, _ = resoudre(donnees, parcours)
            if not ok:
                c.erreur(f"{rel} : site.data.{parcours} n'existe pas dans _data/")

        # chemins passant par un {% assign %}
        alias = {nom: cible for nom, cible in RE_ASSIGN.findall(corps)}
        for nom, suite in RE_VAR.findall(corps):
            if nom not in alias:
                continue
            parcours = f"{alias[nom]}.{suite.rstrip('.')}"
            parcours = re.sub(r"\.(first|last|size)$", "", parcours)
            ok, _ = resoudre(donnees, parcours)
            if not ok:
                c.erreur(f"{rel} : {nom}.{suite} → site.data.{parcours} n'existe pas")

    # configuration
    config = yaml.safe_load(open(os.path.join(RACINE, "_config.yml"), encoding="utf-8"))
    exclus = set(config.get("exclude") or [])
    for attendu in EXCLUS_ATTENDUS:
        if attendu not in exclus:
            c.erreur(f"_config.yml : « {attendu} » a disparu de `exclude:` — "
                     f"ce fichier serait publie en ligne")
    if config.get("url", "").find("CHANGEME") != -1:
        c.avertir("_config.yml : `url` vaut encore CHANGEME — a renseigner avant publication")

    # --- secrets : trois verrous, verifies a chaque passage
    dossier_secrets = os.path.join(RACINE, ".secrets")
    if os.path.isdir(dossier_secrets):
        if ".secrets/" not in exclus:
            c.erreur("_config.yml : .secrets/ absent de `exclude:` — "
                     "le jeton serait publie sur le site")
        gitignore = os.path.join(RACINE, ".gitignore")
        contenu = open(gitignore, encoding="utf-8").read() if os.path.exists(gitignore) else ""
        if ".secrets/" not in contenu:
            c.erreur(".gitignore : .secrets/ absent — le jeton entrerait dans "
                     "l'historique Git, qui est definitif")
        try:
            suivis = subprocess.run(["git", "ls-files", ".secrets"], cwd=RACINE,
                                    capture_output=True, text=True).stdout.strip()
        except FileNotFoundError:
            suivis = ""
            c.avertir("git absent : impossible de verifier qu'aucun secret "
                      "n'est suivi par l'index")
        if suivis:
            c.erreur("des fichiers de .secrets/ sont SUIVIS PAR GIT : "
                     + suivis.replace("\n", ", ")
                     + " — a retirer de l'index et a considerer comme compromis")
        for nom in os.listdir(dossier_secrets):
            chemin = os.path.join(dossier_secrets, nom)
            if os.path.isfile(chemin) and os.stat(chemin).st_mode & 0o077:
                c.erreur(f".secrets/{nom} est lisible par d'autres — "
                         f"chmod 600 .secrets/{nom}")

    if os.path.isdir(os.path.join(RACINE, "_site")):
        c.avertir("_site/ existe : verifier qu'il est bien ignore par Git")

    figures = os.path.join(RACINE, "_includes", "graphiques")
    nb = len(os.listdir(figures)) if os.path.isdir(figures) else 0
    print(f"pages controlees : {len(permaliens) + 1}")
    print(f"figures          : {nb}")
    print(f"jeux de donnees  : {', '.join(sorted(donnees))}")

    if c.avertissements:
        print(f"\n{len(c.avertissements)} avertissement(s) :")
        for a in c.avertissements:
            print(f"  ~ {a}")
    if c.erreurs:
        print(f"\n{len(c.erreurs)} ERREUR(S) :")
        for e in c.erreurs:
            print(f"  ! {e}")
        return 1
    print("\nOK  rien qui casserait le rendu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
