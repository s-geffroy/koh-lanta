#!/usr/bin/env python3
"""Croise les deux sources et ecrit _data/participations.yml et personnes.yml.

Aucune des deux sources ne suffit seule :

  * le wiki Fandom couvre les 34 saisons et donne le nom complet, l'age, la
    profession et le total des voix recues, mais sa table est incomplete sur
    six saisons et il ne dit le sexe que par l'accord du participe ;
  * Wikipedia en francais ne couvre que quinze saisons, mais sa table est
    complete, donne le sexe en clair et borne l'appartenance aux tribus en
    jours -- donc la trajectoire.

Pour chaque saison, la source de reference est celle dont l'effectif tombe
juste ; l'autre vient completer, champ par champ. Chaque valeur retenue garde
la trace de sa provenance dans `sources`.
"""
import collections
import os
import re
import sys
import unicodedata

# Le module qui ecrit et relit _data/ (virgule decimale), dans tools/.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import donnees  # noqa: E402
from coquilles import corriger  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))

import parse_fandom as F
import parse_wikipedia_fr as W
import parse_personnes as I
import lieux

# Wikitexte brut des pages sources, tel que recupere par specs/sources/fetch*.py.
# Hors du site publie : `specs/` est dans la liste `exclude:` de _config.yml.
WIKI = os.environ.get("KL_WIKI", os.path.join(RACINE, "specs", "sources", "wiki"))

# Ordre de preference par champ. « w » = Wikipedia fr, « f » = Fandom.
PREFERENCE = {
    "genre":         ["w", "f"],
    "age":           ["w", "f"],
    "profession":    ["w", "f"],
    "localisation":  ["w", "f"],
    "tribu":         ["w", "f"],
    "couleur":       ["w"],
    "parcours":      ["w"],
    # Le jour lu chez Wikipedia est celui de la derniere bascule de tribu, pas
    # celui du depart : sur une saison entiere il vaut le jour de reunification
    # pour tout le monde. Fandom donne le jour de sortie en clair.
    "jour_sortie":   ["f", "w"],
    # Wikipedia dit « Éliminé » tout court ; Fandom precise « aux poteaux »,
    # « a l'orientation », « aux ambassadeurs ». La nuance porte des statistiques
    # entieres, elle prime.
    "sort":          ["f", "w"],
    "motif":         ["f", "w"],
    "nom_complet":   ["f"],
    "votes_recus":   ["f"],
    "edition_origine": ["f"],
}

LIBELLE = {
    "w": "wikipedia-fr",
    "f": "fandom",
}

# Les coquilles de la source, corrigees nommement. Chaque ligne est un fait
# verifiable dans le wikitexte lui-meme, pas une correction d'usage : sur
# La Nouvelle Edition, la table ecrit « [[Philippe Duron|Phiippe]] » -- le
# libelle affiche perd un « l » que la cible du lien porte, et que toutes les
# autres cellules de la meme page ecrivent correctement. Sans cela, « Phiippe »
# entre dans la comparaison des prenoms avec le fichier INSEE.
# Ce qu'une source ecrit quand l'aventure n'est pas finie pour cette personne.
# C'est une AFFIRMATION, pas une absence : elle prime sur tout sort deduit
# ailleurs.
RE_EN_JEU = re.compile(r"encore en jeu|toujours en jeu", re.I)

COQUILLES = {
    ("sp4", "Phiippe"): "Philippe",
}

# LES NOMS QUE LES TABLES DE SAISON POINTENT PAR UNE REDIRECTION. Le lien
# « [[Lola Besse|Lola]] » du tableau d'All Stars ne mene pas a une page
# intitulee « Lola Besse » : l'API Fandom repond que ce titre REDIRIGE vers
# « Lola Labesse », et c'est ce que son article ecrit de lui-meme -- « Lola
# Labesse, nee le 12 mars 1996 ». Le site publiait donc un nom que sa propre
# source a corrige, dans le H1 comme dans l'adresse.
#
# UNE TABLE ET NON UNE REGLE, et c'est delibere. Onze noms du site sont des
# redirections ; le titre canonique n'est pas toujours le meilleur nom a
# PUBLIER. « Philippe Bizet » redirige vers « Phil Bizet » : la page est bien
# la meme personne, mais un diminutif ne remplace pas un prenom dans un H1.
# Adopter mecaniquement le titre canonique aurait rebaptise onze fiches, dont
# celle-la. Chaque entree est donc verifiee et voulue.
#
# Verifier une redirection, avant d'ajouter une ligne :
#   action=query&titles=<nom>&redirects=1  sur kohlanta.fandom.com/fr/api.php
#
# « Philippe Bizet » -> « Phil Bizet » est la SEULE des onze redirections
# qu'on n'applique pas, et son absence est voulue : voir ci-dessus.
NOMS_CANONIQUES = {
    "Carinne Fossey Elka": "Carinne Elka-Dioza",
    "Charlène Hoffness": "Charlène Hoffsess",
    "Fouzi de la Fuente": "Fouzi Ould Bouamama",
    "François-Xavier Arguillère": "François-Xavier Renou",
    "Julie Navarro-Camilleri": "Julie Navarro",
    "Lola Besse": "Lola Labesse",
    "Marie Boyer": "Marie Besnier",
    "Marta Morino": "Marta Molino",
    # Le seul qui ne change PAS d'identifiant : la translitteration efface
    # l'accent, « Matteo » et « Mattéo » donnent tous deux `matteo-real`.
    # L'adresse ne bouge pas, le nom affiche si.
    "Matteo Real": "Mattéo Real",
    "Nicolas Leoni": "Nicolas Roy",
}

# Une tribu nommee par erreur. La legende de la fiche francaise de
# La Revanche des Heros ecrit « Mawar (jour 1 - 6) » a la teinte #fc5d5d, qui
# est celle de Nekmao dans cette meme legende -- et « Mawar » est le nom de la
# tribu rouge de Malaisie, une autre saison. Les deux autres sources, la fiche
# anglaise et le wiki Fandom, ne connaissent que Klahan et Nekmao. Deux sources
# contre une, et la couleur pour arbitre : la correction est ecrite ici plutot
# que subie a chaque lecture.
TRIBUS_FAUTIVES = {
    ("sp3", "Mawar"): "Nekmao",
}


def cle(nom):
    return F.slug(nom or "")

def indexer(rows):
    """Index par prenom. Les homonymes d'une meme saison sont conserves."""
    idx = {}
    for r in rows:
        idx.setdefault(cle(r.get("nom")), []).append(r)
    return idx


def mots(texte):
    return {m for m in re.split(r"\W+", (texte or "").lower()) if len(m) > 3}


def apparier(r, candidats):
    """Choisit, parmi des homonymes, celui qui est la meme personne.

    Deux Lea en saison 25, deux Cecile en 26, deux Jerome en 27 : ce sont bien
    des personnes differentes, pas des doublons. Le prenom ne suffit donc pas.
    L'age les separe sans ambiguite dans tous les cas rencontres ; le metier
    sert de second recours.
    """
    if len(candidats) == 1:
        return candidats[0]

    def score(c):
        s = 0
        if r.get("age") and c.get("age"):
            s += 100 if r["age"] == c["age"] else -abs(r["age"] - c["age"])
        communs = mots(r.get("profession")) & mots(c.get("profession"))
        s += 10 * len(communs)
        if r.get("jour_sortie") and c.get("jour_sortie") and r["jour_sortie"] == c["jour_sortie"]:
            s += 5
        return s

    classes = sorted(candidats, key=score, reverse=True)
    if len(classes) > 1 and score(classes[0]) == score(classes[1]):
        return None          # indepartageable : on prefere ne rien croiser
    return classes[0]

