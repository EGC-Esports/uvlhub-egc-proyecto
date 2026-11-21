"""Unit tests for the convention checks in scripts/ci.

The workflows (and the local git hooks) rely on these scripts to accept or reject
commits and branch names, so a wrong regex would let bad commits through or block
valid ones. scripts/ is not a package, so the modules are loaded from their path.
"""

import importlib.util
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts" / "ci"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


commit_msg = _load("check_commit_msg")
branch_name = _load("check_branch_name")
release_notes = _load("release_notes")


@pytest.mark.parametrize(
    "subject",
    [
        "feat(fakenodo): simular publicación de depósito (#12)",
        "fix(dataset): validar columnas obligatorias del CSV (#15)",
        "docs(diario): añadir acta de la reunión del 23 de noviembre (#30)",
        "ci: ejecutar los tests en todas las ramas (#7)",
        "refactor(auth)!: cambiar el modelo de sesión (#40)",
        "Merge branch 'feat/12-fakenodo' into trunk",
        'Revert "feat(fakenodo): simular publicación de depósito (#12)"',
    ],
)
def test_valid_commit_subjects_are_accepted(subject):
    assert commit_msg.is_valid_subject(subject)


@pytest.mark.parametrize(
    "subject",
    [
        "feat(fakenodo): simular publicación de depósito",  # no issue
        "feat(fakenodo): simular publicación de depósito #12",  # issue without brackets
        "feat(fakenodo): simular publicación (#12) de depósito",  # issue not at the end
        "feature(fakenodo): simular publicación de depósito (#12)",  # unknown type
        "Feat(fakenodo): simular publicación de depósito (#12)",  # uppercase type
        "feat(Fakenodo): simular publicación de depósito (#12)",  # uppercase scope
        "feat(fakenodo):simular publicación de depósito (#12)",  # no space after colon
        "feat(fakenodo): (#12)",  # no description
        "arreglos varios",
        "",
    ],
)
def test_invalid_commit_subjects_are_rejected(subject):
    assert not commit_msg.is_valid_subject(subject)


def test_subject_skips_git_comment_lines():
    message = "# Please enter the commit message\n\nfeat(dataset): subir CSV (#3)\n\ncuerpo\n# comentario\n"
    assert commit_msg.subject_from_message(message) == "feat(dataset): subir CSV (#3)"


def test_hook_mode_exit_code(tmp_path):
    good = tmp_path / "good"
    good.write_text("fix(auth): corregir login (#9)\n", encoding="utf-8")
    bad = tmp_path / "bad"
    bad.write_text("corregir login\n", encoding="utf-8")

    assert commit_msg.main([str(good)]) == 0
    assert commit_msg.main([str(bad)]) == 1


def _git(repo, *args):
    subprocess.run(
        ["git", "-c", "user.name=ci", "-c", "user.email=ci@example.com", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def test_git_mode_checks_only_the_given_range(tmp_path, monkeypatch):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "commit heredado sin formato")
    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "feat(dataset): subir CSV (#3)")
    monkeypatch.chdir(tmp_path)

    # The leading "--" used to swallow the range and check the whole history.
    assert commit_msg.main(["--git", "--", "HEAD~1..HEAD"]) == 0
    assert commit_msg.main(["--git", "HEAD~1..HEAD"]) == 0
    assert commit_msg.main(["--git", "HEAD"]) == 1
    assert commit_msg.main(["--git", "HEAD..HEAD"]) == 0  # nothing new
    assert commit_msg.main(["--git"]) == 2  # a range is mandatory


@pytest.mark.parametrize(
    "name",
    ["main", "trunk", "feat/12-fakenodo", "fix/15-validacion", "ci/3-workflows-en-todas-las-ramas", "docs/30-acta"],
)
def test_valid_branch_names_are_accepted(name):
    assert branch_name.is_valid_branch(name)


@pytest.mark.parametrize(
    "name",
    [
        "test-workflows",
        "feat/fakenodo",  # no issue number
        "feat/12_fakenodo",  # underscore
        "feat/12-Fakenodo",  # uppercase
        "feature/12-fakenodo",  # unknown type
        "build/12-docker",  # build is a commit type, not a branch type
        "develop",
    ],
)
def test_invalid_branch_names_are_rejected(name):
    assert not branch_name.is_valid_branch(name)


