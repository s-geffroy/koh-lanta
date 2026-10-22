"""Les coquilles des sources, corrigees a la PUBLICATION.

Les wikis ont leurs fautes de frappe, et l'extraction les recopiait jusque sur
le site : « Directeur d'hotêl », « Poteries en équikibre », « Non Gagnant
Jo ur 35 », vingt motifs « Eliminé » sans leur majuscule accentuee. La revue
d'orthographe du 19 octobre 2026 les a trouvees.

On ne corrige PAS les sources (specs/sources/ reste la copie fidele de ce qui
a ete telecharge, c'est la preuve de provenance) ni la lecture : les
rapprochements -- un nom d'epreuve cite ici et releve la -- se font sur le texte
d'origine. La correction s'applique a ce qui est ecrit dans _data/, et
seulement la.

C'est une TABLE, pas une regle generale, et elle doit le rester : chaque
entree est une faute constatee. Une correction automatique « a la francaise »
reecrirait des noms propres.
"""
import re

# texte fautif -> texte juste, tel qu'il apparait dans une valeur
CORRECTIONS = {
    "hotêl": "hôtel",
    "équikibre": "équilibre",
    "Jo ur": "Jour",
    "réunifiiée": "réunifiée",
    "réunifée": "réunifiée",
    "Penalité": "Pénalité",
    "A bout de souffle": "À bout de souffle",
    # Revue du 22 octobre 2026 : les professions et les types d'epreuve, tels
    # que les fiches les publient. Chaque ligne est une valeur constatee.
    "Chaffeur d'autocar": "Chauffeur d'autocar",            # mohamed-derradji
    "La Revache des Héros": "La Revanche des Héros",        # isabelle-da-silva
    "Agents de joueurs de football": "Agent de joueurs de football",  # nelson-parente
    # lili-gasnier : le departement est mal ecrit (« Villaine ») et colle au
    # metier sans preposition.
    "Cheffe d'entreprise Ille-et-Villaine": "Cheffe d'entreprise en Ille-et-Vilaine",
    "Pompier Volontaire": "pompier volontaire",
    "Conseillère Financière": "Conseillère financière",
    "Ouvrier Teinturier": "Ouvrier teinturier",
    "Pilote de Karting": "Pilote de karting",
    "Patron de pizzerias": "patron de pizzerias",
    "Navigateur / Instructeur": "Navigateur / instructeur",
    "Étudiant, Mannequin": "Étudiant, mannequin",
    "Ex chef d'entreprise": "Ex-chef d'entreprise",
    "électro-ménager": "électroménager",
    "agro-alimentaire": "agroalimentaire",
    # La capitale sans son accent, en tete de valeur.
    "Etudiant": "Étudiant",
    "Educatrice": "Éducatrice",
    "Equilibre": "Équilibre",                               # type d'epreuve
    "Force et Statique": "Force et statique",               # type d'epreuve
}

# Une valeur ENTIERE fautive : remplacer en sous-chaine toucherait des mots
# justes. « Cuisiner » est la profession de teheiura-teahui en 2012.
VALEURS = {
    "Cuisiner": "Cuisinier",
}

# Les titres de saison cites ENTRE PARENTHESES dans une profession
# (« Ingénieur (Palau, Le Choc des Héros & La Revanche des Héros) ») : le site
# ecrit « héros » en minuscule, comme les titres de _data/saisons.yml. La
# correction ne vaut qu'a l'interieur d'une parenthese -- `edition_origine`,
# qui sert a rapprocher les saisons, n'en porte pas et reste tel quel.
RE_PARENTHESE = re.compile(r"\([^()]*\)")

# Une capitale sans son accent en tete de mot : « Eliminé » -> « Éliminé ».
RE_ELIMIN = re.compile(r"\bElimin")


def corriger(valeur):
    """Corrige toutes les chaines d'une structure (dict, liste, chaine)."""
    if isinstance(valeur, str):
        valeur = VALEURS.get(valeur, valeur)
        for faux, juste in CORRECTIONS.items():
            valeur = valeur.replace(faux, juste)
        valeur = RE_PARENTHESE.sub(
            lambda m: m.group(0).replace(" des Héros", " des héros"), valeur)
        return RE_ELIMIN.sub("Élimin", valeur)
    if isinstance(valeur, dict):
        return {k: corriger(v) for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [corriger(v) for v in valeur]
    return valeur
