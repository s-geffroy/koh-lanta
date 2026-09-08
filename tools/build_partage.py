#!/usr/bin/env python3
"""Fabrique l'image de partage du site (og:image).

POURQUOI. Le depot ne contenait aucune image : tout le visuel est en SVG
inline. Consequence invisible depuis le site lui-meme -- partage sur un
reseau, dans une messagerie ou dans un salon d'equipe, chaque page sortait
sans vignette, avec la seule ligne de texte. Une carte suffit ; elle est
la meme pour tout le site, ce qui est le bon compromis quand il y a 599 pages
et aucune photo.

    tools/atelier python3 tools/build_partage.py

LA POLICE N'EST PAS CELLE DU SITE. Fraunces et IBM Plex Mono sont chargees
depuis Google Fonts par le navigateur ; le conteneur ne les a pas, et rien
n'autorise a les installer sur l'hote. La carte est donc composee en DejaVu,
livree avec matplotlib. C'est une vignette de partage, pas une page : la forme
et les deux couleurs portent l'identite, pas la graisse des terminaisons.

Les chiffres ne sont pas ecrits ici : ils sont lus dans `_data/stats.yml`,
pour qu'une carte perimee soit impossible.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                              # noqa: E402
from matplotlib.patches import Polygon, Rectangle            # noqa: E402
import yaml                                                  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "assets", "partage.png")

# Les jetons de assets/css/style.scss, recopies : la feuille de style est du
# Sass compile par GitHub, elle n'est pas lisible d'ici sans l'interpreter.
SABLE = "#edefe9"
ENCRE = "#101a18"
ENCRE_DOUCE = "#4c5a56"
JAUNE = "#eda100"
ROUGE = "#e34948"

LARGEUR, HAUTEUR = 1200, 630
# Marge droite sous laquelle une ligne ne doit jamais descendre.
MARGE = 72


def texte(ax, fig, x, y, contenu, taille, couleur, **kw):
    """Ecrit, puis retrecit tant que la ligne deborde de la carte.

    La premiere version debordait de 51 pixels a droite : « et ce que les
    chiffres en disen ». Rien ne le signale -- la figure est enregistree sans
    broncher, et la coupe ne se voit qu'en regardant l'image. On mesure donc.
    """
    t = ax.text(x, y, contenu, color=couleur, fontsize=taille,
                va="baseline", ha="left", **kw)
    rendu = fig.canvas.get_renderer()
    while taille > 8:
        largeur = t.get_window_extent(renderer=rendu).x1
        if largeur <= LARGEUR - MARGE:
            return t
        taille -= 1
        t.set_fontsize(taille)
    return t


def main():
    with open(os.path.join(RACINE, "_data", "stats.yml"), encoding="utf-8") as f:
        g = yaml.safe_load(f)["general"]

    fig = plt.figure(figsize=(LARGEUR / 100, HAUTEUR / 100), dpi=100)
    fig.patch.set_facecolor(SABLE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, LARGEUR)
    ax.set_ylim(0, HAUTEUR)
    ax.axis("off")
    ax.set_facecolor(SABLE)
    fig.canvas.draw()

    # Le bandeau du haut : jaune et rouge a parts STRICTEMENT egales. Cette
    # egalite est le resultat le plus repete du site (douze victoires chacune) ;
    # elle n'est pas un choix graphique et ne se reamenage pas.
    ax.add_patch(Rectangle((0, HAUTEUR - 16), LARGEUR / 2, 16, color=JAUNE, lw=0))
    ax.add_patch(Rectangle((LARGEUR / 2, HAUTEUR - 16), LARGEUR / 2, 16,
                           color=ROUGE, lw=0))

    # La torche de l'enseigne, meme decoupe que `.enseigne-totem` : pointe en
    # haut, deux bandeaux d'egale hauteur.
    x, bas, larg, haut = 96, 170, 62, 290
    pointe, epaule, milieu = bas + haut, bas + haut * 0.84, bas + haut / 2
    ax.add_patch(Polygon([(x + larg / 2, pointe), (x + larg, epaule),
                          (x + larg, bas), (x, bas), (x, epaule)],
                         closed=True, facecolor=JAUNE, lw=0))
    ax.add_patch(Polygon([(x, bas), (x + larg, bas), (x + larg, milieu),
                          (x, milieu)], closed=True, facecolor=ROUGE, lw=0))

    gauche = x + larg + 56
    texte(ax, fig, gauche, 372, "Koh-Lanta", 80, ENCRE, weight="bold")
    texte(ax, fig, gauche + 4, 312, "E N   C H I F F R E S", 23, ENCRE_DOUCE,
          family="monospace")
    texte(ax, fig, gauche, 236,
          f"{g['saisons_diffusees']} saisons  ·  {g['participations']} "
          f"participations  ·  {g['personnes']} aventuriers", 28, ENCRE)
    texte(ax, fig, gauche, 186,
          "Chaque épreuve, chaque bulletin de vote, et ce qu’ils disent du jeu.",
          21, ENCRE_DOUCE)

    fig.savefig(SORTIE, facecolor=SABLE)
    plt.close(fig)
    print(f"ecrit : {SORTIE}  ({os.path.getsize(SORTIE)} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
