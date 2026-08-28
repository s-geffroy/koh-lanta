#!/usr/bin/env python3
"""Extrait le detail des conseils depuis la matrice des votes du wiki Fandom.

La table « Detail des votes » est transposee : un episode par COLONNE, un
votant par LIGNE. Elle est en outre truffee de `colspan` (un episode qui couvre
plusieurs conseils) et de `rowspan` (« Jury final » etale sur deux lignes). Une
lecture naive decale toutes les colonnes des la premiere fusion.

On la remet donc a plat : la table est developpee en une grille rectangulaire
ou chaque cellule fusionnee est recopiee dans toutes les cases qu'elle couvre.
Ensuite seulement on lit :

  ligne « Episode »          -> le numero d'episode de chaque colonne
  ligne « Elimine »          -> qui part a ce conseil
  ligne « Votes »            -> le decompte, sous la forme « 6/10 »
  lignes suivantes           -> le bulletin de chaque votant

Un nom barre (<s>Nom</s>) signale une voix annulee par un collier d'immunite :
l'information est conservee telle quelle, elle sert a mesurer l'effet reel des
colliers.
"""
import re
import sys

from parse_fandom import plain, extract_table, slug

RE_COLSPAN = re.compile(r'colspan\s*=\s*"?(\d+)"?', re.I)
RE_ROWSPAN = re.compile(r'rowspan\s*=\s*"?(\d+)"?', re.I)
RE_BARRE = re.compile(r"<s>(.*?)</s>", re.S | re.I)


def cellules_brutes(ligne):
    """Coupe une ligne de tableau en cellules, attributs conserves."""
    cells, buf, t, l = [], None, 0, 0
    for texte in ligne.split("\n"):
        s = texte.strip()
        debut = t == 0 and l == 0 and (s.startswith("|") or s.startswith("!"))
        if debut:
            if buf is not None:
                cells.append("\n".join(buf))
            reste = s[1:]
            morceaux = re.split(r"\|\||!!", reste)
            buf = [morceaux[0]]
            for m in morceaux[1:]:
                cells.append("\n".join(buf))
                buf = [m]
        elif buf is not None:
            buf.append(texte)
        t += texte.count("{{") - texte.count("}}")
        l += texte.count("[[") - texte.count("]]")
    if buf is not None:
        cells.append("\n".join(buf))
    return cells


def separer_attributs(cell):
    """Rend (attributs, contenu) pour une cellule."""
    m = re.match(r'^([^|\[{\n]*?)\|(?!\|)', cell)
    if m and "=" in m.group(1):
        return m.group(1), cell[m.end():]
    return "", cell


def developper(table):
    """Developpe la table en grille rectangulaire, fusions recopiees."""
    lignes = re.split(r"\n\|-+[^\n]*", table)
    # Le premier morceau contient la ligne d'ouverture `{| ...` ET, souvent, la
    # premiere ligne d'en-tete. Jeter le morceau entier ferait disparaitre cette
    # en-tete -- et avec elle le report de ses `rowspan`, ce qui decale toutes
    # les colonnes. On ne retire donc que la ligne d'ouverture elle-meme.
    if lignes:
        premier = [x for x in lignes[0].split("\n")
                   if not x.lstrip().startswith(("{|", "|+"))]
        lignes[0] = "\n".join(premier)
    lignes = [l for l in lignes if l.strip()]

    grille = []
    # cellules encore actives verticalement : colonne -> (contenu, lignes restantes)
    reports = {}

    for ligne in lignes:
        rang = []
        col = 0
        # d'abord replacer les cellules reportees depuis les lignes du dessus
        def poser_reports():
            nonlocal col
            while col in reports:
                contenu, restant = reports[col]
                rang.append(contenu)
                if restant <= 1:
                    del reports[col]
                else:
                    reports[col] = (contenu, restant - 1)
                col += 1

        poser_reports()
        for cell in cellules_brutes(ligne):
            attrs, contenu = separer_attributs(cell)
            largeur = int(RE_COLSPAN.search(attrs).group(1)) if RE_COLSPAN.search(attrs) else 1
            hauteur = int(RE_ROWSPAN.search(attrs).group(1)) if RE_ROWSPAN.search(attrs) else 1
            for _ in range(largeur):
                rang.append(contenu)
                if hauteur > 1:
                    reports[col] = (contenu, hauteur - 1)
                col += 1
                poser_reports()
        grille.append(rang)
    return grille