@pytest.mark.parametrize(
    "remote_branch",
    ["refs/heads/feat/12-fakenodo", "refs/heads/trunk", "refs/tags/v0.1.0", ""],
)
def test_pre_push_accepts_task_branches_trunk_and_tags(remote_branch):
    assert branch_name.check_pre_push({"PRE_COMMIT_REMOTE_BRANCH": remote_branch}) == 0


def test_pre_push_rejects_badly_named_branches():
    assert branch_name.check_pre_push({"PRE_COMMIT_REMOTE_BRANCH": "refs/heads/test-workflows"}) == 1


def test_pre_push_blocks_main_unless_explicitly_allowed():
    env = {"PRE_COMMIT_REMOTE_BRANCH": "refs/heads/main"}
    assert branch_name.check_pre_push(env) == 1
    assert branch_name.check_pre_push({**env, "ALLOW_PUSH_TO_MAIN": "1"}) == 0


def test_pre_commit_hooks_pin_the_same_lint_versions_as_the_ci():
    """The hook and lint.yml must agree, or code that passes locally fails in CI (and vice versa)."""
    import yaml

    root = SCRIPTS_DIR.parent.parent
    pinned = {}
    for line in (root / "requirements-lint.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            package, _, version = line.partition("==")
            pinned[package.lower()] = version

    config = yaml.safe_load((root / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    revs = {}
    plugins = {}
    for repo in config["repos"]:
        for hook in repo.get("hooks", []):
            if hook["id"] in ("flake8", "black", "isort"):
                revs[hook["id"]] = repo["rev"]
                for dependency in hook.get("additional_dependencies", []):
                    package, _, version = dependency.partition("==")
                    plugins[package.lower()] = version

    assert revs == {tool: pinned[tool] for tool in ("flake8", "black", "isort")}
    assert plugins == {"flake8-pyproject": pinned["flake8-pyproject"]}


def test_release_notes_group_commits_by_type():
    commits = [
        ("a1", "feat(fakenodo): simular depósito (#12)"),
        ("b2", "fix(dataset): validar CSV (#15)"),
        ("c3", "refactor(auth)!: nuevo modelo de sesión (#40)"),
        ("d4", "actualizar cosas"),
    ]
    notes = release_notes.render("v0.2.0", "v0.1.0", commits)

    assert "Cambios desde v0.1.0." in notes
    assert "### Nuevas funcionalidades\n\n- **fakenodo:** simular depósito (#12) (a1)" in notes
    assert "### Correcciones\n\n- **dataset:** validar CSV (#15) (b2)" in notes
    assert "### Cambios incompatibles\n\n- **auth:** nuevo modelo de sesión (#40) (c3)" in notes
    assert "### Otros cambios\n\n- actualizar cosas (d4)" in notes
    assert "### Documentación" not in notes


def test_release_notes_from_git_tags(tmp_path, monkeypatch, capsys):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "feat(auth): login (#1)")
    _git(tmp_path, "tag", "-a", "v0.1.0", "-m", "v0.1.0")
    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "fix(auth): logout (#2)")
    _git(tmp_path, "tag", "-a", "v0.2.0", "-m", "v0.2.0")
    monkeypatch.chdir(tmp_path)

    assert release_notes.main(["v0.2.0"]) == 0
    notes = capsys.readouterr().out
    assert "Cambios desde v0.1.0." in notes
    assert "**auth:** logout (#2)" in notes
    assert "login" not in notes

    # No earlier tag, and this repository does not contain the UVLHub fork point.
    assert release_notes.main(["v0.1.0"]) == 0
    notes = capsys.readouterr().out
    assert "Primera release del proyecto." in notes
    assert "**auth:** login (#1)" in notes


def test_release_notes_for_the_first_release():
    notes = release_notes.render("v0.1.0", release_notes.FORK_POINT, [])
    assert "Primera release del proyecto: cambios desde el fork de UVLHub." in notes
    assert release_notes.FORK_POINT not in notes
