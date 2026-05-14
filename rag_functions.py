import os
from dotenv import load_dotenv
from openai import OpenAI

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_db")
DATA_PATH = os.path.join(BASE_DIR, "data", "timetable_info.txt")


def load_documents():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        text = file.read()

    document = Document(page_content=text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents([document])

    return chunks


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={
            "device": "cpu",
            "local_files_only": True
        },
        encode_kwargs={"normalize_embeddings": True}
    )


def create_vectorstore():
    chunks = load_documents()
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )

    return vectorstore


def load_vectorstore():
    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )

    return vectorstore


def get_rag_answer(user_question):
    vectorstore = load_vectorstore()

    docs = vectorstore.similarity_search(user_question, k=3)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
너는 성신여자대학교 AI융합학부 학생을 위한 AI 수강 추천 챗봇이다.

반드시 아래 참고 문서 내용만 근거로 답변해라.
참고 문서에 없는 내용은 절대 추측하지 말고
"문서에서 확인할 수 없습니다."라고 답해라.

답변은 반드시 아래 형식을 정확히 지켜라.

-----------------------------------

(질문에 대한 한 줄 요약)

[추천 과목]
- 과목명
- 과목명
- 과목명
-교양과목 자유선택

[추천 학점 구성]
- 전공: X학점
- 필수교양: X학점
- 공통/핵심교양: X학점
총 X학점


[참고사항]
- 졸업 요건 충족을 위해 필수교양을 꼭 수강하세요
-1학년에는 각 학기마다 비사토/창사글 두 수업중 하나를 필수로 수강해야합니다.

-----------------------------------

규칙:
1. 한국어로만 답변해라.
2. 줄글로 길게 쓰지 마라.
3. 반드시 줄바꿈을 사용해라.
4. 추천 과목은 bullet point(-) 형식으로 작성해라.
5. 대학생이 보기 쉽게 깔끔하게 정리해라.
6. 부족한 졸업요건이 있다면 우선 반영해라.
7. 사용자가 목표 학점을 지정하지 않았을 경우 기본적으로 18학점 기준으로 추천해라.
8. 사용자가 특정 학기(예: 1학년 2학기)를 명시하면 반드시 해당 학기 커리큘럼 기준으로만 추천해라.
9. 이전 학기 과목을 반복 추천하지 마라.
10. 1학년 학생에게는 전공만 추천하면 안 된다.
11. 1학년 기본 추천 구성:
   - 전공 9학점
   - 필수교양 3학점
   - 공통/핵심교양 6학점
12. 2학년 이상은 전공 비중을 더 높게 추천할 수 있다.
13. 공통교양 필수 과목 중 비판적사고와토론, 창의적사고와글쓰기는
한 학기 추천에서 보통 둘 다 동시에 추천하지 않는다.

대신 아래 형식처럼 선택형으로 제시해라:
- 비판적사고와토론 또는 창의적사고와글쓰기

14. 여러 선택지가 가능한 교양 과목은 모두 나열하지 말고
"과목 A 또는 과목 B" 형식으로 간결하게 제시해라.

[참고 문서]
{context}

[사용자 질문]
{user_question}

[답변]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content