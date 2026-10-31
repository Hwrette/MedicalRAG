from pathlib import Path

from dotenv import load_dotenv
from google import genai

# 이 Python 파일과 같은 폴더에 있는 .env를 읽습니다.
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

# GEMINI_API_KEY 환경변수를 사용해 요청을 준비합니다.
client = genai.Client()

print("실행중")

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="안녕! API가 무엇인지 한국어로 두 문장으로 설명해 줘.",
)

print(response.text)
