#!/usr/bin/env python3
"""Indicateurs avances, par aventurier et par saison.

Les definitions s'inspirent de celles que la communaute statistique de
*Survivor* a stabilisees -- True Dork Times et survivor-reference.com -- puis
les adaptent a Koh-Lanta et, surtout, a ce que CES donnees permettent
reellement de calculer. Chaque indicateur porte son denominateur, parce que
c'est lui qui decide de ce qu'un chiffre veut dire.

Deux principes tiennent tout :

  * un indicateur au bulletin ne se calcule que sur les conseils dont le
    depouillement est COMPLET -- ailleurs, l'absence d'un bulletin serait lue
    comme un vote qui n'a pas eu lieu ;
  * un ratio sans effectif minimal ne veut rien dire : une seule reussite sur
    un seul essai afficherait 100 %. Chaque classement porte donc un seuil.
"""
import math
from collections import Counter, defaultdict

SEUIL_CONSEILS = 4        # sous ce nombre, un taux de vote n'a pas de sens
SEUIL_EPREUVES = 8        # idem pour un ratio d'epreuves


def eliminations(conseils):
    """Les conseils qui font sortir quelqu'un -- et eux seuls.

    Le dernier scrutin d'une saison n'est pas un conseil mais le vote du jury
    final : y ecrire un nom veut dire « qu'il gagne ». Le compter comme une
    elimination inverserait le sens de chaque bulletin. Huit saisons sont
    concernees, pour 49 bulletins.

    Tout calcul portant sur les eliminations passe par ici. Les lignes plus
    anciennes n'ayant pas de champ `type`, l'absence vaut `elimination`.
    """
    return [c for c in conseils if c.get("type", "elimination") != "jury"]


def votes_du_jury(conseils):
    """L'inverse : les scrutins finaux, ou l'on vote POUR."""
    return [c for c in conseils if c.get("type") == "jury"]


def _episode_de_sortie(conseils, parts, epreuves):
    """(saison, personne) -> episode ou la personne quitte le jeu."""
    sortie = {}
    for c in conseils:
        if c.get("elimine_rattache") and c.get("episode"):
            try:
                sortie[(c["saison"], c["elimine"])] = int(c["episode"])
            except (TypeError, ValueError):
                pass
    dernier = defaultdict(int)
    for source in (conseils, epreuves):
        for x in source:
            try:
                dernier[x["saison"]] = max(dernier[x["saison"]], int(x.get("episode") or 0))
            except (TypeError, ValueError):
                pass
    for p in parts:
        if p.get("sort") in ("vainqueur", "finaliste"):
            sortie.setdefault((p["saison"], p["id"]), dernier.get(p["saison"], 0))
    return sortie, dernier


