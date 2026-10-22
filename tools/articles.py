"""Les chiffres des articles, mis en forme pour etre lus tels quels.

Les articles (`_posts/`) s'appuient sur les donnees sans les presenter : ils
citent une poignee de resultats du registre des tests, et doivent rester justes
quand une saison s'ajoute. Ils lisent donc leurs chiffres ici, dans
`stats.articles`, deja ecrits a la francaise -- le gabarit ne calcule ni ne
formate rien.

Un chiffre qui bouge peut faire mentir la phrase qui l'entoure : « n'est pas
confirmee » ecrit en toutes lettres ne suit pas la p-valeur. Chaque test cite
porte donc ce que le TEXTE en affirme (`AFFIRMATIONS`), et `conforme` dit si
les donnees le disent encore. `tools/verifie_site.py` refuse un article dont
une affirmation ne tient plus : il faut alors relire la phrase, pas le chiffre.

Une seule mesure est propre aux articles : la frequence des issues d'un
conseil (`issues`). Toutes les autres viennent du registre publie.
"""
import datetime
import os
import re
from collections import Counter

# Ce que le texte des articles affirme de chaque test qu'il cite :
# (retenu apres correction, sens de l'ecart observe). `None` : le texte ne dit
# rien du sens. Changer une phrase des articles, c'est changer cette table.
AFFIRMATIONS = {
    "vote_isole": (True, "+"),             # perdre son dernier allie expose
    "persistance_alliances": (True, "+"),  # les alliances durent
    "trahison": (True, "-"),               # on vise moins un ancien co-votant
    "retour_de_baton": (True, "+"),        # la cible d'hier rend la pareille
    "menace_voix": (True, "+"),            # vise hier, sorti demain
    "cible_persistante": (True, "+"),      # vise hier, vise encore
    "menace_sommet": (False, None),        # la menace n'a pas de sommet
    "vote_bandeau_apres_fusion": (True, "-"),  # le camp d'origine protege
    "decimation": (True, "+"),             # les sorties s'enchainent par camp
    "bandeau_minoritaire": (True, "+"),    # le camp minoritaire expose
    "sexe_minoritaire": (True, "-"),       # le sexe minoritaire protege
    "camp_perdant": (True, "+"),           # voter avec la minorite expose (de justesse, 21 oct. 2026)
    "fusion_serre": (True, "+"),           # le vote se divise apres la reunification
    "fusion_sexe": (True, "-"),            # moins de femmes eliminees ensuite
    "fusion_force": (False, None),         # la competence n'est pas une menace
    "age_bascule_fusion": (False, "+"),    # meme sens, mais sous le seuil (21 oct. 2026)
    "ambassadeurs_force": (False, None),   # les ambassadeurs ne visent pas les forts
    "ambassadeurs_survie": (True, "-"),    # plus tot, de justesse (4e bascule, 22 oct. 2026)
    "prevision_conseil": (True, "-"),      # le modele voit venir la sortie
    "pronostic_vainqueur": (False, None),  # le profil ne designe pas le vainqueur
}

# Les tests dont la statistique est une DIFFERENCE : elle s'affiche signee, et
# le texte en cite la valeur absolue, « augmente de 18,6 points », le verbe
# portant le sens. Une liste de cles et non une regle sur l'unite : « points de
# rang » designe une difference pour `fusion_force` et un niveau pour
# `ambassadeurs_force`, qui afficherait alors « +48,5 ».
DIFFERENCES = {"vote_isole", "persistance_alliances", "menace_voix", "cible_persistante",
               "menace_sommet", "bandeau_minoritaire", "sexe_minoritaire", "camp_perdant",
               "fusion_serre", "fusion_sexe", "fusion_force", "age_bascule_fusion"}


def decimal(x, n=1):
    """32.7 -> « 32,7 ». Meme regle que `decimal()` de build_fiches.py : la
    virgule, et pas de zero inutile -- « 37 », pas « 37,0 »."""
    x = round(float(x), n)
    if x == int(x):
        return str(int(x))
    return f"{x:.{n}f}".rstrip("0").replace(".", ",")


