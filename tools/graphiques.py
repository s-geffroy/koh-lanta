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
ENCRE_MUETTE = "var(--encre-muette)"
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


def survie(series, toutes, *, titre, description, jour_max, mediane,
           largeur=1000, hauteur=400, note=None):
    """Les courbes de survie des deux bandeaux, l'une sur l'autre.

    C'est la figure d'ouverture du site. Elle ne montre pas un ecart : elle
    montre une COINCIDENCE. Deux courbes qui se superposent disent en une image
    ce que la page « Jaune contre rouge » met une section a demontrer -- et la
    surface pleine dessous rappelle qu'il s'agit de gens qui s'en vont.

    `series` : [{"couleur": "jaune", "valeurs": [% restants au jour 1..N]}]
    `toutes` : la meme courbe, tous bandeaux confondus, pour la surface.
    """
    if not series or not toutes:
        return ""
    haut, bas, gauche, droite = 30, 46, 52, 22
    piste_l = largeur - gauche - droite
    piste_h = hauteur - haut - bas

    def px(jour):
        return gauche + piste_l * (jour - 1) / max(1, jour_max - 1)

    def py(part):
        return haut + piste_h * (1 - part / 100.0)

    fig = Figure(largeur, hauteur, titre, description)

    # Les repères horizontaux, et eux seuls : pas de cadre, pas d'axe vertical.
    for part in (0, 25, 50, 75, 100):
        y = py(part)
        fig.ajouter(f'<line x1="{gauche}" y1="{y:.1f}" x2="{largeur - droite}" '
                    f'y2="{y:.1f}" stroke="{GRILLE}" stroke-width="1"/>')
        fig.ajouter(_texte(gauche - 10, y, f"{part} %", ancre="end",
                           couleur=ENCRE_MUETTE, taille=12))

    # La masse : tous les aventuriers confondus, en aplat tres pale. Elle donne
    # la forme generale sans jamais concurrencer les deux traits.
    aire = " ".join(f"{px(j + 1):.1f},{py(v):.1f}" for j, v in enumerate(toutes))
    fig.ajouter(f'<polygon points="{px(1):.1f},{py(0):.1f} {aire} '
                f'{px(len(toutes)):.1f},{py(0):.1f}" fill="{ENCRE}" '
                f'fill-opacity="0.07"/>')

    # Le jour median, marque avant les courbes pour passer dessous.
    if mediane:
        x = px(mediane)
        fig.ajouter(f'<line x1="{x:.1f}" y1="{py(100):.1f}" x2="{x:.1f}" '
                    f'y2="{py(0):.1f}" stroke="{ENCRE_MUETTE}" stroke-width="1" '
                    f'stroke-dasharray="3 4"/>')
        fig.ajouter(_texte(x + 8, py(88), f"jour {mediane}", couleur=ENCRE,
                           taille=13, gras=True))
        fig.ajouter(_texte(x + 8, py(80), "la moitié est partie",
                           couleur=ENCRE_DOUCE, taille=12))

    # Les deux courbes. Un liseré de la couleur du fond les separe la ou elles
    # se croisent : sans lui, la seconde effacerait la premiere.
    for serie in series:
        teinte = TRIBUS.get(serie["couleur"], ENCRE)
        pts = " ".join(f"{px(j + 1):.1f},{py(v):.1f}"
                       for j, v in enumerate(serie["valeurs"]))
        fig.ajouter(f'<polyline points="{pts}" fill="none" stroke="{SURFACE}" '
                    f'stroke-width="5" stroke-linejoin="round" stroke-opacity="0.8"/>')
        fig.ajouter(f'<polyline points="{pts}" fill="none" stroke="{teinte}" '
                    f'stroke-width="2.6" stroke-linejoin="round" '
                    f'stroke-linecap="round"><title>'
                    f'{e(serie["couleur"])} : {e(serie.get("effectif", ""))} aventuriers, '
                    f'mediane au jour {e(serie.get("mediane", ""))}</title></polyline>')

    # Les etiquettes directes -- pas de cartouche, qui demanderait un
    # aller-retour de l'oeil. On les pose au jour ou les deux courbes sont le
    # PLUS eloignees : partout ailleurs elles se touchent, et deux pastilles
    # superposees feraient une tache au lieu de deux reperes.
    if len(series) == 2:
        ecarts = [abs(a - b) for a, b in zip(series[0]["valeurs"], series[1]["valeurs"])]
        repere = max(range(len(ecarts)), key=lambda i: ecarts[i]) + 1
    else:
        repere = max(2, int(jour_max * 0.62))
    ordre = sorted(series, key=lambda s: -s["valeurs"][repere - 1])
    for rang, serie in enumerate(ordre):
        teinte = TRIBUS.get(serie["couleur"], ENCRE)
        v = serie["valeurs"][repere - 1]
        decalage = -13 if rang == 0 else 15   # le plus haut au-dessus, l'autre dessous
        fig.ajouter(f'<circle cx="{px(repere):.1f}" cy="{py(v):.1f}" r="4.5" '
                    f'fill="{teinte}" stroke="{SURFACE}" stroke-width="2"/>')
        fig.ajouter(_texte(px(repere) + 11, py(v) + decalage,
                           f'tribu {serie["couleur"]}', couleur=ENCRE,
                           taille=13, gras=True))

    # L'axe des jours.
    for jour in range(10, jour_max + 1, 10):
        fig.ajouter(_texte(px(jour), hauteur - bas + 20, f"jour {jour}",
                           ancre="middle", couleur=ENCRE_MUETTE, taille=12))
    if note:
        fig.ajouter(_texte(gauche, hauteur - bas + 38, note,
                           couleur=ENCRE_MUETTE, taille=12))

    return (f'<div class="vitrine">\n'
            + fig.rendu().replace('<figure class="figure">\n', '')
                         .replace('</figure>\n', '')
            + '</div>\n')


