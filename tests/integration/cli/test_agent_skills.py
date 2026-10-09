"""Exercise the packaged skill's consumer lifecycle with real file I/O."""

import json
from pathlib import Path

import pytest

from codex_django_cli.agent_skills import orchestrator
from codex_django_cli.agent_skills.fs_transaction import FSError
from codex_django_cli.agent_skills.manifest_rules import ManifestError, build_manifest, parse_manifest
from codex_django_cli.main import main

pytestmark = pytest.mark.integration


def test_install_status_update_delete_preserve_user_content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "consumer"
    project.mkdir()
    agents = project / "AGENTS.md"
    agents.write_bytes(b"# Local rules\r\nKeep this line.\r\n")
    monkeypatch.setattr(orchestrator, "get_package_version", lambda: "test-version")
    orchestrator.perform_install(project)
    skill = project / ".agents" / "skills" / "codex-django-cli"
    manifest = json.loads((skill / ".manifest.json").read_text(encoding="utf-8"))
    assert manifest["package_version"] == "test-version"
    assert "SKILL.md" in manifest["files"]
    assert orchestrator.check_status(project)[0]
    assert agents.read_bytes().startswith(b"# Local rules\r\nKeep this line.\r\n")

    # A newer package drops a managed reference and adds another. Local additions remain.
    original_payload = orchestrator.get_payload_files
    payload = original_payload()
    removed = "references/delivery.md"
    replacement = "references/new.md"
    payload.pop(removed)
    payload[replacement] = b"New packaged reference.\n"
    (skill / "local-notes.md").write_text("Keep me", encoding="utf-8")
    monkeypatch.setattr(orchestrator, "get_payload_files", lambda: payload)
    assert not orchestrator.check_status(project)[0]
    orchestrator.perform_install(project, update=True)
    assert not (skill / removed).exists()
    assert (skill / replacement).read_bytes() == payload[replacement]
    assert (skill / "local-notes.md").read_text(encoding="utf-8") == "Keep me"
    assert orchestrator.check_status(project)[0]

    orchestrator.perform_delete(project)
    assert not (skill / "SKILL.md").exists()
    assert not (skill / ".manifest.json").exists()
    assert (skill / "local-notes.md").exists()
    assert agents.read_bytes() == b"# Local rules\r\nKeep this line.\r\n"


@pytest.mark.parametrize("action", ["update", "delete"])
def test_local_managed_edit_blocks_mutation(tmp_path: Path, action: str) -> None:
    project = tmp_path / "consumer"
    project.mkdir()
    orchestrator.perform_install(project)
    skill = project / ".agents" / "skills" / "codex-django-cli"
    readme = skill / "SKILL.md"
    readme.write_text("Local edit", encoding="utf-8")
    before_agents = (project / "AGENTS.md").read_bytes()
    before_manifest = (skill / ".manifest.json").read_bytes()

    with pytest.raises(orchestrator.OrchestratorError, match="Local managed content changed"):
        if action == "update":
            orchestrator.perform_install(project, update=True)
        else:
            orchestrator.perform_delete(project)

    assert readme.read_text(encoding="utf-8") == "Local edit"
    assert (skill / ".manifest.json").read_bytes() == before_manifest
    assert (project / "AGENTS.md").read_bytes() == before_agents


def test_unowned_directory_and_invalid_manifest_are_rejected(tmp_path: Path) -> None:
    project = tmp_path / "consumer"
    skill = project / ".agents" / "skills" / "codex-django-cli"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("User owned", encoding="utf-8")
    with pytest.raises(orchestrator.OrchestratorError, match="without ownership manifest"):
        orchestrator.perform_install(project)
    assert (skill / "SKILL.md").read_text(encoding="utf-8") == "User owned"


@pytest.mark.parametrize("bad_name", ["../outside.md", "references/../outside.md", "skill.md"])
def test_manifest_rejects_unsafe_or_aliased_payload_paths(bad_name: str) -> None:
    with pytest.raises(ManifestError):
        build_manifest("test-version", {"SKILL.md": b"skill", bad_name: b"bad"})


def test_corrupt_manifest_does_not_change_consumer(tmp_path: Path) -> None:
    project = tmp_path / "consumer"
    project.mkdir()
    orchestrator.perform_install(project)
    skill = project / ".agents" / "skills" / "codex-django-cli"
    manifest_path = skill / ".manifest.json"
    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    original["files"]["../outside.md"] = "0" * 64
    corrupt = json.dumps(original).encode("utf-8")
    manifest_path.write_bytes(corrupt)
    with pytest.raises(orchestrator.OrchestratorError, match="Corrupt ownership manifest"):
        orchestrator.perform_delete(project)
    assert manifest_path.read_bytes() == corrupt
    assert (skill / "SKILL.md").exists()
    with pytest.raises(ManifestError):
        parse_manifest(corrupt)


def test_failed_write_rolls_back_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "consumer"
    project.mkdir()
    agents = project / "AGENTS.md"
    agents.write_bytes(b"User instructions\n")
    original_replace = orchestrator.FSTransaction.apply.__globals__["os"].replace
    calls = 0

    def fail_second_replace(source: Path, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated write failure")
        original_replace(source, target)

    monkeypatch.setattr("codex_django_cli.agent_skills.fs_transaction.os.replace", fail_second_replace)
    with pytest.raises(FSError, match="rolled back"):
        orchestrator.perform_install(project)
    assert agents.read_bytes() == b"User instructions\n"
    assert not (project / ".agents" / "skills" / "codex-django-cli" / "SKILL.md").exists()


def test_public_cli_dispatches_skill_lifecycle(tmp_path: Path) -> None:
    project = tmp_path / "consumer"
    project.mkdir()
    target = str(project)
    assert main(["skills", "status", "--project", target]) == 1
    assert main(["skills", "install", "--project", target]) == 0
    assert main(["skills", "status", "--project", target]) == 0
    assert main(["skills", "update", "--project", target]) == 0
    assert main(["skills", "delete", "--project", target]) == 0
