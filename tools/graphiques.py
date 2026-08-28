#!/usr/bin/env python3
"""Fabrique les graphiques du site, en SVG, dans _includes/graphiques/.

Pourquoi du SVG ecrit a la main plutot qu'une bibliotheque ? Parce que les
figures sont INLINEES dans les pages par Jekyll ({% include %}), et non
chargees comme images. Inlinees, elles heritent des variables CSS de la page :
les couleurs suivent le theme clair ou sombre du lecteur, ce qu'un PNG ou un
SVG exporte ne sait pas faire.

Chaque figure porte :
  * un <title> et un <desc> pour les lecteurs d'ecran ;
  * un <title> par marque, ce qui donne l'infobulle native du navigateur, sans
    une ligne de JavaScript ;
  * des etiquettes de valeur lisibles, pour que la couleur ne porte jamais
    l'information a elle seule.

Palette : celle du guide de visualisation, dans son ordre -- l'ordre des teintes
est le mecanisme de lisibilite pour les daltoniens, il ne se reamenage pas.

    tools/atelier python3 tools/graphiques.py
"""
import html
import os
import sys

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SORTIE = os.path.join(RACINE, "_includes", "graphiques")

# Roles CSS, definis dans assets/css/style.scss. On n'ecrit jamais un hexa ici.
SERIES = [f"var(--serie-{i})" for i in range(1, 9)]
ENCRE = "var(--encre)"
ENCRE_DOUCE = "var(--encre-douce)"
GRILLE = "var(--grille)"
SURFACE = "var(--surface)"

# Couleurs propres aux tribus : ici la teinte EST la donnee (une tribu jaune est
# jaune a l'ecran), elle ne suit donc pas l'ordre categoriel.
TRIBUS = {
    "jaune": "var(--tribu-jaune)", "rouge": "var(--tribu-rouge)",
    "bleu": "var(--tribu-bleu)", "vert": "var(--tribu-vert)",
    "orange": "var(--tribu-orange)", "violet": "var(--tribu-violet)",
    "noir": "var(--tribu-noir)", "blanc": "var(--tribu-blanc)",
}


def e(t):
    return html.escape(str(t), quote=True)


class Figure:
    """Un SVG en cours d'ecriture."""

    def __init__(self, largeur, hauteur, titre, description):
        self.l, self.h = largeur, hauteur
        self.titre, self.description = titre, description
        self.corps = []

    def ajouter(self, fragment):
        self.corps.append(fragment)

    def rendu(self):
        return (
            f'<figure class="figure">\n'
            f'<svg class="graphique" viewBox="0 0 {self.l} {self.h}" '
            f'role="img" preserveAspectRatio="xMidYMid meet" '
            f'aria-label="{e(self.titre)}">\n'
            f'  <title>{e(self.titre)}</title>\n'
            f'  <desc>{e(self.description)}</desc>\n'
            + "\n".join("  " + x for x in self.corps)
            + "\n</svg>\n</figure>\n"
        )


def _texte(x, y, contenu, *, ancre="start", couleur=ENCRE_DOUCE, taille=13,
           gras=False, ligne_de_base="middle"):
    poids = ' font-weight="600"' if gras else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{ancre}" '
            f'dominant-baseline="{ligne_de_base}" fill="{couleur}" '
            f'font-size="{taille}"{poids}>{e(contenu)}</text>')


