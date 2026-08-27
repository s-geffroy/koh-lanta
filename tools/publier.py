#!/usr/bin/env python3
"""Active GitHub Pages, declenche la construction, et rend compte.

Pousser suffit a mettre a jour un site Pages -- mais encore faut-il que Pages
soit ACTIVE sur le depot, ce qui est un reglage a faire une fois, par l'API.
La cle SSH du depot est une cle de deploiement : elle autorise le push, jamais
l'API. Il faut donc un jeton.

Le jeton se lit dans /secrets/github.token (monte en lecture seule dans le
conteneur, hors du depot). Il n'est JAMAIS affiche, ni journalise, ni ecrit
ailleurs : un depot Pages est public et son historique definitif.

    tools/atelier python3 tools/publier.py            etat du site
    tools/atelier python3 tools/publier.py --activer  activer Pages si besoin
    tools/atelier python3 tools/publier.py --attendre  suivre la construction
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

DEPOT = "s-geffroy/koh-lanta"
API = "https://api.github.com"

# Le depot entier est monte sur /depot dans le conteneur : le jeton y est donc
# visible sans montage supplementaire. Les deux chemins designent le meme
# fichier, vu du conteneur ou de l'hote.
CHEMINS_JETON = [
    "/depot/.secrets/github.token",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 ".secrets", "github.token"),
]


class Probleme(Exception):
    pass


def lire_jeton():
    for chemin in CHEMINS_JETON:
        if not os.path.exists(chemin):
            continue
        mode = os.stat(chemin).st_mode & 0o077
        if mode:
            raise Probleme(
                f"{chemin} est lisible par d'autres (permissions trop larges).\n"
                f"  Corrige avec :  chmod 600 {chemin}")
        jeton = open(chemin, encoding="utf-8").read().strip()
        if not jeton:
            raise Probleme(f"{chemin} est vide.")
        if len(jeton) < 20 or " " in jeton:
            raise Probleme(f"{chemin} ne ressemble pas a un jeton "
                           f"(trop court, ou contenant une espace).")
        return jeton
    raise Probleme(
        "aucun jeton trouve.\n"
        "  Depose-le dans .secrets/github.token a la racine du projet\n"
        "  (une seule ligne, permissions 600). Marche a suivre : README.md.")


def masquer(texte, jeton):
    """Garde-fou : rien de ce qui sort ne doit contenir le jeton."""
    return texte.replace(jeton, "***") if jeton else texte


def appel(methode, chemin, jeton, corps=None):
    donnees = json.dumps(corps).encode() if corps is not None else None
    req = urllib.request.Request(
        API + chemin, data=donnees, method=methode,
        headers={
            "Authorization": f"Bearer {jeton}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "koh-lanta-publication/1.0",
            "Content-Type": "application/json",
        })
    def lire(reponse):
        brut = reponse.read().decode() or "{}"
        try:
            corps = json.loads(brut)
        except json.JSONDecodeError:
            corps = {"message": brut[:200]}
        # GitHub dit exactement quelle permission manque, dans un en-tete.
        # Le lire evite de faire deviner, et de tatonner sur les droits.
        exigees = reponse.headers.get("x-accepted-github-permissions")
        if exigees:
            corps["_permissions_exigees"] = exigees
        return corps

    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, lire(r)
    except urllib.error.HTTPError as e:
        return e.code, lire(e)


def etat(jeton):
    code, d = appel("GET", f"/repos/{DEPOT}/pages", jeton)
    return code, d


def diagnostic_permission(code, d):
    message = (d or {}).get("message", "")
    if code == 401:
        return ("le jeton est refuse (401). Il est peut-etre expire, mal copie, "
                "ou revoque.")
    if code == 403:
        exigees = (d or {}).get("_permissions_exigees")
        detail = ""
        if exigees:
            noms = {"pages": "Pages", "administration": "Administration",
                    "contents": "Contents", "metadata": "Metadata"}
            lisible = ", ".join(
                f"« {noms.get(x.split('=')[0], x.split('=')[0])} » en "
                + ("ecriture" if x.endswith("write") else "lecture")
                for x in exigees.split(","))
            detail = (f"\n  GitHub exige exactement : {lisible}"
                      f"\n  (en-tete brut : {exigees})")
        return ("le jeton n'a pas le droit demande (403)." + detail
                + "\n  Ces permissions se modifient sur un jeton existant, "
                  "sans le regenerer.")
    if code == 404 and "Not Found" in message:
        return ("depot introuvable AVEC ce jeton (404). Verifie que le jeton "
                "porte bien sur s-geffroy/koh-lanta.")
    return None


def activer(jeton):
    code, d = etat(jeton)
    if code == 200:
        print(f"Pages est deja actif — source : {d.get('source')}, "
              f"statut : {d.get('status')}")
        return d
    if code != 404:
        raise Probleme(diagnostic_permission(code, d)
                       or f"reponse inattendue ({code}) : {d}")

    print("Pages n'est pas actif sur le depot. Activation…")
    code, d = appel("POST", f"/repos/{DEPOT}/pages", jeton,
                    {"source": {"branch": "main", "path": "/"}})
    if code in (201, 204):
        print("  Pages active : branche main, dossier racine.")
        return d
    souci = diagnostic_permission(code, d)
    raise Probleme(souci or f"activation refusee ({code}) : "
                            f"{(d or {}).get('message', d)}")


def derniere_construction(jeton):
    code, d = appel("GET", f"/repos/{DEPOT}/pages/builds/latest", jeton)
    return (d if code == 200 else None)


def attendre(jeton, patience=300):
    """Suit la construction jusqu'a son terme. Ne boucle pas indefiniment."""
    debut = time.monotonic()
    dernier = None
    while time.monotonic() - debut < patience:
        b = derniere_construction(jeton)
        statut = (b or {}).get("status")
        if statut != dernier:
            print(f"  construction : {statut or 'aucune encore'}")
            dernier = statut
        if statut == "built":
            code, d = etat(jeton)
            print(f"  site : {d.get('html_url')}")
            return True
        if statut == "errored":
            erreur = (b or {}).get("error", {}).get("message")
            print(f"  ECHEC de la construction : {erreur}")
            return False
        time.sleep(10)
    print(f"  toujours pas construit apres {patience} s — "
          f"regarde l'onglet Actions du depot.")
    return False


def main():
    jeton = None
    try:
        jeton = lire_jeton()
        if "--activer" in sys.argv:
            activer(jeton)
        code, d = etat(jeton)
        if code == 200:
            print(f"depot   : {DEPOT}")
            print(f"url     : {d.get('html_url')}")
            print(f"source  : {d.get('source')}")
            print(f"statut  : {d.get('status')}")
            b = derniere_construction(jeton)
            if b:
                print(f"derniere construction : {b.get('status')} "
                      f"({b.get('created_at')})")
                if b.get("error", {}).get("message"):
                    print(f"  erreur : {b['error']['message']}")
        elif code == 404:
            print("Pages n'est pas actif sur ce depot. "
                  "Relance avec --activer pour l'activer.")
        else:
            raise Probleme(diagnostic_permission(code, d)
                           or f"reponse inattendue ({code}) : {d}")
        if "--attendre" in sys.argv:
            return 0 if attendre(jeton) else 1
        return 0
    except Probleme as e:
        print(f"ARRET : {masquer(str(e), jeton)}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ARRET : {masquer(type(e).__name__ + ': ' + str(e), jeton)}",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
