from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


DEFAULT_KNOWLEDGE_FILE = "sample_knowledge.json"


@dataclass(frozen=True)
class KnowledgeSource:
    filename: str
    document: Any
    root_kind: str
    item_count: int
    preview: str


@dataclass(frozen=True)
class ChatEntry:
    speaker: str
    message: str


def load_history(raw_history: str | None) -> list[ChatEntry]:
    """Convert persisted chat history into safe display records."""
    if not raw_history:
        return []

    try:
        items = json.loads(raw_history)
    except json.JSONDecodeError:
        return []

    if not isinstance(items, list):
        return []

    return [
        ChatEntry(speaker=item["speaker"], message=item["message"])
        for item in items
        if isinstance(item, dict)
        and isinstance(item.get("speaker"), str)
        and isinstance(item.get("message"), str)
    ]


def save_history(entries: list[ChatEntry]) -> str:
    """Serialize chat records for persistent key-value storage."""
    return json.dumps(
        [{"speaker": entry.speaker, "message": entry.message} for entry in entries],
        ensure_ascii=False,
    )


def load_bundled_knowledge(filename: str) -> KnowledgeSource:
    """Load a JSON knowledge file bundled with the app."""
    try:
        raw_data = Path("assets", filename).read_bytes()
    except OSError as error:
        raise ValueError("기본 지식 파일을 찾을 수 없습니다.") from error
    return load_knowledge_source(filename, raw_data)


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
        document=document,
        root_kind=root_kind,
        item_count=item_count,
        preview=preview,
    )


def knowledge_status(source: KnowledgeSource | None) -> str:
    if source is None:
        return "연결된 JSON 지식 파일이 없습니다."
    return f"연결됨: {source.filename} ({source.root_kind} {source.item_count}개)"


def _search_terms(message: str) -> list[str]:
    return re.findall(r"[0-9A-Za-z가-힣_]{2,}", message.lower())


def _records(document: Any) -> list[tuple[str, Any]]:
    if isinstance(document, dict):
        return [(str(key), value) for key, value in document.items()]
    if isinstance(document, list):
        return [(f"항목 {index + 1}", value) for index, value in enumerate(document)]
    return [("지식", document)]


def _format_match(label: str, record: Any) -> str:
    text = json.dumps(record, ensure_ascii=False, indent=2)
    if len(text) > 800:
        text = f"{text[:800]}\n..."
    return f"[{label}]\n{text}"


def assistant_reply(message: str, source: KnowledgeSource | None) -> str:
    """Searches the selected JSON file with a simple, schema-independent rule."""
    if source is None:
        return "먼저 JSON 지식 파일을 불러온 뒤 질문해 주세요."

    terms = _search_terms(message)
    if not terms:
        return "두 글자 이상의 검색어를 포함해 질문해 주세요."

    matches: list[tuple[int, str, Any]] = []
    for label, record in _records(source.document):
        searchable = f"{label} {json.dumps(record, ensure_ascii=False)}".lower()
        score = sum(term in searchable for term in terms)
        if score:
            matches.append((score, label, record))

    if not matches:
        return f"'{source.filename}'에서 질문과 일치하는 지식 항목을 찾지 못했습니다. 다른 표현으로 질문해 주세요."

    matches.sort(key=lambda item: item[0], reverse=True)
    results = [_format_match(label, record) for _, label, record in matches[:3]]
    return "JSON 지식 파일에서 찾은 관련 항목입니다.\n\n" + "\n\n".join(results)
