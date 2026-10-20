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
from collections import Counter

from parse_fandom import (plain, slug, extract_table, extract_tables,
                          indices_de_tribu, COULEURS_HEX, RE_SURLIGNE)
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

# Teintes employees par les tableaux pour designer une tribu. La table est
# tenue dans parse_fandom : elle sert aussi a separer les homonymes.
COULEURS = COULEURS_HEX


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
    # « {{Surligné|#5dce5d|Maxime}} » : le nom surligne a la couleur de sa
    # tribu. Le nettoyage general efface le modele ENTIER, nom compris -- le
    # confort de Maxime et Naïs (Revanche des 4 Terres, episode 5) devenait
    # « et ». La couleur reste lue a part par indices_de_tribu.
    brut = RE_SURLIGNE.sub(r" \2 ", brut)
    # Les attributs HTML restes colles a la cellule ne sont pas des noms.
    brut = re.sub(r"\b[\w-]+\s*=\s*\"?[^\"|\s]*\"?", " ", brut)
    brut = re.sub(r"\([^)]*\)", " ", brut)
    brut = re.sub(r"<br\s*/?>", "\n", brut, flags=re.I)
    # Couper AVANT le nettoyage : `plain` ecrase les retours a la ligne, et
    # deux vainqueurs separes par <br> se retrouveraient colles en un seul nom.
    morceaux = []
    for ligne in brut.split("\n"):
        # « Alban [Romuald] » : Alban gagne et emmene Romuald. Le nom entre
        # crochets est l'INVITE de la recompense, pas un vainqueur -- Fandom,
        # la ou il couvre la meme saison, ne cite qu'Alban. Le lire comme un
        # second gagnant donnait neuf victoires de confort de trop.
        propre = re.sub(r"\[[^\]]*\]", " ", plain(ligne))
        for bout in re.split(r"\bet\b|,|/|&|\u2022|\[|\]", propre):
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


def _colonne_date(grille, i_entete):
    """La colonne de diffusion, quand aucune colonne ne numerote les episodes.

    Les tableaux « Challenges » de Wikipedia en anglais n'ont pas de colonne
    d'episode : ils ont une DATE DE DIFFUSION, et une ligne par elimination.
    Numeroter les lignes y fabrique donc autant d'« episodes » que de sorties
    -- vingt-et-un pour le Cambodge, qui en compte quatorze. La date, elle, est
    recopiee par le `rowspan` sur toutes les lignes d'un meme soir : compter
    les dates DISTINCTES rend le vrai numero d'episode, sans rien deviner.
    """
    for col, cell in enumerate(grille[i_entete]):
        if re.search(r"air\s*date|diffusion|^date$", texte(cell), re.I):
            return col
    return None


def numeros_d_episode(cellule):
    """Les numeros d'une cellule d'episode, ecrits en clair ou par un modele.

    Wikipedia ecrit « {{9e|épisode}} », « {{1er|épisode}} » : le nettoyage du
    texte efface le modele, et avec lui le numero. Sans ce repli, la saison
    etait numerotee en comptant les lignes -- et un episode tenant sur deux
    lignes (deux conseils le meme soir) decalait d'un cran toutes les
    epreuves qui suivaient.

    Fandom ecrit parfois deux soirs sur une ligne, « 7/8ème épisode » ou
    « 12ème et 13ème épisode » : on rend les deux, comme le ferait une case
    fusionnee sur deux lignes. Ce qui suit une parenthese est un commentaire
    (« 11ème épisode (finale) »), pas un numero.
    """
    clair = texte(cellule).split("(")[0]
    nums = [int(n) for n in re.findall(r"\d{1,2}", clair)]
    if not nums:
        brut = re.sub(r"<ref.*?(?:/>|</ref>)", "", cellule or "", flags=re.S)
        nums = [int(n) for n in
                re.findall(r"\{\{\s*(\d{1,2})\s*(?:er|re|e|ème|è)?\s*\|", brut)]
    return nums


