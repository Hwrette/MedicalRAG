from collections.abc import Callable

import flet as ft


def build_start(on_start: Callable[[], None]) -> ft.Control:
    def open_menu(_event) -> None:
        on_start()

    return ft.Column(
        controls=[
            ft.Row(
                controls=[ft.Text("전문가 시스템 채팅", text_align=ft.TextAlign.CENTER, size=28)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[ft.Text("기본 JSON 지식 파일로 필요한 정보를 질문해 보세요.", text_align=ft.TextAlign.CENTER)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Button(content="시작하기", width=240, height=68, on_click=open_menu),
            ft.Row(
                controls=[ft.Text("나중에 assets/sample_knowledge.json 파일을 바꾸면 됩니다.", text_align=ft.TextAlign.CENTER)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
