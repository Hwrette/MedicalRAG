from collections.abc import Callable

import flet as ft


def build_menu(on_chat: Callable[[], None], on_history: Callable[[], None]) -> ft.Control:
    def open_chat(_event) -> None:
        on_chat()

    def open_history(_event) -> None:
        on_history()

    return ft.Column(
        controls=[
            ft.Text("무엇을 할까요?", text_align=ft.TextAlign.CENTER, size=24),
            ft.Button(
                content=ft.Column(
                    controls=[
                        ft.Text("채팅 시작", text_align=ft.TextAlign.CENTER, size=26),
                        ft.Text("기본 지식 파일로 질문하기", text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=320,
                height=142,
                on_click=open_chat,
            ),
            ft.Button(
                content=ft.Column(
                    controls=[
                        ft.Text("기록", text_align=ft.TextAlign.CENTER, size=26),
                        ft.Text("이전 채팅 내용 확인하기", text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=320,
                height=142,
                on_click=open_history,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
