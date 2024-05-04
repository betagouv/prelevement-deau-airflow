#!/bin/bash

# Exporter les dépendances avec Poetry
poetry export --without-hashes --format=requirements.txt -o requirements.txt

# Vérifier si requirements.txt a changé
git diff --exit-code requirements.txt > /dev/null

# Si requirements.txt a changé, retourner 1 pour échouer le hook
if [ $? -ne 0 ]; then
  echo "requirements.txt has changed. Please add it to your commit."
  exit 1
fi
