#!/usr/bin/env python3
"""Extrait les vainqueurs d'epreuves depuis les bilans par episode.

Les sources presentent la meme information sous trois formes selon l'epoque et
la langue :

  A. « Bilan par episode » (Wikipedia fr et Fandom) -- un tableau avec une
     colonne Confort et une colonne Immunite, plus le conseil ;
  B. « Season summary » (Wikipedia en) -- Reward / Immunity, plus l'elimine ;
  C. « Challenges » (Wikipedia en, saisons 10 et 11) -- reward / Immunity
     seuls, les episodes n'etant designes que par leur ordre.

Les trois passent par le meme developpement de grille que les matrices de
votes : les `colspan` et `rowspan` y sont recopies, sans quoi les colonnes se
decalent des la premiere fusion.

Une cellule d'epreuve contient soit un nom de TRIBU (epreuve collective), soit
un nom de PERSONNE (epreuve individuelle). Departager les deux n'est pas une
devinette : on compare aux tribus declarees de la saison et aux participations
deja constituees.
"""
import re
import sys

from parse_fandom import plain, slug, extract_table
from parse_votes import developper, texte

# Ce qui n'est pas un vainqueur : pas d'epreuve, epreuve annulee, cellule vide.
RE_AUCUN = re.compile(
    r"^(aucun|aucune|none|nobody|pas d'|non disput|annul|neant|"
    r"[-\u2013\u2014.]*|\d+)$", re.I)

# Une cellule nomme parfois l'EPREUVE (« Épreuve des poteaux ») ou porte un
# artefact de colonne anglaise plutot qu'un vainqueur. Ce ne sont pas des noms.
RE_PAS_UN_VAINQUEUR = re.compile(
    r"^([ée]preuve\b|challenge\b|treasure|final challenge|initial challenge|"
    r"eliminated|perchs|quiz|duel\b|jury\b|koh-lanta|runner-?up|orienteering|"
    r"poles?\b|conseil\b|no elimination|jour\s*\d|\d+\s*-\s*\d+$|"
    r"vainqueur|finaliste|winner)", re.I)

RE_COULEUR = re.compile(
    r'(?:bgcolor|background-color)\s*[:=]\s*"?\s*(#[0-9A-Fa-f]{3,6})', re.I)

# Teintes employees par les tableaux pour designer une tribu.
COULEURS = {
    "#fee347": "jaune", "#ffff00": "jaune", "#fc5d5d": "rouge", "#ff0000": "rouge",
    "#5dadec": "bleu", "#0000ff": "bleu", "#5dce5d": "vert", "#00ff00": "vert",
    "#f39442": "orange", "#ffa500": "orange", "#b25080": "violet", "#800080": "violet",
    "#000000": "noir", "#ffffff": None, "#ececec": None, "#dcdcdc": None,
}


def couleur_de(cellule):
    m = RE_COULEUR.search(cellule or "")
    return COULEURS.get(m.group(1).lower()) if m else None


def noms_dans(cellule):
    """Rend les noms cites dans une cellule d'epreuve.

    Une cellule peut en porter plusieurs : deux vainqueurs ex aequo, ou un
    prenom suivi de sa tribu entre parentheses -- laquelle est un contexte, pas
    un second vainqueur.
    """
    brut = re.sub(r"<ref.*?(?:/>|</ref>)", "", cellule or "", flags=re.S)
    brut = re.sub(r"\{\{efn[^}]*\}\}", "", brut, flags=re.I)
    # Wikipedia en enveloppe le vainqueur dans {{stribe|tribu}} pour une epreuve
    # collective, {{stribe|tribu|Nom}} pour une individuelle. Le nettoyage
    # general effacerait le modele et son contenu : on le deballe avant.
    brut = re.sub(r"\{\{\s*stribe\s*\|\s*([^|}]*)\s*\|\s*([^}]*)\}\}",
                  r" \2 ", brut, flags=re.I)
    brut = re.sub(r"\{\{\s*stribe\s*\|\s*([^|}]*)\}\}", r" \1 ", brut, flags=re.I)
    # Les attributs HTML restes colles a la cellule ne sont pas des noms.
    brut = re.sub(r"\b[\w-]+\s*=\s*\"?[^\"|\s]*\"?", " ", brut)
    brut = re.sub(r"\([^)]*\)", " ", brut)
    brut = re.sub(r"<br\s*/?>", "\n", brut, flags=re.I)
    # Couper AVANT le nettoyage : `plain` ecrase les retours a la ligne, et
    # deux vainqueurs separes par <br> se retrouveraient colles en un seul nom.
    morceaux = []
    for ligne in brut.split("\n"):
        for bout in re.split(r"\bet\b|,|/|&|\u2022|\[|\]", plain(ligne)):
            bout = bout.strip(" '\"«»…:;.-[]")
            if not bout or RE_AUCUN.match(bout) or len(bout) >= 40 or len(bout) < 2:
                continue
            if "{" in bout or "}" in bout or "=" in bout:
                continue          # residu de modele ou d'attribut, pas un nom
            if RE_PAS_UN_VAINQUEUR.match(bout):
                continue          # nom de l'epreuve, pas de son vainqueur
            # Le modele anglais suffixe le parametre de tribu par la langue :
            # « chaperafr » designe la tribu Chapera.
            bout = re.sub(r"(?<=[a-z])fr$", "", bout)
            # residus d'appels de note (« Teheiura note 1 »)
            bout = re.sub(r"\s+notes?\s*\d*$", "", bout, flags=re.I).strip()
            morceaux.append(bout)
    return morceaux


