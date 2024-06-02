import unittest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Discord.database_connect import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.mock_bot = MagicMock()
        self.database = Database(self.mock_bot)

    def test_connect_with_db(self):
        with patch('mysql.connector.connect') as mock_connect:
            self.database.connect_with_db()
            mock_connect.assert_called_once()

    def test_add_new_guild(self):
        mock_cursor = MagicMock()
        self.database.cursor = mock_cursor
        self.database.add_new_guild(123456, "TestGuild")
        mock_cursor.execute.assert_called_once()

    def test_servers_verification(self):
        mock_cursor = MagicMock()
        mock_servers = [MagicMock(id=123), MagicMock(id=456)]
        self.database.cursor = mock_cursor
        self.database.servers_verification(mock_servers)
        mock_cursor.execute.assert_called()

    def test_one_server_verification(self):
        mock_cursor = MagicMock()
        mock_server = MagicMock(id=123)
        self.database.cursor = mock_cursor
        self.database.one_server_verification(mock_server)
        mock_cursor.execute.assert_called()

    def test_get_results(self):
        mock_cursor = MagicMock()
        self.database.cursor = mock_cursor
        self.database.get_results("SELECT * FROM table", ())
        mock_cursor.execute.assert_called_once_with("SELECT * FROM table", ())

    def test_send_data(self):
        mock_cursor = MagicMock()
        self.database.cursor = mock_cursor
        self.database.send_data("INSERT INTO table VALUES (%s)", (123,))
        mock_cursor.execute.assert_called_once_with("INSERT INTO table VALUES (%s)", (123,))

    def test_get_specific_value(self):
        mock_cursor = MagicMock()
        self.database.cursor = mock_cursor
        self.database.get_specific_value(123, "basic_roles")
        mock_cursor.execute.assert_called_once()

    def test_check_role_permissions(self):
        mock_member = MagicMock()
        mock_member.guild_permissions.administrator = True
        self.assertTrue(self.database.check_role_permissions(mock_member, 123))

    def test_check_type(self):
        mock_guild = MagicMock()
        self.database.bot.get_guild.return_value = mock_guild
        results = self.database.check_type(123, 456, "roles")
        self.assertEqual(results, 123)

if __name__ == '__main__':
    unittest.main()
