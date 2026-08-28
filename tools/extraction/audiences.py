#!/usr/bin/env python3
"""Lit les audiences televisees dans le wikitexte deja recupere.

Le site a longtemps ecrit qu'aucune donnee d'audience n'existait en source
publique. C'etait faux : l'article general de Wikipedia porte un tableau par
saison -- lancement, finale, moyenne, part de marche, recettes publicitaires --
et une quinzaine d'articles de saison portent en plus le detail episode par
episode.

Rien n'est telecharge ici : on relit `specs/sources/wiki/`, deja versionne.

    tools/atelier python3 tools/extraction/audiences.py --ecrire
"""
import argparse
import os
import re
import sys
import unicodedata

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
WIKI = os.path.join(RACINE, "specs", "sources", "wiki")
SORTIE = os.path.join(RACINE, "_data", "audiences.yml")

RE_NOMBRE = re.compile(r"\{\{\s*formatnum\s*:\s*([0-9  ]+)\s*\}\}", re.I)
RE_PART = re.compile(r"(\d{1,2})[,.](\d)\s*%")
# « (2012) », mais aussi « (2012-2013) » pour une saison a cheval sur deux
# annees civiles : c'est la premiere qui identifie la saison chez nous.
RE_ANNEE = re.compile(r"<small>\s*\((\d{4})(?:\s*[-–]\s*\d{4})?\)\s*</small>")
RE_LIEN = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")
RE_DATE = re.compile(r"\{\{\s*date\s*\|\s*(\d{1,2})\s*\|\s*([^|}]+?)\s*\|\s*(\d{4})", re.I)
RE_EURO = re.compile(r"\{\{\s*[EÉ]uro\s*\|\s*([0-9 ]+)\s*\}\}", re.I)
# Les lignes de synthese d'un tableau d'audiences par episode.
# Le jour de diffusion, dans la colonne « Jour et horaire ». La cellule porte
# souvent un rowspan : plusieurs saisons partagent la meme case, et seule la
# premiere la contient. On reporte donc la derniere valeur vue.
JOURS = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
RE_JOUR = re.compile(r"\b(" + "|".join(JOURS) + r")\b")

RE_AGREGAT = re.compile(r"\b(bilan|moyenne|total|ensemble de la saison)\b", re.I)

MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
        "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10,
        "novembre": 11, "decembre": 12}


def sansaccents(t):
    t = unicodedata.normalize("NFD", t or "")
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


def _entier(t):
    return int(re.sub(r"[^0-9]", "", t)) if t and re.search(r"\d", t) else None


def _nombres(bloc):
    return [_entier(m.group(1)) for m in RE_NOMBRE.finditer(bloc)]


def _parts(bloc):
    """Les parts de marche, dans l'ordre. On ecarte celles des notes de bas de
    page : une reference peut contenir « 17,7 % » dans son titre."""
    sans_ref = re.sub(r"<ref[^>]*>.*?</ref>", " ", bloc, flags=re.S | re.I)
    sans_ref = re.sub(r"<ref[^>]*/>", " ", sans_ref, flags=re.I)
    return [float(f"{m.group(1)}.{m.group(2)}") for m in RE_PART.finditer(sans_ref)]


def _tableaux(texte):
    """Rend les blocs `{| ... |}` du wikitexte.

    Le piege est le modele : « {{Heure|21|}} » contient la sequence `|}`, et un
    compteur naif y voit la fin du tableau -- il le coupe au bout de deux
    lignes. On empile donc les deux ouvertures, `{{` et `{|`, et une fermeture
    ne compte que si elle correspond a la derniere ouverture vue.
    """
    sortie, i = [], 0
    while True:
        d = texte.find("{|", i)
        if d < 0:
            return sortie
        pile, j = ["W"], d + 2
        while j < len(texte) - 1 and pile:
            duo = texte[j:j + 2]
            if duo == "{{":
                pile.append("T"); j += 2; continue
            if duo == "{|":
                pile.append("W"); j += 2; continue
            if duo == "}}" and pile[-1] == "T":
                pile.pop(); j += 2; continue
            if duo == "|}" and pile[-1] == "W":
                pile.pop(); j += 2; continue
            j += 1
        sortie.append(texte[d:j])
        i = j


