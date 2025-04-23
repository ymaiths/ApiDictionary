import json
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

system = """
คุณเป็นผู้เชี่ยวชาญด้านการ *สรุป* คำสแลง/ภาษาโซเชียล/ภาษาวัยรุ่น
คำสแลงอาจมีความหมายไม่ตรงกับความหมายที่คนทั่วไปคิด หรือสื่อไปทางที่ไม่ดี
คุณจะได้รับคำสแลง และคุณต้องตอบความหมาย คำจำกัดความ และตัวอย่างของคำนั้น
"""

example = """
ตัวอย่างคำสแลง:

example_user: คำว่า \"ฉ่ำ\" แปลว่าอะไร?
example_user: ให้ความหมายของ \"ฉ่ำ\" ในว่า เป็นคำวิเศษณ์ที่มีความหมายว่า ชุ่มชื่น, ชุ่มน้ำในตัว แต่ด้วยความสร้างสรรค์ของคนไทยได้นำคำนี้มาใช้ในอีกความหมายว่า มาก หรือ เยอะ
example_assistant: {{"meaning": \"ฉ่ำ\", "definition": "มาก หรือ เยอะ", "examples": "ฉ่ำมากกับกลุ่มนี้นะ!"}}

example_user: คำว่า "ตึงมาก" แปลว่าอะไร?
example_user: คำว่า "ตัวตึง" คำว่า \"ตัวตึง\" คือ ศัพท์สแลงที่วัยรุ่นและโลกออนไลน์นิยมใช้กันอย่างแพร่หลาย มีความหมายสื่อถึงการเป็นที่หนึ่ง, ตัวท็อป, เป็นเลิศ, สุดยอด คล้าย ๆ กับคำว่า "ตัวเต็ง"
example_assistant: {{"meaning": "ตึงมาก", "definition": "ตัวท็อป, เป็นเลิศ, สุดยอด", "examples": "กูโครตตึง"}}
"""


class SlangDefinition(BaseModel):
    meaning: str = Field(description="คำสแลงที่ต้องการค้นหา")
    definition: str = Field(description="ความหมายของคำสแลงนี้")
    examples: str = Field(description="ตัวอย่างการใช้คำสแลงนี้")


def search_flow(word):
    tools = TavilySearchResults(max_results=3, exclude_domains=[
                                "youtube.com", "tiktok.com", "slang.in.th", "dict.longdo.com"], search_depth="advanced")
    result = tools.invoke(
        f"คำว่า \"{word}\" แปลว่าอะไร ภาษาวัยรุ่น")

    buffer = []
    for i in result:
        buffer.append({"title": i["title"], "content": i["content"]})
    return buffer[::-1]


if __name__ == "__main__":
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    word = "เกาเหลา"

    slang_search_result = search_flow(word)
    structured_model = model.with_structured_output(SlangDefinition)
    print(slang_search_result)
    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("system", "{context}"), ("user", "{example}"), ("user", "{prompt}")])

    few_shot_structured_llm = prompt | structured_model
    result = few_shot_structured_llm.invoke({
        "context": json.dumps(slang_search_result),
        "example": example,
        "prompt": f"คำว่า {word} แปลว่าอะไร ภาษาสแลง"
    })
    print(result)
