import flet as ft


def main(page: ft.Page):
    messages = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, auto_scroll=True)
    message_input = ft.TextField(hint_text="메시지를 입력하세요", expand=True)

    def send_message(e):
        message = message_input.value.strip()
        if not message:
            return

        messages.controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(message),
                        padding=10,
                        border=ft.Border.all(),
                        border_radius=ft.BorderRadius.all(10),
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        )
        message_input.value = ""
        page.update()

    message_input.on_submit = send_message

    page.add(
        ft.Column(
            controls=[
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
    )


ft.run(main)
