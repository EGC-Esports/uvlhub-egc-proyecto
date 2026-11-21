"""Comprueba que los mensajes de commit siguen Conventional Commits con la issue al final.

Formato de la primera línea (acta fundacional §7.5)::

    tipo(ámbito opcional)!: descripción (#N)

Se dejan pasar sin comprobar los mensajes que empiezan por ``Merge `` y ``Revert ``,
porque los genera git al integrar o revertir.

Dos modos de uso:

* Hook ``commit-msg`` de git, que pasa la ruta del fichero con el mensaje::

    python scripts/ci/check_commit_msg.py .git/COMMIT_EDITMSG

* CI, sobre un conjunto de commits. Lo que va detrás de ``--git`` son revisiones
  para ``git log`` (un rango, ``HEAD``, ``^rama``…)::

    python scripts/ci/check_commit_msg.py --git -- origin/trunk..HEAD

Seguridad: las revisiones solo pueden tener los caracteres de un nombre de rama o
de un rango y nunca empezar por ``-``, y van detrás de ``--end-of-options``, así que
git nunca las toma por opciones (``--output=fichero`` escribiría en disco). En modo
hook solo se abre un fichero de dentro del directorio ``.git`` del repositorio.

Sale con código 1 si algún mensaje no cumple el formato.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

TYPES = ("feat", "fix", "docs", "test", "ci", "refactor", "chore", "build", "perf", "style", "revert")

COMMIT_PATTERN = re.compile(r"^(" + "|".join(TYPES) + r")(\([a-z0-9-]+\))?!?: .+ \(#\d+\)$")

IGNORED_PREFIXES = ("Merge ", "Revert ")

# Una revisión de git: ref, sha, HEAD~1, ^refs/remotes/origin/trunk, A..B, A...B.
# Empieza siempre por letra o número (tras un ^ opcional): nunca por "-".
_REF = r"[A-Za-z0-9][A-Za-z0-9._/@{}~^-]*"
REVISION_PATTERN = re.compile(rf"\^?{_REF}(\.\.\.?{_REF})?")

EXAMPLES = (
    "feat(fakenodo): simular publicación de depósito (#12)",
    "fix(dataset): validar columnas obligatorias del CSV (#15)",
    "docs(diario): añadir acta de la reunión del 23 de noviembre (#30)",
)


def is_valid_subject(subject: str) -> bool:
    """True si la primera línea del mensaje cumple el formato o es un merge/revert de git."""
    if subject.startswith(IGNORED_PREFIXES):
        return True
    return bool(COMMIT_PATTERN.match(subject))


def subject_from_message(message: str) -> str:
    """Primera línea con contenido, ignorando los comentarios que añade git (``#``)."""
    for line in message.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def safe_revisions(revisions: list[str]) -> list[str]:
    """Las revisiones si todas tienen forma de revisión de git; si no, ValueError."""
    for revision in revisions:
        if not REVISION_PATTERN.fullmatch(revision):
            raise ValueError(f"«{revision}» no es una revisión de git válida (rama, sha o rango A..B)")
    return list(revisions)


def commits_from_git(revisions: list[str]) -> list[tuple[str, str]]:
    """Lista de (sha corto, asunto) de los commits que devuelve ``git log <revisions>``."""
    output = subprocess.run(
        ["git", "log", "--format=%h%x1f%s", "--end-of-options", *safe_revisions(revisions)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    commits = []
    for line in output.splitlines():
        if line:
            sha, _, subject = line.partition("\x1f")
            commits.append((sha, subject))
    return commits


def report_error(text: str) -> None:
    # En GitHub Actions, ::error:: hace que el fallo salga como anotación en el resumen del run.
    prefix = "::error title=Commit no válido::" if os.getenv("GITHUB_ACTIONS") == "true" else "ERROR: "
    print(f"{prefix}{text}")


def print_help_footer() -> None:
    print()
    print("Formato esperado: tipo(ámbito opcional): descripción (#N)")
    print(f"Tipos permitidos: {', '.join(TYPES)}")
    print("Ejemplos válidos:")
    for example in EXAMPLES:
        print(f"  {example}")


def git_dir() -> Path:
    """Directorio de git del repositorio actual (en un worktree, el de ese worktree)."""
    output = subprocess.run(
        ["git", "rev-parse", "--absolute-git-dir"], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout
    return Path(output.strip()).resolve()


def message_file_inside_git_dir(path: str) -> Path:
    """La ruta resuelta si está dentro del directorio de git (donde git deja COMMIT_EDITMSG); si no, ValueError."""
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(git_dir()):
        raise ValueError(f"«{path}» no está dentro del directorio .git del repositorio")
    return resolved


def check_commits(git_args: list[str]) -> int:
    """Modo CI: comprueba todos los commits que devuelve ``git log <git_args>``."""
    if not git_args:
        report_error("--git necesita un rango de commits, p. ej. origin/trunk..HEAD")
        return 2
    try:
        commits = commits_from_git(git_args)
    except ValueError as exc:
        report_error(str(exc))
        return 2
    if not commits:
        print("No hay commits nuevos que comprobar.")
        return 0
    invalid = [(sha, subject) for sha, subject in commits if not is_valid_subject(subject)]
    for sha, subject in commits:
        mark = "MAL" if (sha, subject) in invalid else "ok "
        print(f"[{mark}] {sha} {subject}")
    if invalid:
        print()
        for sha, subject in invalid:
            report_error(f"{sha}: «{subject}» no sigue el formato tipo(ámbito): descripción (#N)")
        print_help_footer()
        return 1
    print(f"\nLos {len(commits)} commits cumplen el formato.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    # --git se separa a mano: con argparse, un "--" detrás hacía que el rango acabara en
    # el argumento posicional y git log recorriera toda la historia.
    if argv[:1] == ["--git"]:
        git_args = argv[1:]
        if git_args[:1] == ["--"]:
            git_args = git_args[1:]
        return check_commits(git_args)

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("message_file", help="Fichero con el mensaje de commit (hook commit-msg).")
    args = parser.parse_args(argv)

    try:
        message_file = message_file_inside_git_dir(args.message_file)
    except ValueError as exc:
        report_error(str(exc))
        return 2
    subject = subject_from_message(message_file.read_text(encoding="utf-8"))
    if is_valid_subject(subject):
        return 0
    report_error(f"«{subject}» no sigue el formato tipo(ámbito): descripción (#N)")
    print_help_footer()
    return 1


if __name__ == "__main__":
    sys.exit(main())