def fusionner_saison(saison, rows_f, rows_w, rapport, saisons_connues=()):
    sid = saison["id"]
    attendu = saison.get("nb_candidats") or 0

    # source de reference : celle dont l'effectif tombe juste
    if len(rows_w) == attendu and rows_w:
        base_code, base, autre_code, autre = "w", rows_w, "f", rows_f
    elif len(rows_f) == attendu and rows_f:
        base_code, base, autre_code, autre = "f", rows_f, "w", rows_w
    else:
        if len(rows_w) >= len(rows_f):
            base_code, base, autre_code, autre = "w", rows_w, "f", rows_f
        else:
            base_code, base, autre_code, autre = "f", rows_f, "w", rows_w
        rapport.append(
            f"{sid} : aucune source ne donne l'effectif attendu ({attendu}) — "
            f"fandom={len(rows_f)}, wikipedia={len(rows_w)} ; "
            f"reference = {LIBELLE[base_code]}")

    idx_autre = indexer(autre)
    couleurs = {F.slug(t["nom"]): t.get("couleur") for t in saison.get("tribus", [])}

    out = []
    for r in base:
        k = cle(r.get("nom"))
        jumeau = None
        if k in idx_autre:
            jumeau = apparier(r, idx_autre[k])
            if jumeau is None:
                rapport.append(f"{sid} : « {r.get('nom')} » a un homonyme dans la "
                               f"saison et rien ne les departage")

        dispo = {base_code: r}
        if jumeau:
            dispo[autre_code] = jumeau

        fiche = {champ: None for champ in PREFERENCE}
        provenance = {}
        for champ, ordre in PREFERENCE.items():
            for code in ordre:
                src = dispo.get(code)
                if src and src.get(champ) not in (None, "", []):
                    fiche[champ] = src[champ]
                    provenance[champ] = LIBELLE[code]
                    break

        # Sur les editions de retour, la colonne « profession » porte parfois
        # l'edition d'origine (« Palawan », « Pacifique ») ou un palmares.
        # Ce ne sont pas des metiers : les y laisser polluerait la taxonomie.
        titres = {F.slug(x.get("titre") or "") for x in saisons_connues}
        pr = fiche.get("profession")
        if pr and (F.slug(pr) in titres
                   or "\u2020" in pr or re.search(r"d[ée]c[ée]d", pr, re.I)
                   or re.search(r"\b([ée]limin|vainqueur|finaliste|gagnant)", pr, re.I)):
            if not fiche.get("edition_origine"):
                fiche["edition_origine"] = pr
                provenance["edition_origine"] = provenance.get("profession", "?")
            fiche["profession"] = None
            provenance.pop("profession", None)

        # La profession porte parfois le departement colle devant ou derriere.
        # On l'en detache pour que la taxonomie des metiers reste propre.
        if fiche.get("profession"):
            lieu, metier = lieux.separer(fiche["profession"])
            if lieu:
                fiche["profession"] = metier
                if not fiche.get("localisation"):
                    fiche["localisation"] = lieu
                    provenance["localisation"] = provenance.get("profession", "?")

        nom = COQUILLES.get((sid, r.get("nom")), r.get("nom"))
        fiche["nom"] = nom
        if not fiche.get("nom_complet"):
            fiche["nom_complet"] = nom
        # Le titre CANONIQUE de la page, quand celui que la table de saison
        # pointe n'est qu'une redirection vers lui. L'identifiant -- donc
        # l'adresse de la fiche -- en sort.
        if fiche["nom_complet"] in NOMS_CANONIQUES:
            # LE NOM DE LA SOURCE EST CONSERVE, et ce n'est pas de la
            # documentation : les tableaux de VOTES l'ecrivent encore. Un
            # libelle de bulletin sort de l'extraction en « Julie
            # Navarro-Camilleri Julie » -- nom complet puis prenom, colles --
            # et le rattachement cherche le plus long prefixe qui soit un nom
            # complet connu. Adopter « Julie Navarro » sans garder l'ancienne
            # forme faisait perdre un bulletin : essaye, et le conseil est
            # ressorti avec `elimine_rattache: false`.
            fiche["nom_source"] = fiche["nom_complet"]
            fiche["nom_complet"] = NOMS_CANONIQUES[fiche["nom_complet"]]
            provenance["nom_complet"] = "titre canonique Fandom (redirection)"
        fiche["saison"] = sid
        fiche["id"] = F.slug(fiche["nom_complet"])

        if not fiche.get("couleur") and fiche.get("tribu"):
            c = couleurs.get(F.slug(fiche["tribu"]))
            if c:
                fiche["couleur"] = c
                provenance["couleur"] = "saisons.yml"

        # Signaler les vrais desaccords, pas les ecarts structurels connus.
        # L'ecart sur le jour entre les deux sources est attendu (Wikipedia
        # borne a la derniere bascule de tribu) : il n'est signale que s'il va
        # dans le sens inverse, c'est-a-dire si Fandom sort quelqu'un plus tot
        # que sa derniere tribu connue.
        if jumeau:
            src = {base_code: r, autre_code: jumeau}
            w, f = src.get("w", {}), src.get("f", {})
            if w.get("age") is not None and f.get("age") is not None and w["age"] != f["age"]:
                rapport.append(f"{sid} / {nom} : age diverge — "
                               f"wikipedia-fr={w['age']}, fandom={f['age']} "
                               f"(retenu : {fiche.get('age')})")
            jw, jf = w.get("jour_sortie"), f.get("jour_sortie")
            if jw is not None and jf is not None and jf < jw:
                rapport.append(f"{sid} / {nom} : jour de sortie incoherent — "
                               f"fandom={jf} anterieur a la derniere tribu connue "
                               f"chez wikipedia-fr ({jw})")
            sw, sf = w.get("sort"), f.get("sort")
            if sw and sf and sw != sf and sw != "elimine_conseil":
                rapport.append(f"{sid} / {nom} : sort diverge — "
                               f"wikipedia-fr={sw}, fandom={sf} "
                               f"(retenu : {fiche.get('sort')})")

        # « Encore en jeu » : la source le DIT, et elle a le dernier mot.
        #
        # Sur une saison en cours de diffusion, la colonne de depart d'un
        # tableau de candidats est vide -- personne n'est encore sorti. La
        # colonne voisine, elle, porte le palmares anterieur (« Vainqueur de
        # la saison 9 », « Eliminee le 12e jour du Choc des heros ») et le
        # lecteur de Wikipedia finit par la prendre pour un depart. All Stars
        # 2026 s'est ainsi retrouvee avec trois vainqueurs et quatre
        # finalistes pour quatre conseils joues.
        #
        # `parse_wikipedia_fr` ecarte desormais les cellules de palmares avant
        # de chercher le depart, mais son motif exige le mot « saison » et
        # certaines les nomment par leur titre. Plutot que d'allonger un motif
        # sans fin, on s'appuie sur ce qu'une source AFFIRME : quand elle
        # ecrit « Encore en jeu », l'aventurier n'a pas de sort, et aucune
        # deduction faite ailleurs ne peut en inventer un.
        if RE_EN_JEU.search(fiche.get("motif") or ""):
            if fiche.get("sort"):
                rapport.append(f"{sid} / {nom} : « {fiche['motif']} » — sort "
                               f"« {fiche['sort']} » deduit d'un palmares, ecarte")
            fiche["sort"] = None
            provenance.pop("sort", None)

        # UN RETOUR EN JEU, SUR UNE SAISON QUI N'EST PAS FINIE. All Stars 2026
        # ramene cinq elimines dans l'aventure : leur ligne garde
        # l'elimination -- « Eliminee au conseil, Jour 12 » -- et une cellule
        # suivante annonce « Retour dans l'aventure, Jour 19 ». Lue seule, la
        # premiere fait sortir du jeu quelqu'un qui y joue encore, et la fiche
        # publiait « sort au conseil le 12e jour ».
        #
        # La condition `en_cours` n'est pas une precaution, c'est le sens de la
        # regle : sur une saison TERMINEE, un retour est suivi d'un second
        # depart, et c'est ce depart qui compte. La seule a porter un retour
        # sans depart final est une saison en cours de diffusion -- ou la
        # bonne reponse est qu'il n'y a pas encore de sort.
        elif (not saison.get("en_cours") and (dispo.get("f") or {}).get("retour_en_jeu")
                and (dispo.get("w") or {}).get("sort")):
            # UN REVENANT, SUR UNE SAISON TERMINEE : sa ligne Fandom tient
            # plusieurs etats -- « Eliminee au conseil, Jour 12 », « Reintegree,
            # Jour 34 », « Finaliste » -- et le lecteur garde le PREMIER. Tania
            # Cakarevic, finaliste du Feu sacre, etait ainsi enregistree sortie
            # au douzieme jour ; la colonne du jury ou elle recoit deux voix
            # passait pour un conseil, et le juré Esteban pour un vote d'outre-
            # tombe. Wikipedia donne l'etat FINAL : il prime ici.
            w = dispo["w"]
            if fiche.get("sort") != w.get("sort"):
                rapport.append(f"{sid} / {nom} : revenant — sort final « {w.get('sort')} » "
                               f"(wikipedia-fr) retenu contre « {fiche.get('sort')} », "
                               f"premier depart lu chez Fandom")
                for champ in ("sort", "motif", "jour_sortie"):
                    if w.get(champ) not in (None, ""):
                        fiche[champ] = w[champ]
                        provenance[champ] = LIBELLE["w"] + " (revenant : etat final)"
        elif (not saison.get("en_cours") and (dispo.get("f") or {}).get("depart_final")):
            # UN REVENANT DONT FANDOM ECRIT LE SECOND DEPART sur une ligne de
            # continuation (voir `parse_fandom.depart_final`) : le sort est le
            # point d'arrivee, le jour aussi.
            libelle, jour = dispo["f"]["depart_final"]
            sort_final, _ = F.classify(libelle)
            if (sort_final, jour) != (fiche.get("sort"), fiche.get("jour_sortie")):
                rapport.append(f"{sid} / {nom} : revenant — depart final « {libelle} », "
                               f"jour {jour}, retenu contre « {fiche.get('sort')} », "
                               f"jour {fiche.get('jour_sortie')} (premier depart)")
                fiche["sort"], fiche["motif"], fiche["jour_sortie"] = sort_final, libelle, jour
                for champ in ("sort", "motif", "jour_sortie"):
                    provenance[champ] = LIBELLE["f"] + " (revenant : depart final)"
        elif saison.get("en_cours") and (dispo.get("f") or {}).get("retour_en_jeu"):
            if fiche.get("sort"):
                rapport.append(f"{sid} / {nom} : revenu en jeu le "
                               f"{(dispo['f'] or {}).get('jour_sortie')}e jour "
                               f"apres « {fiche.get('motif')} » — saison en "
                               f"cours, aucun depart definitif a ce jour")
            fiche["sort"] = None
            fiche["jour_sortie"] = None
            # Le motif aussi, et ce n'est pas un detail d'affichage : faute de
            # sort, c'est LUI que la colonne « Sort » du casting publie.
            fiche["motif"] = (dispo["f"] or {}).get("retour_en_jeu")
            provenance.pop("sort", None)
            provenance.pop("jour_sortie", None)

        fiche["sources"] = provenance
        out.append(fiche)
    return out

# Prenoms que le recoupement ne tranche pas : ni l'accord du participe, ni le
# modele {{♀}}/{{♂}} ne les couvrent, et ils n'apparaissent nulle part ailleurs
# dans le jeu de donnees. Tranches a la main, un par un.
GENRE_MANUEL = {
    "videli": "h",        # Vidéli Dittmar, saison 4, décorateur-sculpteur
    "mama": "f",          # Mama Diarra, saison 6
    "cega": "h",          # Céga, saison 8, magasinier
    "charlie": "f",       # Charlie, saison 15, restauratrice de meubles
    "brahma": "h",        # Brahma, saison 17, éducateur spécialisé
    "jesta": "f",         # Jesta Hillmann, finaliste de la saison 16
    "ines": "f",          # Inès Loucif, finaliste de L'Île des héros
    "kaouther": "f",
    "naouel": "f",
    "alisea": "f",
    "carinne": "f",
    "manuella": "f",
    # Prenoms sans ambiguite, restes sans accord parce que la personne a
    # abandonne (« Abandon medical » ne s'accorde pas) ou a ete finaliste.
    "richard": "h", "odile": "f", "aude": "f", "jean-claude": "h", "ali": "h",
    "kevin": "h", "christopher": "h", "jennifer": "f", "valentin": "h",
    "gerard": "h", "manon": "f", "margot": "f", "corinne": "f", "marc": "h",
    "marius": "h", "bastien": "h", "jean-philippe": "h", "adrien": "h",
    "jade": "f", "sara": "f", "coumba": "f", "karima": "f", "cindy": "f",
    "patrick": "h", "freddy": "h", "ugo": "h", "teheiura": "h",
}

