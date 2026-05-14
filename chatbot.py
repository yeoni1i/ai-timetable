
import os
from openai import OpenAI
from dotenv import load_dotenv
from rag_functions import get_rag_answer


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def get_chatbot_answer(user_message):
    system_prompt = """
너는 AI 시간표 추천 서비스의 챗봇이다.

사용자의 질문에 대해 다음 내용을 도와준다.
1. 시간표 추천 서비스 사용 방법
2. 공강, 난이도, 졸업요건, 목표 학점 설명
3. 1학년 학생이 시간표를 짤 때 고려할 점
4. 추천 결과를 해석하는 방법

모르는 내용은 추측하지 말고 모른다고 말한다.
답변은 한국어로 쉽고 간단하게 한다.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3
    )

    return get_rag_answer(user_message)

