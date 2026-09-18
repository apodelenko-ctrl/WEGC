#!/usr/bin/env python3
"""Prepare/start an isolated EspoCRM 10+ lab, never a production mail sender.

Python 3.10+, standard library only. Image digests are selected and verified by
LOCAL against official releases. Preparing files makes no network requests.
Keep the generated directory outside Git: it contains local installation secrets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import unittest


def checked_image(value: str, repository: str) -> str:
    pattern = re.escape(repository) + r"@sha256:[a-f0-9]{64}"
    if not re.fullmatch(pattern, value):
        raise ValueError(f"Require verified digest: {repository}@sha256:<64 hex>")
    return value


def compose_spec(espo: str, database: str, project: str) -> dict:
    checked_image(espo, "espocrm/espocrm")
    checked_image(database, "mariadb")
    mounts = ["app-data:/var/www/html/data", "app-custom:/var/www/html/custom",
              "app-client-custom:/var/www/html/client/custom"]
    return {
        "name": project,
        "services": {
            "db": {
                "image": database,
                "environment": {
                    "MARIADB_ROOT_PASSWORD_FILE": "/run/secrets/db_root",
                    "MARIADB_DATABASE": "espocrm", "MARIADB_USER": "espocrm",
                    "MARIADB_PASSWORD_FILE": "/run/secrets/db_user"},
                "secrets": ["db_root", "db_user"],
                "volumes": ["database:/var/lib/mysql"],
                "networks": ["lab"],
                "healthcheck": {
                    "test": ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"],
                    "interval": "20s", "timeout": "10s", "start_period": "20s", "retries": 5}},
            "crm": {
                "image": espo,
                "environment": {
                    "ESPOCRM_DATABASE_HOST": "db", "ESPOCRM_DATABASE_USER": "espocrm",
                    "ESPOCRM_DATABASE_NAME": "espocrm",
                    "ESPOCRM_DATABASE_PASSWORD_FILE": "/run/secrets/db_user",
                    "ESPOCRM_ADMIN_USERNAME": "mira_lab_admin",
                    "ESPOCRM_ADMIN_PASSWORD_FILE": "/run/secrets/crm_admin",
                    "ESPOCRM_SITE_URL": "http://127.0.0.1:18080"},
                "secrets": ["db_user", "crm_admin"],
                "volumes": mounts.copy(), "networks": ["lab"],
                "ports": ["127.0.0.1:18080:80"],
                "depends_on": {"db": {"condition": "service_healthy"}},
                "healthcheck": {
                    "test": ["CMD", "bin/command", "app-check"],
                    "interval": "30s", "timeout": "20s", "start_period": "60s", "retries": 8}},
            "daemon": {
                "image": espo, "entrypoint": "docker-daemon.sh",
                "volumes": mounts.copy(), "networks": ["lab"],
                "depends_on": {"crm": {"condition": "service_healthy"}}}
        },
        "volumes": {name: {} for name in ["database", "app-data", "app-custom", "app-client-custom"]},
        "networks": {"lab": {"internal": True}},
        "secrets": {name: {"file": f"./secrets/{name}.txt"}
                    for name in ["db_root", "db_user", "crm_admin"]}
    }


def private_write(path: Path, text: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write(text)


def prepare(target: Path, espo: str, database: str) -> dict:
    raw = target.expanduser().absolute()
    if raw.is_symlink() or raw.exists():
        raise ValueError("Target must be a NEW directory; nothing will be overwritten.")
    root = raw.resolve()
    for parent in root.parents:
        if (parent / ".git").exists():
            raise ValueError("Install secrets outside any Git worktree.")
    if not root.parent.is_dir():
        raise ValueError("Parent directory must already exist.")
    project = "mira-crm-lab-" + hashlib.sha256(str(root).encode()).hexdigest()[:10]
    spec = compose_spec(espo, database, project)  # validate BEFORE writing anything
    root.mkdir(mode=0o700)
    (root / "secrets").mkdir(mode=0o700)
    # _FILE credentials never appear in compose, output, Git, or the manifest.
    for name in spec["secrets"]:
        private_write(root / "secrets" / f"{name}.txt", secrets.token_urlsafe(36))
    text = json.dumps(spec, ensure_ascii=False, indent=2) + "\n"
    private_write(root / "compose.json", text)
    manifest = {
        "schemaVersion": 1, "scope": "local_isolated_lab_only",
        "project": project, "compose_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "images": {"espo": espo, "database": database},
        "smtp_configured": False, "production_deployed": False,
        "note": "File generation is not Docker, application, or mail acceptance."
    }
    private_write(root / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    private_write(root / ".gitignore", "*\n")
    return manifest


def runtime_report() -> dict:
    docker = shutil.which("docker")
    report = {"docker_cli_available": docker is not None,
              "compose_available": False, "engine_available": False,
              "status": "BLOCKED_RUNTIME", "application_started": False}
    if docker is None:
        return report
    for key, args in [("compose_available", [docker, "compose", "version"]),
                      ("engine_available", [docker, "info", "--format", "{{.ServerVersion}}"] )]:
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=15, check=False)
            report[key] = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            report[key] = False
    if report["compose_available"] and report["engine_available"]:
        report["status"] = "RUNTIME_AVAILABLE_NOT_APPLICATION_ACCEPTANCE"
    return report


def start(target: Path) -> int:
    root = target.expanduser().resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    raw = (root / "compose.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest["compose_sha256"]:
        raise ValueError("Compose changed since preparation; do not run an unreviewed config.")
    expected = compose_spec(manifest["images"]["espo"], manifest["images"]["database"],
                            manifest["project"])
    if json.loads(raw) != expected:
        raise ValueError("Not the isolated generated lab specification.")
    for name in expected["secrets"]:
        file = root / "secrets" / f"{name}.txt"
        if file.is_symlink() or file.resolve().parent != root / "secrets":
            raise ValueError("Secret must be a regular local lab file.")
        if os.name == "posix" and file.stat().st_mode & 0o077:
            raise ValueError("Secret file permissions are too broad.")
    status = runtime_report()
    if status["status"] == "BLOCKED_RUNTIME":
        print(json.dumps(status)); return 2
    docker = shutil.which("docker")
    assert docker is not None
    base = [docker, "compose", "--project-name", manifest["project"],
            "-f", str(root / "compose.json")]
    check = subprocess.run(base + ["config", "--quiet"], cwd=root, timeout=30, check=False)
    if check.returncode:
        return check.returncode
    # No shell, privilege escalation, host network, DNS changes, or production mounts.
    # --wait reports container health only; it does NOT prove UI or mail acceptance.
    result = subprocess.run(base + ["up", "-d", "--wait", "--wait-timeout", "300"],
                            cwd=root, timeout=420, check=False)
    print(json.dumps({"compose_exit_code": result.returncode,
                      "scope": "lab_container_health_only", "mail_acceptance": False}))
    return result.returncode


class Checks(unittest.TestCase):
    E = "espocrm/espocrm@sha256:" + "a" * 64  # synthetic, NOT a downloaded image
    D = "mariadb@sha256:" + "b" * 64

    def spec(self): return compose_spec(self.E, self.D, "mira-crm-lab-test")
    def test_01_requires_digest(self):
        with self.assertRaises(ValueError): checked_image("espocrm/espocrm:latest", "espocrm/espocrm")
    def test_02_rejects_other_repository(self):
        with self.assertRaises(ValueError): checked_image("other/espocrm@sha256:" + "a" * 64, "espocrm/espocrm")
    def test_03_internal_network(self): self.assertIs(self.spec()["networks"]["lab"]["internal"], True)
    def test_04_loopback_only(self):
        exposed = [p for s in self.spec()["services"].values() for p in s.get("ports", [])]
        self.assertEqual(exposed, ["127.0.0.1:18080:80"])
    def test_05_v10_volume_layout(self):
        targets = {x.split(":", 1)[1] for x in self.spec()["services"]["crm"]["volumes"]}
        self.assertEqual(targets, {"/var/www/html/data", "/var/www/html/custom", "/var/www/html/client/custom"})
    def test_06_daemon_shares_app_data(self):
        s = self.spec()["services"]; self.assertEqual(s["crm"]["volumes"], s["daemon"]["volumes"])
    def test_07_no_plaintext_credentials(self):
        for service in self.spec()["services"].values():
            for key in service.get("environment", {}):
                if "PASSWORD" in key: self.assertTrue(key.endswith("_FILE"))
    def test_08_no_host_network_privileged_or_restart(self):
        for service in self.spec()["services"].values():
            self.assertFalse(service.get("privileged", False)); self.assertNotIn("network_mode", service)
            self.assertNotIn("restart", service)
    def test_09_private_files_and_distinct_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "lab"; prepare(root, self.E, self.D)
            vals = [x.read_text() for x in (root / "secrets").iterdir()]
            self.assertEqual(len(set(vals)), 3)
            if os.name == "posix":
                self.assertEqual(root.stat().st_mode & 0o777, 0o700)
                for p in (root / "secrets").iterdir(): self.assertEqual(p.stat().st_mode & 0o777, 0o600)
    def test_10_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): prepare(Path(tmp), self.E, self.D)
    def test_11_git_worktree_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / ".git").write_text("gitdir: elsewhere")
            with self.assertRaises(ValueError): prepare(root / "lab", self.E, self.D)
    def test_12_manifest_hash_and_smtp_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "lab"; manifest = prepare(root, self.E, self.D)
            self.assertEqual(manifest["compose_sha256"], hashlib.sha256((root / "compose.json").read_bytes()).hexdigest())
            self.assertIs(manifest["smtp_configured"], False)
            self.assertNotIn("SMTP", (root / "compose.json").read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", type=Path, metavar="NEW_DIRECTORY")
    mode.add_argument("--start", type=Path, metavar="PREPARED_DIRECTORY")
    mode.add_argument("--check-runtime", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--espo-image")
    parser.add_argument("--db-image")
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
        return 0 if result.wasSuccessful() else 1
    if args.check_runtime:
        report = runtime_report(); print(json.dumps(report, indent=2))
        return 2 if report["status"] == "BLOCKED_RUNTIME" else 0
    if args.start:
        return start(args.start)
    if not args.espo_image or not args.db_image:
        parser.error("--prepare needs verified --espo-image and --db-image digests selected by LOCAL")
    report = prepare(args.prepare, args.espo_image, args.db_image)
    print(json.dumps(report, indent=2))
    print("Prepared only. Secrets remain inside the local directory; do NOT upload it.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f"Stopped safely: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
