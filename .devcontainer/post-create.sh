#!/bin/sh
# ----------------------------------------------------------------------------
# Se ejecuta una vez cada vez que se crea el contenedor del devcontainer
# (postCreateCommand), desde /workspace.
#
# Instala las herramientas de lint con las MISMAS versiones que la CI
# (requirements-lint.txt, el lock que usa .github/workflows/lint.yml) en un
# entorno aparte, /opt/lint. No van en /opt/venv porque requirements.txt fija
# otras versiones de black, flake8, isort y de sus dependencias (click,
# packaging...), y mezclarlas cambiaría las librerías de la aplicación.
#
# El editor usa /opt/lint/bin/{black,isort,flake8} (ver devcontainer.json), así
# que formatear al guardar da el mismo resultado que el job de Lint.
#
# También deja pre-commit en el PATH: si los hooks se instalaron en el
# ordenador (pre-commit install), al hacer commit desde el contenedor el hook
# no encuentra el Python del ordenador y recurre al pre-commit del PATH.
# ----------------------------------------------------------------------------

set -e

LINT_VENV=/opt/lint

python -m venv "$LINT_VENV"
"$LINT_VENV/bin/pip" install --no-cache-dir --require-hashes --only-binary :all: -r requirements-lint.txt
"$LINT_VENV/bin/pip" install --no-cache-dir "pre-commit==4.7.0"
ln -sf "$LINT_VENV/bin/pre-commit" /usr/local/bin/pre-commit

echo "Herramientas de lint instaladas en $LINT_VENV:"
"$LINT_VENV/bin/black" --version | head -1
"$LINT_VENV/bin/isort" --version-number
"$LINT_VENV/bin/flake8" --version
