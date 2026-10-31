from collections.abc import Callable

import flet as ft

from models import ChatEntry


def build_history(entries: list[ChatEntry], on_back: Callable[[], None]) -> ft.Control:
    def go_back(_event) -> None:
        on_back()

    if entries:
        records = [
            ft.Text(f"{entry.speaker}: {entry.message}") for entry in entries
        ]
    else:
        records = [ft.Text("아직 저장된 채팅 기록이 없습니다.")]

    return ft.Column(
        controls=[
            ft.Text("채팅 기록"),
            ft.Button(content="뒤로", on_click=go_back),
            ft.ListView(controls=records, expand=True),
        ],
        expand=True,
    )
