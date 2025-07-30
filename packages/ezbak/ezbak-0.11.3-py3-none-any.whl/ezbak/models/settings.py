"""Settings model for EZBak backup configuration and management."""

import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from environs import Env, validate
from environs.exceptions import EnvValidationError
from nclutils import err_console, logger

from ezbak.constants import (
    DEFAULT_COMPRESSION_LEVEL,
    ENVAR_PREFIX,
    BackupType,
    LogLevel,
    RetentionPolicyType,
    StorageType,
)
from ezbak.controllers.retention_policy_manager import RetentionPolicyManager

env = Env(prefix=ENVAR_PREFIX)
env.read_env()


@dataclass
class Settings:
    """Configuration settings for EZBak backup operations.

    Stores all configuration parameters needed for backup operations including source/destination paths, retention policies, compression settings, and operational flags. Provides validation and property accessors for computed values like resolved paths and retention policy objects.
    """

    action: str | None = None
    name: str | None = None
    source_paths: list[Path] | None = None
    storage_paths: list[Path] | None = None
    storage_location: StorageType = StorageType.LOCAL

    strip_source_paths: bool = False
    delete_src_after_backup: bool = False
    exclude_regex: str | None = None
    include_regex: str | None = None
    compression_level: int = DEFAULT_COMPRESSION_LEVEL
    label_time_units: bool = True
    rename_files: bool = False

    max_backups: int | None = None
    retention_yearly: int | None = None
    retention_monthly: int | None = None
    retention_weekly: int | None = None
    retention_daily: int | None = None
    retention_hourly: int | None = None
    retention_minutely: int | None = None

    cron: str | None = None
    tz: str | None = None
    log_level: LogLevel = LogLevel.INFO
    log_file: str | Path | None = None
    log_prefix: str | None = None

    restore_path: str | Path | None = None
    clean_before_restore: bool = False
    chown_uid: int | None = None
    chown_gid: int | None = None

    aws_access_key: str | None = None
    aws_s3_bucket_name: str | None = None
    aws_s3_bucket_path: str | None = None
    aws_secret_key: str | None = None

    _retention_policy: RetentionPolicyManager | None = None
    _tmp_dir: TemporaryDirectory | None = None

    @property
    def retention_policy(self) -> RetentionPolicyManager:
        """Get the retention policy manager for this backup configuration.

        Creates and returns a RetentionPolicyManager based on the configured retention settings.
        Supports count-based, time-based, or keep-all policies depending on the settings provided.
        Caches the result for performance.

        Returns:
            RetentionPolicyManager: The retention policy manager for this backup configuration.
        """
        if self._retention_policy:
            return self._retention_policy

        if self.max_backups is not None:
            policy_type = RetentionPolicyType.COUNT_BASED
            self._retention_policy = RetentionPolicyManager(
                policy_type=policy_type, count_based_policy=self.max_backups
            )
        elif not self.max_backups and any(
            [
                self.retention_yearly,
                self.retention_monthly,
                self.retention_weekly,
                self.retention_daily,
                self.retention_hourly,
                self.retention_minutely,
            ]
        ):
            policy_type = RetentionPolicyType.TIME_BASED
            time_policy = {
                BackupType.MINUTELY: self.retention_minutely,
                BackupType.HOURLY: self.retention_hourly,
                BackupType.DAILY: self.retention_daily,
                BackupType.WEEKLY: self.retention_weekly,
                BackupType.MONTHLY: self.retention_monthly,
                BackupType.YEARLY: self.retention_yearly,
            }
            self._retention_policy = RetentionPolicyManager(
                policy_type=policy_type, time_based_policy=time_policy
            )
        else:
            self._retention_policy = RetentionPolicyManager(
                policy_type=RetentionPolicyType.KEEP_ALL
            )

        return self._retention_policy

    @property
    def tmp_dir(self) -> TemporaryDirectory:
        """Get the temporary directory.

        Returns:
            TemporaryDirectory: The temporary directory.
        """
        if self._tmp_dir is None:
            self._tmp_dir = TemporaryDirectory()
        return self._tmp_dir

    def model_dump(
        self,
    ) -> dict[str, int | str | bool | list[Path | str] | LogLevel | StorageType | None]:
        """Serialize settings to a dictionary representation.

        Converts all settings attributes to a dictionary format for serialization,
        logging, or configuration export purposes.

        Returns:
            dict[str, int | str | bool | list[Path | str] | None]: Dictionary representation of all settings.
        """
        return self.__dict__

    def update(
        self,
        updates: dict[str, str | int | Path | bool | list[Path | str] | LogLevel | StorageType],
    ) -> None:
        """Update settings with provided key-value pairs and reset cached properties.

        Validates that all keys exist as attributes on the settings object before updating. Resets cached properties when their underlying data changes to ensure consistency.

        Args:
            updates (dict[str, str | int | Path | bool | list[Path | str]]): Dictionary of setting keys and their new values.
        """
        for key, value in updates.items():
            try:
                getattr(self, key)
            except AttributeError:
                msg = f"ERROR    | '{key}' does not exist in settings"
                err_console.print(msg)
                sys.exit(1)

            if value is not None:
                if key == "log_level" and isinstance(value, str):
                    setattr(self, key, LogLevel[value.upper()])
                    continue

                if key == "storage_location" and isinstance(value, str):
                    setattr(self, key, StorageType[value.upper()])
                    continue

                setattr(self, key, value)

        # Reset cached properties
        update_keys = updates.keys()

        retention_keys = {
            "retention_yearly",
            "retention_monthly",
            "retention_weekly",
            "retention_daily",
            "retention_hourly",
            "retention_minutely",
        }
        if retention_keys & update_keys:
            self._retention_policy = None

    def validate(self) -> None:
        """Validate that required settings are provided for backup operations.

        Ensures that a backup name, source paths, and destination paths are specified before attempting any backup operations. Raises ValueError if any required settings are missing.

        Raises:
            ValueError: If settings are invalid.
            FileNotFoundError: If any of the paths do not exist.
        """
        if not self.name:
            msg = "No backup name provided"
            logger.error(msg)
            raise ValueError(msg)

        if self.source_paths:
            for source in self.source_paths:
                if not source.exists():
                    msg = f"Source does not exist: {source}"
                    logger.error(msg)
                    raise FileNotFoundError(msg) from None

        if not self.storage_paths and self.storage_location != StorageType.AWS:
            msg = "No storage paths provided"
            logger.error(msg)
            raise ValueError(msg)

        if self.storage_paths:
            for destination in self.storage_paths:
                if not destination.exists():
                    logger.info(f"Create destination: {destination}")
                    destination.mkdir(parents=True, exist_ok=True)


