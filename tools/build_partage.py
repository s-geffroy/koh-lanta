#!/usr/bin/env python3
"""Fabrique les images de partage du site (og:image).

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

Les chiffres ne sont pas ecrits ici : ils sont lus dans `_data/`, pour qu'une
carte perimee soit impossible.

POURQUOI UNE CARTE PAR FICHE, ET CE QUE CA PESE. Une seule carte pour 621
pages donnait le meme apercu au partage de « Claude Dartois » et a celui de
« Palawan ». Une carte par fiche fait 584 fichiers -- d'ou la quantification a
32 couleurs, qui les ramene de 31 a 8 Ko piece, soit 4 Mo pour l'ensemble. Une
carte identique n'est PAS reecrite : sans cela, chaque execution ferait 584
fichiers modifies dans Git pour zero changement reel.
"""
import argparse
import collections
import os
import sys

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                              # noqa: E402
from matplotlib.patches import Polygon, Rectangle            # noqa: E402
from PIL import Image                                        # noqa: E402
import yaml                                                  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_fiches import ordinal                             # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "assets", "partage.png")
DOSSIER = os.path.join(RACINE, "assets", "partage")
DATA = os.path.join(RACINE, "_data")
# 32 couleurs suffisent a une carte plate : le texte reste net et le
# fichier passe de 31 a 8 Ko. Au-dela, on paie sans rien gagner a l'oeil.
COULEURS = 32

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


def fond():
    """La toile commune : le bandeau a parts egales et la torche de l'enseigne."""
    fig = plt.figure(figsize=(LARGEUR / 100, HAUTEUR / 100), dpi=100)
    fig.patch.set_facecolor(SABLE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, LARGEUR)
    ax.set_ylim(0, HAUTEUR)
    ax.axis("off")
    ax.set_facecolor(SABLE)
    fig.canvas.draw()

    # Jaune et rouge a parts STRICTEMENT egales. Cette egalite est le resultat
    # le plus repete du site (douze victoires chacune) ; elle n'est pas un
    # choix graphique et ne se reamenage pas.
    ax.add_patch(Rectangle((0, HAUTEUR - 16), LARGEUR / 2, 16, color=JAUNE, lw=0))
    ax.add_patch(Rectangle((LARGEUR / 2, HAUTEUR - 16), LARGEUR / 2, 16,
                           color=ROUGE, lw=0))

    # La torche de l'enseigne, meme decoupe que `.enseigne-totem`.
    x, bas, larg, haut = 96, 170, 62, 290
    pointe, epaule, milieu = bas + haut, bas + haut * 0.84, bas + haut / 2
    ax.add_patch(Polygon([(x + larg / 2, pointe), (x + larg, epaule),
                          (x + larg, bas), (x, bas), (x, epaule)],
                         closed=True, facecolor=JAUNE, lw=0))
    ax.add_patch(Polygon([(x, bas), (x + larg, bas), (x + larg, milieu),
                          (x, milieu)], closed=True, facecolor=ROUGE, lw=0))
    return fig, ax, x + larg + 56


def carte(chemin, titre, oeil, ligne, note, rapport, taille_titre=64):
    """Compose une carte et ne l'ecrit QUE si elle a change.

    Reecrire 584 fichiers identiques a chaque execution remplirait l'historique
    de Git de bruit -- et rendrait illisible le seul commit ou une carte a
    vraiment bouge.
    """
    fig, ax, gauche = fond()
    texte(ax, fig, gauche + 4, 430, oeil, 21, ENCRE_DOUCE, family="monospace")
    texte(ax, fig, gauche, 340, titre, taille_titre, ENCRE, weight="bold")
    texte(ax, fig, gauche, 268, ligne, 27, ENCRE)
    if note:
        texte(ax, fig, gauche, 214, note, 21, ENCRE_DOUCE)

    tampon = io.BytesIO()
    fig.savefig(tampon, facecolor=SABLE, format="png")
    plt.close(fig)
    tampon.seek(0)
    image = Image.open(tampon).convert("RGB").quantize(colors=COULEURS,
                                                       method=Image.MEDIANCUT)
    sortie = io.BytesIO()
    image.save(sortie, format="PNG", optimize=True)
    octets = sortie.getvalue()

    ancien = None
    if os.path.exists(chemin):
        with open(chemin, "rb") as f:
            ancien = f.read()
    if ancien != octets:
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "wb") as f:
            f.write(octets)
        rapport["ecrites"] += 1
    rapport["total"] += 1