def _entetes(grille):
    """Rend (index_ligne, {colonne: role}) pour la ligne d'en-tete des epreuves.

    Le tableau a deux lignes d'en-tete : la premiere chapeaute les colonnes
    d'un « Épreuves » global, la seconde les distingue en « Confort » et
    « Immunité ». S'arreter a la premiere ferait perdre la distinction, qui est
    tout l'interet. On retient donc la ligne la PLUS precise.
    """
    candidates = []
    for i, rang in enumerate(grille[:6]):
        trouve = {}
        for col, cell in enumerate(rang):
            t = texte(cell).lower()
            if re.fullmatch(r"confort|reward", t):
                trouve[col] = "confort"
            elif re.fullmatch(r"immunit[eé]|immunity", t):
                trouve[col] = "immunite"
            elif re.fullmatch(r"[ée]preuves?(\s+initiale)?|challenges?", t):
                trouve[col] = "epreuve"
        if trouve:
            precision = len({r for r in trouve.values()} - {"epreuve"})
            candidates.append((precision, i, trouve))
    if not candidates:
        return None, {}
    # precision d'abord, puis la ligne la plus haute a precision egale
    precision, i, trouve = max(candidates, key=lambda c: (c[0], -c[1]))
    return i, trouve


def _colonne_episode(grille, i_entete):
    for col, cell in enumerate(grille[i_entete]):
        if re.search(r"[eé]pisode|^n[o°]\.?$", texte(cell), re.I):
            return col
    return None


def parse_tableau(table, saison_id, forme_source):
    grille = developper(table)
    if not grille:
        return []
    i_entete, roles = _entetes(grille)
    if not roles:
        return []
    col_episode = _colonne_episode(grille, i_entete)

    epreuves = []
    numero_implicite = 0
    vus = set()
    for rang in grille[i_entete + 1:]:
        if not rang or all(not texte(c) for c in rang):
            continue
        # Les lignes de finale redefinissent les colonnes : « Confort » et
        # « Immunité » y cedent la place a « Épreuve d'orientation » et
        # « Épreuve des poteaux », et la cellule y liste les QUALIFIÉS, pas un
        # vainqueur. Continuer a lire sous les anciens roles fabriquerait de
        # fausses victoires -- et fausserait justement les ratios d'epreuves,
        # qui sont la raison d'etre de cette couche.
        if any(re.search(r"[ée]preuve d'orientation|[ée]preuve des poteaux|"
                         r"conseil final|final challenge", texte(c), re.I)
               for c in rang):
            break
        if any(re.fullmatch(r"confort|immunit[eé]|reward|immunity", texte(c), re.I)
               for c in rang):
            continue          # en-tete repetee au milieu du tableau

        episode = None
        if col_episode is not None and col_episode < len(rang):
            m = re.search(r"(\d{1,2})", texte(rang[col_episode]))
            if m:
                episode = int(m.group(1))
        if episode is None:
            numero_implicite += 1
            episode = numero_implicite
        else:
            numero_implicite = episode

        for col, role in sorted(roles.items()):
            if col >= len(rang):
                continue
            cellule = rang[col]
            noms = noms_dans(cellule)
            if not noms:
                continue
            signature = (episode, role, tuple(noms))
            if signature in vus:      # colspan : la meme epreuve recopiee
                continue
            vus.add(signature)
            epreuves.append({
                "saison": saison_id,
                "episode": episode,
                "type": role,
                "libelles": noms,
                "couleur": couleur_de(cellule),
                "source": forme_source,
            })
    return epreuves


# Le meme tableau se range sous des titres differents selon les pages. L'ordre
# n'a pas d'importance : la table n'est retenue que si l'en-tete porte bien une
# colonne d'epreuve, sinon on passe au titre suivant.
TITRES = [
    (r"Bilan par [eé]pisode", "bilan par episode"),
    (r"D[eé]roulement", "deroulement"),
    (r"D[eé]tail des [eé]liminations", "detail des eliminations"),
    (r"Season summary", "season summary"),
    (r"Challenges?", "challenges"),
]


def parse_page(wikitexte, saison_id=None):
    for motif, etiquette in TITRES:
        table = extract_table(wikitexte, titre=motif)
        if table is None:
            continue
        lot = parse_tableau(table, saison_id, etiquette)
        if lot:
            return lot
    return []


if __name__ == "__main__":
    import json, os
    for chemin in sys.argv[1:]:
        sid = os.path.basename(chemin).split(".")[0]
        lot = parse_page(open(chemin, encoding="utf-8").read(), sid)
        print(f"=== {sid} : {len(lot)} epreuves ===")
        for x in lot[:6]:
            print("   ", json.dumps(x, ensure_ascii=False))
