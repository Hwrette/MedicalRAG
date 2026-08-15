from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True)
class KnowledgeSource:
    filename: str
    root_kind: str
    item_count: int
    preview: str


def load_knowledge_source(filename: str, raw_data: bytes) -> KnowledgeSource:
    """Validate a JSON knowledge file and return display-safe metadata."""
    try:
        document = json.loads(raw_data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("읽을 수 있는 UTF-8 JSON 파일을 선택해 주세요.") from error

    if isinstance(document, dict):
        root_kind = "객체"
        item_count = len(document)
    elif isinstance(document, list):
        root_kind = "목록"
        item_count = len(document)
    else:
        root_kind = "값"
        item_count = 1

    preview = json.dumps(document, ensure_ascii=False, indent=2)
    return KnowledgeSource(
        filename=filename,
        root_kind=root_kind,
        item_count=item_count,
        preview=preview,
    )


def knowledge_status(source: KnowledgeSource | None) -> str:
    if source is None:
        return "연결된 JSON 지식 파일이 없습니다."
    return f"연결됨: {source.filename} ({source.root_kind} {source.item_count}개)"


def assistant_reply(message: str, source: KnowledgeSource | None) -> str:
    """Temporary reply point for a future JSON-based expert-answer engine."""
    if source is None:
        return "먼저 JSON 지식 파일을 불러오면, 다음 단계에서 이 질문과 연결할 수 있어요."
    return (
        f"'{source.filename}' 지식 파일이 준비되었습니다. "
        "현재는 파일 구조를 확인하는 단계이며, 다음 단계에서 질문과 JSON 내용을 연결할 수 있어요."
    )
