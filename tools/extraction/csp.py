#!/usr/bin/env python3
"""Classe une profession dans un poste de la taxonomie de tools/csp.yml."""
import os
import re
import unicodedata

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_TAXO = None


def _sans_accent(s):
    # Les sources melangent apostrophe droite et courbe : sans normalisation,
    # « Cheffe d'entreprise » et « Cheffe d’entreprise » ne se ressemblent pas.
    s = (s or "").replace("\u2019", "'").replace("\u02bc", "'")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def taxonomie():
    global _TAXO
    if _TAXO is None:
        with open(os.path.join(RACINE, "tools", "csp.yml"), encoding="utf-8") as f:
            _TAXO = yaml.safe_load(f)["postes"]
    return _TAXO


def classer(profession):
    """Rend le code du poste. L'ordre du fichier fait foi : premier trouve, premier pris."""
    if not profession:
        return None
    texte = _sans_accent(profession)
    for poste in taxonomie():
        for mot in poste.get("mots") or []:
            if _sans_accent(mot) in texte:
                return poste["code"]
    return "autre"


def libelles():
    return {p["code"]: p["libelle"] for p in taxonomie()}


if __name__ == "__main__":
    import collections, sys
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    compte = collections.Counter(classer(p["profession"]) for p in parts if p["profession"])
    lib = libelles()
    total = sum(compte.values())
    for code, n in compte.most_common():
        print(f"  {lib.get(code, code):38s} {n:4d}  {100*n/total:5.1f} %")
    autres = [p["profession"] for p in parts if p["profession"] and classer(p["profession"]) == "autre"]
    print(f"\nnon classes ({len(autres)}) :", ", ".join(sorted(set(autres))[:25]))
