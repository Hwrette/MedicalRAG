import flet as ft

from models import ChatEntry, load_history, save_history
from views.chat import build_chat
from views.history import build_history
from views.menu import build_menu
from views.start import build_start


class ExpertChatApp:
    _history_key = "expert_chat_history"

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._history: list[ChatEntry] = []

    async def load_history(self) -> None:
        saved_history = await self._page.shared_preferences.get(self._history_key)
        self._history = load_history(saved_history if isinstance(saved_history, str) else None)

    async def record_message(self, speaker: str, message: str) -> None:
        self._history.append(ChatEntry(speaker=speaker, message=message))
        await self._page.shared_preferences.set(self._history_key, save_history(self._history))

    def show_start(self) -> None:
        self._page.clean()
        self._page.add(build_start(self.show_menu))

    def show_menu(self) -> None:
        self._page.clean()
        self._page.add(build_menu(self.show_chat, self.show_history))

    def show_chat(self) -> None:
        self._page.clean()
        self._page.add(build_chat(self._page, self.record_message, self.show_menu))

    def show_history(self) -> None:
        self._page.clean()
        self._page.add(build_history(self._history, self.show_menu))


async def main(page: ft.Page) -> None:
    page.title = "전문가 시스템 채팅"
    page.theme_mode = ft.ThemeMode.LIGHT
    app = ExpertChatApp(page)
    await app.load_history()
    app.show_start()


ft.run(main)
