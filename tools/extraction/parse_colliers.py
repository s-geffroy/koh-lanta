#!/usr/bin/env python3
"""Extrait le sort des colliers d'immunite depuis les tableaux des sources.

Le collier est la seule mecanique du jeu dont on connaisse le destin complet :
ou il a ete trouve, par qui, s'il a servi, sur qui, et combien de voix il a
annulees. C'est aussi celle sur laquelle circulent le plus d'affirmations
invraisemblables.

Les tableaux changent de colonnes d'une saison a l'autre -- certains ajoutent
la localisation, d'autres l'aventurier protege, d'autres le jour separement de
l'episode. Les colonnes sont donc identifiees par leur INTITULE, jamais par
leur rang.

Une ligne « Non decouvert » est conservee telle quelle : un collier cache que
personne n'a trouve est une information, pas une absence de donnee.
"""
import re
import sys

from parse_fandom import plain, extract_table, indices_de_tribu
from parse_votes import developper, texte

# intitule de colonne -> role. Teste dans l'ordre : le premier qui colle gagne.
ROLES = [
    (r"propri[ée]taire d'origine|d[ée]tenteur|d[ée]couvert par|trouv[ée] par",
     "proprietaire"),
    # « Autre(s) propriétaire(s) » : l'intitule de Wikipedia porte la marque
    # du pluriel entre parentheses. Sans elle dans le motif, la colonne n'etait
    # jamais reconnue, et les 74 colliers perdaient TOUTES leurs transmissions
    # (Victor -> Beatrice -> Steeve a Fidji, Julie -> ... -> Jeremy a Johor).
    (r"autres?(?:\(s\))?\s*propri[ée]taires?", "autres"),
    (r"aventuriers?\s*prot[ée]g[ée]|prot[ée]g[ée]\(s\)", "proteges"),
    (r"votes?\s*annul", "votes_annules"),
    (r"^statut$", "statut"),
    (r"^jour$", "jour"),
    (r"^[ée]pisode$", "episode"),
    (r"localisation|circonstance", "localisation"),
    (r"^objets?$", "objet"),
    (r"d[ée]tails?", "details"),
]

RE_JOUR = re.compile(r"jours?\s*(\d{1,2})", re.I)
RE_RANG = re.compile(r"(\d{1,2})\s*(?:er|re|e|ème|eme)\b", re.I)
RE_FRACTION = re.compile(r"(\d{1,2})\s*/\s*(\d{1,2})")
RE_AUCUN = re.compile(r"^(aucun|aucune|n/?a|non|[-—–.]*|)$", re.I)


def statut_de(t):
    n = plain(t).lower()
    if not n:
        return None
    if "non d" in n and "couvert" in n:
        return "non_decouvert"
    if re.search(r"non\s*(utilis|jou)", n):
        return "non_utilise"
    if re.search(r"utilis|jou[ée]|d[ée]clench", n):
        return "utilise"
    if "perdu" in n or "confisqu" in n:
        return "perdu"
    return None


def noms_dans(cellule):
    """Rend les personnes citees dans une cellule, sans les jours ni les notes."""
    brut = re.sub(r"<ref.*?(?:/>|</ref>)", "", cellule or "", flags=re.S)
    brut = re.sub(r"<small>.*?</small>", " ", brut, flags=re.S | re.I)
    brut = re.sub(r"\([^)]*\)", " ", brut)
    # {{Surligné|#couleur|Nom}} et {{blanc|Nom}} enveloppent le nom
    brut = re.sub(r"\{\{\s*(?:surlign[ée]|blanc|nc|n/a)\s*\|[^|}]*\|([^}]*)\}\}",
                  r" \1 ", brut, flags=re.I)
    brut = re.sub(r"\{\{\s*(?:blanc|nc|n/a)\s*\|([^}]*)\}\}", r" \1 ", brut, flags=re.I)
    out = []
    for bout in re.split(r"\bet\b|,|/|&|\n", plain(brut)):
        bout = bout.strip(" '\"«»…:;.-")
        if not bout or RE_AUCUN.match(bout) or len(bout) > 30 or len(bout) < 2:
            continue
        if re.search(r"jour|[ée]pisode|camp\b|collier|immunit|\d", bout, re.I):
            continue
        if re.search(r"d[ée]couvert|utilis|perdu|conserv|aucun|finalist|"
                     r"vainqueur|[ée]limin|maudit", bout, re.I):
            continue          # un statut ou un sort, pas une personne
        out.append(bout)
    return out


RE_RANG_MODELE = re.compile(r"\{\{\s*(\d{1,2})\s*(?:er|re|e|ere)\s*\}\}", re.I)


def _episode(valeurs):
    """Le rang d'episode est ecrit {{4e}} ou {{1er}} : le nettoyage general
    efface le modele et son contenu. On le lit donc sur la cellule brute."""
    brut_ep = valeurs.get("episode", "") or ""
    m = RE_RANG_MODELE.search(brut_ep) or RE_RANG.search(plain(brut_ep))
    return int(m.group(1)) if m else None


def _jour_utilisation(valeurs):
    """Le jour ou le collier a ete JOUE, colonne « Jour » de l'utilisation :
    {{37e}}. Ce n'est pas le jour ou il a ete trouve (« Victor (jour 11 - 12) »,
    dans la case du detenteur)."""
    brut = valeurs.get("jour", "") or ""
    m = RE_RANG_MODELE.search(brut) or re.fullmatch(r"\s*(\d{1,2})\s*", plain(brut))
    return int(m.group(1)) if m else None