def arcs(noeuds, liens, *, titre, description, largeur=980, hauteur_arc=150,
         etiquettes=None, legende=None, hauteur_etiquettes=96):
    """Diagramme en arcs : des gens sur une ligne, un arc par relation.

    C'est la forme juste quand les entites ont un ORDRE naturel -- ici l'ordre
    de sortie, ou l'ordre d'arrivee dans le programme. Un graphe pose au hasard
    donnerait un nuage de spaghettis dont la disposition ne voudrait rien dire ;
    sur une ligne ordonnee, la portee d'un arc est elle-meme une information.

    `noeuds` : [{"nom":…, "poids":…, "couleur":…}] deja dans l'ordre voulu.
    `liens`  : [{"de": i, "vers": j, "poids": n}] par indices de noeuds.
    """
    if not noeuds:
        return ""
    gauche, droite = 26, 26
    haut = 26 + (22 if legende else 0)
    piste = largeur - gauche - droite
    base = haut + hauteur_arc
    hauteur = base + hauteur_etiquettes
    pas = piste / max(1, len(noeuds) - 1)
    poids_max = max((l.get("poids") or 1) for l in liens) if liens else 1

    def x(i):
        return gauche + pas * i

    fig = Figure(largeur, hauteur, titre, description)

    # Les arcs d'abord : ils passent DERRIERE les points, jamais devant.
    for l in liens:
        a, b = x(l["de"]), x(l["vers"])
        if a == b:
            continue
        r = abs(b - a) / 2
        h = min(hauteur_arc, r)
        p = (l.get("poids") or 1) / poids_max
        # Un arc epais est un lien repete : l'epaisseur porte la meme
        # information que l'opacite, pour qui ne distingue pas les nuances.
        # Courbe de Bezier quadratique plutot qu'arc elliptique : le point de
        # controle se choisit, la hauteur du sommet vaut exactement h, et il
        # n'y a aucun drapeau de sens a interpreter -- donc aucun risque que
        # les arcs partent du mauvais cote de l'axe.
        g_, d_ = min(a, b), max(a, b)
        fig.ajouter(
            f'<path d="M{g_:.1f},{base} Q{(g_ + d_) / 2:.1f},{base - 2 * h:.1f} '
            f'{d_:.1f},{base}" fill="none" stroke="{ENCRE_DOUCE}" '
            f'stroke-width="{0.6 + 2.2 * p:.2f}" opacity="{0.16 + 0.5 * p:.2f}"/>')

    fig.ajouter(f'<line x1="{gauche - 8}" y1="{base}" x2="{largeur - droite + 8}" '
                f'y2="{base}" stroke="var(--axe)" stroke-width="1"/>')

    poids_n = max((n.get("poids") or 1) for n in noeuds)
    for i, n in enumerate(noeuds):
        r = 2.6 + 4.4 * ((n.get("poids") or 1) / poids_n) ** 0.5
        teinte = n.get("couleur") or SERIES[0]
        info = n.get("detail") or n["nom"]
        fig.ajouter(f'<g class="marque"><title>{e(info)}</title>'
                    f'<circle cx="{x(i):.1f}" cy="{base}" r="{r:.1f}" fill="{teinte}" '
                    f'stroke="{SURFACE}" stroke-width="1.5"/></g>')

    # Les noms tournes a la verticale : soixante-dix noms cote a cote ne
    # tiennent pas autrement, et les tronquer les rendrait inutiles.
    if etiquettes is None:
        etiquettes = len(noeuds) <= 46
    if etiquettes:
        for i, n in enumerate(noeuds):
            fig.ajouter(
                f'<text x="{x(i):.1f}" y="{base + 12}" fill="{ENCRE_DOUCE}" '
                f'font-size="11" text-anchor="end" '
                f'transform="rotate(-60 {x(i):.1f} {base + 12})">{e(n["nom"])}</text>')

    if legende:
        xx = gauche
        for nom, teinte in legende:
            fig.ajouter(f'<rect x="{xx}" y="12" width="11" height="11" rx="2" fill="{teinte}"/>')
            fig.ajouter(_texte(xx + 17, 18, nom, couleur=ENCRE, taille=12))
            xx += 26 + 7.2 * len(nom)

    return fig.rendu()