@env.parser_for("list_paths")
def list_paths_parser(value: str) -> list[Path]:
    """Parse a comma-separated list of paths into a list of Path objects.

    Args:
        value (str): A comma-separated list of paths.

    Returns:
        list[Path]: A list of Path objects.
    """
    if not value:
        return None

    return list({Path(path).expanduser().resolve() for path in value.split(",")})


@dataclass
class SettingsManager:
    """Singleton manager for EZBak settings initialization and CLI overrides.

    Provides centralized management of the Settings singleton, handling initialization from environment variables and applying CLI argument overrides while maintaining the singleton pattern for consistent settings access throughout the application.
    """

    _instance: Settings | None = None

    @classmethod
    def initialize(cls) -> Settings:
        """Initialize settings from environment variables using the singleton pattern.

        Creates a Settings instance from environment variables if not already initialized, ensuring consistent settings access throughout the application lifecycle.

        Returns:
            Settings: The initialized settings singleton instance.
        """
        if cls._instance is not None:
            return cls._instance

        try:
            settings = Settings(
                action=env.str(
                    "ACTION",
                    default=None,
                    validate=validate.OneOf(
                        ["backup", "restore", None], error="ACTION must be one of: {choices}"
                    ),
                ),
                name=env.str("NAME", None),
                source_paths=env.list_paths("SOURCE_PATHS", None),
                storage_paths=env.list_paths("STORAGE_PATHS", None),
                storage_location=StorageType(
                    env.str(
                        "STORAGE_LOCATION",
                        default=StorageType.LOCAL.value,
                        validate=validate.OneOf(
                            [x.value for x in StorageType],
                            error="STORAGE_LOCATION must be one of: {choices}",
                        ),
                    )
                ),
                # Backup settings
                strip_source_paths=env.bool("STRIP_SOURCE_PATHS", default=False),
                delete_src_after_backup=env.bool("DELETE_SRC_AFTER_BACKUP", default=False),
                exclude_regex=env.str("EXCLUDE_REGEX", None),
                include_regex=env.str("INCLUDE_REGEX", None),
                compression_level=env.int(
                    "COMPRESSION_LEVEL",
                    default=DEFAULT_COMPRESSION_LEVEL,
                    validate=validate.OneOf(
                        [1, 2, 3, 4, 5, 6, 7, 8, 9],
                        error="COMPRESSION_LEVEL must be one of: {choices}",
                    ),
                ),
                label_time_units=env.bool("LABEL_TIME_UNITS", default=True),
                rename_files=env.bool("RENAME_FILES", default=False),
                # Retention settings
                max_backups=env.int("MAX_BACKUPS", None),
                retention_yearly=env.int("RETENTION_YEARLY", None),
                retention_monthly=env.int("RETENTION_MONTHLY", None),
                retention_weekly=env.int("RETENTION_WEEKLY", None),
                retention_daily=env.int("RETENTION_DAILY", None),
                retention_hourly=env.int("RETENTION_HOURLY", None),
                retention_minutely=env.int("RETENTION_MINUTELY", None),
                # Cron settings
                cron=env.str("CRON", default=None),
                tz=env.str("TZ", None),
                # Logging settings
                log_level=LogLevel(
                    env.str(
                        "LOG_LEVEL",
                        default=LogLevel.INFO.name,
                        validate=validate.OneOf(
                            [x.name for x in LogLevel],
                            error="LOG_LEVEL must be one of: {choices}",
                        ),
                    )
                ),
                log_file=env.str("LOG_FILE", None),
                log_prefix=env.str("LOG_PREFIX", None),
                # Restore settings
                restore_path=env.str("RESTORE_PATH", None),
                clean_before_restore=env.bool("CLEAN_BEFORE_RESTORE", default=False),
                chown_uid=env.int("CHOWN_UID", None),
                chown_gid=env.int("CHOWN_GID", None),
                # AWS settings
                aws_access_key=env.str("AWS_ACCESS_KEY", None),
                aws_s3_bucket_name=env.str("AWS_S3_BUCKET_NAME", None),
                aws_s3_bucket_path=env.str("AWS_S3_BUCKET_PATH", None),
                aws_secret_key=env.str("AWS_SECRET_KEY", None),
            )
        except EnvValidationError as e:
            msg = f"ERROR    | {e}"
            err_console.print(msg)
            sys.exit(1)

        cls._instance = settings
        return settings

    @classmethod
    def apply_cli_settings(
        cls,
        cli_settings: dict[
            str, str | int | Path | bool | list[Path | str] | LogLevel | StorageType
        ],
    ) -> None:
        """Override existing settings with non-None values from CLI arguments.

        Updates the settings singleton with any non-None values provided via command line arguments, preserving existing values for unspecified settings. Filters out None values to avoid overriding existing settings with None.

        Args:
            cli_settings (dict[str, str | int | Path | bool | list[Path | str]]): Dictionary of settings from CLI arguments to apply as overrides.
        """
        settings = cls._instance
        if settings is None:  # pragma: no cover
            msg = "ERROR    | Settings not initialized"
            err_console.print(msg)
            sys.exit(1)

        # Filter out None values to avoid overriding with None
        cli_overrides = {k: v for k, v in cli_settings.items() if v is not None}
        settings.update(cli_overrides)


# Initialize settings singleton
settings = SettingsManager.initialize()