def texte(cell):
    return plain(re.sub(r"<ref.*?(?:/>|</ref>)", "", cell or "", flags=re.S)).strip()


# Une case de la matrice ne contient pas toujours un bulletin. On y trouve
# aussi l'etat du candidat a cet episode (« Éliminée - Jour 3 »), des mentions
# de jury, de penalite, d'exil, ou le nom d'une tribu. Ce ne sont pas des voix.
RE_PAS_UN_VOTE = re.compile(
    r"jour\s*\d|jury|p[ée]nalit|exil|tribu|[îi]le des|abandon|[ée]limin|"
    r"absent|banni|immunis|vainqueur|finaliste|gagnant|vote noir|pas de vote|"
    r"[ée]galit|retour|d[ée]faite|victoire|candidat|votes?\b|"
    r"[\u25ba\u25bc\u25b2]|=\"|\{\{|^[-/.\s]*$|^\d+$|^\d+\s*/\s*\d+$",
    re.I)


def est_un_vote(nom):
    if not nom or len(nom) > 24:
        return False
    return not RE_PAS_UN_VOTE.search(nom)


# Depuis 2020, les tables Fandom n'ecrivent plus le nom vise en clair : elles
# l'enveloppent dans une pastille de tribu, « {{Tribebox-bw|Ilog|Lili}} », dont
# le premier parametre est la tribu et le second le nom. Le nettoyage general
# du wikitexte retire les modeles : sans traitement, ces cellules sont vides et
# le conseil parait sans bulletins. Huit saisons recentes sont dans ce cas.
RE_PASTILLE = re.compile(r"\{\{\s*Tribebox-bw\s*\|([^|}]*)\|([^}]*)\}\}", re.I)


def cible(cell):
    """Rend (nom_vise, voix_annulee)."""
    brut = re.sub(r"<ref.*?(?:/>|</ref>)", "", cell or "", flags=re.S)
    barre = bool(RE_BARRE.search(brut))
    # Le second parametre de la pastille est le nom ; on le sort du modele
    # avant le nettoyage, qui sinon effacerait tout.
    brut = RE_PASTILLE.sub(lambda m: " " + m.group(2).strip() + " ", brut)
    return (plain(brut).strip() or None), barre


# Les intitules de lignes portent une fleche, tantot devant (« ► Votes »),
# tantot derriere (« Votes ► »), selon l'epoque de la saison.
RE_FLECHE = re.compile(r"[\u25ba\u25b6\u25bc\u25b2\s]+")


def etiquette(cell):
    """L'intitule d'une ligne, debarrasse de ses fleches et de son tuyau.

    Certaines tables ecrivent « |►Votes » : le tuyau appartient a la syntaxe du
    tableau et n'a pas ete separe des attributs. Le laisser fait echouer la
    reconnaissance de la ligne -- et, silencieusement, la ligne des votants est
    alors cherchee ailleurs, tout en bas de la table.
    """
    return RE_FLECHE.sub(" ", texte(cell)).strip(" |").strip()


def trouver_ligne(grille, motif, depuis=0, jusqu_a=None):
    """La premiere ligne dont l'intitule correspond, dans une fenetre donnee.

    La fenetre n'est pas un detail : les lignes d'en-tete sont toutes dans les
    cinq premieres, et une ligne de bas de table (« Votes noirs ») porte le
    meme mot. Sans borne, on prend la mauvaise et on perd tous les votants.
    """
    for i, rang in enumerate(grille[depuis:jusqu_a], depuis):
        if rang and re.match(motif, etiquette(rang[0]), re.I):
            return rang
    return None