def petits_multiples(series, *, titre, description, colonnes_par_rang=6,
                     largeur=980, hauteur_vignette=86, unite=""):
    """Une meme courbe repetee, aux memes echelles, pour comparer d'un regard.

    La regle est simple et c'est toute la force de la forme : les axes ne
    changent JAMAIS d'une vignette a l'autre. Une courbe qui plonge plonge
    vraiment, elle n'est pas mise a l'echelle de sa propre case.

    `series` : [{"titre":…, "sous_titre":…, "valeurs":[…], "couleur":…}]
    Les valeurs sont des parts de 0 a 100, regulierement espacees.
    """
    series = [s for s in series if s.get("valeurs")]
    if not series:
        return ""
    marge, entre = 8, 12
    rangs = (len(series) + colonnes_par_rang - 1) // colonnes_par_rang
    case_l = (largeur - 2 * marge - entre * (colonnes_par_rang - 1)) / colonnes_par_rang
    hauteur = marge + rangs * (hauteur_vignette + 34) + 6
    trace_h = hauteur_vignette - 22

    fig = Figure(largeur, hauteur, titre, description)
    for k, s in enumerate(series):
        cx = marge + (k % colonnes_par_rang) * (case_l + entre)
        cy = marge + (k // colonnes_par_rang) * (hauteur_vignette + 34) + 20
        teinte = s.get("couleur") or SERIES[0]
        vals = s["valeurs"]
        pas = case_l / max(1, len(vals) - 1)

        fig.ajouter(_texte(cx, cy - 12, s["titre"], couleur=ENCRE, taille=11, gras=True))
        if s.get("sous_titre"):
            fig.ajouter(_texte(cx + case_l, cy - 12, s["sous_titre"], ancre="end",
                               couleur=ENCRE_MUETTE, taille=10))
        # mi-hauteur : le repere qui permet de lire « la moitie du plateau »
        fig.ajouter(f'<line x1="{cx:.1f}" y1="{cy + trace_h / 2:.1f}" '
                    f'x2="{cx + case_l:.1f}" y2="{cy + trace_h / 2:.1f}" '
                    f'stroke="{GRILLE}" stroke-width="1"/>')

        pts = [(cx + pas * i, cy + trace_h * (1 - v / 100.0)) for i, v in enumerate(vals)]
        aire = (f'M{pts[0][0]:.1f},{cy + trace_h:.1f} '
                + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts)
                + f" L{pts[-1][0]:.1f},{cy + trace_h:.1f} Z")
        fig.ajouter(f'<path d="{aire}" fill="{teinte}" opacity="0.16"/>')
        fig.ajouter(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
                    f'fill="none" stroke="{teinte}" stroke-width="1.8" '
                    f'stroke-linejoin="round"/>')
        fig.ajouter(f'<g class="marque"><title>{e(s.get("detail") or s["titre"])}</title>'
                    f'<rect x="{cx:.1f}" y="{cy - 4:.1f}" width="{case_l:.1f}" '
                    f'height="{trace_h + 8:.1f}" fill="transparent"/></g>')
        fig.ajouter(f'<line x1="{cx:.1f}" y1="{cy + trace_h:.1f}" '
                    f'x2="{cx + case_l:.1f}" y2="{cy + trace_h:.1f}" '
                    f'stroke="var(--axe)" stroke-width="1"/>')
    return fig.rendu()