def indicateurs_individuels(saisons, parts, conseils, epreuves):
    """Rend une ligne d'indicateurs par participation exploitable.

    Les quatre mesures de vote suivent les definitions de la communaute
    *Survivor*, adaptees :

    justesse_vote      bulletins portes sur la personne effectivement eliminee,
                       rapportes aux conseils ou l'aventurier a vote. Mesure
                       s'il etait du bon cote du vote.
    survie_conseil     conseils traverses sans etre elimine, rapportes aux
                       conseils auxquels il a assiste.
    menace             voix recues rapportees aux conseils assistes. Plus le
                       chiffre est haut, plus il etait vise -- donc percu comme
                       menacant, ou comme facile a sortir.
    evasion            conseils survecus ALORS QU'IL AVAIT ETE VISE, rapportes
                       aux conseils ou il a recu au moins une voix. C'est la
                       mesure de ceux qui s'en sortent quand ca chauffe.
    """
    par_saison = {s["id"]: s for s in saisons}
    fiches = {(p["saison"], p["id"]): p for p in parts}
    sortie, dernier_episode = _episode_de_sortie(conseils, parts, epreuves)

    # --- conseils : presence, bulletins, voix recues
    assistes = Counter()          # (saison, personne) -> conseils assistes
    votes_justes = Counter()
    votes_emis = Counter()
    vises = Counter()             # conseils ou il a recu >= 1 voix
    voix_recues = Counter()
    survecus_vise = Counter()

    conseils = eliminations(conseils)
    conseils_par_saison = defaultdict(list)
    for c in conseils:
        conseils_par_saison[c["saison"]].append(c)

    for c in conseils:
        sid = c["saison"]
        ep = c.get("episode")
        try:
            ep = int(ep)
        except (TypeError, ValueError):
            ep = None
        elimine = c.get("elimine") if c.get("elimine_rattache") else None

        # Un « conseil » de la source recouvre parfois un depart SANS vote --
        # abandon, orientation, poteaux. Les compter comme des conseils gonfle
        # le denominateur et ecrase tous les taux. Seul un conseil ou l'on a
        # vote compte ici.
        vote_reel = bool(c.get("votes_exprimes")) or bool(c.get("votes"))
        if ep is not None and vote_reel:
            for (s2, pid), ep_sortie in sortie.items():
                if s2 == sid and ep_sortie >= ep:
                    assistes[(sid, pid)] += 1

        if not c.get("complet"):
            continue          # au bulletin, seuls les conseils complets comptent

        contre = Counter()
        for b in c["votes"]:
            if b.get("cible_rattachee"):
                contre[b["cible"]] += 1
            # La justesse ne se mesure que la ou l'on SAIT qui est parti.
            # Compter le bulletin sans connaitre l'elimine mettrait au
            # denominateur un cas que le numerateur ne peut jamais satisfaire.
            if elimine and b.get("votant_rattache"):
                votes_emis[(sid, b["votant"])] += 1
                if b.get("cible_rattachee") and b["cible"] == elimine:
                    votes_justes[(sid, b["votant"])] += 1
        for pid, n in contre.items():
            vises[(sid, pid)] += 1
            if elimine and pid != elimine:
                survecus_vise[(sid, pid)] += 1

    # --- epreuves individuelles
    gagnees = Counter()
    individuelles = defaultdict(list)
    for e in epreuves:
        if e.get("forme") == "individuelle" and e.get("episode"):
            individuelles[e["saison"]].append(e)
        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                gagnees[(e["saison"], v["id"])] += 1

    lignes = []
    for (sid, pid), p in fiches.items():
        s = par_saison.get(sid, {})
        if s.get("annulee") or s.get("en_cours"):
            continue
        ep_sortie = sortie.get((sid, pid))
        n_assistes = assistes[(sid, pid)]
        n_emis = votes_emis[(sid, pid)]
        n_vises = vises[(sid, pid)]

        disputees = None
        if ep_sortie:
            disputees = sum(1 for e in individuelles.get(sid, [])
                            if e["episode"] <= ep_sortie)

        def taux(num, den, seuil=1):
            return round(100.0 * num / den, 1) if den and den >= seuil else None

        lignes.append({
            "id": pid, "saison": sid,
            "nom": p.get("nom_complet") or p.get("nom"),
            "titre": s.get("titre"), "annee": s.get("annee"),
            "speciale": bool(s.get("speciale")),
            "sort": p.get("sort"), "genre": p.get("genre"), "age": p.get("age"),
            "csp": p.get("_csp"),
            "survie": p.get("_survie"),
            "conseils_assistes": n_assistes,
            "bulletins_emis": n_emis,
            "justesse_vote": taux(votes_justes[(sid, pid)], n_emis, SEUIL_CONSEILS),
            "survie_conseil": taux(
                max(0, n_assistes - (1 if (p.get("sort") or "") == "elimine_conseil" else 0)),
                n_assistes, SEUIL_CONSEILS),
            # Le total des voix recues vient du tableau des candidats, qui le
            # donne pour la saison entiere -- bien plus fiable que la somme des
            # conseils dont on a le depouillement complet.
            "voix_recues": p.get("votes_recus"),
            "menace": (round(p["votes_recus"] / n_assistes, 2)
                       if p.get("votes_recus") is not None
                       and n_assistes >= SEUIL_CONSEILS else None),
            "conseils_vise": n_vises,
            "evasion": taux(survecus_vise[(sid, pid)], n_vises, 2),
            "epreuves_gagnees": gagnees[(sid, pid)],
            "epreuves_disputees": disputees,
            "ratio_epreuves": taux(gagnees[(sid, pid)], disputees, SEUIL_EPREUVES),
        })
    return lignes


def _entropie(compte):
    """Entropie de Shannon normalisee : 0 = un seul beneficiaire, 1 = parfaitement etale."""
    total = sum(compte.values())
    if total <= 0 or len(compte) <= 1:
        return 0.0
    h = -sum((n / total) * math.log(n / total) for n in compte.values() if n)
    return round(h / math.log(len(compte)), 3)


def _concentration(compte):
    """Indice de Herfindahl : 1 = une seule personne rafle tout."""
    total = sum(compte.values())
    if total <= 0:
        return None
    return round(sum((n / total) ** 2 for n in compte.values()), 3)