def signe(x, n=1):
    """+18,6 / −5,4 : le signe moins typographique, pas le trait d'union."""
    t = decimal(abs(x), n)
    if t == "0":
        return t        # un « +0 » se lirait comme un ecart
    return ("+" if x > 0 else "−" if x < 0 else "") + t


def milliers(n):
    """3470 -> « 3 470 », espace insecable."""
    return f"{int(n):,}".replace(",", " ")


def p_texte(p):
    """La p ajustee comme le registre la publie : « 0,0006 », « 0,37 »."""
    if p >= 0.01:
        return decimal(p, 2)
    return decimal(p, 4)


def bloc_test(t):
    retenu_dit, sens_dit = AFFIRMATIONS[t["cle"]]
    obs, att = float(t["observe"]), float(t["attendu"])
    sens = "+" if obs > att else "-"
    ecart = t["cle"] in DIFFERENCES
    n = 3 if abs(obs) < 1 else 1
    conforme = (bool(t["retenu"]) == retenu_dit
                and (sens_dit is None or sens_dit == sens))
    return {
        "observe": signe(obs, n) if ecart else decimal(obs, n),
        "attendu": signe(att, n) if ecart else decimal(att, n),
        # la valeur citee dans une phrase : sans signe, le verbe le porte
        "valeur": decimal(abs(obs), n),
        "valeur_ronde": decimal(abs(obs), 0),
        "attendu_rond": decimal(abs(att), 0),
        "p": p_texte(float(t["p_ajustee"])),
        "retenu": bool(t["retenu"]),
        "conforme": conforme,
        "affirme": ("retenu" if retenu_dit else "non retenu")
                   + (f", ecart {sens_dit}" if sens_dit else ""),
    }


def issues(conseils, par_saison):
    """La frequence des quatre issues d'un conseil d'elimination.

    L'unite est le conseil DECISIF -- celui dont sort un elimine rattache --
    sur les saisons terminees. Un soir peut compter plusieurs conseils : on ne
    lit que le conseil immediatement precedent, jamais le seul `episode`.

    - egalite puis second vote : le conseil precedent, le meme soir, est un
      tour nul (annulation totale) ou un tour sans elimine ; ou bien la boule
      noire a tranche (`tirage`) -- elle ne se tire qu'apres un second vote
      reste a egalite --, ou bien la source atteste le second tour
      (`second_tour`) que la matrice ne montre pas ;
    - renversement : un objet a annule des voix, un seul protege, et sans
      l'objet ce protege en aurait recu plus que l'elimine ;
    - egalite tranchee : le conseil decisif finit lui-meme a egalite en tete,
      tranchee sans second vote ;
    - ordinaire : tout le reste.

    Un conseil decisif sans aucun bulletin n'est pas classe : la source ne dit
    pas comment on est sorti.
    """
    par_num = {(c["saison"], c["numero"]): c for c in conseils}
    compte, sans_bulletin = Counter(), 0
    for c in conseils:
        if c.get("type", "elimination") != "elimination" or not c.get("elimine_rattache"):
            continue
        if par_saison.get(c["saison"], {}).get("en_cours"):
            continue
        if not c.get("votes"):
            sans_bulletin += 1
            continue
        prec = par_num.get((c["saison"], c["numero"] - 1))
        tour_nul = c.get("tirage") or c.get("second_tour") or (
            prec is not None and prec.get("type", "elimination") == "elimination"
            and prec.get("episode") == c.get("episode")
            and (prec.get("annulation") == "totale" or prec.get("sans_elimination")))
        renverse = False
        if c.get("annulation") == "partielle" and len(c.get("proteges") or []) == 1:
            p = c["proteges"][0]
            brut = Counter(b["cible"] for b in c["votes"] if b.get("cible"))
            renverse = p != c["elimine"] and brut[p] > brut[c["elimine"]]
        tete = Counter(b["cible"] for b in c["votes"]
                       if b.get("cible") and not b.get("annule")).most_common(2)
        bloque = len(tete) == 2 and tete[0][1] == tete[1][1]
        compte["egalite_revote" if tour_nul else "renversement" if renverse
               else "egalite_tranchee" if bloque else "ordinaire"] += 1
    n = sum(compte.values())
    out = {"conseils": milliers(n), "sans_bulletin": milliers(sans_bulletin)}
    for k in ("ordinaire", "egalite_revote", "renversement", "egalite_tranchee"):
        out[k] = decimal(100.0 * compte[k] / n) if n else None
    out["ordinaire_rond"] = decimal(100.0 * compte["ordinaire"] / n, 0) if n else None
    return out


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
RACINE_ARTICLES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def date_fr(jour):
    """« 1er octobre 2026 », « 17 octobre 2026 ». Le gabarit indexait une
    liste de mois en Liquid, avec un `minus: 1` ; c'est ici que la date
    s'ecrit, et le premier du mois prend son « er »."""
    numero = "1er" if jour.day == 1 else str(jour.day)
    return f"{numero} {MOIS[jour.month - 1]} {jour.year}"