def parse_page(wikitexte, saison_id=None):
    table = extract_table(wikitexte, titre=r"D[ée]tails? des votes")
    if table is None:
        return []
    grille = developper(table)
    if not grille:
        return []

    # Les trois lignes d'en-tete sont contigues et en haut de table. On borne
    # la recherche : « Votes » se retrouve aussi en pied de table.
    l_episode = trouver_ligne(grille, r"[ÉEée]pisode", jusqu_a=8)
    l_elimine = trouver_ligne(grille, r"[ÉEée]limin", jusqu_a=8)
    if l_episode is None or l_elimine is None:
        return []
    apres = grille.index(l_elimine) + 1
    l_votes = trouver_ligne(grille, r"Votes?\b", depuis=apres, jusqu_a=apres + 3)

    largeur = max(len(l) for l in grille)

    # La colonne d'etiquette occupe une ou plusieurs colonnes selon les
    # saisons : depuis 2020 elle est fusionnee sur trois (colspan="3"). Sa
    # largeur se lit en comptant combien de colonnes repetent son contenu.
    debut_donnees = 1
    if l_episode:
        while (debut_donnees < len(l_episode)
               and l_episode[debut_donnees] == l_episode[0]):
            debut_donnees += 1

    # les lignes de votants : celles qui suivent la ligne des votes
    depart = grille.index(l_votes) + 1 if l_votes is not None else grille.index(l_elimine) + 1
    votants = []
    for rang in grille[depart:]:
        # Le nom du votant est dans la DERNIERE colonne d'etiquette, pas la
        # premiere : quand l'intitule est fusionne sur deux ou trois colonnes,
        # les lignes de votants y logent d'abord leurs pastilles de tribu.
        nom = ""
        for c in range(min(debut_donnees, len(rang)) - 1, -1, -1):
            candidat = re.sub(r'\b\w+\s*=\s*"[^"]*"', "", texte(rang[c])).strip()
            if candidat:
                nom = candidat
                break
        # ecarter les lignes d'en-tete (« ▼ Candidats », « Jury final », les
        # totaux) : ce ne sont pas des votants.
        if not nom or len(nom) > 30:
            continue
        if re.match(r"^[►▼▲]", nom) or not est_un_vote(nom):
            continue
        votants.append((nom, rang))

    conseils = []
    for col in range(debut_donnees, largeur):
        elimine = texte(l_elimine[col]) if col < len(l_elimine) else ""
        if not elimine:
            continue
        episode = texte(l_episode[col]) if col < len(l_episode) else ""
        decompte = texte(l_votes[col]) if l_votes is not None and col < len(l_votes) else ""

        contre = exprimes = None
        m = re.match(r"^(\d+)\s*/\s*(\d+)$", decompte)
        if m:
            contre, exprimes = int(m.group(1)), int(m.group(2))
        elif re.fullmatch(r"\d+", decompte):
            contre = int(decompte)

        bulletins = []
        for nom, rang in votants:
            if col >= len(rang):
                continue
            vise, annule = cible(rang[col])
            if not est_un_vote(vise) or vise == nom:
                continue
            bulletins.append({"votant": nom, "cible": vise, "annule": annule})

        # Un conseil est dit complet quand le nombre de bulletins effectivement
        # lus egale le nombre de voix annonce par la source. Les statistiques
        # au bulletin ne doivent porter que sur ceux-la ; les autres restent
        # utilisables pour leurs agregats (qui part, avec combien de voix).
        complet = (exprimes is not None and len(bulletins) == exprimes)

        conseils.append({
            "saison": saison_id,
            "complet": complet,
            "colonne": col,
            "episode": episode or None,
            "elimine": elimine,
            "votes_contre": contre,
            "votes_exprimes": exprimes,
            "votes": bulletins,
        })

    # Un episode qui couvre plusieurs colonnes (colspan) a ete recopie a
    # l'identique : deux colonnes VOISINES qui portent le meme episode et le
    # meme elimine decrivent un seul et meme conseil.
    uniques = []
    for c in conseils:
        precedent = uniques[-1] if uniques else None
        if (precedent
                and precedent["episode"] == c["episode"]
                and precedent["elimine"] == c["elimine"]
                and c["colonne"] == precedent["colonne"] + 1):
            precedent["colonne"] = c["colonne"]
            if len(c["votes"]) > len(precedent["votes"]):
                precedent["votes"] = c["votes"]
            continue
        uniques.append(c)
    for c in uniques:
        c.pop("colonne")
    for i, c in enumerate(uniques, 1):
        c["numero"] = i
    return uniques


if __name__ == "__main__":
    import json, os
    for path in sys.argv[1:]:
        sid = os.path.basename(path).split(".")[0]
        cs = parse_page(open(path, encoding="utf-8").read(), sid)
        print(f"=== {sid} : {len(cs)} conseils, "
              f"{sum(len(c['votes']) for c in cs)} bulletins ===")
        for c in cs[:3]:
            print(json.dumps(c, ensure_ascii=False)[:220])
