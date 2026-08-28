#!/usr/bin/env python3
"""Ecrit les figures du site dans _includes/graphiques/, a partir de stats.yml.

    tools/atelier python3 tools/build_graphiques.py
"""
import os
import sys

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RACINE, "tools"))
from graphiques import (arcs, barres_horizontales, barres_groupees,  # noqa: E402
                        colonnes, courbes, distribution_nulle, ecrire, foret,
                        frise, halteres, nuage, peigne, pentes,
                        petits_multiples, plan, ENCRE_MUETTE, SERIES, TRIBUS, survie)

NOM_COULEUR = {"jaune": "Jaune", "rouge": "Rouge", "bleu": "Bleu", "vert": "Vert",
               "orange": "Orange", "violet": "Violet", "noir": "Noire", "blanc": "Blanche"}


def _lire(nom):
    with open(os.path.join(RACINE, "_data", nom), encoding="utf-8") as f:
        return yaml.safe_load(f)


# Les noms de variables des modeles sont des identifiants (« metier:sport ») ;
# ce qui s'affiche doit etre du francais.
LISIBLE = {"metier:": "métier : ", "couleur:": "bandeau : ",
           "age_centre_carre": "âge (écart au centre, au carré)",
           "age": "âge", "annee": "année", "taille_casting": "taille du casting"}


def _lisible(nom):
    for brut, propre in LISIBLE.items():
        if nom.startswith(brut) and brut.endswith(":"):
            return propre + nom[len(brut):].replace("_", " ")
    return LISIBLE.get(nom, nom.replace("_", " "))


def figure_survie(stats):
    """La figure d'ouverture : les deux bandeaux, l'un sur l'autre."""
    b = stats.get("survie_bandeau") or {}
    if not b.get("series"):
        return
    ecrire("accueil-survie.svg", survie(
        b["series"], b["toutes"], jour_max=b["jour_max"], mediane=b["mediane"],
        titre="Jaune et rouge tiennent exactement la même distance",
        description=(
            f'Part des aventuriers encore en jeu, jour par jour, sur les saisons '
            f'classiques. La courbe jaune et la courbe rouge se confondent : les '
            f'deux bandeaux ont la même médiane, le jour {b["mediane"]}.'),
        note=f'{b["effectif"]} participations, saisons classiques achevées.'))


