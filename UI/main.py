import flet as ft

from views.chat import build_chat


def main(page: ft.Page) -> None:
    page.title = "전문가 시스템 채팅"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(build_chat(page))


ft.run(main)
