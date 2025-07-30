"""
Database utility functions for synth_codeai.

This module provides utility functions for common database operations.
"""

import inspect
from typing import List, Type

import peewee

from synth_codeai.database.connection import get_db
from synth_codeai.database.models import BaseModel, initialize_database
from synth_codeai.logging_config import get_logger

logger = get_logger(__name__)


def ensure_tables_created(models: List[Type[BaseModel]] = None) -> None:
    """
    Ensure that database tables for the specified models exist.

    If no models are specified, this function will attempt to discover
    all models that inherit from BaseModel.

    Args:
        models: Optional list of model classes to create tables for
    """
    db = initialize_database()

    if models is None:
        # If no models are specified, try to discover them
        models = []
        try:
            # Import all modules that might contain models
            # This is a placeholder - in a real implementation, you would
            # dynamically discover and import all modules that might contain models
            from synth_codeai.database import models as models_module

            # Find all classes in the module that inherit from BaseModel
            for name, obj in inspect.getmembers(models_module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BaseModel)
                    and obj != BaseModel
                ):
                    models.append(obj)
        except ImportError as e:
            logger.warning(f"Error importing model modules: {e}")

    if not models:
        logger.warning("No models found to create tables for")
        return

    try:
        with db.atomic():
            db.create_tables(models, safe=True)
        logger.info(f"Successfully created tables for {len(models)} models")
    except peewee.DatabaseError as e:
        logger.error(f"Database Error: Failed to create tables: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error: Failed to create tables: {str(e)}")
        raise


def get_model_count(model_class: Type[BaseModel]) -> int:
    """
    Get the count of records for a specific model.

    Args:
        model_class: The model class to count records for

    Returns:
        int: The number of records for the model
    """
    try:
        return model_class.select().count()
    except peewee.DatabaseError as e:
        logger.error(f"Database Error: Failed to count records: {str(e)}")
        return 0


def truncate_table(model_class: Type[BaseModel]) -> None:
    """
    Delete all records from a model's table.

    Args:
        model_class: The model class to truncate
    """
    db = initialize_database()
    try:
        with db.atomic():
            model_class.delete().execute()
        logger.info(f"Successfully truncated table for {model_class.__name__}")
    except peewee.DatabaseError as e:
        logger.error(f"Database Error: Failed to truncate table: {str(e)}")
        raise
