"""Lit les pages individuelles Fandom et en tire un enregistrement par
(personne, saison).

Les pages de saison ne portent ni la residence, ni le detail des tribus avec
leurs jours, ni le compte des victoires par edition. L'`Infobox Aventuriers`
des pages individuelles porte tout cela. Ce module ne fait que LIRE et
normaliser : c'est fusionner.py qui decide quoi retenir.

La saisie y est libre, donc irreguliere : casse flottante des cles, champs
concatenes sur une meme ligne, tribus notees « (Jour 1 - 9) » ou « [1-7] ».
Tout ce qui n'est pas reconnu avec certitude est laisse de cote plutot que
devine -- la regle du depot.
"""
import hashlib, json, os, re, unicodedata
import yaml

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGES = os.path.join(RACINE, "specs", "sources", "personnes")

# Les titres Fandom des saisons, tels qu'ils apparaissent dans les liens de
# l'infobox et dans les parentheses du champ « Situation Geographique ».
TITRES = {
    "s01": ["les aventuriers de koh-lanta", "les aventuriers de koh-lanta (saison 1)", "saison 1"],
    "s02": ["nicoya"], "s03": ["bocas del toro"], "s04": ["panama"],
    "s05": ["pacifique"], "s06": ["vanuatu"], "s07": ["palawan"],
    "s08": ["caramoan"], "s09": ["palau"], "s10": ["vietnam"],
    "s11": ["raja ampat"], "s12": ["malaisie"], "s14": ["johor"],
    "s15": ["thailande"], "s16": ["l'ile au tresor", "l'ile au tresor (saison 16)"],
    "s17": ["cambodge"], "s18": ["fidji"], "s20": ["la guerre des chefs"],
    "s21": ["les 4 terres"], "s22": ["les armes secretes"],
    "s23": ["le totem maudit"], "s24": ["le feu sacre"],
    "s25": ["les chasseurs d'immunite"], "s26": ["la tribu maudite"],
    "s27": ["la revanche des 4 terres"], "s28": ["les reliques du destin"],
    "sp1": ["le retour des heros"], "sp2": ["le choc des heros"],
    "sp3": ["la revanche des heros"], "sp4": ["la nouvelle edition"],
    "sp5": ["le combat des heros"], "sp6": ["l'ile des heros"],
    "sp7": ["la legende"], "sp8": ["all stars", "all-stars", "all stars (2026)"],
}

RE_MODELE = re.compile(r"\{\{\s*Infobox[ _]Aventuriers(.*)", re.I | re.S)
RE_CLE = re.compile(r"\|\s*([^=|{}\[\]\n]{2,40}?)\s*=")
RE_LIEN = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")
RE_JOURS = re.compile(r"[\(\[]\s*jours?\s*(\d+)\s*[-–]\s*(\d+)\s*[\)\]]", re.I)
RE_JOURS_NU = re.compile(r"[\(\[]\s*(\d+)\s*[-–]\s*(\d+)\s*[\)\]]")


def sansaccents(t):
    t = unicodedata.normalize("NFD", t or "")
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


SAISON_DE = {}
for sid, noms in TITRES.items():
    for n in noms:
        SAISON_DE[sansaccents(n)] = sid


def _saison(texte):
    """Rend l'identifiant de saison designe par un libelle ou un lien."""
    if not texte:
        return None
    m = RE_LIEN.search(texte)
    if m:
        for bout in (m.group(2), m.group(1)):
            if not bout:
                continue
            cle = sansaccents(bout).replace("koh-lanta :", "").replace("koh-lanta:", "").strip()
            if cle in SAISON_DE:
                return SAISON_DE[cle]
    cle = sansaccents(texte).replace("koh-lanta :", "").replace("koh-lanta:", "").strip()
    return SAISON_DE.get(cle)


def _decouper_modele(texte):
    """Rend {cle normalisee: valeur} pour l'infobox, cles a rang compris.

    On ne peut pas couper sur « | » : les liens et les tableaux en contiennent.
    On repere donc les cles « |Nom = » et on prend tout jusqu'a la suivante.
    """
    m = RE_MODELE.search(texte)
    if not m:
        return {}
    corps = m.group(1)
    # Couper au }} de fermeture du modele, en tenant compte des {{ imbriques.
    profondeur, fin = 1, len(corps)
    i = 0
    while i < len(corps) - 1:
        if corps[i:i + 2] == "{{":
            profondeur += 1; i += 2; continue
        if corps[i:i + 2] == "}}":
            profondeur -= 1
            if profondeur == 0:
                fin = i; break
            i += 2; continue
        i += 1
    corps = corps[:fin]

    champs, marques = {}, list(RE_CLE.finditer(corps))
    for k, mk in enumerate(marques):
        borne = marques[k + 1].start() if k + 1 < len(marques) else len(corps)
        champs[mk.group(1).strip()] = corps[mk.end():borne].strip()
    return champs