def parse_tableau(table, saison_id, forme_source, couleurs_admises=None):
    grille, hauteurs = developper(table, avec_hauteur=True)
    if not grille:
        return []
    i_entete, roles = _entetes(grille)
    if not roles:
        return []
    col_episode = _colonne_episode(grille, i_entete)
    # Le format « classement » double les DEUX epreuves. Un confort seul sur
    # deux colonnes est autre chose : a Palawan, un gagnant par tribu.
    premiere_confort = None
    if sum(1 for r in roles.values() if r == "immunite") >= 2:
        premiere_confort = min((c for c, r in roles.items() if r == "confort"),
                               default=None)
    col_date = _colonne_date(grille, i_entete) if col_episode is None else None
    dates_vues = []

    epreuves = []
    numero_implicite = 0
    vus = set()
    # L'episode de chaque ligne, pour savoir lesquels une case fusionnee couvre.
    episode_de_ligne = {}
    for r in range(i_entete + 1, len(grille)):
        rang = grille[r]
        hauts = hauteurs[r]
        if not rang or all(not texte(c) for c in rang):
            continue
        # Les lignes de finale redefinissent les colonnes : « Confort » et
        # « Immunité » y cedent la place a « Épreuve d'orientation » et
        # « Épreuve des poteaux », et la cellule y liste les QUALIFIÉS, pas un
        # vainqueur. Continuer a lire sous les anciens roles fabriquerait de
        # fausses victoires -- et fausserait justement les ratios d'epreuves,
        # qui sont la raison d'etre de cette couche.
        # Les tableaux anglais nomment ces colonnes a leur facon -- « Treasure
        # Hunt », « Orienteering Challenge », « Poles Challenge », « perchs
        # challenge » -- et la regle francaise les laissait passer : le trio
        # de l'orientation devenait un confort, le gagnant des poteaux une
        # immunite (Kôh-Lanta Vanuatu, Cambodge, Nicoya).
        if any(re.search(r"[ée]preuve d'orientation|[ée]preuve des poteaux|"
                         r"conseil final|final challenge|final council|"
                         r"treasure hunt|orienteering|poles? challenge|"
                         r"perchs? challenge", texte(c), re.I)
               for c in rang):
            break
        if any(re.fullmatch(r"confort|immunit[eé]|reward|immunity", texte(c), re.I)
               for c in rang):
            continue          # en-tete repetee au milieu du tableau

        episode = None
        numeros = []
        if col_episode is not None and col_episode < len(rang):
            numeros = numeros_d_episode(rang[col_episode])
            episode = numeros[0] if numeros else None
        if episode is None and col_date is not None and col_date < len(rang):
            jour = texte(rang[col_date])
            if jour:
                if not dates_vues or dates_vues[-1] != jour:
                    dates_vues.append(jour)
                episode = len(dates_vues)
        if episode is None:
            numero_implicite += 1
            episode = numero_implicite
        episode_de_ligne[r] = numeros or [episode]
        numero_implicite = max(episode_de_ligne[r])

        for col, role in sorted(roles.items()):
            if col >= len(rang):
                continue
            if col < len(hauts) and hauts[col] == 0:
                continue          # copie d'une case fusionnee : deja lue plus haut
            # Avec trois tribus, Fandom ecrit deux colonnes par epreuve : la
            # premiere et la deuxieme. A l'immunite, la deuxieme est protegee
            # aussi -- l'elimine vient toujours de la tribu non protegee,
            # verifie sur les douze soirs (s17, s20, s21). Au
            # confort, seule la premiere « remporte » : le recit dit de la
            # deuxieme qu'elle « finit deuxième ». Regle arretee avec
            # l'utilisateur le 20 octobre 2026.
            if role == "confort" and premiere_confort is not None and col != premiere_confort:
                continue
            cellule = rang[col]
            noms = noms_dans(cellule)
            if not noms:
                continue
            signature = (episode, role, tuple(noms))
            if signature in vus:      # colspan : la meme epreuve recopiee
                continue
            vus.add(signature)
            entree = {
                "saison": saison_id,
                "episode": episode,
                "type": role,
                "libelles": noms,
                "indices": indices_de_tribu(cellule, couleurs_admises),
                "couleur": couleur_de(cellule),
                "source": forme_source,
                "_lignes": (r, r + max(hauts[col] if col < len(hauts) else 1, 1) - 1),
            }
            epreuves.append(entree)
    # Une case fusionnee sur deux episodes est UNE epreuve, pas deux : elle
    # comptait double. Les saisons recentes (s24 a s28, sp6, sp8) etalent ainsi
    # un cycle sur deux soirs, et leurs notes disent ou tombe chaque epreuve :
    # « Pour l'épreuve de confort et les ambassadeurs » sur le premier,
    # « Pour l'épreuve d'immunité et le conseil » sur le second. Le confort va
    # donc au premier episode couvert, l'immunite au dernier -- celui de son
    # conseil, que le tableau des votes numerote de meme.
    for e in epreuves:
        debut, fin = e.pop("_lignes")
        couverts = sorted({n for x in range(debut, fin + 1)
                           for n in episode_de_ligne.get(x, [])})
        if len(couverts) > 1:
            e["episode"] = couverts[-1] if e["type"] == "immunite" else couverts[0]
    return epreuves if not _est_un_classement(epreuves) else []


