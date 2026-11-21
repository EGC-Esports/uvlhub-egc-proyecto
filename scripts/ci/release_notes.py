"""Genera las notas de una release a partir de los commits desde el tag anterior.

Agrupa los commits por su tipo de Conventional Commits y deja la referencia ``(#N)``
tal cual, para que GitHub la enlace con la issue. Los merges no se listan: con
EGCFlow cada tarea entra en ``trunk`` con un merge ``--no-ff``, y sus commits ya
aparecen uno a uno.

Uso::

    python scripts/ci/release_notes.py v0.2.0               # desde el tag anterior
    python scripts/ci/release_notes.py v0.2.0 --since v0.1.0

Escribe el Markdown por la salida estándar.

Seguridad: el tag y --since solo pueden tener los caracteres de una revisión de git
y nunca empezar por ``-``, y van detrás de ``--end-of-options``, así que git nunca
los toma por opciones.
"""

import argparse
import re
import subprocess
import sys

SECTIONS = (
    ("feat", "Nuevas funcionalidades"),
    ("fix", "Correcciones"),
    ("perf", "Rendimiento"),
    ("refactor", "Refactorizaciones"),
    ("test", "Pruebas"),
    ("ci", "Integración y despliegue continuos"),
    ("build", "Construcción y dependencias"),
    ("docs", "Documentación"),
    ("style", "Estilo"),
    ("chore", "Mantenimiento"),
    ("revert", "Reversiones"),
)

# Último commit del fork de UVLHub, anterior al trabajo del equipo. La primera release
# no tiene tag anterior, y sin esto sus notas listarían toda la historia del upstream.
FORK_POINT = "cb8bec81b1b79db8f361bc2f210e4dd31df219d7"

TYPE_PATTERN = re.compile(r"^(?P<type>[a-z]+)(\((?P<scope>[a-z0-9-]+)\))?(?P<breaking>!)?: (?P<description>.+)$")

# Una revisión de git: tag, sha, v0.2.0^, A..B. Empieza siempre por letra o número.
_REF = r"[A-Za-z0-9][A-Za-z0-9._/@{}~^-]*"
REVISION_PATTERN = re.compile(rf"{_REF}(\.\.\.?{_REF})?")


def safe_revisions(revisions: list[str]) -> list[str]:
    """Las revisiones si todas tienen forma de revisión de git; si no, ValueError."""
    for revision in revisions:
        if not REVISION_PATTERN.fullmatch(revision):
            raise ValueError(f"«{revision}» no es una revisión de git válida")
    return list(revisions)


def git(options: list[str], revisions: list[str]) -> subprocess.CompletedProcess:
    """Ejecuta git con opciones fijas del código y revisiones validadas tras --end-of-options."""
    return subprocess.run(
        ["git", *options, "--end-of-options", *safe_revisions(revisions)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def previous_tag(tag: str) -> str | None:
    """Último tag ``v*`` alcanzable desde el commit anterior a ``tag``, o None si es la primera release."""
    result = git(["describe", "--tags", "--abbrev=0", "--match", "v*"], [f"{tag}^"])
    return (result.stdout.strip() or None) if result.returncode == 0 else None


def fork_point_for(tag: str) -> str | None:
    """FORK_POINT si es antecesor de ``tag`` (siempre lo es en este repositorio), si no None."""
    result = git(["merge-base", "--is-ancestor"], [FORK_POINT, tag])
    return FORK_POINT if result.returncode == 0 else None


def commits_between(since: str | None, tag: str) -> list[tuple[str, str]]:
    revision = f"{since}..{tag}" if since else tag
    result = git(["log", "--no-merges", "--format=%h%x1f%s"], [revision])
    if result.returncode != 0:
        raise RuntimeError(f"git log falló: {result.stderr.strip()}")
    return [tuple(line.split("\x1f", 1)) for line in result.stdout.splitlines() if line]


def render(tag: str, since: str | None, commits: list[tuple[str, str]]) -> str:
    grouped: dict[str, list[str]] = {key: [] for key, _ in SECTIONS}
    breaking: list[str] = []
    others: list[str] = []

    for sha, subject in commits:
        match = TYPE_PATTERN.match(subject)
        if not match or match["type"] not in grouped:
            others.append(f"- {subject} ({sha})")
            continue
        scope = f"**{match['scope']}:** " if match["scope"] else ""
        entry = f"- {scope}{match['description']} ({sha})"
        grouped[match["type"]].append(entry)
        if match["breaking"]:
            breaking.append(entry)

    lines = [f"## {tag}", ""]
    if since == FORK_POINT:
        lines.append("Primera release del proyecto: cambios desde el fork de UVLHub.")
    elif since:
        lines.append(f"Cambios desde {since}.")
    else:
        lines.append("Primera release del proyecto.")
    lines.append("")

    if breaking:
        lines += ["### Cambios incompatibles", "", *breaking, ""]
    for key, title in SECTIONS:
        if grouped[key]:
            lines += [f"### {title}", "", *grouped[key], ""]
    if others:
        lines += ["### Otros cambios", "", *others, ""]
    if not commits:
        lines += ["No hay commits nuevos desde la release anterior.", ""]

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tag", help="Tag de la release, p. ej. v0.2.0")
    parser.add_argument("--since", help="Tag desde el que contar. Por defecto, el tag v* anterior.")
    args = parser.parse_args(argv)

    try:
        since = args.since or previous_tag(args.tag) or fork_point_for(args.tag)
        notes = render(args.tag, since, commits_between(since, args.tag))
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
