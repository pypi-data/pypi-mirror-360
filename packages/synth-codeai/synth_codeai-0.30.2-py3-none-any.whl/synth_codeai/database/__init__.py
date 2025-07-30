"""
Database package for synth_codeai.

This package provides database functionality for the synth_codeai application,
including connection management, models, utility functions, and migrations.
"""

from synth_codeai.database.connection import DatabaseManager, close_db, get_db, init_db
from synth_codeai.database.migrations import (
    MigrationManager,
    create_new_migration,
    ensure_migrations_applied,
    get_migration_status,
    init_migrations,
)
from synth_codeai.database.models import BaseModel, initialize_database
from synth_codeai.database.utils import ensure_tables_created, get_model_count, truncate_table

__all__ = [
    "init_db",
    "get_db",
    "close_db",
    "DatabaseManager",
    "BaseModel",
    "initialize_database",
    "get_model_count",
    "truncate_table",
    "ensure_tables_created",
    "init_migrations",
    "ensure_migrations_applied",
    "create_new_migration",
    "get_migration_status",
    "MigrationManager",
]
