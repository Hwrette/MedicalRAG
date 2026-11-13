"""1단계: 로컬 PDF를 페이지별로 읽고 본문 추출 결과를 확인합니다."""

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter

import json

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_core.vectorstores import InMemoryVectorStore

import time


SOURCE_DIR = Path(__file__).resolve().parent / "RAGtexts" / "sources"


def load_pdf_documents():
    documents = []
    pdf_paths = sorted(SOURCE_DIR.glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"PDF 파일이 없습니다: {SOURCE_DIR}")

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        empty_pages = []
        page_documents = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                empty_pages.append(page_number)
                continue

            # 본문과 PDF 파일명·페이지 번호를 함께 보관합니다.
            page_documents.append(Document(
                page_content=text,
                metadata={"source": pdf_path.name, "page": page_number},
            ))

        documents.extend(page_documents)
        print(f"\n파일: {pdf_path.name}")
        print(f"전체 {len(reader.pages)}쪽 / 텍스트 추출 {len(page_documents)}쪽")
        if page_documents:
            print("첫 본문 미리보기:", page_documents[0].page_content[:250])
        if empty_pages:
            print("텍스트가 없는 페이지(이미지 또는 빈 페이지 확인 필요):", empty_pages)

    return documents


if __name__ == "__main__":
    documents = load_pdf_documents()
    print(f"\n읽어 온 페이지 문서: {len(documents)}개")
    # print("이번 단계에서는 파일 저장, 청킹, 임베딩, API 호출을 하지 않습니다.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    chunks = splitter.split_documents(documents)

    print(f"나눠진 조각: {len(chunks)}개")
    print("첫 조각:", chunks[0].page_content)
    print("출처:", chunks[0].metadata)

    output_path = SOURCE_DIR.parent / "chunks.json"

    for chunk_id, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk_id"] = chunk_id

    chunk_data = [
        {
            "id": index,
            "text": chunk.page_content,
            "metadata": chunk.metadata,
        }
        for index, chunk in enumerate(chunks, start=1)
    ]

    output_path.write_text(
        json.dumps(chunk_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("조각 저장 위치:", output_path)

        # prepare_rag.py 옆의 .env에서 API 키 읽기
    load_dotenv(Path(__file__).resolve().parent / ".env")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
    )

    # 먼저 세 조각으로 API 연결과 변환 확인
    # sample_chunks = chunks[:3]

    vector_store = InMemoryVectorStore(embeddings)

    # 한 번에 20개씩 임베딩해서 저장소에 추가
    for start in range(0, len(chunks), 20):
        batch = chunks[start:start + 20]
        vector_store.add_documents(batch)

        completed = start + len(batch)
        print(f"임베딩 진행: {completed}/{len(chunks)}")

        if completed < len(chunks):
            time.sleep(20)

    # 본문·출처·벡터를 함께 파일로 저장
    index_dir = SOURCE_DIR.parent / "index"
    index_dir.mkdir(parents=True, exist_ok=True)

    index_path = index_dir / "wounds.json"
    vector_store.dump(str(index_path))

    print("검색용 데이터 저장 완료:", index_path)