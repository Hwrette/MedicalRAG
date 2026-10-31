from collections.abc import Awaitable, Callable

import flet as ft

from models import (
    DEFAULT_KNOWLEDGE_FILE,
    KnowledgeSource,
    assistant_reply,
    knowledge_status,
    load_bundled_knowledge,
)


def build_chat(
    page: ft.Page,
    record_message: Callable[[str, str], Awaitable[None]],
    on_back: Callable[[], None],
) -> ft.Control:
    try:
        source: KnowledgeSource | None = load_bundled_knowledge(DEFAULT_KNOWLEDGE_FILE)
        source_note = "기본 JSON 지식 파일이 연결되었습니다."
    except ValueError as error:
        source = None
        source_note = str(error)

    messages = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, auto_scroll=True)
    source_status = ft.Text(knowledge_status(source))
    source_preview = ft.Text(source_note, max_lines=5)
    message_input = ft.TextField(hint_text="질문을 입력하세요", expand=True)

    def add_message(message: str, alignment: ft.MainAxisAlignment) -> None:
        messages.controls.append(ft.Row(controls=[ft.Text(message)], alignment=alignment))

    async def send_message(_event) -> None:
        message = message_input.value.strip()
        if not message:
            return

        reply = assistant_reply(message, source)
        add_message(message, ft.MainAxisAlignment.END)
        add_message(reply, ft.MainAxisAlignment.START)
        message_input.value = ""
        await record_message("나", message)
        await record_message("전문가 시스템", reply)
        page.update()

    def return_to_menu(_event) -> None:
        on_back()

    message_input.on_submit = send_message
    add_message("기본 지식 파일을 검색합니다. 예: 운영 시간, 문의, 서비스 안내", ft.MainAxisAlignment.START)

    return ft.Column(
        controls=[
            ft.Text("전문가 시스템 채팅", size=24),
            ft.Button(content="뒤로", height=52, on_click=return_to_menu),
            source_status,
            source_preview,
            messages,
            ft.Row(
                controls=[
                    message_input,
                    ft.Button(content="보내기", icon=ft.Icons.SEND, height=52, on_click=send_message),
                ]
            ),
        ],
        expand=True,
    )
