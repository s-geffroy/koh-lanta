"""Ecrire et relire `_data/` : la virgule decimale se pose ICI, et nulle part
ailleurs.

Liquid n'a pas de filtre de nombre a la francaise, et ce depot ne met rien en
forme dans un gabarit. Un flottant ecrit nu dans `_data/` sortait donc tel quel
sur le site : « 54.2 % », et meme « 100.0 » ou « 6.0 ». C'etait le cas de 701
nombres sur 34 pages quand on l'a compte, le 19 octobre 2026.

La regle est donc posee a l'ecriture, pour tout `_data/` :

  * un flottant rond s'ecrit en entier : 100.0 -> 100 ;
  * un autre s'ecrit a la francaise, ENTRE GUILLEMETS : 54.2 -> "54,2".
    Les guillemets ne sont pas decoratifs : le YAML de Ruby lit « 54,2 » nu
    comme le nombre 542 (voir `RE_NOMBRE_RUBY`) ;
  * les chiffres ne changent pas : la forme la plus courte qui redonne le meme
    flottant (`repr`), jamais un arrondi de plus.

Et a la relecture, `charger()` rend les nombres aux scripts Python : « 54,2 »
y redevient 54.2. Tout script qui lit ou ecrit `_data/` passe par ce module --
`yaml.safe_load` y lirait des chaines, et `yaml.safe_dump` y remettrait des
points.

Ce que ce module ne fait PAS : arrondir, ou separer les milliers. Un nombre
qui doit s'afficher arrondi s'arrondit dans le script qui le calcule ; un
texte (« 8 127 000 téléspectateurs ») se fabrique en `_texte` a cote.
"""
import math
import re

import yaml

# LES CHAINES QUE LE YAML DE RUBY LIT COMME DES NOMBRES, ET QUE PYYAML ECRIT
# NUES. Le piege a ete paye en ligne. YAML 1.1 -- la version que Psych
# implemente, donc celle de Jekyll -- accepte la VIRGULE comme separateur de
# milliers dans un entier : « 39,9 » y vaut trois cent quatre-vingt-dix-neuf.
# PyYAML ne connait pas cette forme : il n'y voit qu'une chaine et l'ecrit sans
# guillemets. On force donc les guillemets des que la chaine ressemble a un
# nombre pour Ruby.
RE_NOMBRE_RUBY = re.compile(r"^[-+]?[0-9][0-9_,]*(\.[0-9_]*)?$")

# Ce que `decimal_fr()` ecrit, et que `charger()` reconnait.
RE_DECIMAL_FR = re.compile(r"^[-\u2212]?[0-9]+,[0-9]+$")


# LES ESPACES INSECABLES DE LA TYPOGRAPHIE FRANCAISE (21 octobre 2026). Avant
# « : », une espace insecable ; avant « ; ? ! » et « », et apres « », une
# espace fine insecable. Une espace ordinaire laisse le navigateur couper la
# ligne juste avant le signe, qui ouvre alors la ligne suivante. On en a
# compte 7 981 sur les 622 pages publiees. La regle est posee ICI, a
# l'ecriture de toute chaine de `_data/`, et dans `graphiques.ecrire` pour
# les figures : un script qui ecrit « Pourquoi ? » n'a pas a y penser.
#
# Les lookaheads evitent ce qui n'est pas de la ponctuation de phrase : une
# image Markdown (« ![ »), un « != », un « :8 ». Un signe suivi d'un marqueur
# Markdown (« partir ?** ») est une fin de phrase : `*` et `_` sont admis.
INSECABLE = "\u00a0"
FINE = "\u202f"
RE_ESPACE_DEUX_POINTS = re.compile(r"(?<=[^\s\u00a0\u202f]) :(?=[\s<*_]|$)")
RE_ESPACE_AVANT = re.compile(r"(?<=[^\s\u00a0\u202f]) ([;?!»])(?=[\s<»)\]\"'.,…*_:;?!]|$)")
RE_ESPACE_APRES = re.compile(r"« (?=\S)")
# Le signe pour cent prend lui aussi une espace fine insecable (23 octobre
# 2026) : 3 126 « 54 % » publies avec une espace ordinaire, que le navigateur
# pouvait couper entre le nombre et le signe. Apres un chiffre ou une
# variable Liquid fermee (« }} % »), jamais ailleurs.
RE_ESPACE_POURCENT = re.compile(r"(?<=[0-9}]) %(?=[\s<)\]\"'.,…*_:;?!»]|$)")

# L'APOSTROPHE TYPOGRAPHIQUE, entre deux lettres. Kramdown la pose dans la
# prose Markdown, mais rien ne la posait dans ce qui sort d'un gabarit HTML,
# d'un bloc HTML ou des donnees : 370 apostrophes droites restaient publiees.
# Elle n'est posee QU'A L'AFFICHAGE (`ecrire(..., affichage=True)`), jamais
# dans les donnees sources, ou elle casserait les rapprochements de noms.
# « Taha'a » garde son signe : c'est une okina, pas une elision.
RE_APOSTROPHE = re.compile(r"(?<=[A-Za-zÀ-ÖØ-öø-ÿœŒ])(?:'|&#x27;|&#39;)(?=[A-Za-zÀ-ÖØ-öø-ÿœŒ])")
APOSTROPHES_GARDEES = ("Taha'a",)


