import unittest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Discord.recruitment import Recruitment

class TestRecruitment(unittest.TestCase):
    def setUp(self):
        self.mock_interaction = MagicMock()
        self.mock_interaction.client = MagicMock()
        self.mock_interaction.guild_id = 123456
        self.mock_interaction.user = MagicMock(color=0xFFFFFF, mention="mock_mention")
        self.mock_log_channel = MagicMock()

        self.recruitment = Recruitment(interaction=self.mock_interaction, log_channel=self.mock_log_channel)

    @patch('Discord.recruitment.requests.post')
    @patch('Discord.recruitment.requests.get')
    async def test_add_player_to_whitelist(self, mock_post, mock_get):
        mock_user = MagicMock(id=123)
        self.recruitment.get_user = MagicMock(return_value=mock_user)

        await self.recruitment.add_player_to_whitelist("player_name", 1, in_house="in_house", recru_process="recru_process", comment="comment", request="request")
        
        mock_user.send.assert_called_once_with('''Witamy w rodzie, teraz kilka linków pomocniczych dla ciebie :saluting_face:
              Ankieta jednostek, pamiętaj zrobić jak tylko będziesz miał chwilkę czasu, to maks 2-3min:
              https://cb-social.vercel.app/

              Rozpiska jednostek na TW (można sobie dodać do zakładki):
              https://

              Oraz poradniki:
              https://discord.com/channels/1232957904597024882/1235004633974313123
              ''')
        self.mock_interaction.send.assert_called_once_with(content="Rekrutacja!!", view=self.recruitment)

    @patch('Discord.recruitment.requests.post')
    @patch('Discord.recruitment.requests.get')
    async def test_add_player_to_whitelist_existing_player(self, mock_post, mock_get):
        mock_get.return_value.json.return_value = {"whitelist": [{"usernameDiscord": "player_name"}]}
        mock_user = MagicMock(id=123)
        self.recruitment.get_user = MagicMock(return_value=mock_user)

        await self.recruitment.add_player_to_whitelist("player_name", 1, in_house="in_house", recru_process="recru_process", comment="comment", request="request")
        
        self.mock_interaction.send.assert_called_once_with(content="Gracz o takim samym nicku już istnieje!!", embed=MagicMock(title='Gracz: player_name, DC: mock_mention', color=0xFFFFFF, description="Nie został znaleziony!!"))
        self.mock_log_channel.send.assert_not_called()

    @patch('Discord.recruitment.requests.post')
    @patch('Discord.recruitment.requests.get')
    async def test_add_player_to_whitelist_request_exception(self, mock_post, mock_get):
        mock_get.side_effect = Exception("Error message")

        await self.recruitment.add_player_to_whitelist("player_name", 1, in_house="in_house", recru_process="recru_process", comment="comment", request="request")

        self.mock_log_channel.send.assert_called_once_with(content="Wystąpił błąd żądania: Error message")

if __name__ == '__main__':
    unittest.main()
