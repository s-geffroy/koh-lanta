#!/usr/bin/env python3
"""Separe une localisation collee a une profession.

Sur plusieurs saisons, le wiki Fandom ecrit « Savoie Gerante d'un centre de
vacances » dans une seule cellule : le departement precede le metier, sans
ponctuation. Wikipedia, lui, tient les deux colonnes separees. Pour que la
taxonomie des professions ne soit pas polluee par des noms de lieux, on retire
le prefixe quand il correspond a un lieu connu.

La liste est fermee et verifiable : departements francais, regions,
collectivites d'outre-mer, et les quelques pays d'ou viennent des candidats.
"""
import re
import unicodedata

# Les cent departements, ecrits comme le fichier de population de l'INSEE les
# ecrit : c'est cette graphie-la qu'on stocke, faute de quoi « Val-De-Marne »
# et « Val-de-Marne » sont deux departements et le rapprochement echoue.
DEPARTEMENTS = """
Ain, Aisne, Allier, Alpes-de-Haute-Provence, Hautes-Alpes, Alpes-Maritimes,
Ardèche, Ardennes, Ariège, Aube, Aude, Aveyron, Bouches-du-Rhône, Calvados,
Cantal, Charente, Charente-Maritime, Cher, Corrèze, Corse, Corse-du-Sud,
Haute-Corse, Côte-d'Or, Côtes-d'Armor, Creuse, Dordogne, Doubs, Drôme, Eure,
Eure-et-Loir, Finistère, Gard, Haute-Garonne, Gers, Gironde, Hérault,
Ille-et-Vilaine, Indre, Indre-et-Loire, Isère, Jura, Landes, Loir-et-Cher,
Loire, Haute-Loire, Loire-Atlantique, Loiret, Lot, Lot-et-Garonne, Lozère,
Maine-et-Loire, Manche, Marne, Haute-Marne, Mayenne, Meurthe-et-Moselle,
Meuse, Morbihan, Moselle, Nièvre, Nord, Oise, Orne, Pas-de-Calais,
Puy-de-Dôme, Pyrénées-Atlantiques, Hautes-Pyrénées, Pyrénées-Orientales,
Bas-Rhin, Haut-Rhin, Rhône, Haute-Saône, Saône-et-Loire, Sarthe, Savoie,
Haute-Savoie, Paris, Seine-Maritime, Seine-et-Marne, Yvelines, Deux-Sèvres,
Somme, Tarn, Tarn-et-Garonne, Var, Vaucluse, Vendée, Vienne, Haute-Vienne,
Vosges, Yonne, Territoire de Belfort, Essonne, Hauts-de-Seine,
Seine-Saint-Denis, Val-de-Marne, Val-d'Oise
"""

# Ce qui n'est pas un departement mais reste une origine possible : les
# collectivites d'outre-mer, les regions -- quand la source ne dit pas mieux --
# et les quelques pays d'ou viennent des candidats.
AUTRES_LIEUX = """
Guadeloupe, Martinique, Guyane, La Réunion, Mayotte,
Nouvelle-Calédonie, Polynésie française, Saint-Martin, Saint-Barthélemy,
Wallis-et-Futuna, Saint-Pierre-et-Miquelon,
Auvergne-Rhône-Alpes, Bourgogne-Franche-Comté, Bretagne, Centre-Val de Loire,
Grand Est, Hauts-de-France, Île-de-France, Normandie, Nouvelle-Aquitaine,
Occitanie, Pays de la Loire, Provence-Alpes-Côte d'Azur,
Belgique, Suisse, Luxembourg, Canada, Québec, Maroc, Algérie, Tunisie,
Sénégal, Espagne, Portugal, Italie, Allemagne, Royaume-Uni, Angleterre,
États-Unis, Monaco, Grèce, Australie
"""