def figure_peigne():
    """La figure d'ouverture : un trait par aventurier, trie par duree tenue.

    Elle ne passe pas par stats.yml : elle a besoin des participations une par
    une, pas d'un agregat. C'est le principe meme de la figure.
    """
    participations = _lire("participations.yml")
    traits = sorted(
        ({"jour": p["jour_sortie"],
          "couleur": TRIBUS.get(p.get("couleur"), "var(--encre-muette)")}
         for p in participations if p.get("jour_sortie")),
        key=lambda t: t["jour"])

    jours = [t["jour"] for t in traits]
    mediane = jours[len(jours) // 2]

    # La legende ne nomme que les deux couleurs qui traversent le programme.
    # Les autres n'existent que sur les saisons a trois ou quatre tribus : les
    # citer une par une remplirait la ligne sans rien apprendre.
    legende = [("Tribu jaune", TRIBUS["jaune"]), ("Tribu rouge", TRIBUS["rouge"]),
               ("Autres tribus", "var(--encre-muette)")]

    ecrire("peigne-torches.svg", peigne(
        traits, jour_max=max(jours), mediane=mediane, legende=legende,
        titre=f"Les {len(traits)} aventuriers, du premier jour au dernier",
        description=(
            f"Un trait par participation, trié du plus court séjour au plus long. "
            f"La longueur du trait est le nombre de jours tenus, sa couleur celle "
            f"de la tribu de départ. La moitié des aventuriers quitte le jeu avant "
            f"le jour {mediane}.")))
    return len(traits), mediane, max(jours)


def main():
    stats = yaml.safe_load(open(os.path.join(RACINE, "_data", "stats.yml"), encoding="utf-8"))
    print("figures ecrites :")

    # --- la figure d'ouverture, et le peigne qui l'etait avant elle -------
    figure_survie(stats)
    n, mediane, jmax = figure_peigne()
    print(f"    (peigne : {n} traits, mediane jour {mediane}, maximum jour {jmax})")

    figures_ajoutees(stats)
    figure_epreuves_nommees()
    figure_prenoms()
    figure_nuage()
    figures_des_modeles(stats)

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
    # --- epreuves ---------------------------------------------------------
    e = stats.get("epreuves") or {}
    if e:
        ecrire("epreuves-ratios.svg", barres_horizontales(
            [{"libelle": x["personne"], "valeur": x["ratio"],
              "detail": f'{x["personne"]} ({x["titre"]}, {x["annee"]}) : '
                        f'{x["gagnees"]} victoires sur {x["disputees"]} épreuves '
                        f'individuelles disputées, soit {x["ratio"]} %'}
             for x in e["classement_ratio"][:12]],
            titre="Les meilleurs ratios d'épreuves individuelles",
            description="Part des épreuves individuelles remportées, "
                        "parmi celles disputées avant sa sortie.",
            unite=" %", couleur=SERIES[0], marge_gauche=200))

        ecrire("epreuves-cumuls.svg", barres_horizontales(
            [{"libelle": x["personne"], "valeur": x["victoires"],
              "detail": f'{x["personne"]} : {x["victoires"]} victoires '
                        f'individuelles, toutes saisons confondues'}
             for x in e["meilleurs_cumuls"][:10]],
            titre="Les plus grands nombres de victoires individuelles",
            description="Total des épreuves individuelles remportées, "
                        "toutes participations confondues.",
            couleur=SERIES[2], marge_gauche=200))

        ecrire("epreuves-metier.svg", barres_horizontales(
            [{"libelle": x["libelle"], "valeur": x["victoires_par_aventurier"],
              "detail": f'{x["libelle"]} : {x["victoires"]} victoires pour '
                        f'{x["aventuriers"]} aventuriers, soit '
                        f'{x["victoires_par_aventurier"]} par personne'}
             for x in e["par_metier"][:10] if x["victoires_par_aventurier"]],
            titre="Victoires d'épreuves par métier",
            description="Nombre moyen d'épreuves individuelles remportées "
                        "par aventurier de chaque famille de métiers.",
            couleur=SERIES[1]))

        ecrire("epreuves-age.svg", colonnes(
            [{"libelle": x["tranche"].replace(" ans", "").replace(" et plus", "+"),
              "valeur": x["victoires_par_aventurier"],
              "detail": f'{x["tranche"]} : {x["victoires"]} victoires pour '
                        f'{x["aventuriers"]} aventuriers'}
             for x in e["par_age"] if x["victoires_par_aventurier"]],
            titre="Victoires d'épreuves selon l'âge",
            description="Nombre moyen d'épreuves individuelles remportées "
                        "par aventurier, par tranche d'âge.",
            couleur=SERIES[0], hauteur=280))

        ecrire("epreuves-genre.svg", barres_horizontales(
            [{"libelle": x["libelle"], "valeur": x["victoires_par_aventurier"],
              "couleur": SERIES[4] if x["genre"] == "f" else SERIES[0],
              "detail": f'{x["libelle"]} : {x["victoires"]} victoires pour '
                        f'{x["aventuriers"]} aventuriers'}
             for x in e["par_genre"]],
            titre="Victoires d'épreuves selon le sexe",
            description="Nombre moyen d'épreuves individuelles remportées par aventurier.",
            marge_gauche=110))
    # --- colliers ---------------------------------------------------------
    co = stats.get("colliers") or {}
    if co:
        ecrire("colliers-issues.svg", barres_horizontales(
            [{"libelle": i["libelle"], "valeur": i["part_totale"],
              "detail": f'{i["libelle"]} : {i["effectif"]} colliers sur '
                        f'{co["colliers"]}, soit {i["part_totale"]} %'}
             for i in co["issues"]],
            titre="Le destin des colliers d'immunité",
            description="Ce que devient chaque collier caché dans le jeu.",
            unite=" %", couleur=SERIES[3], marge_gauche=250))

        ecrire("colliers-saison.svg", colonnes(
            [{"libelle": str(x["annee"]), "valeur": x["colliers"],
              "detail": f'{x["titre"]} ({x["annee"]}) : {x["colliers"]} colliers, '
                        f'{x["joues"]} joués, {x["voix_annulees"]} voix annulées'}
             for x in co["par_saison"]],
            titre="Nombre de colliers par saison",
            description="Colliers cachés dans le jeu, saison par saison.",
            couleur=SERIES[3], hauteur=280))

    # --- jeu social -------------------------------------------------------
    ind = stats.get("indicateurs") or {}
    if ind:
        if ind.get("fantomes_issue"):
            ecrire("fantomes-issue.svg", barres_groupees(
                [{"libelle": x["libelle"],
                  "valeurs": [x["part_fantomes"], x["part_endurants"]],
                  "details": [f'{x["effectif"]} des {ind["nb_fantomes"]} fantômes, '
                              f'soit {x["part_fantomes"]} %',
                              f'{x["part_endurants"]} % des {ind["endurants"]} '
                              f'aventuriers ayant traverse autant de conseils']}
                 for x in ind["fantomes_issue"]],
                [{"nom": "Les « fantômes »", "couleur": SERIES[0]},
                 {"nom": "Ceux qui ont tenu autant", "couleur": SERIES[1]}],
                titre="Ce que devient un aventurier que personne ne vise",
                description="Sort final des aventuriers n'ayant reçu aucune voix, "
                            "compare a ceux qui ont traverse autant de conseils "
                            "qu'eux -- et non a l'ensemble, qui melangerait le "
                            "fait de n'etre pas vise et celui d'aller loin.",
                unite=" %", marge_gauche=210))

        if ind.get("menace_par_sort"):
            ordre = ["elimine_conseil", "elimine_orientation", "elimine_poteaux",
                     "finaliste", "vainqueur"]
            lib = {"elimine_conseil": "Éliminé au conseil",
                   "elimine_orientation": "Éliminé à l'orientation",
                   "elimine_poteaux": "Éliminé aux poteaux",
                   "finaliste": "Finaliste", "vainqueur": "Vainqueur"}
            ecrire("menace-sort.svg", barres_horizontales(
                [{"libelle": lib[k], "valeur": ind["menace_par_sort"][k],
                  "detail": f'{lib[k]} : {ind["menace_par_sort"][k]} voix reçues '
                            f'par conseil en moyenne'}
                 for k in ordre if k in ind["menace_par_sort"]],
                titre="Être visé, et finir la saison",
                description="Nombre moyen de voix reçues par conseil, selon le sort final.",
                couleur=SERIES[7], marge_gauche=210))

        # --- indicateurs par saison
        sa = [x for x in ind.get("saisons", [])
              if not x["speciale"] and not x["en_cours"]]
        ecrire("saisons-domination.svg", colonnes(
            [{"libelle": str(x["numero"]), "valeur": x["domination_epreuves"],
              "detail": f'{x["titre"]} ({x["annee"]}) : indice {x["domination_epreuves"]}, '
                        f'meilleur total {x["victoires_du_meilleur"]} victoires'}
             for x in sa if x["domination_epreuves"]],
            titre="Un aventurier a-t-il écrasé les épreuves ?",
            description="Indice de concentration des victoires individuelles. "
                        "Plus il est haut, plus un seul aventurier a tout raflé.",
            couleur=SERIES[2], largeur=760, hauteur=300, etiquettes_valeurs=False))

        ecrire("saisons-dispersion.svg", colonnes(
            [{"libelle": str(x["numero"]), "valeur": x["dispersion_votes"],
              "detail": f'{x["titre"]} ({x["annee"]}) : dispersion {x["dispersion_votes"]} '
                        f'(0 = le camp vote d\'un bloc, 1 = chacun vote seul)'}
             for x in sa if x["dispersion_votes"]],
            titre="Le camp vote-t-il d'un bloc ?",
            description="Dispersion moyenne des bulletins au conseil, par saison.",
            couleur=SERIES[6], largeur=760, hauteur=300, etiquettes_valeurs=False))

        ecrire("saisons-abandon.svg", colonnes(
            [{"libelle": str(x["numero"]), "valeur": x["taux_abandon"],
              "detail": f'{x["titre"]} ({x["annee"]}) : {x["abandons"]} abandons '
                        f'sur {x["effectif"]} aventuriers'}
             for x in sa],
            titre="Le taux d'abandon, saison après saison",
            description="Part des aventuriers ayant abandonné, par saison.",
            unite=" %", couleur=SERIES[1], largeur=760, hauteur=300,
            etiquettes_valeurs=False))

        ecrire("saisons-tension.svg", colonnes(
            [{"libelle": str(x["numero"]), "valeur": x["tension_conseils"],
              "detail": f'{x["titre"]} ({x["annee"]}) : {x["tension_conseils"]} % '
                        f'des conseils se jouent à une voix près'}
             for x in sa if x["tension_conseils"]],
            titre="Des conseils serrés ou écrasants ?",
            description="Part des conseils où l'élimination s'est jouée à une voix près.",
            unite=" %", couleur=SERIES[0], largeur=760, hauteur=300,
            etiquettes_valeurs=False))
    return 0



def figures_ajoutees(stats):
    """Les figures de la seconde serie : revenants, risque, casting, prenoms.

    Elles sont ecrites a part pour que la premiere serie reste lisible, mais
    elles suivent exactement les memes regles : couleurs prises aux variables
    CSS, jamais en hexadecimal ; une etiquette de valeur sur chaque marque ;
    un <title> par marque pour l'infobulle native.
    """
    # ------------------------------------------------------------ revenants
    r = stats.get("revenants") or {}
    if r.get("paradoxe"):
        ecrire("revenants-paradoxe.svg", barres_horizontales(
            [{"libelle": x["libelle"], "valeur": x["survie_moyenne"],
              "couleur": SERIES[2] if i == 1 else (SERIES[1] if i == 2 else SERIES[0]),
              "detail": f'{x["libelle"]} : {x["effectif"]} aventures, '
                        f'{x["survie_moyenne"]} % de la saison en moyenne'}
             for i, x in enumerate(r["paradoxe"])],
            titre="Le paradoxe des revenants",
            description="Part moyenne de la saison passée en jeu, selon que "
                        "l'aventurier a été rappelé ou non, et selon qu'il "
                        "s'agit de sa première aventure ou d'un retour.",
            unite=" %", marge_gauche=260, largeur=880, valeur_max=100))

    g = (r.get("graphe") or {})
    if g.get("noeuds"):
        ecrire("revenants-graphe.svg", arcs(
            [{"nom": n["nom"].split()[0], "poids": n["degre"],
              "couleur": SERIES[0] if n["saisons"] == 2 else SERIES[1],
              "detail": f'{n["nom"]} — {n["saisons"]} saisons, '
                        f'{n["degre"]} aventuriers croisés parmi les revenants'}
             for n in g["noeuds"]],
            [{"de": a["de"], "vers": a["vers"], "poids": a["poids"]}
             for a in g["aretes"]],
            titre="Le petit monde des revenants",
            description="Chaque point est un aventurier revenu au moins deux "
                        "fois, rangé par ordre d'arrivée dans le programme. Un "
                        "arc relie deux personnes ayant partagé une saison.",
            legende=[("Deux saisons", SERIES[0]), ("Trois et plus", SERIES[1])],
            etiquettes=False, hauteur_etiquettes=16, hauteur_arc=190))

    if r.get("carrieres"):
        ecrire("revenants-carrieres.svg", barres_horizontales(
            [{"libelle": c["nom"], "valeur": c["jours"],
              "couleur": SERIES[0] if c["part_du_temps"] < 100 else SERIES[2],
              "detail": f'{c["nom"]} : {c["jours"]} jours sur '
                        f'{c["jours_possibles"]} possibles ({c["part_du_temps"]} %), '
                        f'en {c["saisons"]} saisons'}
             for c in r["carrieres"][:12]],
            titre="Les plus longues carrières",
            description="Jours de jeu cumulés sur toutes les participations. "
                        "En vert, ceux qui n'ont jamais été éliminés : ils ont "
                        "joué 100 % du temps possible.",
            unite=" j", marge_gauche=180, largeur=880))

    if r.get("duos"):
        ecrire("revenants-duos.svg", barres_horizontales(
            [{"libelle": f'{d["a"].split()[0]} et {d["b"].split()[0]}',
              "valeur": d["saisons"], "couleur": SERIES[3],
              "detail": f'{d["a"]} et {d["b"]} : {d["saisons"]} saisons ensemble'}
             for d in r["duos"][:10]],
            titre="Les duos qui n'en finissent pas",
            description="Nombre de saisons partagées par les mêmes deux personnes.",
            unite=" saisons", marge_gauche=210, largeur=880))

    # --------------------------------------------------------------- risque
    q = stats.get("risque") or {}
    if q.get("tranches"):
        # Le dernier palier vaut 100 % par construction -- tout le monde sort a
        # la fin. L'afficher ecraserait l'echelle et n'apprendrait rien.
        lot = [t for t in q["tranches"] if t["tranche"] < 100 and t["encore_en_jeu"] > 20]
        ecrire("risque-courbe.svg", colonnes(
            [{"libelle": f'{t["tranche"]} %', "valeur": t["risque"],
              "detail": f'À {t["tranche"]} % de la saison : {t["sortants"]} sortants '
                        f'sur {t["encore_en_jeu"]} encore en jeu'}
             for t in lot],
            titre="Le risque de sortir, selon l'avancement de la saison",
            description="Part des aventuriers encore en jeu qui quittent "
                        "l'aventure à ce moment-là. La finale est exclue : "
                        "tout le monde en sort.",
            unite=" %", couleur=SERIES[1], largeur=880, hauteur=300))

    if q.get("jours_les_plus_meurtriers"):
        ecrire("risque-jours.svg", barres_horizontales(
            [{"libelle": f'Jour {x["jour"]}', "valeur": x["sortants"],
              "couleur": SERIES[7],
              "detail": f'Jour {x["jour"]} : {x["sortants"]} départs'}
             for x in q["jours_les_plus_meurtriers"]],
            titre="Les jours qui font le plus de sortants",
            description="Nombre de départs par jour de jeu, saisons classiques.",
            marge_gauche=110, largeur=760))

    # ---------------------------------------------------- petits multiples
    ss = stats.get("survie_saisons") or []
    if ss:
        ecrire("saisons-petits-multiples.svg", petits_multiples(
            [{"titre": (f'{x["numero"]}' if x["numero"] and not x["speciale"]
                        else x["titre"][:13]),
              "sous_titre": str(x["annee"]),
              "valeurs": x["restants"],
              "couleur": SERIES[4] if x["speciale"] else SERIES[0],
              "detail": f'{x["titre"]} ({x["annee"]}) — {x["effectif"]} aventuriers'}
             for x in ss],
            titre="Les trente-trois saisons, à la même échelle",
            description="Part des aventuriers encore en jeu, du premier au "
                        "dernier jour de chaque saison. Les axes sont "
                        "identiques partout : les courbes se comparent "
                        "directement. En rose, les éditions spéciales."))

    # -------------------------------------------------------------- casting
    c = stats.get("casting") or {}
    if c.get("etendues"):
        ecrire("casting-ages.svg", halteres(
            [{"libelle": f'{x["titre"]} ({x["annee"]})',
              "min": x["min"], "median": x["median"], "max": x["max"],
              "couleur": SERIES[4] if x["speciale"] else SERIES[0],
              "detail": f'{x["titre"]} ({x["annee"]}) : de {x["min"]} à '
                        f'{x["max"]} ans, médiane {x["median"]}'}
             for x in c["etendues"]],
            titre="L'âge du casting, saison par saison",
            description="Du plus jeune au plus âgé de chaque casting ; le point "
                        "creux marque l'âge médian. Le nombre à droite est "
                        "l'écart entre les deux extrêmes.",
            unite=" ans", largeur=880, marge_gauche=230,
            legende=[("Édition classique", SERIES[0]), ("Édition spéciale", SERIES[4])]))

    if c.get("generations"):
        ecrire("casting-generations.svg", colonnes(
            [{"libelle": f'{x["decennie"]}', "valeur": x["effectif"],
              "detail": f'Nés dans les années {x["decennie"]} : {x["effectif"]} aventuriers'}
             for x in c["generations"]],
            titre="La génération des aventuriers",
            description="Année de naissance déduite de l'âge annoncé et de "
                        "l'année de la saison, par décennie de naissance.",
            couleur=SERIES[6], largeur=760, hauteur=290))

    # ------------------------------------------------------------ programme
    pr = stats.get("programme") or {}
    if pr.get("saisons"):
        lignes = [x for x in pr["saisons"] if x.get("debut")]
        annees = [int(x["debut"][:4]) for x in lignes]
        ecrire("programme-frise.svg", frise(
            [{"libelle": f'{x["titre"]} ({x["annee"]})',
              "debut": int(x["debut"][:4]) + (int(x["debut"][5:7]) - 1) / 12.0,
              "fin": (int(x["fin"][:4]) + (int(x["fin"][5:7]) - 1) / 12.0
                      if x.get("fin") else None),
              "couleur": SERIES[4] if x["speciale"] else SERIES[0],
              "detail": f'{x["titre"]} — diffusée du {x["debut"]} au '
                        f'{x.get("fin") or "?"}, le {x.get("jour_semaine") or "?"}'}
             for x in lignes],
            titre="Vingt-cinq ans de diffusion",
            description="Période de diffusion de chaque saison. Les creux sont "
                        "aussi parlants que les barres.",
            debut=min(annees), fin=max(annees) + 1, largeur=920,
            legende=[("Édition classique", SERIES[0]), ("Édition spéciale", SERIES[4])]))

    if pr.get("jour_de_lancement"):
        ecrire("programme-jours.svg", barres_horizontales(
            [{"libelle": x["jour"].capitalize(), "valeur": x["effectif"],
              "couleur": SERIES[0],
              "detail": f'{x["effectif"]} saisons lancées un {x["jour"]}'}
             for x in pr["jour_de_lancement"]],
            titre="Le jour de la semaine du premier épisode",
            description="Jour de diffusion du premier épisode de chaque saison.",
            marge_gauche=110, largeur=680))

    # ---------------------------------------------------------------- votes
    a = stats.get("arc_des_votes") or {}
    if a.get("noeuds"):
        ecrire("votes-arc.svg", arcs(
            [{"nom": n["nom"], "poids": 1,
              "couleur": TRIBUS.get(n.get("couleur"), ENCRE_MUETTE),
              "detail": f'{n["nom"]} — sorti au jour {n["jour_sortie"]}'}
             for n in a["noeuds"]],
            [{"de": l["de"], "vers": l["vers"], "poids": l["poids"]}
             for l in a["liens"]],
            titre=f'Qui a écrit le nom de qui — {a["titre"]} ({a["annee"]})',
            description="Les aventuriers sont rangés dans l'ordre de leur "
                        "sortie, du premier parti au vainqueur. Un arc relie "
                        "deux personnes dont l'une a écrit le nom de l'autre ; "
                        "plus il est épais, plus elle l'a fait souvent.",
            hauteur_arc=170, hauteur_etiquettes=104))

    v = stats.get("voix_pour_eliminer") or {}
    if v.get("repartition"):
        ecrire("conseils-voix.svg", colonnes(
            [{"libelle": str(x["voix"]), "valeur": x["effectif"],
              "detail": f'{x["effectif"]} conseils se sont joués à '
                        f'{x["voix"]} voix ({x["part"]} %)'}
             for x in v["repartition"]],
            titre="Combien de voix faut-il pour partir ?",
            description="Nombre de bulletins portant le nom de l'éliminé.",
            couleur=SERIES[0], largeur=760, hauteur=300))
    return

def figure_epreuves_nommees():
    """Le catalogue des epreuves recurrentes, par nature."""
    chemin = os.path.join(RACINE, "_data", "epreuves_nommees.yml")
    if not os.path.exists(chemin):
        return
    d = yaml.safe_load(open(chemin, encoding="utf-8")) or {}
    lignes = [x for x in (d.get("par_nature") or []) if x["nature"] != "non qualifiee"]
    if not lignes:
        return
    ecrire("epreuves-natures.svg", barres_horizontales(
        [{"libelle": x["libelle"], "valeur": x["effectif"],
          "detail": f'{x["effectif"]} épreuves récurrentes que le wiki qualifie '
                    f'de « {x["libelle"].lower()} »'}
         for x in lignes],
        titre="Ce que le wiki dit de la nature des épreuves",
        description="Nombre d'épreuves récurrentes portant chaque qualificatif. "
                    "Une épreuve peut en porter deux — « rapidité, force ».",
        unite=" épreuves", couleur=SERIES[2], marge_gauche=130))


def figure_prenoms():
    """Les prenoms du casting compares a ceux de la France, nee les memes annees.

    Seuls les prenoms dont l'ATTENDU atteint 1 sont classes. En dessous, un
    seul porteur suffit a afficher un facteur quarante : l'indice devient un
    artefact du seuil, pas un resultat. C'est la reserve la plus importante de
    cette figure, et elle est appliquee ici plutot que laissee au lecteur.
    """
    chemin = os.path.join(RACINE, "_data", "prenoms.yml")
    if not os.path.exists(chemin):
        return
    d = yaml.safe_load(open(chemin, encoding="utf-8"))
    solides = [x for x in d["prenoms"]
               if not x["absent_du_fichier"] and x["attendu"] >= 1]
    if not solides:
        return
    haut = sorted(solides, key=lambda x: -x["indice"])[:8]
    bas = sorted(solides, key=lambda x: x["indice"])[:8]
    lot = haut + list(reversed(bas))

    ecrire("prenoms-ecart.svg", barres_groupees(
        [{"libelle": x["prenom"], "valeurs": [x["observe"], x["attendu"]],
          "details": [f'{x["prenom"]} : {x["observe"]} aventuriers',
                      f'{x["prenom"]} : {x["attendu"]} attendus si le casting '
                      f'suivait les naissances françaises']}
         for x in lot],
        [{"nom": "Observé à Koh-Lanta", "couleur": SERIES[1]},
         {"nom": "Attendu en France", "couleur": SERIES[0]}],
        titre="Les prénoms sur-représentés, et les absents",
        description="Nombre d'aventuriers portant ce prénom, face au nombre "
                    "attendu si le casting était un échantillon ordinaire des "
                    "naissances françaises des mêmes années. Les huit premiers "
                    "sont sur-représentés, les huit derniers sous-représentés.",
        largeur=880, marge_gauche=150, hauteur_groupe=30))
    print(f"    ({len(solides)} prénoms classés, "
          f"{sum(1 for x in d['prenoms'] if x['absent_du_fichier'])} introuvables)")


def figure_nuage():
    """Un point par aventurier : l'age contre la part de saison tenue.

    L'agregat par tranche d'age lisse ce que cette figure montre en clair --
    a tout age on peut sortir au troisieme jour comme aller en finale. La
    dispersion EST le resultat.
    """
    parts = _lire("participations.yml")
    saisons = {s["id"]: s for s in _lire("saisons.yml")}
    SORTS = {"vainqueur": ("Vainqueurs", SERIES[2]),
             "finaliste": ("Finalistes", SERIES[3])}
    points = []
    for p in parts:
        s = saisons.get(p["saison"], {})
        if s.get("speciale") or s.get("annulee"):
            continue
        d, j, a = s.get("duree_jours"), p.get("jour_sortie"), p.get("age")
        if not (d and j and a):
            continue
        nom, teinte = SORTS.get(p.get("sort"), ("Éliminés et abandons", ENCRE_MUETTE))
        points.append({
            "x": a, "y": 100.0 * j / d, "couleur": teinte,
            "detail": f'{p.get("nom_complet") or p["nom"]} — {a} ans, '
                      f'{s["titre"]} ({s["annee"]}), sorti au jour {j} sur {d}',
            "_rang": 0 if teinte == ENCRE_MUETTE else 1,
        })
    # Les vainqueurs et finalistes dessines en dernier : sinon la masse des
    # elimines les recouvre, et c'est justement eux qu'on cherche.
    points.sort(key=lambda p: p["_rang"])
    ages = [p["x"] for p in points]

    ecrire("longevite-nuage.svg", nuage(
        points, x_min=min(ages), x_max=max(ages),
        titre="L'âge et la longévité, aventurier par aventurier",
        description="Chaque point est une participation à une saison "
                    "classique : son âge en abscisse, la part de la saison "
                    "qu'il a tenue en ordonnée.",
        x_titre="âge au moment du tournage", y_titre="part de la saison tenue",
        legende=[("Vainqueurs", SERIES[2]), ("Finalistes", SERIES[3]),
                 ("Éliminés et abandons", ENCRE_MUETTE)],
        largeur=920, hauteur=400))


def figures_des_modeles(stats):
    """Les figures des quatre axes de tools/modeles.py.

    Une regle traverse ce bloc : un resultat de modele ne se dessine jamais sans
    son incertitude. D'ou les distributions nulles pour les tests de
    permutation, et les graphiques en foret pour les coefficients.
    """
    m = stats.get("modeles") or {}
    if not m:
        return

    # --- A. la recette du casting -----------------------------------------
    par_cle = {t["cle"]: t for t in (m.get("registre") or [])}
    for cle, nom in (("parite", "casting-parite"),
                     ("etendue_ages", "casting-etendue-ages"),
                     ("familles_metiers", "casting-metiers"),
                     ("tribus_femmes", "casting-tribus-femmes"),
                     ("tribus_ages", "casting-tribus-ages"),
                     ("tribus_ages_mediane", "casting-tribus-ages-mediane"),
                     ("pronostic_vainqueur", "pronostic-rang")):
        t = par_cle.get(cle)
        if t and t.get("nulle"):
            # Un test dont l'observe tombe dans la masse merite la teinte
            # muette : la figure doit dire « rien a voir » avant le texte.
            teinte = SERIES[4] if t.get("retenu") else SERIES[5]
            ecrire(f"{nom}.svg", distribution_nulle(t, couleur=teinte))

    casting = m.get("casting") or {}
    if casting.get("carte"):
        couleurs = [SERIES[0], SERIES[2], SERIES[3], SERIES[6], SERIES[7]]
        groupes = {a["code"]: a for a in casting.get("archetypes") or []}
        ecrire("casting-plan.svg", plan(
            [{"x": p["x"], "y": p["y"], "detail": p["detail"],
              "couleur": couleurs[p["groupe"] % len(couleurs)]}
             for p in casting["carte"]],
            titre="Le plan des castings",
            description="Chaque point est un aventurier, place selon les deux "
                        "dimensions qui separent le plus les profils. Les "
                        "etiquettes marquent les modalites.",
            reperes=[r for r in (casting.get("modalites") or [])
                     if abs(r["x"]) + abs(r["y"]) > 0.9][:14],
            x_titre=f'axe 1 — {casting["inertie_axes"][0]} % de l\u2019information',
            y_titre=f'axe 2 — {casting["inertie_axes"][1]} %',
            legende=[(groupes[c]["libelle"], couleurs[c % len(couleurs)])
                     for c in sorted(groupes)]))

    # --- B. le pronostic ---------------------------------------------------
    pron = m.get("pronostic") or {}
    if pron.get("importances"):
        ecrire("pronostic-importances.svg", barres_horizontales(
            [{"libelle": _lisible(i["variable"]),
              "valeur": i["perte"],
              "detail": f'Brouiller « {_lisible(i["variable"])} » déplace le rang '
                        f'du vainqueur de {i["perte"]} place(s).'}
             for i in pron["importances"]],
            titre="Ce qui porte le peu de signal qu'il y a",
            description="Dégradation du rang du vainqueur quand une seule "
                        "variable est brouillée. Toutes restent minuscules.",
            unite=" places", couleur=SERIES[5], marge_gauche=210))

    # --- C. la force -------------------------------------------------------
    f = m.get("force") or {}
    if f.get("classement"):
        ecrire("force-classement.svg", halteres(
            [{"libelle": d["nom"], "min": d["bas"], "median": d["force"],
              "max": d["haut"], "couleur": SERIES[0],
              "detail": f'{d["nom"]} : force {d["force"]} '
                        f'(intervalle {d["bas"]} à {d["haut"]}), '
                        f'{d["victoires"]} victoires en {d["disputees"]} épreuves'}
             for d in f["classement"][:16]],
            titre="La force estimée, avec son incertitude",
            description="Force latente de chaque athlete, corrigee du nombre "
                        "d'epreuves disputees et du niveau des adversaires. Le "
                        "segment est l'intervalle a 95 %.",
            largeur=880, marge_gauche=190))
    if f.get("pentes"):
        ecrire("force-pentes.svg", pentes(
            [{"libelle": d["nom"], "rang_gauche": d["rang_victoires"],
              "rang_droite": d["rang_force"]}
             for d in f["pentes"]],
            titre="Le classement brut, et le classement corrigé",
            description="A gauche le nombre de victoires, a droite la force "
                        "estimee. Une pente montante signale un athlete que le "
                        "total brut sous-estime.",
            gauche="au nombre de victoires", droite="à la force estimée",
            largeur=760, marge=196))

    fj = m.get("force_et_jeu") or {}
    if fj:
        ecrire("force-effets.svg", foret(
            [{"libelle": "Force doublée → bulletins reçus",
              "estimation": fj["voix"]["force"]["estimation"],
              "bas": fj["voix"]["force"]["bas"], "haut": fj["voix"]["force"]["haut"]},
             {"libelle": "Femme → bulletins reçus",
              "estimation": fj["voix"]["femme"]["estimation"],
              "bas": fj["voix"]["femme"]["bas"], "haut": fj["voix"]["femme"]["haut"]},
             {"libelle": "Dix ans de plus → bulletins reçus",
              "estimation": fj["voix"]["age"]["estimation"],
              "bas": fj["voix"]["age"]["bas"], "haut": fj["voix"]["age"]["haut"]}],
            titre="Ce que la force change aux bulletins reçus",
            description="Rapports de taux, a exposition egale. Un intervalle qui "
                        "traverse 1 veut dire qu'on ne peut pas conclure.",
            reference=1.0, largeur=740, marge_gauche=268,
            note="La ligne verticale marque « aucun effet »."))

    # --- D. l'equilibre ----------------------------------------------------
    eq = m.get("equilibre") or {}
    cox = eq.get("cox") or {}
    if cox.get("coefficients"):
        ecrire("equilibre-cox.svg", foret(
            [{"libelle": c["variable"], "estimation": c["rapport"],
              "bas": c["bas"], "haut": c["haut"],
              "detail": f'{c["variable"]} : risque ×{c["rapport"]} '
                        f'(intervalle {c["bas"]} à {c["haut"]})'}
             for c in cox["coefficients"]],
            titre="Qui sort plus vite, à saison identique",
            description="Rapports de risque d'élimination d'un modèle de durée stratifié par saison. Au-dessus de 1, on sort plus vite.",
            reference=1.0, largeur=780, marge_gauche=224,
            note=f'{cox["effectif"]} participations · {cox["eliminations"]} '
                 f'eliminations · {cox["censures"]} sorties censurees'))

    # --- E. les alliances --------------------------------------------------
    al = m.get("alliances") or {}
    if al.get("test"):
        ecrire("alliances-persistance.svg",
               distribution_nulle(al["test"], couleur=SERIES[2]))
    maj = al.get("majorite") or {}
    if maj.get("variables"):
        ecrire("alliances-majorite.svg", foret(
            [{"libelle": v["libelle"], "estimation": v["estimation"],
              "bas": v["bas"], "haut": v["haut"],
              "detail": f'{v["libelle"]} : {v["estimation"]} points de saison '
                        f'(intervalle {v["bas"]} à {v["haut"]})'}
             for v in maj["variables"]],
            titre="Ce qui fait vraiment durer, une fois en jeu",
            description="Points de saison gagnés ou perdus. Le trait vertical "
                        "marque « aucun effet ».",
            reference=0.0, unite=" pts", largeur=760, marge_gauche=268,
            note=f'{maj["effectif"]} participations · variance expliquée '
                 f'{maj["r2"]}'))

    # --- H. l'homophilie du vote -------------------------------------------
    for cle, nom in (("vote_meme_sexe", "vise-sexe"),
                     ("vote_ecart_age", "vise-age"),
                     ("vote_meme_metier", "vise-metier"),
                     ("vote_bandeau_apres_fusion", "vise-bandeau")):
        t = par_cle.get(cle)
        if t and t.get("nulle"):
            teinte = SERIES[2] if t.get("retenu") else SERIES[5]
            ecrire(f"{nom}.svg", distribution_nulle(t, couleur=teinte))

    # --- K. la geographie ---------------------------------------------------
    for cle, nom in (("geographie_regions", "geographie-nulle"),):
        t = par_cle.get(cle)
        if t and t.get("nulle"):
            teinte = SERIES[2] if t.get("retenu") else SERIES[5]
            ecrire(f"{nom}.svg", distribution_nulle(t, couleur=teinte))

    geo = _lire("geographie.yml") or {}
    if geo.get("regions"):
        ecrire("geographie-regions.svg", foret(
            [{"libelle": r["region"], "estimation": r["indice"],
              "bas": r["indice_bas"], "haut": r["indice_haut"],
              "detail": f'{r["region"]} : {r["observe"]} aventuriers pour '
                        f'{r["attendu"]} attendus, soit ×{r["indice"]}'}
             for r in geo["regions"]],
            titre="D'où viennent les aventuriers, région par région",
            description="Indice observe divise par attendu. A 1, la region fournit "
                        "exactement sa part de population. L'intervalle est celui "
                        "de l'effectif observe.",
            reference=1.0, largeur=800, marge_gauche=230,
            note=f'{geo["participations"]} aventuriers localisés · population de '
                 f'20 à 59 ans, année de chaque saison'))

    # --- J. trahison, confort, decimation -----------------------------------
    for cle, nom in (("trahison", "trahison"), ("decimation", "decimation")):
        t = par_cle.get(cle)
        if t and t.get("nulle"):
            teinte = SERIES[2] if t.get("retenu") else SERIES[5]
            ecrire(f"{nom}.svg", distribution_nulle(t, couleur=teinte))

    cf = m.get("confort_maudit") or {}
    if cf:
        ecrire("confort-maudit.svg", foret(
            [{"libelle": "Bulletins visant un gagnant du confort",
              "estimation": cf["observe"], "bas": cf["bas"], "haut": cf["haut"],
              "detail": f'{cf["observe"]} % des bulletins '
                        f'(intervalle {cf["bas"]} à {cf["haut"]}), pour '
                        f'{cf["attendu"]} % attendus'}],
            titre="Gagner le confort rend-il cible ?",
            description='Part des bulletins visant un gagnant du confort du même épisode. Le trait vertical marque la part que ces gagnants représentent parmi les présents.',
            reference=cf["attendu"], unite=" %", largeur=740, marge_gauche=290,
            hauteur_ligne=34,
            note=f'{cf["conseils"]} conseils · {cf["bulletins"]} bulletins · '
                 f'p = {cf["p"]}'))

    # --- I. le jury final ---------------------------------------------------
    ju = m.get("jury_final") or {}
    if ju.get("coefficients"):
        ecrire("jury-coefficients.svg", foret(
            [{"libelle": c["libelle"], "estimation": c["rapport"],
              "bas": c["bas"], "haut": c["haut"],
              "detail": f'{c["libelle"]} : cote ×{c["rapport"]} '
                        f'(intervalle {c["bas"]} à {c["haut"]})'}
             for c in ju["coefficients"]],
            titre="Ce qui décide le vote d'un juré",
            description="Rapports de cotes d'un logit conditionnel : chaque juré "
                        "choisit parmi les finalistes de sa saison.",
            reference=1.0, largeur=780, marge_gauche=300,
            note=f'{ju["bulletins"]} bulletins de jury · {ju["saisons"]} saisons'))

    # --- F. la grille ------------------------------------------------------
    fu = m.get("fusion") or {}
    if fu.get("lignes"):
        ecrire("fusion-grille.svg", plan(
            [{"x": l["casting"], "y": l["episode"], "couleur": SERIES[0],
              "detail": f'{l["titre"]} ({l["annee"]}) : casting de {l["casting"]}, '
                        f'fusion à l\u2019épisode {l["episode"]}'}
             for l in fu["lignes"]]
            + [{"x": l["casting"], "y": l["restants"], "couleur": SERIES[3],
                "detail": f'{l["titre"]} ({l["annee"]}) : {l["restants"]} joueurs '
                          f'encore en jeu à la fusion'}
               for l in fu["lignes"]],
            titre="La fusion suit la grille, pas le nombre de joueurs",
            description="Chaque saison figure deux fois : par l'episode ou la "
                        "fusion tombe, et par le nombre de joueurs qu'elle laisse. "
                        "Le premier ne bouge pas quand le casting grossit ; le "
                        "second suit.",
            x_titre="taille du casting", y_titre="épisodes / joueurs",
            legende=[("épisode de la fusion", SERIES[0]),
                     ("joueurs restants", SERIES[3])],
            largeur=760, hauteur=380))

    # --- G. les ruptures ---------------------------------------------------
    ru = m.get("ruptures") or {}
    if ru.get("test"):
        ecrire("ruptures-nulle.svg", distribution_nulle(ru["test"], couleur=SERIES[6]))
    if ru.get("serie"):
        annees = [str(x["annee"]) for x in ru["serie"]]
        ecrire("ruptures-serie.svg", courbes(
            [{"nom": "taille du casting",
              "valeurs": [x["effectif"] for x in ru["serie"]],
              "couleur": SERIES[0]},
             {"nom": "nombre de conseils",
              "valeurs": [x["conseils"] for x in ru["serie"]],
              "couleur": SERIES[3]}],
            annees,
            titre=f'Les deux séries qui basculent en {ru["annee_rupture"]}',
            description="Taille du casting et nombre de conseils, saison par "
                        "saison. La rupture detectee separe les deux regimes.",
            largeur=880, hauteur=320))

    if ru.get("profil"):
        # Le profil de gain, coupure par coupure. C'est lui qui dit si la date
        # est identifiee : un pic isole, oui ; un plateau, non.
        ecrire("ruptures-profil.svg", colonnes(
            [{"libelle": str(x["annee"]), "valeur": x["gain"],
              "detail": f'coupure avant {x["titre"]} ({x["annee"]}) : gain {x["gain"]}'}
             for x in ru["profil"]],
            titre="Chaque coupure possible, et ce qu'elle sépare",
            description="Gain de séparation pour chaque date de coupure envisageable. "
                        "Un pic isolé désignerait une date ; un plateau dit que "
                        "plusieurs dates se valent.",
            unite="", largeur=880, hauteur=300))

    # --- G bis. l'audience ---------------------------------------------------
    au = m.get("audience") or {}
    if au.get("serie"):
        serie = au["serie"]
        annees = [str(x["annee"]) for x in serie]
        ecrire("audience-serie.svg", courbes(
            [{"nom": "audience moyenne",
              "valeurs": [round(x["moyenne"] / 1e6, 2) for x in serie],
              "couleur": SERIES[0]}],
            annees,
            titre=f'L\u2019audience moyenne, saison par saison '
                  f'({serie[0]["annee"]}\u2013{serie[-1]["annee"]})',
            description="Nombre moyen de téléspectateurs par saison, en millions. "
                        "La série couvre toutes les éditions achevées.",
            unite=" M", largeur=880, hauteur=320))
        ecrire("audience-lancement-finale.svg", courbes(
            [{"nom": "lancement",
              "valeurs": [round((x["lancement"] or 0) / 1e6, 2) for x in serie],
              "couleur": SERIES[0]},
             {"nom": "finale",
              "valeurs": [round((x["finale"] or 0) / 1e6, 2) for x in serie],
              "couleur": SERIES[3]}],
            annees,
            titre="Le lancement et la finale, saison par saison",
            description="Audience du premier et du dernier épisode de chaque saison, "
                        "en millions de téléspectateurs.",
            unite=" M", largeur=880, hauteur=320))
    if au.get("test") or au.get("tests"):
        for t in au.get("tests") or []:
            if t["cle"] == "audience_rupture":
                ecrire("audience-nulle.svg", distribution_nulle(t, couleur=SERIES[1]))
    if au.get("profil"):
        ecrire("audience-profil.svg", colonnes(
            [{"libelle": str(x["annee"]), "valeur": x["gain"],
              "detail": f'coupure avant {x["titre"]} ({x["annee"]}) : gain {x["gain"]}'}
             for x in au["profil"]],
            titre="Chaque coupure possible de la série d\u2019audience",
            description="Gain de séparation pour chaque date de coupure envisageable. "
                        "Un pic isolé désigne une date ; un plateau dirait que "
                        "plusieurs se valent.",
            unite="", largeur=880, hauteur=300))

    # --- G ter. avant et apres la reunification ------------------------------
    aa = m.get("avant_apres") or {}
    if aa.get("avant") and aa.get("apres"):
        av, ap = aa["avant"], aa["apres"]
        rangs = [aa.get("rang_force_avant"), aa.get("rang_force_apres")]
        ecrire("fusion-avant-apres.svg", barres_groupees(
            [{"libelle": "Présents au conseil",
              "valeurs": [av["presents_moyen"], ap["presents_moyen"]],
              "details": [f'{av["presents_moyen"]} en moyenne avant la fusion',
                          f'{ap["presents_moyen"]} après']},
             {"libelle": "Conseils serrés (%)",
              "valeurs": [av["part_serres"], ap["part_serres"]],
              "details": [f'{av["part_serres"]} % avant', f'{ap["part_serres"]} % après']},
             {"libelle": "Femmes parmi les éliminés (%)",
              "valeurs": [av["part_femmes"], ap["part_femmes"]],
              "details": [f'{av["part_femmes"]} % avant', f'{ap["part_femmes"]} % après']},
             {"libelle": "Âge moyen des éliminés",
              "valeurs": [av["age_moyen"], ap["age_moyen"]],
              "details": [f'{av["age_moyen"]} ans avant', f'{ap["age_moyen"]} ans après']},
             {"libelle": "Rang de force de l’éliminé",
              "valeurs": rangs,
              "details": [f'{rangs[0]} sur 100 avant', f'{rangs[1]} après']}],
            [{"nom": "avant la fusion", "couleur": TRIBUS["jaune"]},
             {"nom": "après la fusion", "couleur": TRIBUS["rouge"]}],
            titre="Ce que la réunification change",
            description="Cinq mesures du conseil, avant et après la réunification. "
                        "Le rang de force va de 0, le plus faible du camp, à 100, "
                        "le plus fort.",
            marge_gauche=230, hauteur_groupe=46))
    for t in aa.get("tests") or []:
        if t["cle"] == "fusion_force":
            ecrire("fusion-force-nulle.svg", distribution_nulle(t, couleur=SERIES[3]))
        elif t["cle"] == "fusion_serre":
            ecrire("fusion-serre-nulle.svg", distribution_nulle(t, couleur=SERIES[0]))
        elif t["cle"] == "ambassadeurs_force":
            ecrire("ambassadeurs-nulle.svg", distribution_nulle(t, couleur=SERIES[6]))
        elif t["cle"] == "ambassadeurs_survie":
            ecrire("ambassadeurs-survie.svg", distribution_nulle(t, couleur=SERIES[4]))

    hm = m.get("hasard_mecanique") or {}
    if hm.get("paliers"):
        ecrire("risque-mecanique.svg", barres_groupees(
            [{"libelle": p["palier"],
              "valeurs": [p["observe"], p["mecanique"]],
              "details": [f'{p["observe"]} % observé sur {p["conseils"]} conseils',
                          f'{p["mecanique"]} % attendu avec '
                          f'{p["presents_moyen"]} présents en moyenne']}
             for p in hm["paliers"]],
            [{"nom": "risque observé", "couleur": SERIES[0]},
             {"nom": "1 / nombre de présents", "couleur": SERIES[5]}],
            titre="Le risque monte-t-il, ou le camp se vide-t-il ?",
            description="Risque de sortir à un conseil, par dixième de saison, "
                        "compare au simple 1/nombre-de-presents.",
            unite=" %", largeur=760, marge_gauche=110))


if __name__ == "__main__":
    sys.exit(main())
