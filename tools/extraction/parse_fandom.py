#!/usr/bin/env python3
"""Extrait les candidats d'une page de saison du wiki Fandom Koh-Lanta.

Le wikitexte brut vient de l'API MediaWiki (voir fetch_fandom.py). Une ligne du
tableau « Candidats » donne une participation.

Le tableau change de forme au fil des saisons : nom parfois lie, parfois en
texte brut ; tribu d'origine parfois vide ; bloc <small> portant selon l'edition
« 34 ans, Profession », une localisation, ou l'edition d'origine pour les
retours de heros. Le decoupage se fait donc cellule par cellule, en respectant
l'imbrication des modeles, plutot qu'a coups d'expressions sur la ligne entiere.

Ce script ne devine rien : un champ illisible ressort a None et remonte dans le
rapport, pour etre tranche a la main plutot qu'invente.
"""
import re
import sys
import unicodedata

# --- nettoyage du wikitexte ------------------------------------------------

def strip_refs(t):
    t = re.sub(r"<ref[^>]*/>", "", t)
    t = re.sub(r"<ref.*?</ref>", "", t, flags=re.S)
    return t

# Modeles qui ne font qu'envelopper du texte : leur contenu doit survivre au
# nettoyage. {{nobr|49 ans}} vaut « 49 ans », pas rien du tout.
RE_ENVELOPPE = re.compile(r"\{\{\s*(?:nobr|nowrap|no br)\s*\|(.*?)\}\}", re.I | re.S)

# Un lien de fichier n'est PAS du texte : il affiche une image. Ses options de
# rendu -- « 75px », « vignette », « gauche » -- n'ont donc rien a faire dans
# le nom d'un aventurier. La regle generique des liens les y laissait entrer :
# [[Fichier:Sara.png|75px|link=Sara Tallon]] rendait « 75px|link=Sara Tallon »,
# et 478 eliminations sur 681 restaient non rattachees a cause de cela.
#
# Seule la cible `link=` porte un nom lisible. Le nom du FICHIER en porte un
# aussi (« Marie.png »), mais le lire serait deviner : on ne le fait pas.
RE_FICHIER = re.compile(r"\[\[\s*(?:File|Fichier|Image)\s*:([^\]]*)\]\]", re.I | re.S)
RE_LIEN_CIBLE = re.compile(r"\blink\s*=\s*([^|\]]+)", re.I)


def _sans_fichier(m):
    cible = RE_LIEN_CIBLE.search(m.group(1))
    return " " + cible.group(1).strip() + " " if cible else " "


