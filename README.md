<div style="text-align: center;">
  <img src="https://www.uvlhub.io/static/img/logos/logo-light.svg" alt="Logo">
</div>

# uvlhub.io

Repository of feature models in UVL format integrated with Zenodo and flamapy following Open Science principles - Developed by DiversoLab

## Official documentation

You can consult the official documentation of the project at [docs.uvlhub.io](https://docs.uvlhub.io/)

## Entorno de desarrollo con devcontainer

El repositorio incluye un devcontainer (`.devcontainer/`) que levanta el mismo entorno que `docker/docker-compose.dev.yml` (aplicación, MariaDB y nginx) y abre VS Code dentro del contenedor de la aplicación.

**Requisitos:** Docker (Docker Desktop en Windows y macOS) y VS Code con la extensión *Dev Containers* (`ms-vscode-remote.remote-containers`).

**Uso:**

1. Clona el repositorio y ábrelo en VS Code.
2. Ejecuta *Dev Containers: Reopen in Container* (o acepta el aviso que aparece al abrir la carpeta).
3. La primera vez tarda unos minutos: construye las imágenes, crea las bases de datos `uvlhubdb` y `uvlhubdb_test`, aplica las migraciones y carga los datos de ejemplo.

Al terminar, la aplicación está en <http://localhost> (a través de nginx) y en el puerto 5000 que reenvía VS Code (Flask directamente). Se recarga sola al guardar cambios.

**Qué hace por ti:**

- Si no existe `.env` en la raíz, lo crea copiando `.env.docker.example`. Si ya tienes un `.env` de Vagrant o de una instalación local (`MARIADB_HOSTNAME=localhost`), cámbialo por el de Docker: dentro del contenedor la base de datos se llama `db`.
- Instala en `/opt/lint` flake8, black e isort con las mismas versiones que la CI (`requirements-lint.txt`). VS Code los usa para formatear y ordenar los imports al guardar y para marcar los errores de lint, así que lo que pasa en el editor pasa en el job de Lint. Desde la terminal, usa `pre-commit run --files <ficheros>` o `/opt/lint/bin/black`, `/opt/lint/bin/isort` y `/opt/lint/bin/flake8`: los `black`, `isort` y `flake8` del PATH son los de `requirements.txt` y pueden no coincidir con la CI.
- Instala git y pre-commit dentro del contenedor. Si instalaste los hooks en tu ordenador (`pre-commit install`, ver `.pre-commit-config.yaml`), también se ejecutan al hacer commit desde el contenedor.

**Problemas habituales:**

- *El puerto 3306 u 80 ya está en uso*: el compose publica MariaDB en el 3306 y nginx en el 80. Para el MySQL/MariaDB o el servidor web que tengas en local antes de abrir el devcontainer.
- *Error al arrancar el contenedor `web`*: revisa los logs con `docker logs web_app_container`. Suele ser un `.env` incorrecto o una migración que falla.
- *Cambios en `requirements.txt` o en los Dockerfile*: ejecuta *Dev Containers: Rebuild Container*.