# Les pages individuelles du wiki Fandom donnent parfois la ville, ou une
# province d'Ancien Regime, la ou les tables de saison donnent le departement.
# Cette table les ramene au departement, seul niveau ou la population de
# reference existe (fichier INSEE). Elle est fermee, et chaque ligne est un
# fait verifiable -- pas une deduction.
#
# Les cas ambigus sont volontairement absents : « Brassac » est dans le Tarn
# ET dans le Puy-de-Dome ; « Mauleon » dans les Deux-Sevres ET les
# Pyrenees-Atlantiques. Sans autre indice, on prefere ne rien dire.
VILLES = {
    "Bordeaux": "Gironde",
    "Boulogne-Billancourt": "Hauts-de-Seine",
    "Bandol": "Var",
    "Bressuire": "Deux-Sèvres",
    "Caen": "Calvados",
    "Cannes": "Alpes-Maritimes",
    "Courneuve": "Seine-Saint-Denis",
    "Fourmies": "Nord",
    "Garges-les-Gonesses": "Val-d'Oise",
    "Grenoble": "Isère",
    "La Garenne-Colombes": "Hauts-de-Seine",
    "Lambersart": "Nord",
    "Lausanne": "Suisse",
    "Lille": "Nord",
    "Lyon": "Rhône",
    "Marseille": "Bouches-du-Rhône",
    "Mornant": "Rhône",
    "Nice": "Alpes-Maritimes",
    "Noisy-le-Grand": "Seine-Saint-Denis",
    "Pollestres": "Pyrénées-Orientales",
    "Strasbourg": "Bas-Rhin",
    "Toulouse": "Haute-Garonne",
    # Provinces d'Ancien Regime, encore employees comme adresse.
    "Périgord": "Dordogne",
    "Touraine": "Indre-et-Loire",
    # Orthographes fautives rencontrees sur le wiki.
    "Ille-et-Villaine": "Ille-et-Vilaine",
    "Seine-Maritimes": "Seine-Maritime",
    "Saine-Saint-Denis": "Seine-Saint-Denis",
    "Seines-Saint-Denis": "Seine-Saint-Denis",
    "Puy-du-Dôme": "Puy-de-Dôme",
    "Eure-et-Loire": "Eure-et-Loir",
}

def _norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]+", "-", s.lower()).strip("-")

LIEUX = [x.strip() for x in (DEPARTEMENTS + "," + AUTRES_LIEUX).split(",") if x.strip()]
CONNUS = {_norm(x) for x in LIEUX}
# La graphie de reference, par forme normalisee : c'est elle qu'on ecrit.
CANONIQUE = {_norm(x): x for x in LIEUX}

VERS_DEPARTEMENT = {_norm(k): v for k, v in VILLES.items()}


def normaliser(texte):
    """Ramene une localisation libre a un lieu connu, ou rend None.

    Un lieu reconnu est rendu dans la graphie de reference ci-dessus, celle du
    fichier INSEE : « Val-De-Marne », « Val de Marne » et « Val-de-Marne » sont
    le meme departement, et un seul de ces trois se rapproche de la population.
    Une ville, une province ou une orthographe fautive est remplacee par le
    departement que la table lui associe.

    « Marseille , Bouches-du-Rhone » : on essaie la valeur entiere, puis chaque
    morceau. Tout ce qui n'est reconnu nulle part rend None -- c'est un
    signalement, pas une valeur.
    """
    if not texte:
        return None
    brut = re.sub(r"\s+", " ", str(texte)).strip(" .,;-")
    for morceau in [brut] + [m.strip() for m in re.split(r"[,/;]| - ", brut)]:
        n = _norm(morceau)
        if n in VERS_DEPARTEMENT:
            return VERS_DEPARTEMENT[n]
        if n in CANONIQUE:
            return CANONIQUE[n]
    return None

def separer(texte):
    """Rend (localisation, profession). La localisation vaut None si absente."""
    if not texte:
        return None, texte
    mots = texte.split()
    # on teste les prefixes les plus longs d'abord (« Seine-Saint-Denis »,
    # « Val de Marne », « La Reunion »…)
    for n in range(min(4, len(mots)), 0, -1):
        tete = " ".join(mots[:n])
        if _norm(tete) in CONNUS:
            reste = " ".join(mots[n:]).strip(" ,;-")
            if reste:
                return tete, reste
    # le lieu est parfois rejete en fin de cellule
    for n in range(min(4, len(mots)), 0, -1):
        queue = " ".join(mots[-n:])
        if _norm(queue) in CONNUS:
            reste = " ".join(mots[:-n]).strip(" ,;-")
            if reste:
                return queue, reste
    return None, texte

if __name__ == "__main__":
    for essai in ["Savoie Gérante d'un centre de vacances",
                  "Seine-Saint-Denis Magasinier",
                  "Indre-et-Loire Agriculteur",
                  "Paris Négociante en vins",
                  "Artisan peintre Seine-Maritime",
                  "Décorateur-sculpteur"]:
        print(f"{essai!r:52s} -> {separer(essai)}")