def barres_horizontales(donnees, *, titre, description, unite="",
                        largeur=680, hauteur_barre=26, marge_gauche=190,
                        couleur=None, valeur_max=None):
    """Barres horizontales : la forme juste pour comparer des categories nommees.

    `donnees` : [{"libelle":…, "valeur":…, "detail":…, "couleur":…}]
    """
    donnees = [d for d in donnees if d.get("valeur") is not None]
    if not donnees:
        return ""
    haut, bas, ecart = 16, 30, 8
    hauteur = haut + bas + len(donnees) * (hauteur_barre + ecart) - ecart
    marge_droite = 62
    piste = largeur - marge_gauche - marge_droite
    vmax = valeur_max or max(d["valeur"] for d in donnees) or 1

    fig = Figure(largeur, hauteur, titre, description)
    # graduations, volontairement discretes
    for f in (0.25, 0.5, 0.75, 1.0):
        x = marge_gauche + piste * f
        fig.ajouter(f'<line x1="{x:.1f}" y1="{haut - 6}" x2="{x:.1f}" '
                    f'y2="{hauteur - bas + 4}" stroke="{GRILLE}" stroke-width="1"/>')

    for i, d in enumerate(donnees):
        y = haut + i * (hauteur_barre + ecart)
        longueur = max(3.0, piste * d["valeur"] / vmax)
        teinte = d.get("couleur") or couleur or SERIES[i % len(SERIES)]
        info = d.get("detail") or f'{d["libelle"]} : {d["valeur"]}{unite}'
        fig.ajouter(
            f'<g class="marque"><title>{e(info)}</title>'
            f'<rect x="{marge_gauche}" y="{y}" width="{longueur:.1f}" '
            f'height="{hauteur_barre}" rx="4" fill="{teinte}" '
            f'stroke="{SURFACE}" stroke-width="2"/></g>')
        fig.ajouter(_texte(marge_gauche - 10, y + hauteur_barre / 2, d["libelle"],
                           ancre="end", couleur=ENCRE))
        fig.ajouter(_texte(marge_gauche + longueur + 8, y + hauteur_barre / 2,
                           f'{d["valeur"]}{unite}', couleur=ENCRE, gras=True))

    fig.ajouter(f'<line x1="{marge_gauche}" y1="{haut - 6}" x2="{marge_gauche}" '
                f'y2="{hauteur - bas + 4}" stroke="var(--axe)" stroke-width="1"/>')
    return fig.rendu()


def colonnes(donnees, *, titre, description, unite="", largeur=680, hauteur=300,
             couleur=None, etiquettes_valeurs=True):
    """Colonnes verticales : pour une progression ou une distribution ordonnee."""
    donnees = [d for d in donnees if d.get("valeur") is not None]
    if not donnees:
        return ""
    haut, bas, gauche, droite = 26, 52, 46, 12
    piste_h = hauteur - haut - bas
    piste_l = largeur - gauche - droite
    vmax = max(d["valeur"] for d in donnees) or 1
    pas = piste_l / len(donnees)
    epaisseur = min(46, pas - 8)

    fig = Figure(largeur, hauteur, titre, description)
    for f in (0, 0.25, 0.5, 0.75, 1.0):
        y = haut + piste_h * (1 - f)
        fig.ajouter(f'<line x1="{gauche}" y1="{y:.1f}" x2="{largeur - droite}" '
                    f'y2="{y:.1f}" stroke="{GRILLE}" stroke-width="1"/>')
        fig.ajouter(_texte(gauche - 8, y, f"{vmax * f:.0f}", ancre="end",
                           couleur=ENCRE_DOUCE, taille=11))

    for i, d in enumerate(donnees):
        cx = gauche + pas * i + pas / 2
        h = max(3.0, piste_h * d["valeur"] / vmax)
        y = haut + piste_h - h
        teinte = d.get("couleur") or couleur or SERIES[0]
        info = d.get("detail") or f'{d["libelle"]} : {d["valeur"]}{unite}'
        fig.ajouter(
            f'<g class="marque"><title>{e(info)}</title>'
            f'<rect x="{cx - epaisseur / 2:.1f}" y="{y:.1f}" width="{epaisseur:.1f}" '
            f'height="{h:.1f}" rx="4" fill="{teinte}" stroke="{SURFACE}" '
            f'stroke-width="2"/></g>')
        if etiquettes_valeurs:
            fig.ajouter(_texte(cx, y - 10, f'{d["valeur"]}{unite}', ancre="middle",
                               couleur=ENCRE, taille=11, gras=True))
        fig.ajouter(_texte(cx, hauteur - bas + 16, d["libelle"], ancre="middle",
                           couleur=ENCRE_DOUCE, taille=11))

    fig.ajouter(f'<line x1="{gauche}" y1="{haut + piste_h}" x2="{largeur - droite}" '
                f'y2="{haut + piste_h}" stroke="var(--axe)" stroke-width="1"/>')
    return fig.rendu()