# LE SEXE QUE LA TABLE DE SAISON ECRIT FAUX. Le tableau Fandom accorde la
# cellule de sortie, et c'est d'elle que le genre est lu ; quand l'accord est
# faux, le genre l'est aussi, et avec lui « Eliminé » sur une fiche de femme.
# La page individuelle de la MEME source tranche, par sa categorie et par ses
# pronoms. Une table fermee, par identifiant ; chaque ligne cite sa preuve
# (specs/sources/personnes/<id>.fandom.wiki).
GENRE_CORRIGE = {
    # « Patricia Tanguy est une aventurière des Aventuriers de Koh-Lanta.
    # Elle fait partie de la tribu rouge » ; [[Catégorie:Femmes]].
    "patricia-tanguy": "f",
    # « |Cause du départ = Éliminée au conseil », « est une aventurière de
    # Koh-Lanta : Nicoya » ; [[Catégorie:Femmes]].
    "nelly-baradeau": "f",
    # « Thierry Ramos est un aventurier de Koh-Lanta : Pacifique », « il a été
    # éliminé à l'unanimité » ; [[Catégorie:Hommes]]. La table de saison
    # ecrit « Éliminée au conseil ».
    "thierry-ramos": "h",
    # Trois saisons, et la seule fausse est All Stars (sp4) : « Sara est une
    # aventurière de Koh-Lanta : Malaisie, [...] La Nouvelle Édition » ;
    # [[Catégorie:Femmes]]. Ses deux autres participations sont en « f ».
    "sara-tallon": "f",
}


def corriger_genres(participations, rapport):
    """Applique GENRE_CORRIGE. Avant `completer_genre` : un prenom mal
    genre ne doit pas se propager par recoupement."""
    for p in participations:
        juste = GENRE_CORRIGE.get(p.get("id"))
        if juste and p.get("genre") != juste:
            rapport.append(f"{p['saison']} / {p['id']} : genre {p.get('genre')} "
                           f"corrige en {juste} (page individuelle)")
            p["genre"] = juste
            p.setdefault("sources", {})["genre"] = "page individuelle Fandom (categorie)"


# LE NOM PUBLIE, quand le titre Fandom porte une parenthese d'homonymie. La page
# de Franck s'intitule « Franck (Le Totem Maudit) » parce que la source ne
# donne pas son nom de famille ; la parenthese est un outil du wiki, pas un nom,
# et elle s'affichait dans le H1 de sa fiche et dans les infobulles.
# L'identifiant n'est PAS touche (l'adresse /aventuriers/franck-le-totem-maudit/
# reste) : la correction se pose a l'ecriture, et `nom_source` garde la forme
# de la source, par laquelle les bulletins se rattachent.
NOMS_PUBLIES = {
    "franck-le-totem-maudit": "Franck",
}


def completer_genre(participations, rapport):
    """Comble le sexe manquant par recoupement sur le prenom.

    L'accord du participe (« Éliminée ») et le modele {{♀}} couvrent la grande
    majorite des lignes. Pour le reste, un prenom deja tranche ailleurs dans le
    jeu de donnees fait foi -- a condition qu'il n'ait jamais ete vu des deux
    genres, auquel cas on prefere ne rien dire.
    """
    par_prenom = {}
    for p in participations:
        if p.get("genre"):
            par_prenom.setdefault(F.slug(p["nom"]), set()).add(p["genre"])
    ambigus = {k for k, v in par_prenom.items() if len(v) > 1}

    residuel = []
    for p in participations:
        if p.get("genre"):
            continue
        k = F.slug(p["nom"])
        if k in GENRE_MANUEL:
            p["genre"] = GENRE_MANUEL[k]
            p.setdefault("sources", {})["genre"] = "arbitrage manuel"
        elif k in par_prenom and k not in ambigus:
            p["genre"] = next(iter(par_prenom[k]))
            p.setdefault("sources", {})["genre"] = "recoupement sur le prenom"
        else:
            residuel.append(f"{p['saison']}/{p['nom']}")
    if residuel:
        rapport.append(f"sexe non tranche pour {len(residuel)} participations : "
                       + ", ".join(residuel))

def rattacher_prenoms_nus(participations, rapport):
    """Rend son nom de famille a une participation qui n'a qu'un prenom.

    Les editions de retour presentent parfois les revenants par leur seul
    prenom. Sans nom de famille, la meme personne compte pour deux : le
    palmares des multi-participants s'en trouve fausse, et l'age ne peut plus
    se deduire d'une autre annee.

    Le rattachement n'est fait que si UN SEUL nom complet du jeu de donnees
    porte ce prenom. Des qu'il y a deux porteurs, on s'abstient.
    """
    complets = {}
    for p in participations:
        if p["nom_complet"] != p["nom"]:
            complets.setdefault(F.slug(p["nom"]), set()).add(p["nom_complet"])

    rattaches = 0
    for p in participations:
        if p["nom_complet"] != p["nom"]:
            continue
        candidats = complets.get(F.slug(p["nom"]))
        if candidats and len(candidats) == 1:
            p["nom_complet"] = next(iter(candidats))
            p["id"] = F.slug(p["nom_complet"])
            p.setdefault("sources", {})["nom_complet"] = (
                "rattache a son autre participation")
            rattaches += 1
    if rattaches:
        rapport.append(f"{rattaches} participation(s) rattachee(s) a leur nom "
                       f"complet vu sur une autre saison")


def appliquer_vainqueurs(participations, saisons, rapport):
    """Cale le sort et le jour des finalistes sur ce que la saison declare.

    Les tables sources sont irregulieres sur leurs dernieres lignes : la
    cellule de depart du gagnant est tantot vide, tantot remplie par le nom de
    la tribu reunifiee, et le jour lu chez Wikipedia est celui de la derniere
    bascule de tribu, pas celui de la finale.

    Deux regles remettent tout d'aplomb :
      * la liste des vainqueurs de saisons.yml, tiree du tableau recapitulatif
        de Wikipedia, fait foi sur QUI a gagne ;
      * un vainqueur ou un finaliste quitte le jeu le dernier jour, par
        definition de la finale.

    La premiere sert aussi de controle : une saison ou l'on ne retrouve pas
    tous les vainqueurs declares remonte dans le rapport.
    """
    par_saison = {}
    for p in participations:
        par_saison.setdefault(p["saison"], []).append(p)

    for s in saisons:
        if s.get("annulee") or s.get("en_cours"):
            continue
        lignes = par_saison.get(s["id"], [])
        attendus = {F.slug(x) for x in (s.get("vainqueurs") or [])}
        if not attendus:
            continue

        trouves = []
        for p in lignes:
            noms = {F.slug(p["nom"]), F.slug(p.get("nom_complet") or "")}
            if noms & attendus:
                trouves.append(p)
                if p.get("sort") != "vainqueur":
                    p["sort"] = "vainqueur"
                    p.setdefault("sources", {})["sort"] = "saisons.yml"
            elif p.get("sort") == "vainqueur":
                rapport.append(f"{s['id']} / {p['nom']} : donne vainqueur par la "
                               f"source mais absent de la liste declaree "
                               f"({', '.join(s['vainqueurs'])})")

        if len(trouves) != len(attendus):
            rapport.append(f"{s['id']} : {len(trouves)} vainqueur(s) retrouve(s) "
                           f"sur {len(attendus)} declare(s) "
                           f"({', '.join(s['vainqueurs'])})")

        duree = s.get("duree_jours")
        if not duree:
            continue
        for p in lignes:
            if p.get("sort") in ("vainqueur", "finaliste") and p.get("jour_sortie") != duree:
                p["jour_sortie"] = duree
                p.setdefault("sources", {})["jour_sortie"] = (
                    "dernier jour de la saison (finale)")


def completer_depuis_autres_participations(participations, saisons, rapport):
    """Comble l'age et le metier des joueurs de retour.

    Les editions de heros et les All Stars ne redonnent ni l'age ni la
    profession des revenants : la source suppose qu'on les connait deja. Or on
    les connait : la meme personne a une autre participation, datee. L'age s'en
    deduit par difference d'annees, le metier se reprend tel quel.

    La deduction est datee et tracee : elle n'invente pas une valeur, elle
    reporte une valeur connue d'une annee sur une autre.
    """
    annees = {s["id"]: s.get("annee") for s in saisons}
    par_personne = {}
    for p in participations:
        par_personne.setdefault(p["id"], []).append(p)

    for pid, lignes in par_personne.items():
        if len(lignes) < 2:
            continue
        avec_age = [x for x in lignes if x.get("age") and annees.get(x["saison"])]
        avec_metier = [x for x in lignes if x.get("profession")]
        for p in lignes:
            an = annees.get(p["saison"])
            if p.get("age") is None and avec_age and an:
                ref = min(avec_age, key=lambda x: abs(annees[x["saison"]] - an))
                p["age"] = ref["age"] + (an - annees[ref["saison"]])
                p.setdefault("sources", {})["age"] = (
                    f"deduit de sa participation de {annees[ref['saison']]}")
            if p.get("profession") is None and avec_metier:
                ref = min(avec_metier,
                          key=lambda x: abs((annees.get(x["saison"]) or 0) - (an or 0)))
                p["profession"] = ref["profession"]
                p.setdefault("sources", {})["profession"] = (
                    f"reprise de sa participation de {annees.get(ref['saison'])}")


