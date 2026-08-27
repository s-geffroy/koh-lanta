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

DEPARTEMENTS = """
Ain Aisne Allier Alpes-de-Haute-Provence Hautes-Alpes Alpes-Maritimes Ardeche
Ardennes Ariege Aube Aude Aveyron Bouches-du-Rhone Calvados Cantal Charente
Charente-Maritime Cher Correze Corse Corse-du-Sud Haute-Corse Cote-d-Or
Cotes-d-Armor Creuse Dordogne Doubs Drome Eure Eure-et-Loir Finistere Gard
Haute-Garonne Gers Gironde Herault Ille-et-Vilaine Indre Indre-et-Loire Isere
Jura Landes Loir-et-Cher Loire Haute-Loire Loire-Atlantique Loiret Lot
Lot-et-Garonne Lozere Maine-et-Loire Manche Marne Haute-Marne Mayenne
Meurthe-et-Moselle Meuse Morbihan Moselle Nievre Nord Oise Orne Pas-de-Calais
Puy-de-Dome Pyrenees-Atlantiques Hautes-Pyrenees Pyrenees-Orientales Bas-Rhin
Haut-Rhin Rhone Haute-Saone Saone-et-Loire Sarthe Savoie Haute-Savoie Paris
Seine-Maritime Seine-et-Marne Yvelines Deux-Sevres Somme Tarn Tarn-et-Garonne
Var Vaucluse Vendee Vienne Haute-Vienne Vosges Yonne Territoire-de-Belfort
Essonne Hauts-de-Seine Seine-Saint-Denis Val-de-Marne Val-d-Oise
"""

AUTRES_LIEUX = """
Guadeloupe Martinique Guyane La-Reunion Reunion Mayotte
Nouvelle-Caledonie Polynesie-francaise Saint-Martin Saint-Barthelemy
Wallis-et-Futuna Saint-Pierre-et-Miquelon
Auvergne-Rhone-Alpes Bourgogne-Franche-Comte Bretagne Centre-Val-de-Loire
Grand-Est Hauts-de-France Ile-de-France Normandie Nouvelle-Aquitaine Occitanie
Pays-de-la-Loire Provence-Alpes-Cote-d-Azur
Belgique Suisse Luxembourg Canada Quebec Maroc Algerie Tunisie Senegal
Espagne Portugal Italie Allemagne Royaume-Uni Angleterre Etats-Unis
"""

def _norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]+", "-", s.lower()).strip("-")

CONNUS = {_norm(x) for x in (DEPARTEMENTS + AUTRES_LIEUX).split()}

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
