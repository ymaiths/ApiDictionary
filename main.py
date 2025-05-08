from enum import Enum
import json
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from src.type import SlangDefinition
from src.llm import LLM
load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")

system = """
คุณเป็นผู้เชี่ยวชาญด้านการ *สรุป* คำสแลง/ภาษาโซเชียล/ภาษาวัยรุ่น
คำสแลงมักมีความหมายไม่ตรงกับความหมายที่คนทั่วไปคิดหรือความหมายดั้งเดิม และอาจสื่อไปในทางที่ไม่ดีได้
คุณจะได้รับคำสแลง และคุณต้องตอบความหมาย คำจำกัดความ และตัวอย่างของคำนั้น

คุณต้องตอบคำถามตาม "ข้อมูลจริง" ที่ได้รับ
"""

example = """
ตัวอย่างคำสแลง:

ี๊คน: คำว่า \"ฉ่ำ\" แปลว่าอะไร?
ความรู้: ให้ความหมายของ \"ฉ่ำ\" ในว่า เป็นคำวิเศษณ์ที่มีความหมายว่า ชุ่มชื่น, ชุ่มน้ำในตัว แต่ด้วยความสร้างสรรค์ของคนไทยได้นำคำนี้มาใช้ในอีกความหมายว่า มาก หรือ เยอะ
คำตอบ: {{"meaning": \"ฉ่ำ\", "definition": "มาก หรือ เยอะ", "examples": "ขนาดวันนี้วันหยุดงานยังฉำ่ขนาดนี้"}}

ี๊คน: คำว่า "ตึงมาก" แปลว่าอะไร?
ความรู้: คำว่า "ตัวตึง" คำว่า \"ตัวตึง\" คือ ศัพท์สแลงที่วัยรุ่นและโลกออนไลน์นิยมใช้กันอย่างแพร่หลาย มีความหมายสื่อถึงการเป็นที่หนึ่ง, ตัวท็อป, เป็นเลิศ, สุดยอด คล้าย ๆ กับคำว่า "ตัวเต็ง"
คำตอบ: {{"meaning": "ตึงมาก", "definition": "ตัวท็อป, เป็นเลิศ, สุดยอด", "examples": "กูโครตตึง"}}

คน: คำว่า \"ตัวแม่\" แปลว่าอะไร?
ความรู้:  \"ตัวแม่\" คือ คนที่เป็นที่สุดในด้านใดด้านหนึ่ง หรือชื่นชมว่าเก่ง ตัวอย่าง : เรามันตัวแม่ แปลว่า เราเก่ง เราเริ่ดที่สุด ไม่มีใครมีความสามารถเท่าเราแล้ว
คำตอบ: {{"meaning": "ตัวแม่", "definition": "คนที่เป็นที่สุดในด้านใดด้านหนึ่ง", "examples": "เรามันตัวแม่"}}
"""


def search_flow(word):
    tools = TavilySearchResults(max_results=3, exclude_domains=[
                                "youtube.com", "tiktok.com", "slang.in.th", "dict.longdo.com"], search_depth="advanced", tavily_api_key=tavily_api_key)
    result = tools.invoke(
        f"คำว่า \"{word}\" แปลว่าอะไร ภาษาวัยรุ่น")
    print("tavily result \n", result, "\n\n")

    buffer = "ข้อมูลจริง \n ----------- \n"
    for i in result:
        buffer += f"หัวข้อ \n {i["title"]} \n เนื้อหา \n {i["content"]} \n"
    return buffer


def main(word: str):
    model = LLM(model_name="gemini")
    word = word

    slang_search_result = search_flow(word)

    structured_model = model.with_structured_output(SlangDefinition)
    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("system", "{context}"), ("user", "{example}"), ("user", "{prompt}")])

    few_shot_structured_llm = prompt | structured_model
    result = few_shot_structured_llm.invoke({
        "context": slang_search_result,
        "example": example,
        "prompt": f"คำว่า {word} แปลว่าอะไร ภาษาสแลง"
    })
    return result


if __name__ == "__main__":
    print(main("ฉ่ำ"))
