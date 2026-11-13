"""
Pytest configuration for FINN backend tests.
Ensures complete isolation so test runs never pollute the production SQLite database (finn.db).
"""

import os
import tempfile
import shutil
import pytest
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def isolated_test_database():
    """
    Creates an isolated copy of the database or initializes a fresh temporary database
    specifically for test execution, ensuring zero pollution of backend/finn.db.
    """
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_finn.db")
    prod_db_path = str(Path(__file__).resolve().parent.parent / "finn.db")

    # Point FINN_DB_PATH to the isolated test database
    os.environ["FINN_DB_PATH"] = test_db_path

    # Initialize schema and seed data into test db
    from app.db.database import init_db
    from app.data.seed_data import seed_database

    init_db()
    seed_database()

    yield test_db_path

    # Teardown: remove env var and cleanup temp directory
    if "FINN_DB_PATH" in os.environ:
        del os.environ["FINN_DB_PATH"]
    shutil.rmtree(temp_dir, ignore_errors=True)