def _est_un_classement(epreuves):
    """Un tableau de classement n'a pas de vainqueur : il a un ordre d'arrivee.

    Les saisons a quatre equipes en publient un, juste avant le vrai bilan :
    « Confort » y chapeaute quatre colonnes, une par tribu, dans l'ordre ou
    elles ont fini. Lu comme un tableau de resultats, il fabrique quatre
    victoires par epreuve -- trente-deux fausses lignes pour la seule Revanche
    des 4 Terres, dont le bon tableau se trouve juste en dessous.

    Un `colspan` sur un en-tete legitime produit lui aussi plusieurs colonnes
    pour un role, mais les cellules dessous sont IDENTIQUES et la signature les
    a deja fondues. Ce qui distingue le classement, c'est donc le nombre de
    vainqueurs DIFFERENTS pour un meme role au meme episode.
    """
    groupes = Counter((e["episode"], e["type"]) for e in epreuves)
    if len(groupes) < 2:
        return False
    charges = sum(1 for n in groupes.values() if n >= 3)
    return charges >= len(groupes) / 2


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


def parse_page(wikitexte, saison_id=None, couleurs_admises=None):
    """Le bilan des epreuves d'une page, quel que soit le titre qui le porte.

    Chaque section peut contenir plusieurs tableaux : on les lit tous et on
    garde le plus fourni de ceux qui ont la bonne forme. `parse_tableau`
    ecarte de lui-meme les tableaux de classement, qui n'ont pas de vainqueur
    unique -- sans quoi le plus fourni serait justement le mauvais.
    """
    for motif, etiquette in TITRES:
        meilleur = []
        for table in extract_tables(wikitexte, titre=motif):
            lot = parse_tableau(table, saison_id, etiquette, couleurs_admises)
            if len(lot) > len(meilleur):
                meilleur = lot
        if meilleur:
            return meilleur
    return []


# --- Le guide d'episodes du wiki Survivor (specs/sources/survivor/) ---------
#
# Un troisieme temoin, tenu en anglais par d'autres mains. Son tableau ecrit
# chaque vainqueur dans un modele : « {{tribebox|naga}} » pour une tribu,
# « {{tribebox|naga|Jean-Luc}} » pour une personne. Il range aussi sous
# « Immunity » des choses qui n'en sont pas pour ce site (decision du
# 20 octobre 2026) : un duel gagne, un avantage, une immunite donnee apres un
# changement de tribu ou conservee d'un conseil annule. Ces cases portent
# toujours un appel de note, et c'est la note qu'on lit pour les ecarter.

RE_TRIBEBOX = re.compile(r"\{\{\s*[Tt]ribe(?:box|hl)\d?\s*\|\s*([^|}]*)(?:\|([^{}]*))?\}\}")
RE_APPEL_NOTE = re.compile(r"#endnote\s+([\w-]+)")
RE_NOTE = re.compile(r"\{\{\s*note\s*\|\s*([\w-]+)\s*\|[^}]*\}\}(.*?)(?=\{\{\s*note\s*\||\{\{refend|\n\||$)",
                     re.S)
RE_PAS_UNE_EPREUVE = re.compile(
    r"duel|advantage|given individual immunity|separate immunity|mini-challenge",
    re.I)
# « Christina kept her immunity she won on Day 18 » (Palau) n'est PAS ecarte :
# l'immunite a ete GAGNEE, la note dit seulement qu'elle a servi plus tard.


def _noms_survivor(cellule):
    """[(nom, couleur)] cites dans une case du guide. Une tribu seule rend son
    nom de modele (« naga », « toa26fr ») : il est retraduit par construire."""
    c = re.sub(r"<ref.*?(?:/>|</ref>)", "", cellule or "", flags=re.S)
    c = re.sub(r"\{\{\s*(?:sup|note|textsub|nowrap)\|[^{}]*\}\}", "", c)
    sortie = []
    trouve = False
    for m in RE_TRIBEBOX.finditer(c):
        trouve = True
        tribu, dedans = m.group(1).strip(), m.group(2)
        if dedans is None or not dedans.strip():
            if tribu.lower() not in ("none", "tie"):
                sortie.append(re.sub(r"\d*fr$|\d+$", "", tribu))
            continue
        sortie += _decouper_survivor(dedans)
    if not trouve:
        sortie += _decouper_survivor(c)
    return sortie


def _decouper_survivor(texte_brut):
    t = re.sub(r"\[[^\]]*\]", " ", texte_brut)       # invites de la recompense
    t = re.sub(r"\([^)]*\)", " ", t)                  # beneficiaires, votes
    t = re.sub(r"</?s>", "", t)                       # recompense cedee : gagnee quand meme
    t = re.sub(r"<br\s*/?>", ",", t, flags=re.I)
    t = plain(t)
    noms = []
    for b in re.split(r",|&|\band\b", t):
        b = b.strip(" '\".")
        if b and not re.fullmatch(r"none|neither|n/a|-+|—", b, re.I) and len(b) < 30:
            noms.append(b)
    return noms