def par_saison(saisons):
    """Le tableau de l'article general : une ligne par saison."""
    chemin = os.path.join(WIKI, "koh-lanta.wiki")
    if not os.path.exists(chemin):
        return [], ["article general absent de specs/sources/wiki/"]
    texte = open(chemin, encoding="utf-8").read()

    cible = None
    for t in _tableaux(texte):
        if "Revenus publicitaires" in t and "Lancement" in t and "Finale" in t:
            cible = t
            break
    if cible is None:
        return [], ["tableau des audiences introuvable dans l'article general"]

    # Index des saisons par (titre normalise, annee) puis par annee seule.
    par_titre = {}
    for s in saisons:
        if s.get("annulee"):
            continue
        par_titre[(sansaccents(s.get("titre") or ""), s.get("annee"))] = s

    lignes, rapport = [], []
    jour = None
    for bloc in cible.split("\n|-"):
        marque = RE_ANNEE.search(bloc)
        if not marque:
            continue
        annee = int(marque.group(1))
        # Le libelle de la saison : le texte avant la parenthese d'annee.
        tete = bloc[:marque.start()]
        tete = RE_LIEN.sub(lambda m: m.group(2) or m.group(1), tete)
        # On retire l'italique (deux apostrophes) mais PAS l'apostrophe simple :
        # « L'Île au trésor » n'est pas « L Île au trésor ».
        tete = re.sub(r"<[^>]*>", " ", tete)
        tete = tete.replace("''", " ")
        tete = re.sub(r"[|{}\[\]]", " ", tete)
        tete = re.sub(r"^\s*Koh-Lanta\s*:?\s*", "", tete.strip())
        titre = re.sub(r"\s+", " ", tete).strip(" :–-")

        s = par_titre.get((sansaccents(titre), annee))
        if s is None:
            candidats = [v for (t, a), v in par_titre.items() if a == annee]
            if len(candidats) == 1:
                s = candidats[0]
        if s is None:
            rapport.append(f"audience non rattachee : « {titre} » ({annee})")
            continue

        # Le jour de diffusion, hors references : une note de bas de page parle
        # souvent du vendredi sans que ce soit le jour de cette saison-la.
        sans_ref = re.sub(r"<ref[^>]*>.*?</ref>", " ", bloc, flags=re.S | re.I)
        sans_ref = re.sub(r"<ref[^>]*/>", " ", sans_ref, flags=re.I)
        m = RE_JOUR.search(sans_ref)
        if m:
            jour = m.group(1)

        nb, pdm = _nombres(bloc), _parts(bloc)
        if len(nb) < 3:
            rapport.append(f"{s['id']} : ligne d'audience incomplete "
                           f"({len(nb)} nombres, {len(pdm)} parts)")
            continue
        if len(pdm) < 3:
            # Une part de marche manque parfois dans le tableau. On garde les
            # effectifs, qui sont la mesure principale, et on le dit.
            rapport.append(f"{s['id']} : {3 - len(pdm)} part(s) de marche absente(s)")
            pdm = pdm + [None] * (3 - len(pdm))
        euro = RE_EURO.search(bloc)
        lignes.append({
            "saison": s["id"], "titre": s.get("titre"), "annee": annee,
            "jour": jour,
            "lancement": nb[0], "lancement_pdm": pdm[0],
            "finale": nb[1], "finale_pdm": pdm[1],
            "moyenne": nb[2], "moyenne_pdm": pdm[2],
            "recettes_publicitaires": _entier(euro.group(1)) if euro else None,
        })
    lignes.sort(key=lambda x: (x["annee"], x["saison"]))
    return lignes, rapport