def _roles(grille):
    """Rend (index de la derniere ligne d'en-tete, {colonne: role})."""
    trouve, fin = {}, None
    for i, rang in enumerate(grille[:5]):
        courant = {}
        for col, cell in enumerate(rang):
            t = plain(texte(cell)).strip().lower()
            if not t or len(t) > 40:
                continue
            for motif, role in ROLES:
                if re.search(motif, t, re.I):
                    courant[col] = role
                    break
        if courant:
            trouve.update(courant)
            fin = i
    if "proprietaire" not in trouve.values():
        return None, {}
    return fin, trouve


def parse_page(wikitexte, saison_id=None, couleurs_admises=None):
    table = None
    for titre in (r"Colliers? d'immunit[ée]", r"Bilan des objets d'immunit[ée]",
                  r"Objets d'immunit[ée]", r"Bilan des objets strat[ée]giques",
                  r"Bilan des colliers", r"Objets? strat[ée]giques?"):
        table = extract_table(wikitexte, titre=titre)
        if table is not None:
            break
    if table is None:
        return []
    grille, ecrites = developper(table, avec_origine=True)
    if not grille:
        return []
    i_entete, roles = _roles(grille)
    if not roles:
        return []
    col_proprio = next((c for c, r in roles.items() if r == "proprietaire"), None)

    colliers = []
    for i_rang, rang in enumerate(grille[i_entete + 1:], i_entete + 1):
        if not rang or all(not texte(c) for c in rang):
            continue
        valeurs = {}
        for col, role in roles.items():
            valeurs[role] = rang[col] if col < len(rang) else ""

        # UNE TRANSMISSION, PAS UN NOUVEAU COLLIER. Quand un collier passe de
        # main en main, la source etale la case du proprietaire d'origine sur
        # plusieurs lignes (`rowspan`) et ouvre une ligne par detenteur
        # suivant : « Julie » sur trois lignes, puis Raphaele, Clementine,
        # Jeremy -- et c'est la DERNIERE ligne qui dit si le collier a ete
        # joue. Une ligne dont la case du proprietaire n'est qu'une recopie
        # verticale prolonge donc le collier du dessus. Lue comme un collier
        # a part, elle en fabriquait un de plus, et faisait jouer le collier
        # par celui qui l'avait trouve et cede -- parfois deja sorti du jeu.
        ecrite = ecrites[i_rang] if i_rang < len(ecrites) else []
        suite = (colliers and col_proprio is not None and col_proprio < len(ecrite)
                 and not ecrite[col_proprio])
        if suite:
            prec = colliers[-1]
            for n in noms_dans(valeurs.get("autres", "")):
                if n not in prec["autres_proprietaires"]:
                    prec["autres_proprietaires"].append(n)
            for n in noms_dans(valeurs.get("proteges", "")):
                if n not in prec["proteges"]:
                    prec["proteges"].append(n)
            statut_ = statut_de(valeurs.get("statut", ""))
            if statut_:
                prec["statut"] = statut_
            ep_, jour_u = _episode(valeurs), _jour_utilisation(valeurs)
            if ep_:
                prec["episode_utilisation"] = ep_
            if jour_u:
                prec["jour_utilisation"] = jour_u
            m = RE_FRACTION.search(plain(valeurs.get("votes_annules", "") or ""))
            if m:
                prec["votes_annules"], prec["votes_exprimes"] = int(m.group(1)), int(m.group(2))
            continue

        proprietaires = noms_dans(valeurs.get("proprietaire", ""))
        statut = statut_de(valeurs.get("statut", ""))
        # « Non decouvert » est parfois ecrit dans la colonne du proprietaire
        if not proprietaires:
            brut = plain(valeurs.get("proprietaire", "")).lower()
            if "non d" in brut and "couvert" in brut:
                statut = "non_decouvert"
            else:
                continue

        jour = None
        for source in ("proprietaire", "jour"):
            m = RE_JOUR.search(valeurs.get(source, "") or "")
            if m:
                jour = int(m.group(1))
                break

        episode = _episode(valeurs)

        annules = total = None
        m = RE_FRACTION.search(plain(valeurs.get("votes_annules", "") or ""))
        if m:
            annules, total = int(m.group(1)), int(m.group(2))

        colliers.append({
            "saison": saison_id,
            "localisation": plain(valeurs.get("localisation", "")) or None,
            "proprietaires": proprietaires,
            "autres_proprietaires": noms_dans(valeurs.get("autres", "")),
            "proteges": noms_dans(valeurs.get("proteges", "")),
            "statut": statut,
            "jour_trouve": jour,
            "episode_utilisation": episode,
            "jour_utilisation": _jour_utilisation(valeurs),
            "votes_annules": annules,
            "votes_exprimes": total,
            # Les notes « De la tribu jaune » accrochees aux noms de la ligne :
            # c'est la source qui separe ses homonymes, et il faut la lire.
            "indices": {k: v for cel in valeurs.values()
                        for k, v in indices_de_tribu(cel, couleurs_admises).items()},
        })
    return colliers


if __name__ == "__main__":
    import json, os
    for chemin in sys.argv[1:]:
        sid = os.path.basename(chemin).split(".")[0]
        lot = parse_page(open(chemin, encoding="utf-8").read(), sid)
        print(f"=== {sid} : {len(lot)} colliers ===")
        for x in lot[:6]:
            print("   ", json.dumps(x, ensure_ascii=False))
