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
# Sans lui, un PDF sans couche texte est illisible.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      poppler-utils \
      fonts-dejavu-core \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# PyYAML  : lire et ecrire les fichiers de _data/
# pandas  : agreger les participations, les epreuves et les votes
# numpy   : les calculs derriere les agregats
# matplotlib : produire les graphiques en SVG, sans serveur d'affichage
RUN pip install --no-cache-dir \
      "PyYAML==6.0.2" \
      "pandas==2.2.3" \
      "numpy==2.1.3" \
      "matplotlib==3.9.2"

# matplotlib sans affichage, et un cache ecrivable par l'utilisateur du depot
ENV MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/depot/tools:/depot/tools/extraction

WORKDIR /depot