def plain(t):
    """Reduit un fragment de wikitexte a du texte lisible."""
    t = strip_refs(t)
    for _ in range(3):
        t, n = RE_ENVELOPPE.subn(r"\1", t)
        if not n:
            break
    t = RE_FICHIER.sub(_sans_fichier, t)
    t = re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", t)
    t = re.sub(r"\[\[([^\]|]+)\]\]", r"\1", t)
    for _ in range(3):
        t = re.sub(r"\{\{[^{}]*\}\}", "", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("'''", "").replace("''", "")
    t = re.sub(r"&nbsp;", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

# Quand deux aventuriers d'une saison portent le meme prenom, la source accroche
# au nom une note qui les separe : « Lea<ref name="lea-jaune">De la tribu
# jaune.</ref> ». C'est la source qui desambigue, pas nous -- il suffit de lire
# la note et de la rendre avec le nom qu'elle accompagne.
RE_INDICE_TRIBU = re.compile(
    r"([A-ZÉÈÊÀÂÎÔÛÇ][\wÀ-ÿ'’-]+)\s*<ref[^>]*>\s*De la tribu\s+([a-zà-ÿ]+)", re.I)
# « bleue », « verte » : la tribu est feminine, la couleur du jeu ne l'est pas.
COULEURS_FEMININES = {"bleue": "bleu", "verte": "vert", "violette": "violet",
                      "noire": "noir", "blanche": "blanc", "grise": "gris"}

# Teintes employees par les tableaux pour designer une tribu.
COULEURS_HEX = {
    "#fee347": "jaune", "#ffff00": "jaune", "#fc5d5d": "rouge", "#ff0000": "rouge",
    "#5dadec": "bleu", "#0000ff": "bleu", "#5dce5d": "vert", "#00ff00": "vert",
    "#f39442": "orange", "#ffa500": "orange", "#b25080": "violet", "#800080": "violet",
    "#000000": "noir", "#ffffff": None, "#ececec": None, "#dcdcdc": None,
}

# L'autre facon dont la source separe ses homonymes : elle SURLIGNE le nom a la
# couleur de sa tribu. « {{Surligne|#fee347|Lea}} » vaut la note en toutes
# lettres, et la table des colliers n'emploie que celle-la.
RE_SURLIGNE = re.compile(
    r"\{\{\s*Surlign[ée]e?\s*\|\s*(#[0-9a-fA-F]{3,6})\s*\|\s*([^}|]+?)\s*\}\}", re.I)


# La note de desambiguisation porte un nom, et ce nom dit tout :
# « <ref name="jerome-orange" /> ». Une note ainsi rappelee n'a plus de texte --
# c'est la forme auto-fermante -- mais son nom, lui, voyage avec elle.
RE_NOM_DE_NOTE = re.compile(r"<ref[^>]*\bname\s*=\s*\"?([a-z0-9-]+)\"?", re.I)
COULEURS_CONNUES = {"jaune", "rouge", "bleu", "vert", "orange", "violet", "noir",
                    "blanc", "gris", "rose", "marron"}


def indices_de_tribu(cellule, couleurs_admises=None):
    """{prenom normalise: couleur} — ce que la source dit de ses homonymes.

    Trois ecritures, de la plus sure a la moins sure :

      1. le NOM de la note : « <ref name="jerome-orange" /> ». La source a
         nomme sa note pour separer deux Jerome, et ce nom survit meme quand la
         note est simplement rappelee, sans son texte ;
      2. le TEXTE de la note : « De la tribu jaune » ;
      3. le SURLIGNAGE du nom, a la teinte de sa tribu.

    La troisieme demande une precaution, et elle a ete payee : le surlignage
    suit la tribu du MOMENT, qui apres la reunification n'est plus celle
    d'origine. `couleurs_admises` borne alors la lecture aux couleurs de depart
    de la saison -- sans quoi un Jerome surligne en jaune parce que sa tribu
    reunifiee l'est deviendrait le Jerome de la tribu jaune.
    """
    out = {}
    for m in RE_NOM_DE_NOTE.finditer(cellule or ""):
        tete, _, queue = m.group(1).rpartition("-")
        couleur = COULEURS_FEMININES.get(queue, queue)
        if tete and couleur in COULEURS_CONNUES:
            out[slug(tete)] = couleur
    for m in RE_INDICE_TRIBU.finditer(cellule or ""):
        couleur = m.group(2).lower()
        out.setdefault(slug(m.group(1)), COULEURS_FEMININES.get(couleur, couleur))
    for m in RE_SURLIGNE.finditer(cellule or ""):
        couleur = COULEURS_HEX.get(m.group(1).lower())
        if couleur and (couleurs_admises is None or couleur in couleurs_admises):
            out.setdefault(slug(m.group(2)), couleur)
    return out


def sansaccent(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))

def slug(s):
    s = sansaccent(s).lower().replace("'", "-").replace("’", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")

# --- decoupage du tableau --------------------------------------------------

def split_rows(table):
    """Coupe un wikitableau en lignes, sur les `|-` de premier niveau."""
    rows, buf, t, l = [], [], 0, 0
    for line in table.split("\n"):
        if t == 0 and l == 0 and re.match(r"^\|-", line.strip()):
            rows.append("\n".join(buf)); buf = []
        else:
            buf.append(line)
        t += line.count("{{") - line.count("}}")
        l += line.count("[[") - line.count("]]")
    rows.append("\n".join(buf))
    return rows

def split_cells(row):
    """Coupe une ligne en cellules, sans se laisser piéger par les modeles."""
    cells, buf, t, l = [], None, 0, 0
    for line in row.split("\n"):
        s = line.strip()
        debut = t == 0 and l == 0 and (s.startswith("|") or s.startswith("!"))
        if debut:
            if buf is not None:
                cells.append("\n".join(buf))
            reste = s[1:]
            # « || » sepere deux cellules sur la meme ligne
            morceaux = re.split(r"\|\|", reste)
            buf = [morceaux[0]]
            for m in morceaux[1:]:
                cells.append("\n".join(buf)); buf = [m]
        elif buf is not None:
            buf.append(line)
        t += line.count("{{") - line.count("}}")
        l += line.count("[[") - line.count("]]")
    if buf is not None:
        cells.append("\n".join(buf))
    return [strip_attrs(c) for c in cells]

def strip_attrs(cell):
    """Retire le prefixe d'attributs HTML (`rowspan="3" style="..." |`)."""
    m = re.match(r'^([^|\[{\n]*?)\|(?!\|)', cell)
    if m and "=" in m.group(1):
        return cell[m.end():]
    return cell

# --- motifs de depart ------------------------------------------------------

# (sort normalise, genre implique, expression cherchee dans le libelle)
SORTS = [
    ("vainqueur",            "f", r"gagnante|vainqueure|victorieuse"),
    ("vainqueur",            None, r"vainqueur|gagnant"),
    ("finaliste",            None, r"finaliste"),
    ("elimine_poteaux",      "f", r"elimin[ée]e[^.]*poteaux"),
    ("elimine_poteaux",      "h", r"elimin[ée][^.]*poteaux"),
    ("elimine_orientation",  "f", r"elimin[ée]e[^.]*orientation"),
    ("elimine_orientation",  "h", r"elimin[ée][^.]*orientation"),
    ("elimine_ambassadeurs", "f", r"elimin[ée]e[^.]*ambassadeur"),
    ("elimine_ambassadeurs", "h", r"elimin[ée][^.]*ambassadeur"),
    ("elimine_duel",         "f", r"elimin[ée]e[^.]*(duel|arene|antre|1 contre 1)"),
    ("elimine_duel",         "h", r"elimin[ée][^.]*(duel|arene|antre|1 contre 1)"),
    ("elimine_exil",         "f", r"elimin[ée]e[^.]*(exil|banni)"),
    ("elimine_exil",         "h", r"elimin[ée][^.]*(exil|banni)"),
    # « Echange avec Gregoire » : un seul cas, Palawan 2007. La note de la
    # source ne laisse pas de doute -- « Adrien decide d'abandonner pour
    # permettre a Gregoire de revenir dans le jeu ». C'est donc un abandon
    # volontaire, et le motif d'origine reste lisible dans `motif`.
    ("abandon_volontaire",   None, r"^echange\b"),
    ("abandon_medical",      None, r"abandon m[ée]dical|evacuation|evacue|blessure|raison[s]? m[ée]dicale"),
    ("abandon_volontaire",   None, r"abandon"),
    ("disqualifie",          None, r"disqualifi|exclu|retire de la competition"),
    ("elimine_conseil",      "f", r"elimin[ée]e"),
    ("elimine_conseil",      "h", r"elimin[ée]"),
]

def classify(depart):
    d = sansaccent(depart.lower())
    for sort, genre, motif in SORTS:
        if re.search(motif, d):
            return sort, genre
    return None, None

# --- analyse d'une ligne ---------------------------------------------------

RE_TRIBEBOX  = re.compile(r"\{\{Tribebox-bw\|([^|}]*)", re.I)
RE_TRIBEBOX2 = re.compile(r"\{\{(?:Template:)?Tribebox2\|([^|}]*)\}\}\s*(?:<span[^>]*>([^<]*)</span>)?", re.I)
RE_LINK      = re.compile(r"\[\[([^\]|#]+?)(?:\|([^\]]*?))?\]\]")
RE_SMALL     = re.compile(r"<small>(.*?)</small>", re.S | re.I)
RE_ITAL      = re.compile(r"''(.+?)''", re.S)
RE_AGEPRO    = re.compile(r"^(\d{1,2})\s*ans?\s*[,;]\s*(.+)$", re.S)
RE_JOUR      = re.compile(r"\bJours?\s*(\d{1,2})\b", re.I)
FICHIERS     = ("file:", "fichier:", "image:", "catégorie:", "categorie:", "media:")

def parse_row(row, saison_id=None):
    cells = split_cells(row)
    if not cells:
        return None
    corps = "\n".join(cells)
    if "Tribebox-bw" not in corps:
        return None

    # --- tribu d'origine : la Tribebox-bw, sinon la premiere Tribebox2
    tribu = None
    m = RE_TRIBEBOX.search(corps)
    if m and m.group(1).strip():
        tribu = plain(m.group(1))
    if not tribu:
        for m2 in RE_TRIBEBOX2.finditer(corps):
            nom = plain(m2.group(1) or "") or plain(m2.group(2) or "")
            if nom:
                tribu = nom
                break

    # --- la cellule du nom : la premiere apres celle qui porte la Tribebox-bw
    i_photo = next((i for i, c in enumerate(cells) if "Tribebox-bw" in c), 0)
    cell_nom = cells[i_photo + 1] if i_photo + 1 < len(cells) else ""

    nom_complet = nom_court = None
    for lk in RE_LINK.finditer(cell_nom):
        cible, alias = lk.group(1).strip(), (lk.group(2) or "").strip()
        if cible.lower().startswith(FICHIERS):
            continue
        nom_complet, nom_court = cible, (alias or cible)
        break
    if not nom_complet:
        # Sur les editions de retour, le nom n'est pas lie : il n'apparait que
        # dans le parametre `link=` de la vignette.
        ml = re.search(r"link\s*=\s*([^|\]}]+)", "\n".join(cells[:i_photo + 2]))
        if ml:
            nom_complet = ml.group(1).strip()
            nom_court = nom_complet.split()[0]
    if not nom_complet:
        # nom en texte brut : tout ce qui precede le bloc <small>
        brut = plain(RE_SMALL.sub("", cell_nom))
        brut = re.sub(r"\b\d+px\b.*$", "", brut).strip()
        if brut and "link=" not in brut:
            nom_complet = nom_court = brut
    if not nom_complet:
        return None

    # --- bloc <small> : age + profession, localisation, ou edition d'origine
    age = profession = localisation = edition_origine = None
    for ms in RE_SMALL.finditer(cell_nom):
        interieur = ms.group(1)
        segments = [s for s in (plain(x) for x in RE_ITAL.findall(interieur)) if s]
        if not segments:
            seg = plain(interieur)
            segments = [seg] if seg else []
        for seg in segments:
            ma = RE_AGEPRO.match(seg)
            if ma and age is None:
                age = int(ma.group(1))
                profession = ma.group(2).strip() or None
            elif re.match(r"^\d{1,2}\s*ans?$", seg) and age is None:
                age = int(re.match(r"^(\d{1,2})", seg).group(1))
            elif "koh-lanta" in seg.lower() or re.search(r"saison\s*\d", seg, re.I):
                edition_origine = edition_origine or seg
            elif age is not None and localisation is None:
                localisation = seg
            elif age is None and profession is None and edition_origine is None:
                edition_origine = seg
    if edition_origine is None:
        for lk in RE_LINK.finditer(cell_nom):
            if lk.group(1).lower().startswith("koh-lanta"):
                edition_origine = (lk.group(2) or lk.group(1)).strip()
                break

    # --- cellule de depart : celle qui porte « Jour N » et un libelle
    jour = None
    depart = ""
    for c in cells[i_photo + 1:]:
        texte = plain(c)
        mj = RE_JOUR.search(texte)
        if not mj:
            continue
        if re.search(r"banni|exil|depuis le jour", texte, re.I) and depart:
            continue          # colonne « Ile des bannis », pas le depart
        etiquette = texte[:mj.start()].strip(" -–—:")
        if not etiquette:
            continue
        jour = int(mj.group(1))
        depart = etiquette
        break
    if not depart:
        for c in reversed(cells):
            texte = plain(c)
            if texte and not texte.isdigit() and len(texte) > 3:
                depart = texte
                break

    sort, genre = classify(depart)

    # --- total des votes recus : derniere cellule purement numerique
    votes = None
    for c in cells:
        t = plain(c)
        if re.fullmatch(r"\d{1,3}", t):
            votes = int(t)

    return {
        "id": slug(nom_complet),
        "nom": nom_court,
        "nom_complet": nom_complet,
        "saison": saison_id,
        "age": age,
        "profession": profession,
        "localisation": localisation,
        "edition_origine": edition_origine,
        "tribu": tribu,
        "jour_sortie": jour,
        "sort": sort,
        "genre": genre,
        "motif": depart or None,
        "votes_recus": votes,
    }

def extract_tables(text, titre=r"Candidats?"):
    """Tous les tableaux de la section demandee, dans l'ordre de la page.

    Une section en porte souvent plusieurs : un encart deroulant avant le vrai
    tableau, une annexe apres. S'arreter au premier fait lire l'encart et
    ignorer la donnee -- c'est ce qui arrivait au bilan des epreuves de la
    Revanche des 4 Terres.
    """
    m = re.search(r"^==+\s*" + titre + r"\s*(?:\[[^\]]*\])?\s*==+\s*$",
                  text, re.M | re.I)
    if not m:
        return []
    reste = text[m.end():]
    fin = re.search(r"^==[^=]", reste, re.M)
    section = reste[:fin.start()] if fin else reste
    lignes = section.split("\n")
    tables, i = [], 0
    while i < len(lignes):
        if not lignes[i].lstrip().startswith("{|"):
            i += 1
            continue
        prof, fin_i = 0, len(lignes)
        for j in range(i, len(lignes)):
            nu = lignes[j].lstrip()
            if nu.startswith("{|"):
                prof += 1
            elif nu.startswith("|}"):
                prof -= 1
                if prof == 0:
                    fin_i = j
                    break
        tables.append("\n".join(lignes[i:fin_i]))
        i = fin_i + 1
    return tables


def extract_table(text, titre=r"Candidats?"):
    """Isole le premier tableau de la section demandee."""
    # Certaines pages portent du texte d'interface colle au titre
    # (« Bilan par épisode[modifier | modifier le code] ») : on l'ignore.
    m = re.search(r"^==+\s*" + titre + r"\s*(?:\[[^\]]*\])?\s*==+\s*$",
                  text, re.M | re.I)
    if not m:
        return None
    reste = text[m.end():]
    fin = re.search(r"^==[^=]", reste, re.M)
    section = reste[:fin.start()] if fin else reste
    # En wikitexte, `{|` et `|}` ne delimitent un tableau qu'en debut de ligne.
    # Le chercher n'importe ou fait fermer le tableau sur un `{{Modele|}}`.
    lignes = section.split("\n")
    debut = next((i for i, l in enumerate(lignes) if l.lstrip().startswith("{|")), None)
    if debut is None:
        return None
    prof, fin = 0, len(lignes)
    for i in range(debut, len(lignes)):
        nu = lignes[i].lstrip()
        if nu.startswith("{|"):
            prof += 1
        elif nu.startswith("|}"):
            prof -= 1
            if prof == 0:
                fin = i
                break
    return "\n".join(lignes[debut:fin])

def parse_page(text, saison_id=None):
    table = extract_table(text)
    if table is None:
        return []
    out = []
    for row in split_rows(table):
        if "Tribebox-bw" not in row:
            continue
        p = parse_row(row, saison_id)
        if p:
            out.append(p)
    return out

if __name__ == "__main__":
    import json, os
    for path in sys.argv[1:]:
        sid = os.path.basename(path).split(".")[0]
        print(json.dumps(parse_page(open(path, encoding="utf-8").read(), sid),
                         ensure_ascii=False, indent=1))