def apostrophes(texte):
    if not any(g in texte for g in APOSTROPHES_GARDEES):
        return RE_APOSTROPHE.sub("\u2019", texte)
    morceaux = re.split("(" + "|".join(re.escape(g) for g in APOSTROPHES_GARDEES) + ")", texte)
    return "".join(m if m in APOSTROPHES_GARDEES else RE_APOSTROPHE.sub("\u2019", m)
                   for m in morceaux)


def insecables(texte):
    """« Pourquoi ? » -> « Pourquoi\u202f? » ; seulement l'espace change."""
    texte = RE_ESPACE_DEUX_POINTS.sub(INSECABLE + ":", texte)
    texte = RE_ESPACE_AVANT.sub(lambda m: FINE + m.group(1), texte)
    texte = RE_ESPACE_POURCENT.sub(FINE + "%", texte)
    return RE_ESPACE_APRES.sub("«" + FINE, texte)


def decimal_fr(x):
    """54.2 -> « 54,2 » ; 100.0 -> 100 ; 1e-05 -> « 0,00001 »."""
    if x == int(x):
        return int(x)
    t = repr(x)
    if "e" in t or "E" in t:
        # La notation scientifique n'est pas une ecriture de lecteur : on
        # deplie, sans ajouter de chiffre significatif.
        chiffres = max(0, -int(math.floor(math.log10(abs(x)))) + 15)
        t = f"{x:.{chiffres}f}".rstrip("0")
    return t.replace(".", ",")


class Ecrivain(yaml.SafeDumper):
    """Le `SafeDumper` du depot : chaines numeriques gardees, virgule posee."""


def _chaine(dumper, valeur):
    valeur = insecables(valeur)
    style = '"' if RE_NOMBRE_RUBY.match(valeur) else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", valeur, style=style)


def _flottant(dumper, valeur):
    if not math.isfinite(valeur):
        return dumper.represent_float(valeur)
    v = decimal_fr(valeur)
    if isinstance(v, int):
        return dumper.represent_int(v)
    return dumper.represent_scalar("tag:yaml.org,2002:str", v, style='"')


Ecrivain.add_representer(str, _chaine)
Ecrivain.add_representer(float, _flottant)


class EcrivainAffiche(Ecrivain):
    """Pour les fichiers que le site AFFICHE (stats, fiches) : l'apostrophe
    typographique en plus."""


# L'INTERVALLE prend le tiret demi-cadratin, sans espace : « 18–24 ans »,
# « 2000–2004 », « 90–100 % ». Trois graphies coexistaient. Une date ISO
# (« 2001-08-04 ») n'est pas un intervalle et n'est pas touchee.
RE_INTERVALLE = re.compile(
    r"(?<![\d-])(\d{4})-(\d{4})(?![\d-])"              # 2000-2004
    r"|(?<![\d-])(\d{1,3})-(\d{1,3})(?= ans| ?%|\u202f%)")  # 18-24 ans, 90-100 %


def intervalles(texte):
    return RE_INTERVALLE.sub(lambda m: "\u2013".join(g for g in m.groups() if g), texte)


def _chaine_affichee(dumper, valeur):
    return _chaine(dumper, intervalles(apostrophes(valeur)))


def _flottant_affiche(dumper, valeur):
    """Le signe moins typographique (U+2212) devant un decimal negatif : le
    trait d'union s'affichait « -0,5 », et pouvait se couper en fin de ligne.
    `charger()` relit les deux formes."""
    if not math.isfinite(valeur) or valeur >= 0:
        return _flottant(dumper, valeur)
    v = decimal_fr(valeur)
    if isinstance(v, int):
        return dumper.represent_int(v)
    return dumper.represent_scalar("tag:yaml.org,2002:str", "\u2212" + v.lstrip("-"), style='"')


EcrivainAffiche.add_representer(str, _chaine_affichee)
EcrivainAffiche.add_representer(float, _flottant_affiche)


def ecrire(objet, flux=None, affichage=False, **options):
    """`yaml.safe_dump`, a la francaise. Memes options.

    `affichage=True` pour un fichier que les gabarits affichent tel quel :
    l'apostrophe y devient typographique. Les donnees sources (participations,
    conseils...) gardent l'apostrophe droite de leurs sources."""
    return yaml.dump(objet, flux, Dumper=EcrivainAffiche if affichage else Ecrivain, **options)


def _rendre_nombres(v):
    if isinstance(v, str):
        return (float(v.replace(",", ".").replace("\u2212", "-"))
                if RE_DECIMAL_FR.match(v) else v)
    if isinstance(v, dict):
        # Un champ `_texte` est DEJA du texte mis en forme (« 39,5 ») : il
        # reste une chaine, c'est ce que son nom promet.
        return {k: x if str(k).endswith("_texte") else _rendre_nombres(x)
                for k, x in v.items()}
    if isinstance(v, list):
        return [_rendre_nombres(x) for x in v]
    return v


def charger(flux):
    """`yaml.safe_load`, qui rend leurs nombres aux decimaux francais."""
    return _rendre_nombres(yaml.safe_load(flux))