# --------------------------------------------------------------------------
# Troisieme source : les pages individuelles du wiki Fandom.
#
# Les tables de saison ne portent ni la residence, ni le detail des tribus avec
# leurs jours, ni le compte des victoires par edition. L'`Infobox Aventuriers`
# des pages individuelles porte tout cela. Elle est saisie a la main, donc
# moins sure qu'une table : elle ne sert qu'a COMBLER un champ vide, jamais a
# remplacer une valeur deja etablie. Les desaccords remontent au rapport.
# --------------------------------------------------------------------------

def rattacher_par_categorie(participations, rapport):
    """Rend son nom de famille a un prenom nu, via les categories Fandom.

    `rattacher_prenoms_nus` ne sait faire ce travail que si la personne a joue
    une autre saison sous son nom complet. Pour les autres, le wiki classe ses
    pages par saison : « Categorie:Koh-Lanta : La Guerre des Chefs » contient
    « Victor Rollinger ». On ne retient le nom que si UN SEUL membre de la
    categorie porte ce prenom -- sinon on s'abstient, comme partout ailleurs.
    """
    cats = I.categories()
    if not cats:
        return
    rattaches = 0
    for p in participations:
        if p["nom_complet"] != p["nom"]:
            continue
        candidats = {t for t in cats.get(p["saison"], [])
                     if " " in t and F.slug(t.split()[0]) == F.slug(p["nom"])}
        if len(candidats) == 1:
            p["nom_complet"] = candidats.pop()
            p["id"] = F.slug(p["nom_complet"])
            p.setdefault("sources", {})["nom_complet"] = "categorie Fandom de la saison"
            rattaches += 1
        elif len(candidats) > 1:
            rapport.append(f"{p['saison']} / {p['nom']} : {len(candidats)} pages "
                           f"Fandom portent ce prenom, aucun rattachement")
    if rattaches:
        rapport.append(f"{rattaches} prenom(s) nu(s) rattache(s) par les "
                       f"categories Fandom de leur saison")


def fusionner_identites(participations, rapport):
    """Reunit deux enregistrements qui designent la meme personne.

    Deux orthographes du meme nom -- « Phil Bizet » et « Philippe Bizet »,
    « Clementine Julien » et « Clementine Jullien » -- font deux personnes la
    ou il n'y en a qu'une : le palmares des multi-participants s'en trouve
    fausse. Le wiki tranche tout seul : les deux titres sont une redirection
    l'un de l'autre, donc la MEME page. Deux identifiants dont la page a la
    meme empreinte sont la meme personne, et c'est la page qui dit lequel des
    deux noms est le bon.
    """
    textes, empreintes = {}, {}
    for p in participations:
        pid = p["id"]
        if pid in textes:
            continue
        chemin = I.chemin_page(pid)
        if os.path.exists(chemin):
            t = open(chemin, encoding="utf-8").read()
            textes[pid] = t
            empreintes.setdefault(I.empreinte(t), []).append(pid)

    renommage = {}
    for _, ids in empreintes.items():
        if len(ids) < 2:
            continue
        canon = I.nom_canonique(textes[ids[0]])
        cible = F.slug(canon) if canon else None
        if cible not in ids:
            rapport.append(f"identites confondues {ids} : la page dit "
                           f"« {canon} », qui n'est aucun des deux — laisse en l'etat")
            continue
        for pid in ids:
            if pid != cible:
                renommage[pid] = (cible, canon)

    for p in participations:
        if p["id"] in renommage:
            cible, canon = renommage[p["id"]]
            rapport.append(f"{p['saison']} / {p['nom_complet']} : meme page Fandom "
                           f"que « {canon} » — fusionne")
            p["id"], p["nom_complet"] = cible, canon
            p.setdefault("sources", {})["nom_complet"] = "page Fandom commune (redirection)"


def sans_depart_sans_jour(participations, saisons, rapport):
    """Pas de sort, donc pas de jour de sortie -- sur une saison en cours.

    Un aventurier encore en jeu n'a pas quitte le jeu : lui attribuer un jour
    de sortie est une contradiction, et elle se propage. Le jour alimente la
    facette « parcours » du classement quand le rang manque, et les courbes de
    survie : « Encore en jeu, sorti le 19e jour » compte comme un depart au
    19e jour.

    Deux sources le posaient, chacune de bonne foi. Wikipedia donne le jour de
    la derniere bascule de TRIBU, pas celui du depart -- 19 pour les six
    aventuriers encore en jeu d'All Stars. Et la page individuelle d'un revenu
    garde le nombre de jours qu'il avait au moment de sa premiere sortie :
    trois, pour Maxime, revenu depuis.

    APRES `completer_depuis_pages`, pour la meme raison que `vainqueur_premier`
    -- c'est elle qui reposait la valeur qu'on venait de retirer.
    """
    en_cours = {s["id"] for s in saisons if s.get("en_cours")}
    retires = []
    for p in participations:
        if p["saison"] in en_cours and not p.get("sort") and p.get("jour_sortie"):
            retires.append(f"{p['saison']}/{p['nom']} ({p['jour_sortie']}e jour, "
                           f"{(p.get('sources') or {}).get('jour_sortie')})")
            p["jour_sortie"] = None
            p.get("sources", {}).pop("jour_sortie", None)
    if retires:
        rapport.append(f"jour_sortie : {len(retires)} jour(s) retire(s) a des "
                       f"aventuriers sans sort, saison en cours — "
                       f"{', '.join(retires)}")


def vainqueur_premier(participations, saisons, rapport):
    """Un vainqueur termine premier, par definition de la victoire.

    Meme sorte de regle que le jour de sortie d'un finaliste dans
    `appliquer_vainqueurs`, et elle repare deux defauts opposes.

    Delphine Bano etait donnee 2e sur 18 a Bocas del Toro alors qu'elle a
    gagne. L'infobox Fandom ne sait pas ecrire une egalite du jury : elle a
    donc RANGE les deux gagnantes, 1 et 2. La fiche publiait « son meilleur
    parcours : 2e sur 18 [...] ou elle gagne la saison » -- une phrase qui se
    contredit toute seule.

    Six autres vainqueurs n'avaient aucun rang, faute de page individuelle sur
    le wiki. Le leur etait DEDUIT du jour de sortie, et comme ils sortent le
    dernier jour, la deduction les mettait a egalite avec les finalistes. Il
    devient atteste.

    Ce n'est pas une invention : gagner la saison EST y finir premier, et les
    deux gagnants du Totem maudit portaient deja 1 tous les deux.

    APRES `completer_depuis_pages`, ET C'EST TOUT L'INTERET. Pose avant, la
    regle s'appliquait aux trente-six vainqueurs -- aucun n'avait encore de
    rang -- et effacait la provenance des vingt-neuf que le wiki attestait
    deja correctement. Ici, elle ne touche que ce qui est faux ou manquant.
    """
    corriges, combles = 0, 0
    for p in participations:
        if p.get("sort") != "vainqueur" or p.get("classement") == 1:
            continue
        avant = p.get("classement")
        p["classement"] = 1
        p.setdefault("sources", {})["classement"] = (
            "premier par definition (vainqueur)")
        if avant is None:
            combles += 1
        else:
            corriges += 1
            rapport.append(f"{p['saison']} / {p['nom']} : classement {avant} "
                           f"corrige a 1 — vainqueur de la saison")
    if corriges or combles:
        rapport.append(f"classement : {corriges} rang(s) de vainqueur corrige(s) "
                       f"et {combles} comble(s) — premier par definition")


# LES RANGS QUE L'INFOBOX ECRIT FAUX OU OUBLIE. Deux aventuriers au meme rang,
# un rang manquant que l'ordre des sorties donne sans ambiguite : chaque
# entree tombe exactement dans le trou laisse, et le jour de sortie le
# confirme. TABLE fermee, verifiee le 22 octobre 2026 contre les jours de
# sortie (et la categorie Fandom « 11ème place » pour Anne-Sophie). Une
# saison en cours n'a pas de rang : Maxime, revenu dans All Stars, portait
# « 18e sur 18 ». Cle : (saison, id) ; valeur : (rang ou None, raison).
RANGS_CORRIGES = {
    ("s09", "kaouther-ferdjani"): (12, "sortie jour 15, avant Alexandre (jour 21, 11e) ; le 12e manquait"),
    ("s09", "isabelle-da-silva"): (3, "eliminee aux poteaux jour 38 ; le 3e manquait"),
    ("s24", "anne-sophie-antoine"): (11, "sortie jour 24, avant Grace (jour 23, 12e) ; Fandom « 11ème place »"),
    ("s24", "tania-cakarevic"): (2, "finaliste ; le 2e manquait"),
    ("s25", "maxime-barbet"): (15, "sortie jour 20, apres Sarah (jour 17, 16e) ; le 15e manquait"),
    ("s26", "frederic-khouvilay"): (11, "sortie jour 27, apres Sarah (jour 24, 12e) ; le 11e manquait"),
    ("s26", "charlotte-rasquin"): (2, "finaliste ; le 2e manquait"),
    ("s26", "jacques-roque"): (4, "elimine a l'orientation jour 40 avec Cecile (5e) ; le 4e manquait"),
    ("s27", "mael-lozach"): (2, "finaliste ; le 2e manquait"),
    ("sp7", "alix-noblat"): (7, "deux aventuriers au 6e rang ; le 7e manquait"),
    ("sp8", "maxime-lubian"): (None, "saison en cours, revenu dans l'aventure : pas de rang final"),
}


def corriger_les_rangs(participations, rapport):
    trouves = set()
    for p in participations:
        cle = (p["saison"], p["id"])
        if cle in RANGS_CORRIGES:
            rang, raison = RANGS_CORRIGES[cle]
            p["classement"] = rang
            if rang is None:
                p.get("sources", {}).pop("classement", None)
            else:
                p.setdefault("sources", {})["classement"] = f"table RANGS_CORRIGES : {raison}"
            trouves.add(cle)
    for cle in sorted(set(RANGS_CORRIGES) - trouves):
        raise SystemExit(f"RANGS_CORRIGES : aucune participation {cle}")
    rapport.append(f"classement : {len(trouves)} rang(s) corrige(s) par table")