def dates_des_articles():
    """La date de chaque article, par adresse : `date:` du front matter, a
    defaut le prefixe AAAA-MM-JJ du nom de fichier dans _posts/."""
    dates = {}
    for dossier in ("_posts", "_drafts"):
        chemin_dossier = os.path.join(RACINE_ARTICLES, dossier)
        if not os.path.isdir(chemin_dossier):
            continue
        for nom in sorted(os.listdir(chemin_dossier)):
            if not nom.endswith(".md"):
                continue
            texte = open(os.path.join(chemin_dossier, nom), encoding="utf-8").read()
            entete = texte.split("---", 2)[1] if texte.startswith("---") else ""
            lien = re.search(r"^permalink:\s*(\S+)", entete, re.M)
            quand = re.search(r"^date:\s*(\d{4})-(\d{2})-(\d{2})", entete, re.M) \
                or re.match(r"(\d{4})-(\d{2})-(\d{2})-", nom)
            if lien and quand:
                jour = datetime.date(*(int(x) for x in quand.groups()))
                dates[lien.group(1)] = {"iso": jour.isoformat(), "texte": date_fr(jour)}
    return dates


def en_ans(x):
    """« 1,4 an », « 2,0 ans » : le pluriel commence a deux."""
    return f"{decimal(abs(x))} {'an' if abs(x) < 2 else 'ans'}"


def tout(stats, conseils, par_saison):
    g, c, m = stats["general"], stats["conseils"], stats["modeles"]
    registre = {t["cle"]: t for t in m["registre"]}
    manquants = sorted(set(AFFIRMATIONS) - set(registre))
    if manquants:
        raise SystemExit(f"articles : tests cites absents du registre : {manquants}")
    aa = m["avant_apres"]
    return {
        "dates": dates_des_articles(),
        "saisons": milliers(g["saisons_diffusees"]),
        "aventuriers": milliers(g["personnes"]),
        "conseils": milliers(c["conseils"]),
        "conseils_complets": milliers(c["conseils_complets"]),
        "conseils_incomplets": milliers(c["conseils"] - c["conseils_complets"]),
        "participations": milliers(g["participations"]),
        "bulletins": milliers(c["bulletins"]),
        "nb_tests": milliers(m["nb_tests"]),
        "nb_retenus": milliers(m["nb_retenus"]),
        "force": {
            "rang_avant": decimal(aa["rang_force_avant"]),
            "rang_apres": decimal(aa["rang_force_apres"]),
            "conseils_avant": milliers(aa["force_effectif_avant"]),
            "conseils_apres": milliers(aa["force_effectif_apres"]),
            "epreuves": milliers(m["force"]["epreuves_retenues"]),
            "saisons": milliers(m["force"]["saisons_retenues"]),
        },
        # 6.3 : l'ecart d'age de l'elimine a la moyenne de son camp, avant et
        # apres la reunification (valeurs absolues : la phrase porte le sens).
        "age": {
            "avant": en_ans(m["age_au_conseil"]["ecart_avant"]),
            "apres": en_ans(m["age_au_conseil"]["ecart_apres"]),
            "bascule": en_ans(float(registre["age_bascule_fusion"]["observe"])),
            "conseils": milliers(m["age_au_conseil"]["conseils"]),
        },
        "issues": issues(conseils, par_saison),
        "tests": {cle: bloc_test(registre[cle]) for cle in AFFIRMATIONS},
    }
