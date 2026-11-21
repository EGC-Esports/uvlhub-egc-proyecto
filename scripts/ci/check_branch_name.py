"""Comprueba que el nombre de la rama sigue la convención del equipo (acta fundacional §7.1).

Ramas permitidas: ``main``, ``trunk`` y las ramas de tarea::

    tipo/N-descripcion        p. ej. feat/12-fakenodo, fix/15-validacion

Uso::

    python scripts/ci/check_branch_name.py feat/12-fakenodo
    python scripts/ci/check_branch_name.py            # usa la rama actual de git
    python scripts/ci/check_branch_name.py --pre-push # hook pre-push de pre-commit

En modo ``--pre-push`` toma la rama de destino de las variables que define
pre-commit y, además, impide empujar directamente a ``main`` (§7.6). Solo David
actualiza ``main`` en las releases, y para eso define ``ALLOW_PUSH_TO_MAIN=1``.
Los tags no se comprueban.

Sale con código 1 si el nombre no es válido o el push no está permitido.
"""

import os
import re
import subprocess
import sys

PERMANENT_BRANCHES = ("main", "trunk")

TASK_BRANCH_PATTERN = re.compile(r"^(feat|fix|docs|test|ci|refactor|chore)/\d+-[a-z0-9-]+$")


def is_valid_branch(name: str) -> bool:
    return name in PERMANENT_BRANCHES or bool(TASK_BRANCH_PATTERN.match(name))


def current_branch() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def error_prefix(title: str) -> str:
    return f"::error title={title}::" if os.getenv("GITHUB_ACTIONS") == "true" else "ERROR: "


def check_name(name: str) -> int:
    if is_valid_branch(name):
        print(f"Nombre de rama válido: {name}")
        return 0

    print(f"{error_prefix('Nombre de rama no válido')}«{name}» no sigue la convención tipo/N-descripcion")
    print()
    print("Ramas permitidas: main, trunk o tipo/N-descripcion")
    print("Tipos: feat, fix, docs, test, ci, refactor, chore")
    print("Ejemplos: feat/12-fakenodo, fix/15-validacion")
    print("Para renombrar la rama actual: git branch -m tipo/N-descripcion")
    return 1


def check_pre_push(env: dict[str, str]) -> int:
    """Hook pre-push. pre-commit deja la rama de destino en PRE_COMMIT_REMOTE_BRANCH (refs/heads/...)."""
    remote_ref = env.get("PRE_COMMIT_REMOTE_BRANCH", "")
    if not remote_ref.startswith("refs/heads/"):
        # Tags (refs/tags/...) u otros refs: no son ramas, no hay nada que comprobar.
        return 0
    branch = remote_ref.removeprefix("refs/heads/")

    if branch == "main" and env.get("ALLOW_PUSH_TO_MAIN") != "1":
        print("ERROR: no se empuja directamente a main.")
        print()
        print("El trabajo entra en trunk y main solo avanza en las releases, con")
        print("git merge --ff-only trunk. Si eres quien hace la release, repite el push")
        print("con ALLOW_PUSH_TO_MAIN=1:")
        print("  PowerShell:  $env:ALLOW_PUSH_TO_MAIN=1; git push origin main --tags")
        print("  bash:        ALLOW_PUSH_TO_MAIN=1 git push origin main --tags")
        return 1

    return check_name(branch)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--pre-push"]:
        return check_pre_push(dict(os.environ))
    return check_name(argv[0] if argv else current_branch())


if __name__ == "__main__":
    sys.exit(main())
