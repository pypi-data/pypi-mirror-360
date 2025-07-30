"""Test the ezbak CLI."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
import time_machine

from ezbak.constants import DEFAULT_DATE_FORMAT
from ezbak.entrypoint import main as entrypoint
from ezbak.models.settings import settings

UTC = ZoneInfo("UTC")
frozen_time = datetime(2025, 6, 9, 0, 0, tzinfo=UTC)
frozen_time_str = frozen_time.strftime(DEFAULT_DATE_FORMAT)
fixture_archive_path = Path(__file__).parent / "fixtures" / "archive.tgz"


@pytest.fixture(autouse=True)
def mock_run(mocker):
    """Mock the Run class to prevent infinite loop in scheduler."""
    # Mock the Run class to prevent infinite loop in scheduler
    mock_scheduler = mocker.patch("ezbak.entrypoint.BackgroundScheduler")
    mock_scheduler_instance = mock_scheduler.return_value
    mock_scheduler_instance.running = False
    mocker.patch("time.sleep", return_value=None)


@time_machine.travel(frozen_time, tick=False)
def test_entrypoint_create_backup(filesystem, debug, clean_stderr):
    """Verify that a backup is created correctly."""
    # Given: Source and destination directories from fixture
    src_dir, dest1, dest2 = filesystem

    settings.update(
        {
            "name": "test",
            "action": "backup",
            "source_paths": [src_dir],
            "storage_paths": [dest1, dest2],
            # "log_level": "TRACE",
        }
    )

    entrypoint()

    output = clean_stderr()
    # debug(output)

    filename = f"test-{frozen_time_str}-yearly.tgz"
    assert Path(dest1 / filename).exists()
    assert Path(dest2 / filename).exists()
    assert f"INFO     | Created: …/dest1/{filename}" in output
    assert f"INFO     | Created: …/dest2/{filename}" in output


@time_machine.travel(frozen_time, tick=True)
def test_entrypoint_create_backup_with_cron(mocker, monkeypatch, filesystem, debug, clean_stderr):
    """Verify that a backup is created correctly."""
    # Given: Source and destination directories from fixture
    src_dir, dest1, dest2 = filesystem

    settings.update(
        {
            "name": "test",
            "action": "backup",
            "source_paths": [src_dir],
            "storage_paths": [dest1, dest2],
            "cron": "*/1 * * * *",
        }
    )

    entrypoint()

    output = clean_stderr()
    # debug(output)
    assert "Scheduler started" in output
    assert "Next scheduled run" in output


def test_entrypoint_restore_backup(filesystem, debug, clean_stderr, tmp_path):
    """Verify that a backup is restored correctly."""
    # Given: Source and destination directories from fixture
    src_dir, dest1, _ = filesystem
    backup_name = f"test-{frozen_time_str}-yearly.tgz"
    backup_path = Path(dest1 / backup_name)
    shutil.copy2(fixture_archive_path, backup_path)

    restore_path = Path(tmp_path / "restore")
    restore_path.mkdir(exist_ok=True)

    settings.update(
        {
            "name": "test",
            "action": "restore",
            "source_paths": [src_dir],
            "storage_paths": [dest1],
            "restore_path": restore_path,
        }
    )

    entrypoint()

    output = clean_stderr()
    # debug(output)
    debug(restore_path)

    assert "INFO     | Backup restored to '…/restore'" in output
    assert Path(restore_path / "src" / "baz.txt").exists()
