from collections.abc import Callable

import flet as ft


def build_start(on_start: Callable[[], None]) -> ft.Control:
    def open_chat(_event) -> None:
        on_start()

    return ft.Column(
        controls=[
            ft.Text("전문가 시스템 채팅"),
            ft.Text("JSON 지식 파일을 연결하고 필요한 정보를 질문해 보세요."),
            ft.Button(content="시작하기", on_click=open_chat),
            ft.Text("시작 후 휴대폰에서 JSON 파일을 선택할 수 있습니다."),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