def nuage(points, *, titre, description, x_min, x_max, legende=None,
          largeur=980, hauteur=380, x_titre="", y_titre=""):
    """Un point par individu : la population entiere, sans moyenne.

    Utile quand l'agregat cache la dispersion. Les points se chevauchent : on
    les rend donc semi-transparents et cercles nets, plutot que de secouer
    leur position, ce qui deplacerait la donnee.

    `points` : [{"x":…, "y":…, "couleur":…, "detail":…}] y en 0..100.
    """
    points = [p for p in points if p.get("x") is not None and p.get("y") is not None]
    if not points:
        return ""
    haut, bas, gauche, droite = 26 + (22 if legende else 0), 46, 46, 16
    piste_l = largeur - gauche - droite
    piste_h = hauteur - haut - bas

    def px(v):
        return gauche + piste_l * (v - x_min) / max(1, x_max - x_min)

    def py(v):
        return haut + piste_h * (1 - v / 100.0)

    fig = Figure(largeur, hauteur, titre, description)
    for f in (0, 25, 50, 75, 100):
        y = py(f)
        fig.ajouter(f'<line x1="{gauche}" y1="{y:.1f}" x2="{largeur - droite}" '
                    f'y2="{y:.1f}" stroke="{GRILLE}" stroke-width="1"/>')
        fig.ajouter(_texte(gauche - 8, y, f"{f} %", ancre="end",
                           couleur=ENCRE_DOUCE, taille=11))
    pas_x = 10 if (x_max - x_min) <= 60 else 20
    v = x_min - x_min % pas_x + pas_x
    while v <= x_max:
        fig.ajouter(_texte(px(v), hauteur - bas + 18, str(v), ancre="middle",
                           couleur=ENCRE_DOUCE, taille=11))
        v += pas_x

    for p in points:
        fig.ajouter(
            f'<g class="marque"><title>{e(p.get("detail") or "")}</title>'
            f'<circle cx="{px(p["x"]):.1f}" cy="{py(p["y"]):.1f}" r="4" '
            f'fill="{p.get("couleur") or SERIES[0]}" opacity="0.62"/></g>')

    if x_titre:
        fig.ajouter(_texte(largeur - droite, hauteur - bas + 36, x_titre,
                           ancre="end", couleur=ENCRE_MUETTE, taille=11))
    if y_titre:
        fig.ajouter(_texte(gauche - 8, haut - 12, y_titre, ancre="start",
                           couleur=ENCRE_MUETTE, taille=11))
    if legende:
        x = gauche
        for nom, teinte in legende:
            fig.ajouter(f'<circle cx="{x + 5}" cy="18" r="5" fill="{teinte}"/>')
            fig.ajouter(_texte(x + 15, 18, nom, couleur=ENCRE, taille=12))
            x += 24 + 7.2 * len(nom)
    fig.ajouter(f'<line x1="{gauche}" y1="{haut + piste_h}" x2="{largeur - droite}" '
                f'y2="{haut + piste_h}" stroke="var(--axe)" stroke-width="1"/>')
    return fig.rendu()


def halteres(donnees, *, titre, description, unite="", largeur=880,
             hauteur_ligne=20, marge_gauche=210, legende=None):
    """Un segment par ligne, entre deux bornes, avec un point median.

    C'est la forme d'une ETENDUE. Une barre dirait « de zero a tant » ; ici la
    donnee commence au minimum, et la longueur du segment EST l'ecart.

    `donnees` : [{"libelle":…, "min":…, "median":…, "max":…, "couleur":…}]
    """
    donnees = [d for d in donnees if d.get("min") is not None]
    if not donnees:
        return ""
    haut = 30 + (22 if legende else 0)
    bas, droite = 34, 54
    hauteur = haut + bas + len(donnees) * hauteur_ligne
    piste = largeur - marge_gauche - droite
    vmin = min(d["min"] for d in donnees)
    vmax = max(d["max"] for d in donnees)
    etendue = (vmax - vmin) or 1

    def px(v):
        return marge_gauche + piste * (v - vmin) / etendue

    fig = Figure(largeur, hauteur, titre, description)
    pas = 10
    v = vmin - vmin % pas + pas
    while v <= vmax:
        fig.ajouter(f'<line x1="{px(v):.1f}" y1="{haut - 10}" x2="{px(v):.1f}" '
                    f'y2="{hauteur - bas + 4}" stroke="{GRILLE}" stroke-width="1"/>')
        fig.ajouter(_texte(px(v), haut - 18, f"{v}{unite}", ancre="middle",
                           couleur=ENCRE_DOUCE, taille=11))
        v += pas

    for i, d in enumerate(donnees):
        y = haut + i * hauteur_ligne + hauteur_ligne / 2
        teinte = d.get("couleur") or SERIES[0]
        info = d.get("detail") or (f'{d["libelle"]} : de {d["min"]} à {d["max"]}{unite}')
        fig.ajouter(f'<g class="marque"><title>{e(info)}</title>'
                    f'<line x1="{px(d["min"]):.1f}" y1="{y:.1f}" '
                    f'x2="{px(d["max"]):.1f}" y2="{y:.1f}" stroke="{teinte}" '
                    f'stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
                    f'<circle cx="{px(d["min"]):.1f}" cy="{y:.1f}" r="3.4" fill="{teinte}"/>'
                    f'<circle cx="{px(d["max"]):.1f}" cy="{y:.1f}" r="3.4" fill="{teinte}"/>'
                    + (f'<circle cx="{px(d["median"]):.1f}" cy="{y:.1f}" r="2.6" '
                       f'fill="{SURFACE}" stroke="{teinte}" stroke-width="1.6"/>'
                       if d.get("median") is not None else "")
                    + '</g>')
        fig.ajouter(_texte(marge_gauche - 10, y, d["libelle"], ancre="end",
                           couleur=ENCRE, taille=11))
        fig.ajouter(_texte(px(d["max"]) + 9, y, f'{d["max"] - d["min"]}{unite}',
                           couleur=ENCRE_DOUCE, taille=11))

    if legende:
        x = marge_gauche
        for nom, teinte in legende:
            fig.ajouter(f'<rect x="{x}" y="8" width="11" height="11" rx="2" fill="{teinte}"/>')
            fig.ajouter(_texte(x + 17, 14, nom, couleur=ENCRE, taille=12))
            x += 26 + 7.2 * len(nom)
    return fig.rendu()


