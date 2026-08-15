import flet as ft

from models import KnowledgeSource, assistant_reply, knowledge_status, load_knowledge_source


def build_chat(page: ft.Page) -> ft.Control:
    source: KnowledgeSource | None = None
    messages = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, auto_scroll=True)
    source_status = ft.Text(knowledge_status(source))
    source_preview = ft.Text("JSON 파일을 선택하면 여기에서 일부 내용을 확인할 수 있습니다.", max_lines=5)
    message_input = ft.TextField(hint_text="질문을 입력하세요", expand=True)
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    def add_message(message: str, alignment: ft.MainAxisAlignment) -> None:
        messages.controls.append(ft.Row(controls=[ft.Text(message)], alignment=alignment))

    def send_message(_event) -> None:
        message = message_input.value.strip()
        if not message:
            return

        add_message(message, ft.MainAxisAlignment.END)
        add_message(assistant_reply(message, source), ft.MainAxisAlignment.START)
        message_input.value = ""
        page.update()

    async def choose_json(_event) -> None:
        nonlocal source
        files = await file_picker.pick_files(
            dialog_title="JSON 지식 파일 선택",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
            allow_multiple=False,
            with_data=True,
        )
        if not files:
            return

        selected_file = files[0]
        if selected_file.bytes is None:
            add_message("파일 내용을 가져오지 못했습니다. 다시 선택해 주세요.", ft.MainAxisAlignment.START)
            page.update()
            return

        try:
            source = load_knowledge_source(selected_file.name, selected_file.bytes)
        except ValueError as error:
            add_message(str(error), ft.MainAxisAlignment.START)
        else:
            source_status.value = knowledge_status(source)
            source_preview.value = source.preview
            add_message(f"{source.filename} 파일을 지식 소스로 불러왔습니다.", ft.MainAxisAlignment.START)
        page.update()

    message_input.on_submit = send_message
    add_message("JSON 지식 파일을 연결한 뒤 질문을 시작해 보세요.", ft.MainAxisAlignment.START)

    return ft.Column(
        controls=[
            ft.Text("전문가 시스템 채팅"),
            ft.Button(
                content="JSON 파일 불러오기",
                icon=ft.Icons.DESCRIPTION,
                on_click=choose_json,
            ),
            source_status,
            source_preview,
            messages,
            ft.Row(
                controls=[
                    message_input,
                    ft.Button(content="보내기", icon=ft.Icons.SEND, on_click=send_message),
                ]
            ),
        ],
        expand=True,
    )