def cartes_des_aventuriers(fiches, joueurs_classes, rapport):
    for cid, e in sorted((fiches.get("aventuriers") or {}).items()):
        parts = sorted(e["participations"], key=lambda p: p["annee"])
        if len(parts) == 1:
            ligne = f"Koh-Lanta {parts[0]['titre']} ({parts[0]['annee']})"
        else:
            ligne = (f"{len(parts)} saisons de Koh-Lanta, "
                     f"de {parts[0]['annee']} à {parts[-1]['annee']}")
        note = None
        if e.get("rang") and joueurs_classes:
            note = (f"{ordinal(e['rang'])} sur {joueurs_classes} "
                    f"au classement des aventuriers")
        carte(os.path.join(DOSSIER, "aventuriers", cid + ".png"),
              e["nom"], "LES AVENTURIERS", ligne, note, rapport)


def cartes_des_saisons(fiches, rapport):
    for cid, s in sorted((fiches.get("saisons") or {}).items()):
        morceaux = [f"{s['effectif']} aventuriers"]
        if s.get("duree_jours"):
            morceaux.append(f"{s['duree_jours']} jours")
        if s.get("conseils"):
            morceaux.append(f"{s['conseils']} conseils")
        noms = [v["nom"] for v in (s.get("vainqueurs") or [])]
        note = f"Victoire de {' et '.join(noms)}" if noms else None
        oeil = f"KOH-LANTA {s['annee']}"
        carte(os.path.join(DOSSIER, "saisons", cid + ".png"),
              s["titre"], oeil, "  ·  ".join(morceaux), note, rapport)


def cartes_des_epreuves(epreuves, rapport):
    for cid, e in sorted((epreuves.get("epreuves") or {}).items()):
        morceaux = [f"{e['apparitions']} fois courue",
                    f"{len(e['editions'])} éditions"]
        r = e.get("record")
        note = (f"Record : {r['nom']}, {r['victoires']} victoires"
                if r and r["victoires"] > 1 else None)
        carte(os.path.join(DOSSIER, "epreuves", cid + ".png"),
              e["nom"], "LES ÉPREUVES", "  ·  ".join(morceaux), note, rapport)


def lire(nom):
    chemin = os.path.join(DATA, nom + ".yml")
    if not os.path.exists(chemin):
        return {}
    with open(chemin, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tout", action="store_true",
                    help="fabrique aussi une carte par fiche (584 fichiers)")
    a = ap.parse_args()

    stats = lire("stats")
    g = stats["general"]
    rapport = collections.Counter()

    fig, ax, gauche = fond()
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

    if not a.tout:
        print("carte generale seule (--tout pour les 584 fiches)")
        return 0

    fiches = lire("fiches")
    cartes_des_aventuriers(fiches,
                           (stats.get("classement") or {}).get("joueurs_classes"),
                           rapport)
    cartes_des_saisons(fiches, rapport)
    cartes_des_epreuves(lire("epreuves_fiches"), rapport)
    poids = sum(os.path.getsize(os.path.join(b, f))
                for b, _, fs in os.walk(DOSSIER) for f in fs)
    print(f"cartes : {rapport['total']} ({rapport['ecrites']} ecrites, "
          f"{rapport['total'] - rapport['ecrites']} inchangees), "
          f"{poids // 1024} Ko au total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