def voix_d_une_saison_en_cours(participations, saisons, rapport):
    """Une saison en cours n'a pas de total de voix fiable : l'infobox est
    saisie a la main, apres coup, et souvent en retard. All Stars donnait
    « 0 » a Joana et a Naoil, sorties au conseil -- leurs fiches publiaient
    « Jamais visee ». On ne publie pas un total que la source n'a pas fini
    d'ecrire."""
    en_cours = {s["id"] for s in saisons if s.get("en_cours")}
    n = 0
    for p in participations:
        if p["saison"] in en_cours and p.get("votes_recus") is not None:
            p["votes_recus"] = None
            p.get("sources", {}).pop("votes_recus", None)
            n += 1
    if n:
        rapport.append(f"votes_recus : {n} total(aux) d'une saison en cours retire(s)")


def verifier_classements(participations, saisons, rapport):
    """Ecarte les rangs finaux impossibles, signale les rangs en double.

    Le rang vient d'une infobox saisie a la main. Deux fautes s'y rencontrent :
    un rang superieur a l'effectif de la saison -- la page compte alors une
    autre saison -- et deux aventuriers au meme rang. La premiere rend la
    valeur inutilisable, on la retire ; la seconde est parfois legitime (une
    saison a deux vainqueurs), on se contente de la dire.
    """
    par_saison = collections.defaultdict(list)
    for p in participations:
        par_saison[p["saison"]].append(p)

    retires, doubles = 0, []
    for sid, lignes in sorted(par_saison.items()):
        effectif = len(lignes)
        for p in lignes:
            if p.get("classement") and p["classement"] > effectif:
                p["classement"] = None
                p.get("sources", {}).pop("classement", None)
                retires += 1
        compte = collections.Counter(p["classement"] for p in lignes if p.get("classement"))
        for rang, n in sorted(compte.items()):
            if n > 1:
                doubles.append(f"{sid} rang {rang} x{n}")
    if retires:
        rapport.append(f"classement : {retires} rang(s) superieur(s) a l'effectif "
                       f"de la saison, retire(s)")
    if doubles:
        rapport.append(f"classement : {len(doubles)} rang(s) partage(s) par deux "
                       f"aventuriers — " + ", ".join(doubles))


def normaliser_lieux(participations, rapport):
    """Ramene chaque localisation a un lieu de la liste fermee de lieux.py.

    Les sources melangent le departement, la ville et l'orthographe libre.
    Sans cette passe, « Toulouse » et « Haute-Garonne » sont deux endroits
    differents, et la comparaison avec la population INSEE perd les deux.
    Ce qui n'est reconnu nulle part est laisse tel quel et signale : on ne
    remplace jamais une valeur par une devinette.
    """
    changes, inconnus = [], collections.Counter()
    for p in participations:
        brut = p.get("localisation")
        if not brut:
            continue
        propre = lieux.normaliser(brut)
        if propre is None:
            inconnus[brut] += 1
        elif propre != brut:
            changes.append(f"{p['saison']}/{p['nom']} {brut!r} -> {propre!r}")
            p["localisation"] = propre
    if changes:
        rapport.append(f"localisation : {len(changes)} valeur(s) ramenee(s) a un "
                       f"lieu de la liste — " + ", ".join(changes[:6])
                       + (" …" if len(changes) > 6 else ""))
    if inconnus:
        rapport.append(f"localisation : {sum(inconnus.values())} valeur(s) hors "
                       f"liste, laissees telles quelles — "
                       + ", ".join(f"{k} ({n})" for k, n in inconnus.most_common()))


def _nom_de_tribu(saison, nom):
    """Ramene une etape de parcours au nom DECLARE de la tribu.

    Les fiches ecrivent « |Tengah » (un tuyau d'infobox colle), « Lanta-Naï »,
    « LankawaÏ », « Wasai », « Bokkor » -- un caractere de travers, et l'etape
    ne se rattache plus a sa tribu, donc a sa couleur. On ne corrige qu'a UNE
    lettre pres, et seulement si une seule tribu de la saison est a cette
    distance. Toutes les graphies de la reunification deviennent « Tribu
    réunifiée ». Les etats -- « Éliminée », « Bannie », « Aucune tribu » -- ne
    ressemblent a aucune tribu et restent tels quels.
    """
    propre = nom.strip(" |")
    if re.fullmatch(r"(?:tribu\s+)?r[ée]unifi[ée]+e?", propre, re.I):
        return "Tribu réunifiée"
    declares = [t["nom"] for t in saison.get("tribus", [])]
    cle = F.slug(propre)
    for t in declares:
        if F.slug(t) == cle:
            return t
    proches = [t for t in declares if _une_lettre(F.slug(t), cle)]
    return proches[0] if len(proches) == 1 else propre


def _une_lettre(a, b):
    """Vrai si a et b different d'une insertion, d'une suppression ou d'une substitution."""
    if a == b or abs(len(a) - len(b)) > 1 or min(len(a), len(b)) < 4:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    court, long_ = sorted((a, b), key=len)
    return any(long_[:i] + long_[i + 1:] == court for i in range(len(long_)))


def _couleur_de(saison, tribu):
    for t in saison.get("tribus", []):
        if F.slug(t["nom"]) == F.slug(tribu):
            return t.get("couleur")
    return None


# Champs que la page individuelle peut apporter, et ce qu'ils deviennent.
# `jours` alimente le jour de sortie ; les autres portent leur propre nom.
DEPUIS_PAGE = ["localisation", "profession", "age", "votes_recus", "parcours",
               "classement", "victoires_collectives", "victoires_individuelles"]


def completer_depuis_pages(participations, saisons, rapport):
    """Comble les champs vides avec l'infobox de la page individuelle.

    Regle unique : on ne comble que du vide. Un desaccord entre la table de
    saison et la page individuelle est signale, jamais tranche en silence --
    la table est relue par plus de monde, elle garde la main.
    """
    par_saison = {s["id"]: s for s in saisons}
    personnes = {}
    for p in participations:
        personnes.setdefault(p["id"], []).append(p["saison"])
    lu, alertes = I.tout([{"id": k, "participations": v} for k, v in personnes.items()])
    # Les infobox ne nomment pas toujours la saison de chaque rang ; quand le
    # compte tombe juste, parse_personnes l'attribue par ordre chronologique.
    # C'est routinier : on le compte plutot que de l'enumerer.
    deduits = [x for x in alertes if "deduite du rang" in x]
    rapport += [x for x in alertes if x not in deduits]
    if deduits:
        rapport.append(f"{len(deduits)} rang(s) d'infobox attribue(s) par ordre "
                       f"chronologique, faute de champ « Saison »")

    combles, desaccords = {}, {}
    for p in participations:
        champs = lu.get((p["id"], p["saison"]))
        if not champs:
            continue
        for champ in DEPUIS_PAGE:
            if champ not in champs:
                continue
            valeur = champs[champ]
            if champ == "parcours":
                s_ = par_saison.get(p["saison"], {})
                valeur = [{"tribu": _nom_de_tribu(s_, e["tribu"]),
                           "couleur": _couleur_de(s_, _nom_de_tribu(s_, e["tribu"])),
                           "jour_debut": e["jour_debut"], "jour_fin": e["jour_fin"]}
                          for e in valeur]
            if p.get(champ) in (None, "", []):
                p[champ] = valeur
                p.setdefault("sources", {})[champ] = "fandom (page individuelle)"
                combles[champ] = combles.get(champ, 0) + 1
            elif champ in ("age", "localisation", "votes_recus") and p[champ] != valeur:
                desaccords.setdefault(champ, []).append(
                    f"{p['saison']}/{p['nom']} {p[champ]!r} vs {valeur!r}")
        # Le jour de sortie : la page donne le nombre de jours passes en jeu.
        if p.get("jour_sortie") is None and champs.get("jours"):
            duree = par_saison.get(p["saison"], {}).get("duree_jours")
            if not duree or champs["jours"] <= duree:
                p["jour_sortie"] = champs["jours"]
                p.setdefault("sources", {})["jour_sortie"] = "fandom (page individuelle)"
                combles["jour_sortie"] = combles.get("jour_sortie", 0) + 1

        # Le nombre de jours en jeu de la page, garde pour completer_les_jours.
        if champs.get("jours"):
            p["_jours_page"] = champs["jours"]

    for champ, n in sorted(combles.items()):
        rapport.append(f"{champ} : {n} valeur(s) comblee(s) par les pages individuelles")
    for champ, liste in sorted(desaccords.items()):
        rapport.append(f"{champ} : {len(liste)} desaccord(s) table / page individuelle "
                       f"(table retenue) — " + ", ".join(liste[:6])
                       + (" …" if len(liste) > 6 else ""))


SURVIVOR = os.path.join(os.path.dirname(os.path.dirname(ICI)), "specs", "sources", "survivor")

# Les noms que le wiki Survivor ecrit autrement, au point qu'aucun
# rapprochement ne les retrouve. TABLE fermee, chaque ligne avec sa preuve.
ALIAS_SURVIVOR = {
    ("s04", "SL"): ("sabira",
        "meme ligne en tout : Chapera puis Mogo, « 3rd Voted Out, Day 10 » ; "
        "Wikipedia anglais la nomme Sabira Lamia, d'ou les initiales, et la page "
        "Fandom de Linda envoie « SL » chez les Mogo au jour 8"),
}


