#!/usr/bin/env python3
"""Extrait les candidats d'une page de saison de Wikipedia en francais.

Wikipedia couvre moins de saisons que le wiki Fandom, mais sa table « Candidats »
est plus soigneuse et porte deux choses que Fandom n'a pas :

  * le sexe, en clair, via les modeles {{♀}} et {{♂}} ;
  * l'appartenance aux tribus bornee en jours, via {{Légende|#couleur|Tribu
    (jour A - B)}}, ce qui donne la trajectoire complete et le jour de sortie.

L'ordre des colonnes bouge d'une saison a l'autre : les cellules sont donc
identifiees par leur contenu, jamais par leur rang.
"""
import re
import sys
import unicodedata

from parse_fandom import (plain, sansaccent, classify, split_rows, split_cells,
                          extract_table)

# Le symbole est tantot dans un modele ({{♀}}), tantot ecrit nu dans la
# cellule. Les deux formes comptent.
RE_GENRE   = re.compile(r"\{\{\s*(♀|♂|Femme|Homme)\s*\}\}|(?<![\w])(♀|♂)(?![\w])", re.I)
RE_GRAS    = re.compile(r"'''(.+?)'''", re.S)
RE_AGE     = re.compile(r"\b(\d{1,2})\s*ans?\b")
RE_LEGENDE = re.compile(r"\{\{\s*Légende\s*\|\s*(#[0-9A-Fa-f]{3,6})\s*\|\s*([^}]*?)\}\}")
# Un palmares, pas un metier : « Vainqueur de la saison 5 », « Éliminé a
# l'orientation de la saison 11 », « Finaliste de L'Ile des heros ».
RE_PALMARES = re.compile(
    r"\b(vainqueur|vainqueure|gagnant|gagnante|finaliste|élimin|elimin|abandon)\b"
    r"[^.]{0,60}\b(saison|édition|edition|koh-lanta)\b", re.I)

RE_JOURS   = re.compile(r"\(?\s*jours?\s*(\d{1,2})\s*(?:[–\-—]\s*(\d{1,2}))?\s*\)?", re.I)

# Couleurs employees par les tableaux de Wikipedia pour les tribus.
COULEURS = {
    "#fee347": "jaune", "#fc5d5d": "rouge", "#5dadec": "bleu",
    "#5dce5d": "vert",  "#f39442": "orange", "#b25080": "violet",
    "#000000": "noir",  "#ffffff": "blanc",  "#ececec": None,
}

def parse_tribus(cell):
    """Rend [(tribu, couleur, jour_debut, jour_fin)] dans l'ordre du parcours."""
    out = []
    for m in RE_LEGENDE.finditer(cell):
        couleur = COULEURS.get(m.group(1).lower(), None)
        texte = plain(m.group(2))
        mj = RE_JOURS.search(texte)
        debut = fin = None
        if mj:
            debut = int(mj.group(1))
            fin = int(mj.group(2)) if mj.group(2) else debut
            texte = texte[:mj.start()].strip()
        nom = texte.strip(" ()–-—")
        if nom:
            out.append((nom, couleur, debut, fin))
    return out

def parse_row(row, saison_id=None):
    cells = split_cells(row)
    if not cells:
        return None
    corps = "\n".join(cells)
    if not RE_GENRE.search(corps) and not RE_LEGENDE.search(corps):
        return None

    genre = None
    mg = RE_GENRE.search(corps)
    if mg:
        symbole = (mg.group(1) or mg.group(2) or "").lower()
        genre = "f" if symbole in ("♀", "femme") else "h"

    nom = None
    for c in cells:
        m = RE_GRAS.search(c)
        if m:
            nom = plain(m.group(1))
            break

    age = None
    localisation = None
    tribus = []
    depart = None
    profession = None

    restantes = []
    for c in cells:
        t = plain(c)
        if RE_LEGENDE.search(c):
            tribus = parse_tribus(c)
            continue
        if "{{Drapeau" in c or "{{drapeau" in c:
            localisation = t or None
            continue
        if age is None and RE_AGE.search(t) and len(t) < 20:
            age = int(RE_AGE.search(t).group(1))
            continue
        if RE_GENRE.search(c):
            continue
        if nom and t == nom:
            continue
        if t:
            restantes.append(t)

    # le depart est la derniere cellule textuelle qui ressemble a un sort
    for t in reversed(restantes):
        if classify(t)[0]:
            depart = t
            restantes.remove(t)
            break
    # Sur les editions de retour, la colonne qui tient lieu de metier porte en
    # fait un palmares (« Vainqueur de la saison 5 »). Ce n'est pas une
    # profession : la ranger comme telle fausserait la taxonomie des metiers.
    for t in list(restantes):
        if RE_PALMARES.search(t):
            restantes.remove(t)
    if restantes:
        profession = restantes[0]

    sort, genre_deduit = classify(depart or "")
    if genre is None:
        genre = genre_deduit

    jour = None
    if tribus:
        derniers = [t[3] for t in tribus if t[3] is not None]
        if derniers:
            jour = max(derniers)

    if not nom:
        return None
    return {
        "nom": nom,
        "saison": saison_id,
        "age": age,
        "profession": profession,
        "localisation": localisation,
        "genre": genre,
        "tribu": tribus[0][0] if tribus else None,
        "couleur": tribus[0][1] if tribus else None,
        "parcours": [{"tribu": t[0], "couleur": t[1], "jour_debut": t[2], "jour_fin": t[3]}
                     for t in tribus],
        "jour_sortie": jour,
        "sort": sort,
        "motif": depart,
    }

def parse_page(text, saison_id=None):
    table = extract_table(text)
    if table is None:
        return []
    out = []
    for row in split_rows(table):
        p = parse_row(row, saison_id)
        if p:
            out.append(p)
    return out

if __name__ == "__main__":
    import json, os
    for path in sys.argv[1:]:
        sid = os.path.basename(path).split(".")[0]
        print(json.dumps(parse_page(open(path, encoding="utf-8").read(), sid),
                         ensure_ascii=False, indent=1))
