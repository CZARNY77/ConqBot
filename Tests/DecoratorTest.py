import unittest
import asyncio # Importujemy moduł asyncio do obsługi pętli zdarzeń asynchronicznych
from unittest.mock import MagicMock, AsyncMock

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Discord.programming_patterns.Decorator import BasicButtonView, ClickCounterDecorator, StyleChangerDecorator, DecoratedView


class TestButtonView(unittest.TestCase):
    # Test dla widoku podstawowego przycisku
    def test_basic_button_view(self):
        asyncio.run(self._test_basic_button_view())  # Uruchamiamy test w kontekście pętli asyncio

    # Metoda asynchroniczna pomocnicza do testowania widoku podstawowego przycisku
    async def _test_basic_button_view(self):
        view = BasicButtonView()  # Tworzymy instancję widoku podstawowego przycisku
        self.assertIsInstance(view, BasicButtonView)  # Sprawdzamy, czy widok jest instancją klasy BasicButtonView

    # Test dla dekoratora zliczającego kliknięcia
    def test_click_counter_decorator(self):
        asyncio.run(self._test_click_counter_decorator())  # Uruchamiamy test w kontekście pętli asyncio

    # Metoda asynchroniczna pomocnicza do testowania dekoratora zliczającego kliknięcia
    async def _test_click_counter_decorator(self):
        mock_view = MagicMock()  # Tworzymy atrapę obiektu widoku
        mock_view.interaction_check = AsyncMock(return_value=True)  # Definiujemy metodę asynchroniczną w atrapie
        decorator = ClickCounterDecorator(mock_view)  # Tworzymy instancję dekoratora zliczającego kliknięcia
        self.assertIsInstance(decorator, ClickCounterDecorator)  # Sprawdzamy, czy dekorator jest instancją klasy ClickCounterDecorator

    # Test dla dekoratora zmieniającego styl
    def test_style_changer_decorator(self):
        asyncio.run(self._test_style_changer_decorator())  # Uruchamiamy test w kontekście pętli asyncio

    # Metoda asynchroniczna pomocnicza do testowania dekoratora zmieniającego styl
    async def _test_style_changer_decorator(self):
        mock_view = MagicMock()  # Tworzymy atrapę obiektu widoku
        mock_view.interaction_check = AsyncMock(return_value=True)  # Definiujemy metodę asynchroniczną w atrapie
        decorator = StyleChangerDecorator(mock_view)  # Tworzymy instancję dekoratora zmieniającego styl
        self.assertIsInstance(decorator, StyleChangerDecorator)  # Sprawdzamy, czy dekorator jest instancją klasy StyleChangerDecorator

    # Test dla widoku zdekorowanego
    def test_decorated_view(self):
        asyncio.run(self._test_decorated_view())  # Uruchamiamy test w kontekście pętli asyncio

    # Metoda asynchroniczna pomocnicza do testowania widoku zdekorowanego
    async def _test_decorated_view(self):
        mock_bot = MagicMock()  # Tworzymy atrapę obiektu bota Discord
        mock_view = MagicMock()  # Tworzymy atrapę obiektu widoku
        mock_view.interaction_check = AsyncMock(return_value=True)  # Definiujemy metodę asynchroniczną w atrapie
        view = DecoratedView(mock_bot)  # Tworzymy instancję widoku zdekorowanego
        self.assertIsInstance(view, DecoratedView)  # Sprawdzamy, czy widok jest instancją klasy DecoratedView

if __name__ == '__main__':
    unittest.main()  # Uruchamiamy testy jednostkowe