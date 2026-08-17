import flet as ft

from views.chat import build_chat
from views.start import build_start


class ExpertChatApp:
    def __init__(self, page: ft.Page) -> None:
        self._page = page

    def show_start(self) -> None:
        self._page.clean()
        self._page.add(build_start(self.show_chat))

    def show_chat(self) -> None:
        self._page.clean()
        self._page.add(build_chat(self._page))


def main(page: ft.Page) -> None:
    page.title = "전문가 시스템 채팅"
    page.theme_mode = ft.ThemeMode.LIGHT
    ExpertChatApp(page).show_start()


ft.run(main)
