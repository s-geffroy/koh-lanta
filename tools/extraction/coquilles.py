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
}

# Une capitale sans son accent en tete de mot : « Eliminé » -> « Éliminé ».
RE_ELIMIN = re.compile(r"\bElimin")


def corriger(valeur):
    """Corrige toutes les chaines d'une structure (dict, liste, chaine)."""
    if isinstance(valeur, str):
        for faux, juste in CORRECTIONS.items():
            valeur = valeur.replace(faux, juste)
        return RE_ELIMIN.sub("Élimin", valeur)
    if isinstance(valeur, dict):
        return {k: corriger(v) for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [corriger(v) for v in valeur]
    return valeur