def courbes(series, abscisses, *, titre, description, unite="", largeur=680,
            hauteur=320, legende=True):
    """Une ou plusieurs courbes sur un axe commun. Jamais deux echelles."""
    series = [s for s in series if any(v is not None for v in s["valeurs"])]
    if not series or not abscisses:
        return ""
    haut, bas, gauche, droite = 26, 56, 46, 16
    if legende and len(series) > 1:
        haut += 26
    piste_h = hauteur - haut - bas
    piste_l = largeur - gauche - droite
    toutes = [v for s in series for v in s["valeurs"] if v is not None]
    vmax = max(toutes) or 1
    vmin = min(0, min(toutes))
    etendue = (vmax - vmin) or 1
    pas = piste_l / max(1, len(abscisses) - 1)

    def px(i):
        return gauche + pas * i

    def py(v):
        return haut + piste_h * (1 - (v - vmin) / etendue)

    fig = Figure(largeur, hauteur, titre, description)
    for f in (0, 0.25, 0.5, 0.75, 1.0):
        y = haut + piste_h * (1 - f)
        fig.ajouter(f'<line x1="{gauche}" y1="{y:.1f}" x2="{largeur - droite}" '
                    f'y2="{y:.1f}" stroke="{GRILLE}" stroke-width="1"/>')
        fig.ajouter(_texte(gauche - 8, y, f"{vmin + etendue * f:.0f}", ancre="end",
                           couleur=ENCRE_DOUCE, taille=11))

    for k, s in enumerate(series):
        teinte = s.get("couleur") or SERIES[k % len(SERIES)]
        points = [(px(i), py(v)) for i, v in enumerate(s["valeurs"]) if v is not None]
        if len(points) > 1:
            trace = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            fig.ajouter(f'<polyline points="{trace}" fill="none" stroke="{teinte}" '
                        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, v in enumerate(s["valeurs"]):
            if v is None:
                continue
            fig.ajouter(
                f'<g class="marque"><title>'
                f'{e(s["nom"])} — {e(abscisses[i])} : {v}{e(unite)}</title>'
                f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="4.5" fill="{teinte}" '
                f'stroke="{SURFACE}" stroke-width="2"/></g>')
        # etiquette directe en bout de courbe : l'identite ne tient pas a la couleur
        dernier = max((i for i, v in enumerate(s["valeurs"]) if v is not None), default=None)
        if dernier is not None and len(series) <= 4:
            fig.ajouter(_texte(px(dernier) + 8, py(s["valeurs"][dernier]), s["nom"],
                               couleur=ENCRE, taille=11, gras=True))

    for i, a in enumerate(abscisses):
        fig.ajouter(_texte(px(i), hauteur - bas + 18, a, ancre="middle",
                           couleur=ENCRE_DOUCE, taille=11))

    if legende and len(series) > 1:
        x = gauche
        for k, s in enumerate(series):
            teinte = s.get("couleur") or SERIES[k % len(SERIES)]
            fig.ajouter(f'<rect x="{x}" y="14" width="11" height="11" rx="3" '
                        f'fill="{teinte}"/>')
            fig.ajouter(_texte(x + 17, 20, s["nom"], couleur=ENCRE, taille=12))
            x += 24 + 7.2 * len(s["nom"])

    fig.ajouter(f'<line x1="{gauche}" y1="{haut + piste_h}" x2="{largeur - droite}" '
                f'y2="{haut + piste_h}" stroke="var(--axe)" stroke-width="1"/>')
    return fig.rendu()


def ecrire(nom, contenu):
    if not contenu:
        print(f"  (vide) {nom}")
        return
    os.makedirs(SORTIE, exist_ok=True)
    chemin = os.path.join(SORTIE, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"  {nom}  ({len(contenu)} o)")


def barres_groupees(donnees, series, *, titre, description, unite="",
                    largeur=680, hauteur_groupe=42, marge_gauche=200):
    """Deux ou trois series comparees sur les memes categories.

    C'est la forme juste quand un chiffre ne veut rien dire seul : « 31 % de
    vainqueurs » ne se lit que face au taux d'ensemble. Les barres d'un meme
    groupe se touchent, les groupes sont espaces -- la comparaison se fait a
    l'interieur du groupe, pas entre groupes.

    `donnees` : [{"libelle":…, "valeurs":[…], "details":[…]}]
    `series`  : [{"nom":…, "couleur":…}]
    """
    donnees = [d for d in donnees if any(v is not None for v in d["valeurs"])]
    if not donnees or not series:
        return ""
    haut, bas, ecart = 44, 26, 12
    epaisseur = (hauteur_groupe - 2 * (len(series) - 1)) / len(series)
    hauteur = haut + bas + len(donnees) * (hauteur_groupe + ecart) - ecart
    marge_droite = 66
    piste = largeur - marge_gauche - marge_droite
    vmax = max(v for d in donnees for v in d["valeurs"] if v is not None) or 1

    fig = Figure(largeur, hauteur, titre, description)
    for f in (0.25, 0.5, 0.75, 1.0):
        x = marge_gauche + piste * f
        fig.ajouter(f'<line x1="{x:.1f}" y1="{haut - 8}" x2="{x:.1f}" '
                    f'y2="{hauteur - bas + 2}" stroke="{GRILLE}" stroke-width="1"/>')

    # legende : avec plusieurs series, l'identite ne peut pas tenir a la couleur
    x = marge_gauche
    for k, s in enumerate(series):
        teinte = s.get("couleur") or SERIES[k % len(SERIES)]
        fig.ajouter(f'<rect x="{x}" y="12" width="11" height="11" rx="3" fill="{teinte}"/>')
        fig.ajouter(_texte(x + 17, 18, s["nom"], couleur=ENCRE, taille=12))
        x += 26 + 7.2 * len(s["nom"])

    for i, d in enumerate(donnees):
        y0 = haut + i * (hauteur_groupe + ecart)
        fig.ajouter(_texte(marge_gauche - 10, y0 + hauteur_groupe / 2, d["libelle"],
                           ancre="end", couleur=ENCRE))
        for k, s in enumerate(series):
            v = d["valeurs"][k] if k < len(d["valeurs"]) else None
            if v is None:
                continue
            y = y0 + k * (epaisseur + 2)
            longueur = max(2.0, piste * v / vmax)
            teinte = s.get("couleur") or SERIES[k % len(SERIES)]
            info = (d.get("details") or [None] * len(series))[k] \
                or f'{d["libelle"]} — {s["nom"]} : {v}{unite}'
            fig.ajouter(
                f'<g class="marque"><title>{e(info)}</title>'
                f'<rect x="{marge_gauche}" y="{y:.1f}" width="{longueur:.1f}" '
                f'height="{epaisseur:.1f}" rx="3" fill="{teinte}" '
                f'stroke="{SURFACE}" stroke-width="1"/></g>')
            fig.ajouter(_texte(marge_gauche + longueur + 7, y + epaisseur / 2,
                               f'{v}{unite}', couleur=ENCRE, taille=11, gras=True))

    fig.ajouter(f'<line x1="{marge_gauche}" y1="{haut - 8}" x2="{marge_gauche}" '
                f'y2="{hauteur - bas + 2}" stroke="var(--axe)" stroke-width="1"/>')
    return fig.rendu()


def peigne(traits, *, titre, description, jour_max, mediane=None, legende=None,
           largeur=1000, hauteur_traits=336):
    """Un trait par aventurier : sa longueur est le nombre de jours tenus.

    C'est la figure d'ouverture du site, et la seule qui ne resume rien -- elle
    montre TOUT le jeu de donnees, une personne par ligne. Triee par duree, la
    frontiere droite du peigne est exactement la courbe de survie du programme,
    mais dessinee avec ses individus au lieu d'un trace moyen.

    Chaque trait porte la couleur du bandeau de depart : la teinte EST la
    donnee, elle ne suit pas l'ordre categoriel.

    `traits` : [{"jour": int, "couleur": "var(--tribu-…)"}], deja triees du
    plus court sejour au plus long.
    """
    if not traits:
        return ""
    haut, bas, gauche, droite = 46, 34, 4, 116
    if legende:
        haut += 22
    piste_l = largeur - gauche - droite
    hauteur = haut + hauteur_traits + bas
    pas = hauteur_traits / len(traits)
    # Un trait un peu plus epais que le pas : les lignes se joignent, la masse
    # se lit comme une surface au lieu d'une rayure.
    epaisseur = max(0.55, pas * 1.05)

    def px(jour):
        return gauche + piste_l * (jour / jour_max)

    fig = Figure(largeur, hauteur, titre, description)

    # Axe des jours, pose en haut : c'est la ou le regard entre.
    graduations = [j for j in range(10, jour_max, 10)] + [jour_max]
    for j in graduations:
        x = px(j)
        fig.ajouter(f'<line x1="{x:.1f}" y1="{haut - 12}" x2="{x:.1f}" '
                    f'y2="{haut + hauteur_traits}" stroke="{GRILLE}" stroke-width="1"/>')
        fig.ajouter(_texte(x, haut - 22, f"jour {j}", ancre="middle",
                           couleur=ENCRE_DOUCE, taille=12))

    # Les traits, regroupes par couleur : un seul <path> par teinte plutot que
    # six cents elements. La page reste legere et le rendu immediat.
    groupes = {}
    for i, t in enumerate(traits):
        y = haut + i * pas + pas / 2
        longueur = max(1.2, px(t["jour"]) - gauche)
        groupes.setdefault(t["couleur"], []).append(
            f'M{gauche:.1f},{y:.2f}h{longueur:.1f}')

    fig.ajouter('<g class="peigne-traits">')
    for teinte, morceaux in groupes.items():
        fig.ajouter(f'<path d="{"".join(morceaux)}" stroke="{teinte}" '
                    f'stroke-width="{epaisseur:.2f}" fill="none" '
                    f'stroke-linecap="butt"/>')
    fig.ajouter('</g>')

    # L'annotation unique : la moitie du plateau est sortie avant ce jour-la.
    if mediane:
        y = haut + hauteur_traits / 2
        fig.ajouter(f'<line x1="{gauche}" y1="{y:.1f}" x2="{largeur - droite + 8}" '
                    f'y2="{y:.1f}" stroke="{ENCRE}" stroke-width="1" '
                    f'stroke-dasharray="2 3" opacity="0.55"/>')
        fig.ajouter(_texte(largeur - droite + 14, y,
                           f"moitié sortie avant le jour {mediane}",
                           couleur=ENCRE, taille=12, gras=True))

    fig.ajouter(_texte(largeur - droite + 14, haut + 8, "un trait,",
                       couleur=ENCRE_DOUCE, taille=12))
    fig.ajouter(_texte(largeur - droite + 14, haut + 24, "un aventurier",
                       couleur=ENCRE_DOUCE, taille=12))
    fig.ajouter(_texte(largeur - droite + 14, haut + hauteur_traits - 8,
                       f"{jour_max} jours", couleur=ENCRE, taille=12, gras=True))

    if legende:
        x = gauche
        for nom, teinte in legende:
            fig.ajouter(f'<rect x="{x}" y="12" width="11" height="11" rx="2" fill="{teinte}"/>')
            fig.ajouter(_texte(x + 17, 18, nom, couleur=ENCRE, taille=12))
            x += 26 + 7.2 * len(nom)

    fig.ajouter(f'<line x1="{gauche}" y1="{haut - 12}" x2="{gauche}" '
                f'y2="{haut + hauteur_traits}" stroke="var(--axe)" stroke-width="1"/>')

    return (f'<div class="peigne">\n'
            + fig.rendu().replace('<figure class="figure">\n', '')
                         .replace('</figure>\n', '')
            + '</div>\n')