def parcours_depuis_survivor(participations, saisons, rapport):
    """Le parcours VIDE, lu dans le tableau des candidats du wiki Survivor.

    53 participations n'avaient aucun parcours : ni legende datee sur
    Wikipedia, ni tribu sur la fiche Fandom. Le tableau « Castaways » du wiki
    Survivor donne, pour chacun, une colonne par phase -- tribu d'origine,
    tribus recomposees, tribu reunifiee -- et « out » une fois sorti. Certains
    en-tetes datent la phase (« Day 5 Tribes ») : ce jour-la ouvre l'etape.
    Les autres jours sont poses ensuite par completer_les_jours, aux memes
    conditions que pour tout le monde. On ne comble que du vide.
    """
    from parse_votes import developper
    par_saison = {s["id"]: s for s in saisons}
    vides = collections.defaultdict(dict)
    for p in participations:
        if not p.get("parcours"):
            for n in (p.get("nom_complet"), p.get("nom")):
                if n:
                    vides[p["saison"]].setdefault(F.slug(n), p)
    combles = 0
    for sid, cibles in vides.items():
        chemin = os.path.join(SURVIVOR, sid + ".wiki")
        if not os.path.exists(chemin):
            continue
        texte = open(chemin, encoding="utf-8").read()
        m = re.search(r"==\s*(?:Castaways|Contestants)\s*==\s*(\{\|.*?\n\|\})", texte, re.S)
        if not m:
            continue
        grille = developper(m.group(1))
        entete = next((i for i, r in enumerate(grille[:4])
                       if any("original tribe" in F.plain(c).lower() for c in r)), None)
        if entete is None:
            continue
        phases = [(c, F.plain(x)) for c, x in enumerate(grille[entete])
                  if re.search(r"tribe", F.plain(x), re.I)]
        # Les deux wikis n'ecrivent pas toujours le meme nom de famille
        # (« Délisia Fettasi » / « Délisia Fettache »). A defaut du nom complet,
        # le PRENOM rattache -- s'il est unique des deux cotes : une seule
        # personne de ce prenom dans la saison, une seule ligne au tableau.
        liens = [re.search(r"link=([^\]|]+)", x).group(1).strip()
                 for r_ in grille[entete + 1:] for x in r_[:2] if "link=" in x]
        prenoms_tableau = collections.Counter(F.slug(l.split()[0]) for l in liens)
        prenoms_saison = collections.Counter(
            F.slug((q.get("nom") or "").split()[0]) for q in participations
            if q["saison"] == sid and q.get("nom"))
        par_prenom = {F.slug((q.get("nom") or "").split()[0]): q for q in cibles.values()}
        for rang in grille[entete + 1:]:
            lien = next((re.search(r"link=([^\]|]+)", x) for x in rang if "link=" in x), None)
            if not lien:
                continue
            # Le nom AFFICHE fait foi avant le lien, qui porte parfois une
            # coquille (« link=Marilyne Hemelsdae » pour Maryline Hemelsdael).
            affiche = next((re.search(r"'''\[\[([^\]|]+)", x) for x in rang if "'''[[" in x), None)
            noms = [n.group(1).strip() for n in (affiche, lien) if n]
            p = next((cibles[F.slug(n)] for n in noms if F.slug(n) in cibles), None)
            alias = ALIAS_SURVIVOR.get((sid, noms[0]))
            if not p and alias:
                p = next((q for q in cibles.values() if q["id"] == alias[0]), None)
            prenom = F.slug(noms[-1].split()[0])
            if (not p and prenoms_tableau[prenom] == 1 and prenoms_saison[prenom] == 1):
                p = par_prenom.get(prenom)
            if not p or p.get("parcours"):
                continue
            etapes = []
            for c, titre in phases:
                if c >= len(rang):
                    continue
                t = re.search(r"\{\{\s*tribebox\d?\s*\|\s*([^|}]+)", rang[c])
                if not t or t.group(1).strip().lower() == "out":
                    continue
                code = t.group(1).strip()
                nom = ("Tribu réunifiée" if code.lower().startswith("merged")
                       else _nom_de_tribu(par_saison.get(sid, {}), re.sub(r"\d*fr$|\d+$", "", code)))
                jour = re.search(r"day\s*(\d+)", titre, re.I)
                if etapes and etapes[-1]["tribu"] == nom:
                    continue
                if etapes and jour:
                    etapes[-1]["jour_fin"] = int(jour.group(1))
                etapes.append({"tribu": nom,
                               "couleur": _couleur_de(par_saison.get(sid, {}), nom),
                               "jour_debut": int(jour.group(1)) if jour else None,
                               "jour_fin": None})
            # Sortie avant la formation des tribus : la ligne n'a aucune
            # colonne de tribu, et sa vignette porte « none ».
            if not etapes and re.search(r"tribebox2\s*\|\s*none", rang[0], re.I):
                etapes = [{"tribu": "Aucune tribu", "couleur": None,
                           "jour_debut": None, "jour_fin": None}]
            if etapes:
                p["parcours"] = etapes
                p.setdefault("sources", {})["parcours"] = "wiki Survivor (tableau des candidats)"
                combles += 1
    rapport.append(f"parcours : {combles} parcours vide(s) comble(s) par le wiki Survivor")


def completer_les_jours(participations, rapport):
    """Pose les jours d'un parcours que la fiche ne date pas -- quand ils sont SURS.

    Les fiches des saisons anciennes donnent la suite des tribus sans jours
    (« Kumo<br/>Tribu réunifiée »), et Wikipedia n'a rien de date pour elles.
    Decision de l'utilisateur (20 octobre 2026) : completer le sur, signaler le
    reste. Trois faits, et rien d'autre :

      * le jour 1, seulement si la page le prouve : sortie au jour S apres J
        jours en jeu, et S - J + 1 == 1. Un remplacant arrive plus tard (Claire,
        Cambodge, jour 4), un revenant a un trou : dans ces deux cas le calcul
        ne tombe pas sur 1, et on ne pose rien ;
      * le jour de reunification, lu chez les AUTRES aventuriers dates de la
        saison, et seulement s'ils s'accordent tous ;
      * le jour de sortie, pour la derniere etape.

    Un echange de tribus sans date reste sans date.
    """
    reunion = collections.defaultdict(set)
    for p in participations:
        for e in p.get("parcours") or []:
            if re.search(r"r[ée]unifi", e["tribu"], re.I) and e.get("jour_debut"):
                reunion[p["saison"]].add(e["jour_debut"])
    # Le jour d'un echange de tribus, lu de meme : une transition entre deux
    # tribus d'avant la reunification, datee chez les autres. Une saison a
    # plusieurs echanges donne plusieurs jours, et alors rien n'est pose.
    echange = collections.defaultdict(set)
    for p in participations:
        pc = p.get("parcours") or []
        for a, b in zip(pc, pc[1:]):
            if (b.get("jour_debut") and not re.search(r"r[ée]unifi|aucune", a["tribu"] + b["tribu"], re.I)
                    and a["tribu"] != b["tribu"]):
                echange[p["saison"]].add(b["jour_debut"])
    poses = 0
    for p in participations:
        jours = p.pop("_jours_page", None)
        pc = p.get("parcours") or []
        if not pc or all(e.get("jour_debut") is not None and e.get("jour_fin") is not None
                         for e in pc):
            continue
        avant = [dict(e) for e in pc]
        sortie = p.get("jour_sortie")
        d = reunion.get(p["saison"])
        d = next(iter(d)) if d and len(d) == 1 else None
        s = echange.get(p["saison"])
        s = next(iter(s)) if s and len(s) == 1 else None
        reunie = [bool(re.search(r"r[ée]unifi", e["tribu"], re.I)) for e in pc]
        etat = [bool(re.match(r"aucune", e["tribu"], re.I)) for e in pc]
        # Chaque fait sur se pose seul ; aucun n'en suppose un autre.
        if jours and sortie and sortie - jours + 1 == 1 and pc[0].get("jour_debut") is None:
            pc[0]["jour_debut"] = 1
        for i, e in enumerate(pc):
            if reunie[i] and d and i > 0 and (sortie is None or sortie >= d):
                if e.get("jour_debut") is None:
                    e["jour_debut"] = d
                if pc[i - 1].get("jour_fin") is None:
                    pc[i - 1]["jour_fin"] = d
        if (len(pc) >= 2 and s and not reunie[1] and not etat[0] and pc[0]["tribu"] != pc[1]["tribu"]
                and (sortie is None or sortie >= s)):
            if pc[0].get("jour_fin") is None:
                pc[0]["jour_fin"] = s
            if pc[1].get("jour_debut") is None:
                pc[1]["jour_debut"] = s
        # La derniere etape finit au jour de sortie -- si elle est bien la
        # derniere : la reunification, un etat, ou une sortie avant la
        # reunification. Sinon la fiche a peut-etre omis une etape.
        # Pas pour un REVENANT : son jour de sortie est sa premiere
        # elimination, et le parcours continue apres (Maxime, All Stars :
        # sorti au jour 3, banni, revenu).
        der = len(pc) - 1
        revenant = any(RE_ETAT.match(e["tribu"]) for e in pc[:der])
        if (sortie and pc[der].get("jour_fin") is None and not revenant
                and (pc[der].get("jour_debut") is None or sortie >= pc[der]["jour_debut"])
                and (reunie[der] or etat[der] or (d and sortie <= d))):
            pc[der]["jour_fin"] = sortie
        if pc != avant:
            p.setdefault("sources", {})["parcours_jours"] = (
                "deduits, seulement quand ils sont surs : jour 1 par la page "
                "individuelle, reunification et echange lus chez les autres "
                "aventuriers dates de la saison, jour de sortie")
            poses += 1
    rapport.append(f"parcours : jours poses sur {poses} participation(s), "
                   f"seulement quand ils sont surs")


def corriger_tribus(participations, rapport):
    """Applique TRIBUS_FAUTIVES a la tribu de depart et au parcours."""
    corriges = 0
    for p in participations:
        bon = TRIBUS_FAUTIVES.get((p["saison"], p.get("tribu")))
        if bon:
            p["tribu"] = bon
            p.setdefault("sources", {})["tribu"] = "correction, cf. TRIBUS_FAUTIVES"
            corriges += 1
        for etape in p.get("parcours") or []:
            bon = TRIBUS_FAUTIVES.get((p["saison"], etape.get("tribu")))
            if bon:
                etape["tribu"] = bon
                corriges += 1
    if corriges:
        rapport.append(f"tribu : {corriges} nom(s) corrige(s) — nom de tribu "
                       f"fautif dans la source, arbitre par les deux autres")