def distribution_nulle(test, *, titre=None, description=None, largeur=680,
                       hauteur=250, couleur=None):
    """Ce que le hasard produirait, et ou tombe ce qu'on observe.

    La figure signature d'un test de permutation, et la seule facon honnete de
    montrer une p-value : la silhouette est la distribution des dizaines de
    milliers de tirages ; le trait vertical est la valeur reelle. Si le trait
    tombe dans la masse, il n'y a rien a annoncer -- et cela se VOIT, au lieu
    de se deduire d'un nombre.

    `test` : un element du registre de tools/modeles.py.
    """
    nulle = test.get("nulle") or {}
    cases = nulle.get("cases") or []
    if not cases:
        return ""
    bas, haut = nulle["bornes"]
    etendue = (haut - bas) or 1.0
    marge_g, marge_d = 46, 22
    plafond, sol = 46, 46
    piste = largeur - marge_g - marge_d
    sommet = max(cases) or 1

    def px(v):
        return marge_g + piste * (v - bas) / etendue

    fig = Figure(largeur, hauteur,
                 titre or test.get("libelle") or "Distribution nulle",
                 description or test.get("question") or "")
    zero = hauteur - sol
    fig.ajouter(f'<line x1="{marge_g}" y1="{zero}" x2="{largeur - marge_d}" '
                f'y2="{zero}" stroke="{GRILLE}" stroke-width="1"/>')

    teinte = couleur or SERIES[4]
    largeur_case = piste / len(cases)
    for i, n in enumerate(cases):
        if not n:
            continue
        h = (hauteur - plafond - sol) * n / sommet
        x = marge_g + i * largeur_case
        borne_b = bas + etendue * i / len(cases)
        borne_h = bas + etendue * (i + 1) / len(cases)
        info = (f"{n} tirages sur {test.get('tirages')} entre "
                f"{borne_b:.3g} et {borne_h:.3g}")
        fig.ajouter(f'<g class="marque"><title>{e(info)}</title>'
                    f'<rect x="{x + 0.8:.1f}" y="{zero - h:.1f}" '
                    f'width="{max(0.6, largeur_case - 1.6):.1f}" height="{h:.1f}" '
                    f'fill="{teinte}" opacity="0.45"/></g>')

    # La moyenne des tirages : ce que le hasard donne « en general ».
    xm = px(nulle["moyenne_nulle"])
    fig.ajouter(f'<line x1="{xm:.1f}" y1="{plafond - 6}" x2="{xm:.1f}" y2="{zero}" '
                f'stroke="{ENCRE_MUETTE}" stroke-width="1" stroke-dasharray="3 3"/>')
    fig.ajouter(_texte(xm, plafond - 12, "attendu", ancre="middle",
                       couleur=ENCRE_MUETTE, taille=11))

    # La valeur observee.
    xo = px(nulle["observe"])
    ancre = "end" if xo > marge_g + piste * 0.6 else "start"
    decalage = -7 if ancre == "end" else 7
    fig.ajouter(f'<line x1="{xo:.1f}" y1="{plafond - 20}" x2="{xo:.1f}" y2="{zero + 6}" '
                f'stroke="{ENCRE}" stroke-width="2.4"/>')
    unite = (" " + test["unite"]) if test.get("unite") else ""
    fig.ajouter(_texte(xo + decalage, plafond - 24,
                       f'observé : {test["observe"]}{unite}', ancre=ancre,
                       couleur=ENCRE, taille=12, gras=True))

    for v, ancre_t in ((bas, "start"), (haut, "end")):
        fig.ajouter(_texte(px(v), zero + 18, f"{v:.3g}", ancre=ancre_t,
                           couleur=ENCRE_DOUCE, taille=11))
    p = test.get("p_ajustee", test.get("p"))
    mention = "p < 0,001" if p is not None and p < 0.001 else f"p = {p}".replace(".", ",")
    fig.ajouter(_texte(largeur - marge_d, zero + 34,
                       f'{test.get("tirages", 0):,}'.replace(",", " ")
                       + f" tirages · {mention}", ancre="end",
                       couleur=ENCRE_MUETTE, taille=11))
    return fig.rendu()


