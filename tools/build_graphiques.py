#!/usr/bin/env python3
"""Ecrit les figures du site dans _includes/graphiques/, a partir de stats.yml.

    tools/atelier python3 tools/build_graphiques.py
"""
import os
import sys

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RACINE, "tools"))
from graphiques import (barres_horizontales, colonnes, courbes, ecrire,  # noqa: E402
                        SERIES, TRIBUS)

NOM_COULEUR = {"jaune": "Jaune", "rouge": "Rouge", "bleu": "Bleu", "vert": "Vert",
               "orange": "Orange", "violet": "Violet", "noir": "Noire", "blanc": "Blanche"}


def main():
    stats = yaml.safe_load(open(os.path.join(RACINE, "_data", "stats.yml"), encoding="utf-8"))
    print("figures ecrites :")

    # --- vainqueurs -------------------------------------------------------
    v = stats["vainqueurs"]
    ecrire("vainqueurs-age.svg", colonnes(
        [{"libelle": t["tranche"].replace(" ans", "").replace(" et plus", "+"),
          "valeur": t["effectif"],
          "detail": f'{t["tranche"]} : {t["effectif"]} vainqueurs, {t["part"]} % du total'}
         for t in v["par_tranche"]],
        titre="Âge des vainqueurs au moment du sacre",
        description="Nombre de vainqueurs par tranche d'âge, saisons classiques.",
        couleur=SERIES[0], hauteur=280))

    ecrire("vainqueurs-metier.svg", barres_horizontales(
        [{"libelle": m["libelle"], "valeur": m["effectif"],
          "detail": f'{m["libelle"]} : {m["effectif"]} victoires ({m["part"]} % des vainqueurs)'}
         for m in v["par_metier"][:9]],
        titre="Métier des vainqueurs",
        description="Nombre de victoires par famille de métiers, saisons classiques.",
        couleur=SERIES[0]))

    # --- tribus -----------------------------------------------------------
    couleurs = [c for c in stats["couleurs"] if c["effectif"] >= 8]
    ecrire("tribus-victoires.svg", barres_horizontales(
        [{"libelle": NOM_COULEUR.get(c["couleur"], c["couleur"]), "valeur": c["victoires"],
          "couleur": TRIBUS.get(c["couleur"]),
          "detail": f'Tribu {NOM_COULEUR.get(c["couleur"], c["couleur"]).lower()} : '
                    f'{c["victoires"]} victoires pour {c["effectif"]} aventuriers'}
         for c in sorted(couleurs, key=lambda x: -x["victoires"])],
        titre="Victoires finales par couleur de tribu initiale",
        description="Nombre de vainqueurs selon la couleur de leur tribu de départ.",
        marge_gauche=110))

    ecrire("tribus-survie.svg", barres_horizontales(
        [{"libelle": NOM_COULEUR.get(c["couleur"], c["couleur"]),
          "valeur": c["survie_moyenne"], "couleur": TRIBUS.get(c["couleur"]),
          "detail": f'Tribu {NOM_COULEUR.get(c["couleur"], c["couleur"]).lower()} : '
                    f'{c["survie_moyenne"]} % de la saison en moyenne '
                    f'({c["effectif"]} aventuriers)'}
         for c in sorted(couleurs, key=lambda x: -(x["survie_moyenne"] or 0))],
        titre="Durée de survie moyenne par couleur de tribu",
        description="Part de la saison passée dans le jeu, en pourcentage, par couleur.",
        unite=" %", marge_gauche=110, valeur_max=100))

    # --- metiers ----------------------------------------------------------
    metiers = [m for m in stats["metiers"] if m["effectif"] >= 15]
    ecrire("metiers-finale.svg", barres_horizontales(
        [{"libelle": m["libelle"], "valeur": m["taux_finale"],
          "detail": f'{m["libelle"]} : {m["finales"]} finales sur {m["effectif"]} '
                    f'aventuriers, soit {m["taux_finale"]} %'}
         for m in sorted(metiers, key=lambda x: -(x["taux_finale"] or 0))],
        titre="Accès à la finale selon le métier",
        description="Part des aventuriers de chaque famille de métiers ayant atteint la finale.",
        unite=" %", couleur=SERIES[2]))

    ecrire("metiers-casting.svg", barres_horizontales(
        [{"libelle": m["libelle"], "valeur": m["effectif"],
          "detail": f'{m["libelle"]} : {m["effectif"]} aventuriers, '
                    f'{m["part_du_casting"]} % du casting'}
         for m in sorted(stats["metiers"], key=lambda x: -x["effectif"])[:10]],
        titre="Composition sociale du casting",
        description="Nombre d'aventuriers par famille de métiers.",
        couleur=SERIES[1]))

    # --- age --------------------------------------------------------------
    ecrire("age-survie.svg", colonnes(
        [{"libelle": a["tranche"].replace(" ans", "").replace(" et plus", "+"),
          "valeur": a["survie_moyenne"],
          "detail": f'{a["tranche"]} : {a["survie_moyenne"]} % de la saison en moyenne '
                    f'({a["effectif"]} aventuriers)'}
         for a in stats["age"]],
        titre="Survie moyenne selon l'âge",
        description="Part de la saison passée dans le jeu, par tranche d'âge.",
        unite=" %", couleur=SERIES[0], hauteur=280))

    ecrire("age-finale.svg", colonnes(
        [{"libelle": a["tranche"].replace(" ans", "").replace(" et plus", "+"),
          "valeur": a["taux_finale"],
          "detail": f'{a["tranche"]} : {a["finales"]} finales sur {a["effectif"]}, '
                    f'soit {a["taux_finale"]} %'}
         for a in stats["age"]],
        titre="Accès à la finale selon l'âge",
        description="Part des aventuriers de chaque tranche d'âge ayant atteint la finale.",
        unite=" %", couleur=SERIES[2], hauteur=280))

    ecrire("age-casting.svg", colonnes(
        [{"libelle": a["tranche"].replace(" ans", "").replace(" et plus", "+"),
          "valeur": a["effectif"],
          "detail": f'{a["tranche"]} : {a["effectif"]} aventuriers, '
                    f'{a["part_du_casting"]} % du casting'}
         for a in stats["age"]],
        titre="Composition du casting par âge",
        description="Nombre d'aventuriers par tranche d'âge.",
        couleur=SERIES[1], hauteur=280))

    # --- genre ------------------------------------------------------------
    dec = stats["genre"]["par_decennie"]
    ecrire("genre-survie.svg", courbes(
        [{"nom": "Femmes", "couleur": SERIES[4],
          "valeurs": [d.get("survie_femmes") for d in dec]},
         {"nom": "Hommes", "couleur": SERIES[0],
          "valeurs": [d.get("survie_hommes") for d in dec]}],
        [d["decennie"] for d in dec],
        titre="Longévité comparée des femmes et des hommes",
        description="Part moyenne de la saison passée dans le jeu, par décennie.",
        unite=" %"))

    g = stats["genre"]["resume"]
    ecrire("genre-finale.svg", barres_horizontales(
        [{"libelle": x["libelle"], "valeur": x["taux_finale"],
          "couleur": SERIES[4] if x["genre"] == "f" else SERIES[0],
          "detail": f'{x["libelle"]} : {x["finales"]} finales sur {x["effectif"]}, '
                    f'soit {x["taux_finale"]} %'}
         for x in g],
        titre="Accès à la finale selon le sexe",
        description="Part des aventurières et des aventuriers ayant atteint la finale.",
        unite=" %", marge_gauche=110))

    # --- sorties ----------------------------------------------------------
    ecrire("sorties-repartition.svg", barres_horizontales(
        [{"libelle": s["libelle"], "valeur": s["part"],
          "detail": f'{s["libelle"]} : {s["effectif"]} aventuriers, {s["part"]} %'}
         for s in stats["sorties"]["repartition"]],
        titre="Comment on quitte Koh-Lanta",
        description="Répartition des motifs de sortie, saisons classiques.",
        unite=" %", couleur=SERIES[0], marge_gauche=210))

    d2 = stats["sorties"]["par_decennie"]
    ecrire("sorties-decennie.svg", courbes(
        [{"nom": "Conseil", "couleur": SERIES[0], "valeurs": [x["conseil"] for x in d2]},
         {"nom": "Abandons", "couleur": SERIES[1], "valeurs": [x["abandons"] for x in d2]},
         {"nom": "Ambassadeurs", "couleur": SERIES[2],
          "valeurs": [x["ambassadeurs"] for x in d2]}],
        [x["decennie"] for x in d2],
        titre="Ce qui fait sortir, décennie après décennie",
        description="Part de chaque motif de sortie, par décennie.",
        unite=" %"))

    # --- saisons ----------------------------------------------------------
    classiques = [s for s in stats["saisons"] if not s["speciale"] and not s["en_cours"]]
    ecrire("saisons-effectif.svg", colonnes(
        [{"libelle": str(s["numero"]), "valeur": s["effectif"],
          "detail": f'Saison {s["numero"]} — {s["titre"]} ({s["annee"]}) : '
                    f'{s["effectif"]} aventuriers'}
         for s in classiques],
        titre="Taille du casting, saison après saison",
        description="Nombre d'aventuriers au départ de chaque saison classique.",
        couleur=SERIES[0], largeur=760, hauteur=300, etiquettes_valeurs=False))

    ecrire("saisons-age.svg", courbes(
        [{"nom": "Âge moyen du casting", "couleur": SERIES[0],
          "valeurs": [s["age_moyen"] for s in classiques]}],
        [str(s["numero"]) for s in classiques],
        titre="Âge moyen du casting, saison après saison",
        description="Moyenne d'âge au départ de chaque saison classique.",
        unite=" ans", largeur=760, legende=False))

    ecrire("saisons-femmes.svg", courbes(
        [{"nom": "Part de femmes", "couleur": SERIES[4],
          "valeurs": [s["part_femmes"] for s in classiques]}],
        [str(s["numero"]) for s in classiques],
        titre="Part de femmes dans le casting",
        description="Pourcentage de femmes au départ de chaque saison classique.",
        unite=" %", largeur=760, legende=False))

    # --- conseils ---------------------------------------------------------
    c = stats["conseils"]
    if c.get("vote_par_genre"):
        libelle = {"f": "une femme", "h": "un homme"}
        ecrire("conseils-genre.svg", barres_horizontales(
            [{"libelle": f'{libelle[x["votant"]]} → {libelle[x["cible"]]}',
              "valeur": x["part"],
              "detail": f'{x["effectif"]} bulletins, soit {x["part"]} % '
                        f'des voix des conseils complets'}
             for x in c["vote_par_genre"]],
            titre="Qui vote contre qui",
            description="Répartition des bulletins selon le sexe du votant et de sa cible.",
            unite=" %", couleur=SERIES[6], marge_gauche=210))
    return 0


if __name__ == "__main__":
    sys.exit(main())
