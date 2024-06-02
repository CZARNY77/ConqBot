import unittest
from unittest.mock import AsyncMock, Mock

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Discord.programming_patterns.Bridge import ActionAddRole, ActionRemoveRole, ButtonTypeAdd, ButtonTypeRemove

class TestBridgePattern(unittest.IsolatedAsyncioTestCase):
    # Testowanie wykonania akcji 1
    async def test_action_add_role_execution(self):
        interaction = Mock()  # Mockowanie interakcji
        interaction.user = Mock()  # Mockowanie użytkownika
        interaction.user.add_roles = AsyncMock()  # Mockowanie metody add_roles
        interaction.response.send_message = AsyncMock()  # Mockowanie metody send_message
        
        action = ActionAddRole()  # Tworzenie instancji Action1
        await action.execute(interaction, role="TestRole")  # Wykonanie akcji
        
        # Sprawdzenie, czy wiadomość została wysłana z oczekiwanym tekstem
        interaction.response.send_message.assert_awaited_with("Dodano role.", ephemeral=True)

    # Testowanie wykonania akcji 2
    async def test_action_remove_role_execution(self):
        interaction = Mock()  # Mockowanie interakcji
        interaction.user = Mock()  # Mockowanie użytkownika
        interaction.user.remove_roles = AsyncMock()  # Mockowanie metody remove_roles
        interaction.response.send_message = AsyncMock()  # Mockowanie metody send_message
        
        action = ActionRemoveRole()  # Tworzenie instancji Action2
        await action.execute(interaction, role="TestRole")  # Wykonanie akcji
        
        # Sprawdzenie, czy wiadomość została wysłana z oczekiwanym tekstem
        interaction.response.send_message.assert_awaited_with("Usunięto role.", ephemeral=True)

    # Testowanie kliknięcia przycisku typu 1
    async def test_button_type1_click(self):
        interaction = Mock()  # Mockowanie interakcji
        interaction.user = Mock()  # Mockowanie użytkownika
        interaction.user.add_roles = AsyncMock()  # Mockowanie metody add_roles
        interaction.response.send_message = AsyncMock()  # Mockowanie metody send_message
        
        action = ActionAddRole()  # Tworzenie instancji Action1
        view = ButtonTypeAdd(action)  # Tworzenie instancji widoku z przyciskiem typu 1
        button = view.children[0]  # Pobranie przycisku z widoku
        
        await button.callback(interaction)  # Kliknięcie przycisku
        
        # Sprawdzenie, czy wiadomość została wysłana z oczekiwanym tekstem
        interaction.response.send_message.assert_awaited_with("Dodano role.", ephemeral=True)

    # Testowanie kliknięcia przycisku typu 2
    async def test_button_type2_click(self):
        interaction = Mock()  # Mockowanie interakcji
        interaction.user = Mock()  # Mockowanie użytkownika
        interaction.user.remove_roles = AsyncMock()  # Mockowanie metody remove_roles
        interaction.response.send_message = AsyncMock()  # Mockowanie metody send_message
        
        action = ActionRemoveRole()  # Tworzenie instancji Action2
        view = ButtonTypeRemove(action)  # Tworzenie instancji widoku z przyciskiem typu 2
        button = view.children[0]  # Pobranie przycisku z widoku
        
        await button.callback(interaction)  # Kliknięcie przycisku
        
        # Sprawdzenie, czy wiadomość została wysłana z oczekiwanym tekstem
        interaction.response.send_message.assert_awaited_with("Usunięto role.", ephemeral=True)

if __name__ == "__main__":
    unittest.main()