def indicateurs_saison(saisons, parts, conseils, epreuves, colliers):
    """Une ligne d'indicateurs par saison.

    Trois mesures meritent un mot, parce qu'elles ne se lisent nulle part
    ailleurs :

    domination_epreuves  concentration de Herfindahl sur les victoires
                         individuelles. Proche de 1 : un seul aventurier a tout
                         rafle. Proche de 0 : les victoires ont circule.
    dispersion_votes     entropie des bulletins d'un conseil, moyennee sur la
                         saison. 0 : le camp vote d'un bloc. 1 : chacun vote
                         dans son coin, plus personne ne controle rien.
    tension_conseils     part des conseils ou l'elimine l'a ete a une voix pres.
    """
    par_saison = {s["id"]: s for s in saisons}
    parts_par_saison = defaultdict(list)
    for p in parts:
        parts_par_saison[p["saison"]].append(p)

    conseils_par_saison = defaultdict(list)
    for c in eliminations(conseils):
        conseils_par_saison[c["saison"]].append(c)

    epreuves_par_saison = defaultdict(list)
    for e in epreuves:
        epreuves_par_saison[e["saison"]].append(e)

    colliers_par_saison = defaultdict(list)
    for c in colliers or []:
        colliers_par_saison[c["saison"]].append(c)

    lignes = []
    for s in saisons:
        if s.get("annulee"):
            continue
        sid = s["id"]
        lot = parts_par_saison.get(sid, [])
        cs = conseils_par_saison.get(sid, [])
        es = epreuves_par_saison.get(sid, [])
        cols = colliers_par_saison.get(sid, [])

        victoires = Counter()
        for e in es:
            if e.get("forme") != "individuelle":
                continue
            for v in e.get("vainqueurs") or []:
                if v.get("type") == "personne" and v.get("id"):
                    victoires[v["id"]] += 1

        dispersions = []
        for c in cs:
            if not c.get("complet"):
                continue
            cibles = Counter(b["cible"] for b in c["votes"] if b.get("cible_rattachee"))
            if sum(cibles.values()) >= 4:
                dispersions.append(_entropie(cibles))

        avec_decompte = [c for c in cs if c.get("votes_exprimes")]
        serres = [c for c in avec_decompte
                  if c["votes_contre"] and c["votes_exprimes"]
                  and c["votes_contre"] * 2 <= c["votes_exprimes"] + 1]

        abandons = sum(1 for p in lot
                       if p.get("sort") in ("abandon_medical", "abandon_volontaire"))
        ages = [p["age"] for p in lot if p.get("age")]
        survies = [p["_survie"] for p in lot if p.get("_survie") is not None]

        lignes.append({
            "id": sid, "numero": s.get("numero"), "titre": s.get("titre"),
            "annee": s.get("annee"), "speciale": bool(s.get("speciale")),
            "en_cours": bool(s.get("en_cours")),
            "effectif": len(lot),
            "duree_jours": s.get("duree_jours"),
            "age_moyen": round(sum(ages) / len(ages), 1) if ages else None,
            "survie_moyenne": round(sum(survies) / len(survies), 1) if survies else None,
            "abandons": abandons,
            "taux_abandon": round(100.0 * abandons / len(lot), 1) if lot else None,
            "conseils": len(cs),
            "conseils_complets": sum(1 for c in cs if c.get("complet")),
            "tension_conseils": (round(100.0 * len(serres) / len(avec_decompte), 1)
                                 if avec_decompte else None),
            "dispersion_votes": (round(sum(dispersions) / len(dispersions), 3)
                                 if dispersions else None),
            "epreuves": len(es),
            "epreuves_individuelles": sum(1 for e in es if e.get("forme") == "individuelle"),
            "domination_epreuves": _concentration(victoires) if victoires else None,
            "meilleur_gagnant": (max(victoires.items(), key=lambda x: x[1])[0]
                                 if victoires else None),
            "victoires_du_meilleur": (max(victoires.values()) if victoires else None),
            "colliers": len(cols),
            "colliers_joues": sum(1 for c in cols if c.get("statut") == "utilise"),
            "voix_annulees": sum(c.get("votes_annules") or 0 for c in cols),
            "mecaniques": s.get("mecaniques") or [],
        })
    return lignes


def fantomes(lignes_individuelles):
    """Aventuriers ayant traverse une saison entiere sans recevoir une seule voix.

    L'equivalent du « Ghost » de la statistique *Survivor* : passer plusieurs
    conseils sans que personne n'ecrive votre nom, c'est une performance sociale
    -- ou une invisibilite totale. Les deux se discutent, le chiffre ne se
    discute pas.
    """
    out = []
    for x in lignes_individuelles:
        # `voix_recues` doit valoir zero, pas etre inconnu : une source muette
        # ferait passer pour intouchable quelqu'un dont on ignore tout.
        if x["voix_recues"] == 0 and x["conseils_assistes"] >= 5:
            out.append(x)
    return sorted(out, key=lambda x: (-x["conseils_assistes"], -(x["survie"] or 0)))