def parse_survivor(wikitexte, saison_id=None):
    notes = {m.group(1): m.group(2) for m in RE_NOTE.finditer(wikitexte)}
    grille, hauteurs = developper(wikitexte, avec_hauteur=True)
    roles, i0 = {}, None
    for i, rang in enumerate(grille[:4]):
        for col, cell in enumerate(rang):
            v = texte(cell).lower()
            if v == "reward":
                roles[col] = "confort"
            elif v == "immunity":
                roles[col] = "immunite"
        if roles:
            i0 = i
            break
    if not roles:
        return []
    epreuves, vus = [], set()
    finale = None
    for r in range(i0 + 1, len(grille)):
        rang = grille[r]
        # La finale tient dans l'episode qui porte la ligne « Jury Vote » :
        # le trio rescape de l'epreuve eliminatoire, un nom par ligne, puis le
        # gagnant des poteaux. Rien de cet episode n'est une epreuve ordinaire.
        if any(re.search(r"jury vote", texte(c), re.I) for c in rang):
            m = re.search(r"\|\s*(\d{1,2})\s*\]\]", rang[0]) if rang else None
            finale = int(m.group(1)) if m else finale
            break
        # Seules les colonnes d'epreuve signalent la finale : la colonne
        # « Finish » ecrit « 1st Jury Member » des la reunification.
        if any(re.search(r"final|orienteering|poles|perch", texte(rang[c]), re.I)
               and not RE_TRIBEBOX.search(rang[c]) for c in roles if c < len(rang)):
            break
        m = re.search(r"\|\s*(\d{1,2})\s*\]\]", rang[0]) if rang else None
        if not m:
            continue
        episode = int(m.group(1))
        for col, role in sorted(roles.items()):
            if col >= len(rang) or hauteurs[r][col] == 0:
                continue
            cellule = rang[col]
            if any(RE_PAS_UNE_EPREUVE.search(notes.get(n, ""))
                   for n in RE_APPEL_NOTE.findall(cellule)):
                continue
            noms = _noms_survivor(cellule)
            signature = (episode, role, tuple(noms))
            if not noms or signature in vus:
                continue
            vus.add(signature)
            # Un duo gagnant s'ecrit parfois sur deux lignes, un nom chacune
            # (Malaisie et Palau, premier soir : « Winners: Camille Sold and
            # Namadia Thaï Thaï », une seule epreuve). Deux lignes qui se
            # suivent et ne citent chacune qu'une PERSONNE, pour la meme
            # epreuve du meme soir, sont fondues. Une tribu ne se fond pas.
            personne = "|" in RE_TRIBEBOX.search(cellule).group(0) and bool(
                (RE_TRIBEBOX.search(cellule).group(2) or "").strip()) \
                if RE_TRIBEBOX.search(cellule) else True
            # Meme fusion pour deux lignes qui portent la MEME note : une
            # egalite (Malaisie, episode 5 : « both tribes [...] split the
            # reward »), ecrite une tribu par ligne.
            appels = set(RE_APPEL_NOTE.findall(cellule))
            prec = next((x for x in reversed(epreuves)
                         if x["episode"] == episode and x["type"] == role), None)
            meme_note = bool(appels) and prec is not None and appels == prec.get("_notes")
            if (prec and prec.get("_ligne") == r - 1 and prec["episode"] == episode
                    and prec["type"] == role
                    and ((personne and prec.get("_personne")) or meme_note)):
                prec["libelles"] += [n for n in noms if n not in prec["libelles"]]
                prec["_ligne"] = r
                continue
            epreuves.append({"saison": saison_id, "episode": episode, "type": role,
                             "libelles": noms, "indices": {}, "couleur": None,
                             "source": "survivor", "_ligne": r, "_personne": personne,
                             "_notes": appels})
    for e in epreuves:
        e.pop("_ligne", None)
        e.pop("_personne", None)
        e.pop("_notes", None)
    return [e for e in epreuves if e["episode"] != finale]


if __name__ == "__main__":
    import json, os
    for chemin in sys.argv[1:]:
        sid = os.path.basename(chemin).split(".")[0]
        lot = parse_page(open(chemin, encoding="utf-8").read(), sid)
        print(f"=== {sid} : {len(lot)} epreuves ===")
        for x in lot[:6]:
            print("   ", json.dumps(x, ensure_ascii=False))