RE_ETAT = re.compile(r"^(aucune|absente?|bannie?|[ée]limin[ée]e?|exil[ée]e?)\b", re.I)


def harmoniser_parcours(participations, saisons, rapport):
    """Toutes les etapes, quelle que soit leur source, nommees et colorees de meme.

    Wikipedia ecrit « Tribu des hommes » sans couleur la ou la saison declare
    cette tribu en bleu ; une fiche ecrit « LankawaÏ ». Le nom est ramene a la
    tribu declaree, et la couleur manquante prise dans la declaration.
    """
    par_saison = {s["id"]: s for s in saisons}
    for p in participations:
        s_ = par_saison.get(p["saison"], {})
        for e in p.get("parcours") or []:
            e["tribu"] = _nom_de_tribu(s_, e["tribu"])
            if e.get("couleur") is None:
                e["couleur"] = _couleur_de(s_, e["tribu"])


# Les jours que le tableau de saison Fandom (ou une legende) donne FAUX, et
# que la majorite des temoins corrige. TABLE fermee : chaque ligne a ete
# confrontee a tous les temoins disponibles -- Wikipedia (fr et en), wiki
# Survivor, fiche Fandom et ses jours de jeu -- le 20 octobre 2026. A egalite,
# rien n'est change sans un temoin de plus : un recit date (Estelle, Vanuatu :
# « Le 22ème jour [...] Le soir-même c'est Estelle qui est éliminée », page de
# Marie, confirme le jour 22). Reste a egalite : Ludovic (Vanuatu).
_NICOYA = ("Wikipedia anglais (colonne Day), wiki Survivor et fiche Fandom "
           "s'accordent ; le tableau de saison Fandom est decale d'un jour")
JOURS_DE_SORTIE = {
    **{("s02", pid): (j, _NICOYA) for pid, j in (
        ("xavier-lemasson", 5), ("caroline-lamotte", 7), ("celine-fortier", 10),
        ("nelly-baradeau", 13), ("pierre-cambon", 16), ("jacky-forteron", 19),
        ("adonis-koupaki", 22), ("jimmy-denis", 25), ("beatrice-cloix-penisson", 28),
        ("francois-xavier-renou", 31), ("isabelle-vial", 34), ("maud-garnier", 37),
        ("marianne-mondon", 38))},
    **{("s22", pid): (27, "Wikipedia fr, bilan : « Jour 27 » ; wiki Survivor ; "
                          "elimines ensemble par les destins lies")
       for pid in ("vincent-blier", "laetitia-saphores")},
    **{("s26", pid): (j, "legende Wikipedia, wiki Survivor et fiche Fandom ; la "
                         "saison dure 41 jours, pas 40")
       for pid, j in (("sophia-mansouri", 39), ("ugo-lartiche", 39),
                      ("jacques-roque", 40), ("cecile-belec", 40), ("ilyesse-benyoub", 41))},
    **{("sp4", pid): (j, "wiki Survivor et parcours de la fiche Fandom")
       for pid, j in (("teheiura-teahui", 19), ("philippe-duron", 21),
                      ("moundir-zoughari", 22))},
    **{("sp7", pid): (j, "legende Wikipedia et wiki Survivor")
       for pid, j in (("coumba-baradji", 18), ("namadia-thai-thai", 19), ("sam-haliti", 32))},
    ("sp7", "freddy-boucher"): (2, "Wikipedia, resume : « Jour 2 : [...] abandon "
                                   "médical de Freddy » ; wiki Survivor"),
    ("s16", "laurent-mischkind"): (15, "page Fandom de Lau : « Au jour 15 [...] le "
                                       "premier pas consiste à faire sortir Laurent » ; "
                                       "wiki Survivor"),
    ("s27", "allan-rousseeuw"): (6, "wiki Survivor, parcours et jours de jeu de la fiche"),
}
# Les etapes de parcours que la source ecrit fausses. (saison, id, tribu) ->
# (debut, fin) ; fin None retire l'etape.
ETAPES_CORRIGEES = {
    ("s08", "christopher-lavaud", "Tribu réunifiée"): ((15, 22),
        "coquille de la fiche (« 15-2 ») : sortie au jour 22, wiki Survivor"),
    ("s15", "julien-castro", "Tribu réunifiée"): ((19, 23),
        "tableau de saison Fandom et wiki Survivor : sortie au jour 23"),
    ("s26", "maxim-iarkov", "Tribu maudite"): ((None, 30),
        "tableau de saison Fandom et wiki Survivor : sortie au jour 30"),
    ("sp3", "patricia-morel", "Klahan"): ((1, 10),
        "battue en duel a la reunion des ambassadeurs (wiki Survivor), sortie a "
        "l'episode 4 selon le tableau des votes de Wikipedia lui-meme"),
    ("sp3", "patricia-morel", "Tribu réunifiée"): (None,
        "jamais dans la tribu reunifiee : sortie avant elle (voir Klahan)"),
}

# Les sorts que la source ecrit trop vagues, ou faux. Le tableau de saison dit
# « Eliminee », sans dire comment, ou « Eliminee au conseil » pour toute
# sortie d'un soir de conseil -- le binome emporte par les destins lies, le
# perdant d'un duel de riposte : la regle par defaut en fait un conseil. TABLE
# fermee, chaque ligne tiree d'un temoin qui nomme la sortie (21 octobre 2026).
# Un troisieme terme fixe le jour, pour un REVENANT dont la ligne Fandom tient
# deux departs et dont la chaine lisait le premier : le sort est le point
# d'arrivee, le jour doit l'etre aussi, sans quoi la fiche publierait « sort
# aux ambassadeurs le 3e jour ». Les duels perdus APRES les destins lies
# (Clemence, Aurelien, Jade) etaient des tentatives de retour : le guide
# d'episodes du wiki Survivor les dit « Eliminated » au jour du conseil.
_LIES = ("elimine_destins_lies",
         "Wikipedia et Fandom : éliminé(e) avec son binôme, sans voix contre soi")
SORTS_CORRIGES = {
    **{(s_, pid): _LIES for s_, pid in (
        ("s12", "camille-sold"), ("s14", "nessim-kouachi"), ("s15", "steve-best"),
        ("s17", "kelly-beaugrand"), ("s20", "sophie-chevalier"), ("s21", "alix-noblat"),
        ("s22", "laetitia-saphores"), ("s23", "louana-roy"), ("s24", "clemence-noquet"),
        ("s25", "aurelien-dulau"), ("s27", "pierre-marie-ponsot"), ("s28", "jade-correa"),
        ("sp5", "yassin-metiri"))},
    ("sp6", "teheiura-teahui"): ("elimine_destins_lies",
        "revenant : Fandom, second départ « Jour 24 » ; Wikipedia : « Teheiura étant en "
        "binôme avec Charlotte, il est également éliminé »", 24),
    ("sp7", "teheiura-teahui"): ("disqualifie",
        "revenant : Wikipedia « Exclu », pour avoir obtenu de la nourriture de pêcheurs ; "
        "Fandom « Éjecté du jeu, Jour 27 »", 27),
    ("s21", "marie-france-schieber"): ("elimine_ambassadeurs",
        "revenante : Fandom, second départ « Éliminée par les ambassadeurs, Jour 22 » ; "
        "Wikipedia : « Les deux ambassadeurs se mettent d'accord pour éliminer Marie-France »", 22),
    **{("s28", pid): ("elimine_duel", "Wikipedia : « perd le duel de riposte » ; tableau "
                                      "des votes Fandom, même note")
       for pid in ("francoise-fournier-grigis", "cindy-sulpice-gonzalez", "daniel-duquesnoy")},
    ("s24", "elodie-migeal"): ("elimine_epreuve",
        "Wikipedia : « celui terminant dernier, à savoir Élodie, est directement éliminé » ; "
        "wiki Survivor : « no vote »"),
    ("s02", "marianne-mondon"): ("elimine_epreuve",
        "tableau des votes Fandom : « Marianne a été la dernière à une épreuve "
        "de questions » ; Wikipedia anglais ne la dit pas « voted out »"),
    ("s17", "maria-beccaris"): ("elimine_epreuve",
        "Wikipedia anglais : « As Maria finished last in the challenge, she was "
        "eliminated » ; tableau Fandom : « épreuve éliminatoire individuelle »"),
}


def corriger_les_jours(participations, rapport):
    """Applique JOURS_DE_SORTIE, SORTS_CORRIGES et ETAPES_CORRIGEES, et le dit."""
    for p in participations:
        s = SORTS_CORRIGES.get((p["saison"], p["id"]))
        if s and p.get("sort") != s[0]:
            rapport.append(f"sort : {p['saison']}/{p['id']} "
                           f"{p.get('sort')} -> {s[0]} ({s[1]})")
            p["sort"] = s[0]
            p.setdefault("sources", {})["sort"] = "corrige : " + s[1]
        if s and len(s) > 2 and p.get("jour_sortie") != s[2]:
            rapport.append(f"jour de sortie : {p['saison']}/{p['id']} "
                           f"{p.get('jour_sortie')} -> {s[2]} (revenant, depart final)")
            p["jour_sortie"] = s[2]
            p.setdefault("sources", {})["jour_sortie"] = "corrige : " + s[1]
        c = JOURS_DE_SORTIE.get((p["saison"], p["id"]))
        if c and p.get("jour_sortie") != c[0]:
            rapport.append(f"jour de sortie : {p['saison']}/{p['id']} "
                           f"{p.get('jour_sortie')} -> {c[0]} ({c[1]})")
            p["jour_sortie"] = c[0]
            p.setdefault("sources", {})["jour_sortie"] = "corrige : " + c[1]
        garde = []
        for e in p.get("parcours") or []:
            k = ETAPES_CORRIGEES.get((p["saison"], p["id"], e["tribu"]))
            if k is None:
                garde.append(e)
                continue
            if k[0] is None:
                rapport.append(f"parcours : {p['saison']}/{p['id']} etape {e['tribu']} retiree ({k[1]})")
                continue
            debut, fin = k[0]
            e["jour_debut"] = debut if debut is not None else e["jour_debut"]
            e["jour_fin"] = fin
            p.setdefault("sources", {})["parcours_jours"] = "corrige : " + k[1]
            garde.append(e)
        if p.get("parcours"):
            p["parcours"] = garde