def _rang(cle):
    """« Tribu3 » -> ('tribu', 3) ; « Tribu » -> ('tribu', 1)."""
    c = sansaccents(cle).replace("-", " ")
    c = re.sub(r"\s+", " ", c).strip()
    m = re.match(r"^(.*?)\s*(\d+)$", c)
    if m:
        return m.group(1).strip(), int(m.group(2))
    return c, 1


ALIAS = {
    "situation geographique": "localisation",
    "cause du depart": "sort",
    "victoires en equipe": "victoires_collectives",
    "victoires individuelles": "victoires_individuelles",
    "votes contre": "votes_recus",
    "nombre de jours a koh lanta": "jours",
    "nombre de jours a koh-lanta": "jours",
    "classement": "classement",
    "tribu": "tribu",
    "saison": "saison",
    "profession": "profession",
    "age": "age",
    "prenom": "prenom",
}


def _propre(v):
    v = re.sub(r"<ref[^>]*>.*?</ref>", " ", v or "", flags=re.S | re.I)
    v = re.sub(r"<!--.*?-->", " ", v, flags=re.S)
    v = re.sub(r"'{2,}", "", v)
    return re.sub(r"[ \t]+", " ", v).strip()


def _entier(v):
    m = re.search(r"-?\d+", _propre(v).replace("&nbsp;", " "))
    return int(m.group(0)) if m else None


def _classement(v):
    m = re.search(r"(\d+)\s*(?:e|er|eme|ème)?\s*(?:/|sur)\s*(\d+)", sansaccents(_propre(v)))
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def _lignes(v):
    """Coupe une valeur multi-lignes : <br/>, retours a la ligne, puces."""
    # Le wiki ecrit <br>, <br/>, mais aussi </br> : les trois coupent la ligne.
    v = re.sub(r"<\s*/?\s*br\s*/?\s*>", "\n", _propre(v), flags=re.I)
    return [re.sub(r"^[\*#]+", "", l).strip("  ") for l in v.split("\n") if l.strip(" *# ")]


def _parcours(v):
    """« Paniman (Jour 1-23)<br/>Tribu réunifiée (Jour 23-29) » -> etapes."""
    etapes = []
    for ligne in _lignes(v):
        m = RE_JOURS.search(ligne) or RE_JOURS_NU.search(ligne)
        nom = RE_LIEN.sub(lambda x: x.group(2) or x.group(1), ligne)
        if m:
            nom = nom[:m.start()] if m.start() < len(nom) else nom
        nom = nom.strip(" ()[]-–,;:")
        if not nom:
            continue
        etapes.append({"tribu": nom,
                       "jour_debut": int(m.group(1)) if m else None,
                       "jour_fin": int(m.group(2)) if m else None})
    return etapes


def _par_saison(v, saisons_du_rang):
    """Champ global module par saison : « Ain (Raja Ampat)<br/>Hérault (La Légende) ».

    Rend {sid: valeur} pour les segments etiquetes, et {None: valeur} pour un
    segment sans parenthese -- la valeur par defaut.
    """
    sortie = {}
    for ligne in _lignes(v):
        m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", ligne)
        if not m:
            val = ligne.strip()
            if val:
                sortie.setdefault(None, val)
            continue
        val, etiquettes = m.group(1).strip(), m.group(2)
        cibles = [s for s in (_saison(e) for e in re.split(r",| et | & |/", etiquettes)) if s]
        if cibles:
            for s in cibles:
                sortie[s] = val
        elif val:
            sortie.setdefault(None, val)
    return sortie


