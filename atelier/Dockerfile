# Atelier de travail du projet koh-lanta.
#
# Ce conteneur ne sert PAS a construire le site : GitHub Pages s'en charge, et
# un Jekyll local donnerait un resultat different (voir CLAUDE.md). Il sert a
# fabriquer les donnees et les graphiques qui, eux, sont commites dans le depot
# et lus par le constructeur de GitHub.
#
# Il est jetable : demarre a la demande par `appctl run atelier`, il ne tourne
# pas en permanence et n'expose aucun port.
FROM python:3.12-slim

# poppler-utils : lire les PDF deposes dans specs/ (pdftotext, pdftoppm).
# git          : verifier qu'aucun secret n'est suivi par l'index. Le conteneur
#                ne pousse rien -- la cle SSH est sur l'hote et n'est pas
#                montee -- il ne fait que lire l'etat du depot.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      poppler-utils \
      git \
      fonts-dejavu-core \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# PyYAML  : lire et ecrire les fichiers de _data/
# pandas  : agreger les participations, les epreuves et les votes
# numpy   : les calculs derriere les agregats
# matplotlib : produire les graphiques en SVG, sans serveur d'affichage
# scipy       : lois et tests exacts derriere les modeles
# scikit-learn: validation croisee, classification, reduction de dimension
# statsmodels : le seul des trois a rendre des erreurs-types, des intervalles
#               et un modele de duree (Cox). Sans lui, pas d'inference : on ne
#               publierait que des points sans incertitude.
RUN pip install --no-cache-dir \
      "PyYAML==6.0.2" \
      "pandas==2.2.3" \
      "numpy==2.1.3" \
      "matplotlib==3.9.2" \
      "scipy==1.14.1" \
      "scikit-learn==1.5.2" \
      "statsmodels==0.14.4"

# matplotlib sans affichage, et un cache ecrivable par l'utilisateur du depot
# Un seul fil de calcul. Ce n'est pas un reglage de performance : le nombre de
# fils change l'ordre des reductions BLAS, donc les derniers chiffres d'une
# moyenne. Les resultats seraient reproductibles a l'oeil et differents au
# diff, et _data/stats.yml bougerait sans qu'aucune donnee n'ait change.
ENV MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    PYTHONPATH=/depot/tools:/depot/tools/extraction

WORKDIR /depot