def foret(donnees, *, titre, description, reference=1.0, unite="",
          largeur=760, hauteur_ligne=26, marge_gauche=232, note=None):
    """Un coefficient par ligne, avec son intervalle et la valeur neutre.

    Un point sans son intervalle laisse croire a une precision qui n'existe
    pas. Ici la longueur du trait EST l'incertitude, et le trait vertical
    marque la valeur qui veut dire « aucun effet » : un intervalle qui la
    traverse se lit d'un coup d'oeil, sans arbitrer sur une p-value.

    `donnees` : [{"libelle":…, "estimation":…, "bas":…, "haut":…, "couleur":…}]
    """
    donnees = [d for d in donnees if d.get("estimation") is not None]
    if not donnees:
        return ""
    haut_marge, bas_marge, droite = 40, 40 + (18 if note else 0), 92
    hauteur = haut_marge + bas_marge + len(donnees) * hauteur_ligne
    piste = largeur - marge_gauche - droite
    vmin = min(min(d["bas"], reference) for d in donnees)
    vmax = max(max(d["haut"], reference) for d in donnees)
    marge = (vmax - vmin) * 0.08 or 0.1
    vmin, vmax = vmin - marge, vmax + marge
    etendue = (vmax - vmin) or 1

    def px(v):
        return marge_gauche + piste * (v - vmin) / etendue

    fig = Figure(largeur, hauteur, titre, description)
    xr = px(reference)
    fig.ajouter(f'<line x1="{xr:.1f}" y1="{haut_marge - 14}" x2="{xr:.1f}" '
                f'y2="{hauteur - bas_marge + 6}" stroke="{ENCRE_DOUCE}" '
                f'stroke-width="1.4" stroke-dasharray="4 3"/>')
    fig.ajouter(_texte(xr, haut_marge - 20, f"{reference:g}", ancre="middle",
                       couleur=ENCRE_DOUCE, taille=11))

    for i, d in enumerate(donnees):
        y = haut_marge + i * hauteur_ligne + hauteur_ligne / 2
        traverse = d["bas"] <= reference <= d["haut"]
        teinte = d.get("couleur") or (ENCRE_MUETTE if traverse else SERIES[0])
        info = d.get("detail") or (
            f'{d["libelle"]} : {d["estimation"]}{unite} '
            f'(intervalle {d["bas"]} à {d["haut"]})')
        fig.ajouter(f'<g class="marque"><title>{e(info)}</title>'
                    f'<line x1="{px(d["bas"]):.1f}" y1="{y:.1f}" '
                    f'x2="{px(d["haut"]):.1f}" y2="{y:.1f}" stroke="{teinte}" '
                    f'stroke-width="2.6" stroke-linecap="round" opacity="0.55"/>'
                    f'<circle cx="{px(d["estimation"]):.1f}" cy="{y:.1f}" r="4.4" '
                    f'fill="{teinte}" stroke="{SURFACE}" stroke-width="1.6"/>'
                    f'</g>')
        fig.ajouter(_texte(marge_gauche - 10, y, d["libelle"], ancre="end",
                           couleur=ENCRE, taille=11.5))
        fig.ajouter(_texte(largeur - droite + 12, y,
                           f'{d["estimation"]}{unite}', couleur=ENCRE_DOUCE,
                           taille=11.5))
    if note:
        fig.ajouter(_texte(marge_gauche, hauteur - 14, note, couleur=ENCRE_MUETTE,
                           taille=11))
    return fig.rendu()