def tribu_sans_etat(participations, rapport):
    """Une tribu de depart n'est jamais un ETAT.

    « Absente » (Marie, Ile des heros : arrivee au jour 3) ou « Bannie » ne
    sont pas des campements. La tribu de depart est alors le premier vrai
    campement du parcours, ou rien si l'aventurier n'en a jamais eu.
    """
    for p in participations:
        if not p.get("tribu") or not RE_ETAT.match(p["tribu"]):
            continue
        vraie = next((e for e in p.get("parcours") or [] if not RE_ETAT.match(e["tribu"])
                      and not re.search(r"r[ée]unifi", e["tribu"], re.I)), None)
        rapport.append(f"tribu : « {p['tribu']} » est un etat ({p['saison']}/{p['id']}) "
                       f"→ {vraie['tribu'] if vraie else 'aucune tribu'}")
        p["tribu"] = vraie["tribu"] if vraie else None
        p["couleur"] = vraie.get("couleur") if vraie else None
        p.setdefault("sources", {})["tribu"] = "premier campement du parcours (etat ecarte)"


def tribu_depuis_le_parcours(participations, rapport):
    """Le premier campement du parcours EST la tribu de depart.

    La table de saison laisse parfois la case vide -- pour Ugo en Legende, dont
    le parcours commence par « Tribu des hommes » avant deux passages par le
    banissement. Ce n'est pas une deduction : le parcours date ses etapes, et
    la premiere est celle du premier jour.
    """
    combles = 0
    for p in participations:
        if p.get("tribu") or not p.get("parcours"):
            continue
        premiere = p["parcours"][0]
        if not premiere.get("tribu"):
            continue
        # « Aucune tribu » est un etat, pas un campement : sortie avant la
        # formation des tribus. La tribu de depart reste vide, et c'est vrai.
        if re.match(r"aucune", premiere["tribu"], re.I):
            continue
        p["tribu"] = premiere["tribu"]
        p.setdefault("sources", {})["tribu"] = "premiere etape du parcours"
        if not p.get("couleur") and premiere.get("couleur"):
            p["couleur"] = premiere["couleur"]
            p["sources"]["couleur"] = "premiere etape du parcours"
        combles += 1
    if combles:
        rapport.append(f"tribu : {combles} valeur(s) comblee(s) par la premiere "
                       f"etape du parcours")


def charger(sid):
    f_path = os.path.join(WIKI, f"{sid}.fandom.wiki")
    w_path = os.path.join(WIKI, f"{sid}.wiki")
    rows_f = F.parse_page(open(f_path, encoding="utf-8").read(), sid) if os.path.exists(f_path) else []
    rows_w = W.parse_page(open(w_path, encoding="utf-8").read(), sid) if os.path.exists(w_path) else []
    return rows_f, rows_w

def main():
    saisons = donnees.charger(open(os.path.join(RACINE, "_data", "saisons.yml")))
    rapport, participations = [], []
    for s in saisons:
        if s.get("annulee"):
            continue
        rows_f, rows_w = charger(s["id"])
        if not rows_f and not rows_w:
            rapport.append(f"{s['id']} : aucune source")
            continue
        participations.extend(fusionner_saison(s, rows_f, rows_w, rapport, saisons))

    rattacher_prenoms_nus(participations, rapport)
    rattacher_par_categorie(participations, rapport)
    fusionner_identites(participations, rapport)
    appliquer_vainqueurs(participations, saisons, rapport)
    corriger_genres(participations, rapport)
    completer_genre(participations, rapport)
    completer_depuis_pages(participations, saisons, rapport)
    # Apres les pages individuelles : c'est d'elles que vient le parcours.
    harmoniser_parcours(participations, saisons, rapport)
    corriger_les_jours(participations, rapport)
    tribu_depuis_le_parcours(participations, rapport)
    parcours_depuis_survivor(participations, saisons, rapport)
    completer_les_jours(participations, rapport)
    tribu_sans_etat(participations, rapport)
    corriger_tribus(participations, rapport)
    normaliser_lieux(participations, rapport)
    sans_depart_sans_jour(participations, saisons, rapport)
    vainqueur_premier(participations, saisons, rapport)
    corriger_les_rangs(participations, rapport)
    verifier_classements(participations, saisons, rapport)
    voix_d_une_saison_en_cours(participations, saisons, rapport)
    completer_depuis_autres_participations(participations, saisons, rapport)

    # champs encore vides
    manques = {}
    for p in participations:
        for champ in ("age", "profession", "genre", "tribu", "jour_sortie", "sort"):
            if p.get(champ) in (None, "", []):
                manques.setdefault(champ, []).append(f"{p['saison']}/{p['nom']}")

    return participations, rapport, manques

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Produit par tools/extraction/fusionner.py, qui croise deux sources :
#   - le wiki Fandom francophone   https://kohlanta.fandom.com/fr/
#   - Wikipedia en francais        https://fr.wikipedia.org/
#   - les pages individuelles du wiki Fandom (residence, tribus datees,
#     palmares d'epreuves), qui ne servent qu'a combler un champ vide
#
# Chaque enregistrement porte un bloc `sources` qui dit, champ par champ, d'ou
# vient la valeur retenue. Regenerer avec :
#
#     tools/atelier python3 tools/extraction/fusionner.py --ecrire
#
"""

# `nom_source` suit `nom_complet` : la forme que la SOURCE ecrit, quand le site
# publie le titre canonique du wiki a sa place. Elle n'est pas decorative --
# les tableaux de votes n'ont pas suivi le renommage, et c'est par elle que
# leurs bulletins se rattachent encore.
ORDRE = ["id", "nom", "nom_complet", "nom_source", "saison", "genre", "age",
         "profession",
         "localisation", "edition_origine", "tribu", "couleur", "parcours",
         "jour_sortie", "sort", "motif", "votes_recus",
         # Apportes par les pages individuelles du wiki Fandom : le rang final
         # et le palmares d'epreuves de l'edition. Ce sont des totaux saisis a
         # la main, pas le detail episode par episode ; ils ne remplacent pas
         # _data/epreuves.yml, ils couvrent les saisons qu'il ignore.
         "classement", "victoires_collectives", "victoires_individuelles",
         "sources"]

def ordonner(p):
    return {k: p[k] for k in ORDRE if k in p}

RE_ELIMINE_MASCULIN = re.compile(r"^Éliminé(?=\s)")
RE_ELIMINE_FEMININ = re.compile(r"^Éliminée(?=\s)")


def accorder(p):
    """Le motif de sortie s'accorde au genre : le wiki ecrit « Eliminé au
    conseil » pour Sara Tallon, et « Éliminée au conseil » pour Thierry Ramos."""
    if isinstance(p.get("motif"), str):
        if p.get("genre") == "f":
            p["motif"] = RE_ELIMINE_MASCULIN.sub("Éliminée", p["motif"])
        elif p.get("genre") == "h":
            p["motif"] = RE_ELIMINE_FEMININ.sub("Éliminé", p["motif"])
    return p


def nom_publie(p):
    """Applique NOMS_PUBLIES apres le calcul de l'identifiant."""
    juste = NOMS_PUBLIES.get(p.get("id"))
    if juste and p.get("nom_complet") != juste:
        p.setdefault("nom_source", p.get("nom_complet"))
        p["nom_complet"] = juste
    return p


def ecrire(participations, saisons):
    """Ecrit _data/participations.yml et _data/personnes.yml."""
    import collections
    chemin_p = os.path.join(RACINE, "_data", "participations.yml")
    participations = [nom_publie(accorder(corriger(p))) for p in participations]
    with open(chemin_p, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        donnees.ecrire([ordonner(p) for p in participations], f,
                       allow_unicode=True, sort_keys=False, width=100)

    annees = {s["id"]: s.get("annee") for s in saisons}
    gens = collections.OrderedDict()
    for p in participations:
        e = gens.setdefault(p["id"], {
            "id": p["id"], "nom": p["nom_complet"], "prenom": p["nom"],
            "genre": p.get("genre"), "participations": [],
        })
        if not e["genre"]:
            e["genre"] = p.get("genre")
        e["participations"].append(p["saison"])
    for e in gens.values():
        e["nb_participations"] = len(e["participations"])

    chemin_g = os.path.join(RACINE, "_data", "personnes.yml")
    with open(chemin_g, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        donnees.ecrire(list(gens.values()), f,
                       allow_unicode=True, sort_keys=False, width=100)
    return chemin_p, chemin_g, len(gens)


if __name__ == "__main__":
    parts, rapport, manques = main()
    print(f"participations fusionnees : {len(parts)}")
    print(f"\n--- champs encore vides ---")
    for champ, qui in sorted(manques.items()):
        print(f"  {champ:12s} {len(qui):4d}   {', '.join(qui[:8])}{' …' if len(qui) > 8 else ''}")
    print(f"\n--- rapport ({len(rapport)} entrées) ---")
    for r in rapport[:40]:
        print("  " + r)
    if len(rapport) > 40:
        print(f"  … et {len(rapport)-40} autres")

    if "--ecrire" in sys.argv:
        saisons = donnees.charger(open(os.path.join(RACINE, "_data", "saisons.yml")))
        cp, cg, n = ecrire(parts, saisons)
        print(f"\necrit : {cp} ({len(parts)} participations)")
        print(f"ecrit : {cg} ({n} personnes)")