def lire(chemin, personne):
    """Rend {sid: {champ: valeur}} pour une page individuelle.

    `personne` est l'enregistrement de personnes.yml : sa liste
    `participations` sert de repli quand l'infobox ne nomme pas les saisons.
    """
    texte = open(chemin, encoding="utf-8").read()
    champs = _decouper_modele(texte)
    if not champs:
        return {}, []

    groupes, globaux, alertes = {}, {}, []
    for cle, brut in champs.items():
        nom, rang = _rang(cle)
        nom = ALIAS.get(nom)
        if not nom or not _propre(brut):
            continue
        if nom in ("localisation", "age", "profession", "prenom"):
            globaux.setdefault(nom, brut)
            continue
        groupes.setdefault(rang, {}).setdefault(nom, brut)

    # Le rang n -> une saison. D'abord par le champ « Saison{n} », sinon, si
    # la personne n'a joue qu'une saison, par elimination.
    saison_du_rang = {}
    for rang, g in groupes.items():
        s = _saison(g.get("saison", ""))
        if s:
            saison_du_rang[rang] = s
    connues = list(personne.get("participations") or [])
    # Les rangs que l'infobox ne nomme pas. On ne les attribue que si le compte
    # tombe juste : autant de rangs muets que de saisons non encore prises. Le
    # rang suit alors l'ordre chronologique, convention constante du wiki.
    muets = sorted(r for r in groupes if r not in saison_du_rang)
    libres = [s for s in connues if s not in saison_du_rang.values()]
    if muets and len(muets) == len(libres):
        for rang, sid in zip(muets, libres):
            saison_du_rang[rang] = sid
            alertes.append(f"{personne['id']} rang {rang} : saison {sid} deduite du rang")

    sortie = {}
    for rang, g in sorted(groupes.items()):
        sid = saison_du_rang.get(rang)
        if not sid:
            if g.keys() - {"saison"}:
                alertes.append(f"{personne['id']} rang {rang} : saison non identifiee")
            continue
        if sid not in connues:
            alertes.append(f"{personne['id']} rang {rang} : saison {sid} absente de ses participations")
            continue
        r = {}
        if "tribu" in g:
            etapes = _parcours(g["tribu"])
            if etapes:
                r["parcours"] = etapes
        if "sort" in g:
            r["motif"] = _propre(RE_LIEN.sub(lambda x: x.group(2) or x.group(1), g["sort"]))
        for champ in ("victoires_collectives", "victoires_individuelles", "votes_recus", "jours"):
            if champ in g:
                n = _entier(g[champ])
                if n is not None and 0 <= n <= 100:
                    r[champ] = n
        if "classement" in g:
            place, sur = _classement(g["classement"])
            if place:
                r["classement"], r["classement_sur"] = place, sur
        if r:
            sortie[sid] = r

    # Les champs globaux, eventuellement module par saison.
    for champ in ("localisation", "profession"):
        if champ not in globaux:
            continue
        valeurs = _par_saison(globaux[champ], saison_du_rang)
        defaut = valeurs.get(None)
        for sid in connues:
            v = valeurs.get(sid, defaut)
            if v:
                v = RE_LIEN.sub(lambda x: x.group(2) or x.group(1), v).strip(" .,;")
                if v:
                    sortie.setdefault(sid, {})[champ] = v
    if "age" in globaux:
        valeurs = _par_saison(globaux["age"], saison_du_rang)
        for sid in connues:
            v = valeurs.get(sid)
            if v is None and len(connues) == 1:
                v = valeurs.get(None)
            n = _entier(v) if v else None
            if n and 15 <= n <= 90:
                sortie.setdefault(sid, {})["age"] = n
    return sortie, alertes


RE_TITRE = re.compile(r"\{\{\s*DISPLAYTITLE\s*:\s*([^}]+)\}\}", re.I)
RE_GRAS = re.compile(r"'''([^']{3,60})'''")


def nom_canonique(texte):
    """Le nom que la page se donne : DISPLAYTITLE, sinon le premier gras.

    Sert a departager deux enregistrements qui pointent la meme page --
    « Phil Bizet » et « Philippe Bizet » sont une redirection l'un de l'autre,
    et la page dit lequel des deux est le nom.
    """
    m = RE_TITRE.search(texte)
    if m:
        return m.group(1).strip()
    corps = texte[texte.find("}}"):] if "{{" in texte[:200] else texte
    m = RE_GRAS.search(corps)
    if m and " " in m.group(1):
        return m.group(1).strip()
    return None


def empreinte(texte):
    return hashlib.md5(texte.encode("utf-8")).hexdigest()


def chemin_page(pid):
    return os.path.join(PAGES, pid + ".fandom.wiki")


def categories():
    """{sid: [titres de pages Fandom classees dans cette saison]}."""
    f = os.path.join(PAGES, "_categories.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}


def tout(personnes=None):
    """Rend ({(id, saison): champs}, alertes).

    `personnes` est une liste d'enregistrements {id, participations}. Par
    defaut on lit _data/personnes.yml, mais fusionner.py passe sa propre liste
    en cours de construction : le fichier n'existe pas encore a ce moment-la.
    """
    if personnes is None:
        personnes = yaml.safe_load(open(os.path.join(RACINE, "_data", "personnes.yml"), encoding="utf-8"))
    lu, alertes = {}, []
    for p in personnes:
        chemin = chemin_page(p["id"])
        if not os.path.exists(chemin):
            continue
        r, a = lire(chemin, p)
        alertes += a
        for sid, champs in r.items():
            lu[(p["id"], sid)] = champs
    return lu, alertes


if __name__ == "__main__":
    import collections
    lu, alertes = tout()
    print(f"{len(lu)} couples (personne, saison) lus")
    c = collections.Counter()
    for champs in lu.values():
        for k in champs:
            c[k] += 1
    for k, n in c.most_common():
        print(f"  {k:24s} {n}")
    print(f"\n{len(alertes)} alertes")
    for a in alertes[:25]:
        print("  ", a)