def plan(points, *, titre, description, x_titre="", y_titre="", reperes=None,
         legende=None, largeur=940, hauteur=440):
    """Un nuage a deux axes libres, pour un plan factoriel.

    `nuage()` impose une ordonnee en pourcentage : ici les deux axes sont des
    coordonnees quelconques, et l'origine -- le profil moyen -- est marquee.

    `points` : [{"x":…, "y":…, "couleur":…, "detail":…}]
    `reperes` : [{"x":…, "y":…, "libelle":…}] — les modalites a nommer.
    """
    points = [p for p in points if p.get("x") is not None and p.get("y") is not None]
    if not points:
        return ""
    marge_g, marge_d = 54, 24
    haut, bas = 30 + (22 if legende else 0), 46
    piste_x = largeur - marge_g - marge_d
    piste_y = hauteur - haut - bas
    tous = points + list(reperes or [])
    xmin, xmax = min(p["x"] for p in tous), max(p["x"] for p in tous)
    ymin, ymax = min(p["y"] for p in tous), max(p["y"] for p in tous)
    mx, my = (xmax - xmin) * 0.06 or 0.1, (ymax - ymin) * 0.08 or 0.1
    xmin, xmax, ymin, ymax = xmin - mx, xmax + mx, ymin - my, ymax + my

    def px(v):
        return marge_g + piste_x * (v - xmin) / ((xmax - xmin) or 1)

    def py(v):
        return haut + piste_y * (1 - (v - ymin) / ((ymax - ymin) or 1))

    fig = Figure(largeur, hauteur, titre, description)
    # Les axes ne se tracent que si zero est VISIBLE. Sur un plan factoriel il
    # l'est toujours -- c'est le profil moyen. Sur un nuage a coordonnees
    # quelconques, il peut etre tres loin du cadre, et la ligne partait alors a
    # mille pixels hors du viewBox.
    if xmin <= 0 <= xmax:
        fig.ajouter(f'<line x1="{px(0):.1f}" y1="{haut}" x2="{px(0):.1f}" '
                    f'y2="{hauteur - bas}" stroke="{GRILLE}" stroke-width="1"/>')
    if ymin <= 0 <= ymax:
        fig.ajouter(f'<line x1="{marge_g}" y1="{py(0):.1f}" x2="{largeur - marge_d}" '
                    f'y2="{py(0):.1f}" stroke="{GRILLE}" stroke-width="1"/>')
    else:
        # Sans axe a l'origine, il faut une graduation : sinon le nuage flotte
        # sans echelle lisible.
        for v in (ymin + (ymax - ymin) * k / 4 for k in range(5)):
            fig.ajouter(f'<line x1="{marge_g}" y1="{py(v):.1f}" '
                        f'x2="{largeur - marge_d}" y2="{py(v):.1f}" '
                        f'stroke="{GRILLE}" stroke-width="1" opacity="0.6"/>')
            fig.ajouter(_texte(marge_g - 8, py(v), f"{v:.0f}", ancre="end",
                               couleur=ENCRE_DOUCE, taille=11))
    if not (xmin <= 0 <= xmax):
        for v in (xmin + (xmax - xmin) * k / 4 for k in range(5)):
            fig.ajouter(_texte(px(v), hauteur - bas + 18, f"{v:.0f}",
                               ancre="middle", couleur=ENCRE_DOUCE, taille=11))

    for p in points:
        teinte = p.get("couleur") or SERIES[0]
        fig.ajouter(f'<g class="marque"><title>{e(p.get("detail") or "")}</title>'
                    f'<circle cx="{px(p["x"]):.1f}" cy="{py(p["y"]):.1f}" r="3.2" '
                    f'fill="{teinte}" opacity="0.42"/></g>')

    for r in (reperes or []):
        fig.ajouter(f'<circle cx="{px(r["x"]):.1f}" cy="{py(r["y"]):.1f}" r="3" '
                    f'fill="{SURFACE}" stroke="{ENCRE}" stroke-width="1.6"/>')
        fig.ajouter(_texte(px(r["x"]) + 7, py(r["y"]) - 1, r["libelle"],
                           couleur=ENCRE, taille=11))

    if x_titre:
        fig.ajouter(_texte(largeur - marge_d, hauteur - 16, x_titre, ancre="end",
                           couleur=ENCRE_DOUCE, taille=11.5))
    if y_titre:
        fig.ajouter(_texte(marge_g, haut - 10, y_titre, couleur=ENCRE_DOUCE,
                           taille=11.5))
    if legende:
        x = marge_g
        for nom, teinte in legende:
            fig.ajouter(f'<circle cx="{x + 5}" cy="13" r="4.5" fill="{teinte}"/>')
            fig.ajouter(_texte(x + 15, 14, nom, couleur=ENCRE, taille=12))
            x += 30 + 7.2 * len(nom)
    return fig.rendu()