def par_episode(saisons):
    """Le detail episode par episode, la ou l'article de saison le donne."""
    lignes, rapport = [], []
    for s in saisons:
        if s.get("annulee"):
            continue
        chemin = os.path.join(WIKI, f"{s['id']}.wiki")
        if not os.path.exists(chemin):
            continue
        texte = open(chemin, encoding="utf-8").read()
        cible = None
        for t in _tableaux(texte):
            if RE_NOMBRE.search(t) and re.search(r"t[ée]l[ée]spectateurs", t, re.I):
                cible = t
                break
        if cible is None:
            continue

        numero, agreges = 0, 0
        for bloc in cible.split("\n|-"):
            nb = _nombres(bloc)
            if not nb:
                continue
            # Le tableau se termine parfois par une ligne de synthese
            # (« Bilan de la saison »). Ce n'est pas un episode.
            if RE_AGREGAT.search(bloc):
                agreges += 1
                continue
            pdm = _parts(bloc)
            d = RE_DATE.search(bloc)
            date = None
            if d:
                mois = MOIS.get(sansaccents(d.group(2)))
                if mois:
                    date = f"{int(d.group(3)):04d}-{mois:02d}-{int(d.group(1)):02d}"
            # Depuis 2022, un episode est coupe en deux et mesure deux fois :
            # la ligne porte alors deux effectifs ET deux parts de marche. Une
            # ligne qui porte deux effectifs pour une seule part n'est pas un
            # episode double : le second nombre y est autre chose (un pic, une
            # audience de rattrapage). On s'aligne donc sur les parts.
            garde = nb[:max(1, len(pdm))]
            for k, v in enumerate(garde):
                numero += 1
                lignes.append({
                    "saison": s["id"], "annee": s.get("annee"),
                    "mesure": numero, "date": date,
                    "telespectateurs": v,
                    "pdm": pdm[k] if k < len(pdm) else None,
                })
        if numero:
            msg = f"{s['id']} : {numero} mesures d'audience par episode"
            if agreges:
                msg += f" ({agreges} ligne(s) de synthese ecartee(s))"
            rapport.append(msg)
    return lignes, rapport


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ecrire", action="store_true")
    a = a.parse_args()

    saisons = yaml.safe_load(open(os.path.join(RACINE, "_data", "saisons.yml"),
                                  encoding="utf-8"))
    saison_lignes, r1 = par_saison(saisons)
    episode_lignes, r2 = par_episode(saisons)

    diffusees = [s for s in saisons if not s.get("annulee")]
    print(f"saisons avec audience : {len(saison_lignes)} sur {len(diffusees)}")
    manquantes = [s["id"] for s in diffusees
                  if s["id"] not in {x["saison"] for x in saison_lignes}]
    if manquantes:
        print(f"sans audience : {', '.join(manquantes)}")
    print(f"mesures par episode   : {len(episode_lignes)} sur "
          f"{len({x['saison'] for x in episode_lignes})} saisons")
    for x in r1 + r2:
        print("  " + x)

    sortie = {
        "source": "https://fr.wikipedia.org/wiki/Koh-Lanta et les articles de saison",
        "champ": "audience TF1 en direct (veille), part de marche 4 ans et plus",
        "saisons": saison_lignes,
        "episodes": episode_lignes,
        "saisons_couvertes": len(saison_lignes),
        "saisons_diffusees": len(diffusees),
        "saisons_sans_audience": manquantes,
        "saisons_par_episode": sorted({x["saison"] for x in episode_lignes}),
    }
    if a.ecrire:
        with open(SORTIE, "w", encoding="utf-8") as f:
            f.write("# Fichier genere par tools/extraction/audiences.py.\n"
                    "# Ne pas editer a la main : toute modification sera ecrasee.\n")
            yaml.safe_dump(sortie, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
