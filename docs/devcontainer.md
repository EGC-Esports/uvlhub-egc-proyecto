# Guía del entorno de desarrollo (Dev Container)

El repositorio dispone de una configuración completa de **Dev Container** en `.devcontainer/` que levanta el entorno común basado en Docker definido en el [Acta Fundacional §8](diario/actas/acta-fundacional.md#8-gestión-de-incidencias-pruebas-y-cicd).

## 1. Qué es y por qué lo usamos

El Dev Container garantiza que los cinco integrantes de **Esports-hub** trabajen exactamente con las mismas versiones de Python (`3.13`), dependencias de aplicación, herramientas de lint (`black`, `isort`, `flake8`) y base de datos MariaDB, evitando diferencias entre sistemas operativos (Windows, macOS o Linux).

## 2. Requisitos previos

- **Docker:** Docker Desktop (Windows/macOS) o Docker Engine + Compose (Linux).
- **Visual Studio Code** con la extensión oficial **Dev Containers** (`ms-vscode-remote.remote-containers`).

## 3. Arquitectura y configuración real en el repositorio

La configuración reside en [`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json), [`.devcontainer/post-create.sh`](../.devcontainer/post-create.sh) y [`docker/docker-compose.dev.yml`](../docker/docker-compose.dev.yml):

| Elemento | Configuración real del repositorio |
| --- | --- |
| **Nombre del Dev Container** | `UVLHub Dev` |
| **Compose asociado** | `docker/docker-compose.dev.yml` (`name: uvlhub`), servicio principal `web` |
| **Servicios arrancados por defecto** | `web` (`web_app_container`), `db` (`mariadb_container`), `nginx` (`nginx_web_server_container`) y `selenium-hub` (`selenium_hub_container`, al declararse `depends_on: [db, selenium-hub]` en `web`) |
| **Otros servicios en el Compose** | `selenium-chrome` y `selenium-firefox` (disponibles en `docker-compose.dev.yml` para pruebas E2E) |
| **Imagen base de `web`** | `python:3.13-slim` (`docker/images/Dockerfile.dev`, multietapa con `/opt/venv` y Docker CLI) |
| **Puertos** | `5000` (Flask directo, reenviado por VS Code), `80` (`nginx`), `3306` (`db` MariaDB); `4442-4444`, `5900-5901` si se levanta Selenium |
| **Variables de entorno** | Si no existe `.env` en la raíz, `initializeCommand` lo copia automáticamente desde `.env.docker.example` (`MARIADB_HOSTNAME=db`, `FLASK_ENV=development`) |
| **Entorno de lint (`/opt/lint`)** | `post-create.sh` instala `requirements-lint.txt` (`black==26.10.1`, `flake8==7.5.0`, `flake8-pyproject==1.2.4`, `isort==9.0.2`) y `pre-commit==4.7.0` |
| **Extensiones de VS Code** | `ms-azuretools.vscode-docker`, `ms-python.python`, `ms-python.debugpy`, `ms-python.black-formatter`, `ms-python.isort`, `ms-python.flake8`, `KevinRose.vsc-python-indent`, `dbaeumer.vscode-eslint`, `twixes.pypi-assistant`, `cstrap.flask-snippets` |
| **Ajustes del editor** | Intérprete `/opt/venv/bin/python`, `pytest` habilitado, formateo al guardar con `/opt/lint/bin/black` y organización de imports con `/opt/lint/bin/isort` |

## 4. Cómo arrancarlo paso a paso

1. Clona el repositorio en tu máquina y abre la carpeta raíz en Visual Studio Code.
2. Pulsa `F1` (o `Ctrl+Shift+P` / `Cmd+Shift+P`) y selecciona **Dev Containers: Reopen in Container**.
3. En el primer arranque, Docker construirá las imágenes, creará `.env` (si no existía), ejecutará `.devcontainer/post-create.sh` y lanzará `docker/entrypoints/development_entrypoint.sh`, que espera a MariaDB, crea `uvlhubdb` y `uvlhubdb_test`, aplica migraciones (`flask db upgrade`) y siembra datos iniciales (`rosemary db:seed -y`).
4. Para verificar que está listo, accede en tu navegador a `http://localhost` (vía `nginx`) o `http://localhost:5000` (Flask directo).
5. Si cambian `requirements.txt`, `requirements-lint.txt` o los `Dockerfile`, ejecuta **Dev Containers: Rebuild Container**.

## 5. Uso diario dentro del Dev Container

- **Aplicación web:** el contenedor `web` arranca Flask con recarga automática (`flask run --host=0.0.0.0 --port=5000 --reload --debug`).
- **Migraciones y seeders:**
  ```bash
  flask db upgrade
  rosemary db:seed -y
  ```
- **Pruebas con `pytest`:**
  ```bash
  pytest -m unit -q
  pytest -m "not e2e and not load"
  ```
- **Lint y formato (mismas versiones que la CI):**
  > **Importante:** Usa siempre `pre-commit run` o los binarios de `/opt/lint/bin/{black,isort,flake8}`; las versiones disponibles directamente en el `PATH` proceden de `requirements.txt` y pueden diferir de las de la CI (`requirements-lint.txt`).
  ```bash
  pre-commit run --files <ficheros>
  # o directamente desde /opt/lint:
  /opt/lint/bin/flake8 app rosemary scripts tests
  /opt/lint/bin/black --check app rosemary scripts tests
  /opt/lint/bin/isort --check-only app rosemary scripts tests
  ```
- **Identidad Git:** comprueba dentro del contenedor que `git config user.name` y `git config user.email` coinciden exactamente con tu cuenta de GitHub.

## 6. Solución de problemas frecuentes

- **Puertos `80` o `3306` ocupados:** detén cualquier servidor web o instancia local de MySQL/MariaDB antes de abrir el Dev Container.
- **`.env` heredado de otra configuración:** si tenías un `.env` local o de Vagrant (`MARIADB_HOSTNAME=localhost`), cámbialo por el de `.env.docker.example` (`MARIADB_HOSTNAME=db`).
- **Error al iniciar el contenedor `web`:** inspecciona los registros con `docker logs web_app_container`.
- **Finales de línea (CRLF vs LF):** el repositorio incluye `.gitattributes`; asegúrate de mantener `LF` en scripts `.sh` para evitar errores al ejecutar entrypoints en Linux.
- **Cambios en `.devcontainer/` o variables de entorno:** ejecuta **Dev Containers: Rebuild Container** para aplicar los cambios.