def pentes(lignes, *, titre, description, gauche, droite, largeur=700,
           hauteur_ligne=25, marge=176):
    """Deux classements, et le trait qui relie la meme personne de l'un a l'autre.

    Un tableau a deux colonnes de rangs se lit mal : l'oeil doit apparier les
    lignes lui-meme. Ici la pente FAIT le travail -- une montee se voit sans
    lire un seul chiffre.

    `lignes` : [{"libelle":…, "rang_gauche": int, "rang_droite": int, "couleur":…}]
    """
    lignes = [l for l in lignes if l.get("rang_gauche") and l.get("rang_droite")]
    if not lignes:
        return ""
    haut, bas = 46, 30
    n = len(lignes)
    hauteur = haut + bas + n * hauteur_ligne
    xg, xd = marge, largeur - marge
    rmax = max(max(l["rang_gauche"], l["rang_droite"]) for l in lignes)
    rmin = min(min(l["rang_gauche"], l["rang_droite"]) for l in lignes)

    def y(rang):
        return haut + (hauteur - haut - bas) * (rang - rmin) / ((rmax - rmin) or 1)

    fig = Figure(largeur, hauteur, titre, description)
    fig.ajouter(_texte(xg, haut - 20, gauche, ancre="end", couleur=ENCRE_DOUCE,
                       taille=11.5, gras=True))
    fig.ajouter(_texte(xd, haut - 20, droite, couleur=ENCRE_DOUCE,
                       taille=11.5, gras=True))

    for l in lignes:
        monte = l["rang_droite"] < l["rang_gauche"]
        teinte = l.get("couleur") or (SERIES[2] if monte else SERIES[1])
        plat = l["rang_droite"] == l["rang_gauche"]
        if plat:
            teinte = ENCRE_MUETTE
        yg, yd = y(l["rang_gauche"]), y(l["rang_droite"])
        info = (f'{l["libelle"]} : {l["rang_gauche"]}\u1d49 au classement brut, '
                f'{l["rang_droite"]}\u1d49 une fois corrige')
        fig.ajouter(f'<g class="marque"><title>{e(info)}</title>'
                    f'<line x1="{xg + 6}" y1="{yg:.1f}" x2="{xd - 6}" y2="{yd:.1f}" '
                    f'stroke="{teinte}" stroke-width="1.8" opacity="0.75"/>'
                    f'<circle cx="{xg + 6}" cy="{yg:.1f}" r="3" fill="{teinte}"/>'
                    f'<circle cx="{xd - 6}" cy="{yd:.1f}" r="3" fill="{teinte}"/>'
                    f'</g>')
        fig.ajouter(_texte(xg - 6, yg, f'{l["rang_gauche"]}. {l["libelle"]}',
                           ancre="end", couleur=ENCRE, taille=11))
        fig.ajouter(_texte(xd + 6, yd, f'{l["rang_droite"]}. {l["libelle"]}',
                           couleur=ENCRE, taille=11))
    return fig.rendu()


def frise(lignes, *, titre, description, debut, fin, largeur=980,
          hauteur_ligne=16, marge_gauche=214, legende=None):
    """Une barre par saison, posee sur un axe de temps commun.

    Les creux se lisent aussi bien que les barres : une annee sans diffusion
    saute aux yeux, ce qu'une simple liste ordonnee ne montrerait pas.

    `lignes` : [{"libelle":…, "debut": annee reelle, "fin":…, "couleur":…}]
    """
    lignes = [l for l in lignes if l.get("debut") is not None]
    if not lignes:
        return ""
    haut = 32 + (22 if legende else 0)
    bas, droite = 30, 20
    hauteur = haut + bas + len(lignes) * hauteur_ligne
    piste = largeur - marge_gauche - droite
    etendue = (fin - debut) or 1

    def px(v):
        return marge_gauche + piste * (v - debut) / etendue

    fig = Figure(largeur, hauteur, titre, description)
    an = debut - debut % 5
    while an <= fin:
        if an >= debut:
            fig.ajouter(f'<line x1="{px(an):.1f}" y1="{haut - 10}" x2="{px(an):.1f}" '
                        f'y2="{hauteur - bas + 4}" stroke="{GRILLE}" stroke-width="1"/>')
            fig.ajouter(_texte(px(an), haut - 18, str(an), ancre="middle",
                               couleur=ENCRE_DOUCE, taille=11))
        an += 5

    for i, l in enumerate(lignes):
        y = haut + i * hauteur_ligne + 2
        x1, x2 = px(l["debut"]), px(l.get("fin") or l["debut"])
        teinte = l.get("couleur") or SERIES[0]
        fig.ajouter(f'<g class="marque"><title>{e(l.get("detail") or l["libelle"])}</title>'
                    f'<rect x="{x1:.1f}" y="{y:.1f}" width="{max(3.0, x2 - x1):.1f}" '
                    f'height="{hauteur_ligne - 5:.1f}" rx="2" fill="{teinte}" '
                    f'stroke="{SURFACE}" stroke-width="1"/></g>')
        fig.ajouter(_texte(marge_gauche - 10, y + (hauteur_ligne - 5) / 2, l["libelle"],
                           ancre="end", couleur=ENCRE, taille=10.5))

    if legende:
        x = marge_gauche
        for nom, teinte in legende:
            fig.ajouter(f'<rect x="{x}" y="8" width="11" height="11" rx="2" fill="{teinte}"/>')
            fig.ajouter(_texte(x + 17, 14, nom, couleur=ENCRE, taille=12))
            x += 26 + 7.2 * len(nom)
    return fig.rendu()
