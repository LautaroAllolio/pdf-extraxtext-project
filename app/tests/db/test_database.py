import pytest
from unittest.mock import MagicMock


class TestCloseDatabase:

    @pytest.mark.asyncio
    async def test_resets_client_and_database_references(self):
        import app.db.database as db_module

        db_module._client = MagicMock()
        db_module._database = MagicMock()

        await db_module.close_database()

        assert db_module._client is None
        assert db_module._database is None