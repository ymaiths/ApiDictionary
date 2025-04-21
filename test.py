import json
import pprint
from scrapeweb import scrape
from thaidictscrape import get_dict_meaning
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import time
import pandas as pd
import re
import requests
import httpx
from openai import OpenAI

load_dotenv()

#germini
import google.generativeai as genai
genai.configure(api_key="AIzaSyBYHGJ2oW2wNmO784MkGtnmIfH0MjtwNcc")
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

openai_api_key = "sk-ymu49yWvJNzyrJ8K2menMxxA99njUxG5IwAileGH9khESe6v"

# class MeaningData(BaseModel):
#     Meaning: Optional[str]
#     PartOfSpeech: Optional[str]
#     Example: Optional[str]
    # คำแนะนำ:
    #     - ให้เก็บข้อมูลของทุกความหมายที่ได้รับ แต่ถ้าความหมายนั้นตรงกับพจนานุกรมฉบับราชบัณฑิตยสถาน ให้แทนค่าด้วย ""
    #     - หากความหมายที่ได้รับมีทั้งความหมายจากพจนานุกรมฉบับราชบัณฑิตยสถานและความหมายอื่น ๆ ให้นำเฉพาะความหมายอื่น ๆ มาเก็บไว้
    #     ตัวอย่าง:
    #         - ความหมายที่ได้รับ: "ฉ่ำดั้งเดิมแปลว่าชุ่มชื้น ชุ่มน้ำ แต่ในปัจจุบันวัยมักใช้แปลว่า เยอะ หรือ มาก"
    #         - ความหมายจากพจนานุกรมฉบับราชบัณฑิตยสถาน: "ชุ่มชื้น อิ่มน้ำ"
    #         - ความหมายสุดท้ายที่ต้องเก็บ: "เยอะ หรือ มาก"

class WordData(BaseModel):
    Meaning: Optional[str] = Field(description="ส่วนของข้อความที่ระบุความหมายของคำที่สนใจ")
    PartOfSpeech: Optional[str] = Field(description="ส่วนของข้อความที่ระบุหรือสื่อถึง Part of speech ของคำที่สนใจ")
    Example: Optional[str] = Field(description="ส่วนของข้อความที่ระบุประโยคตัวอย่างที่มีคำที่สนใจ")

class WordDatas(BaseModel):
    datas: List[WordData]
    
from pydantic import BaseModel
from typing import Optional, List
import time

def structure_scrape_meaning_02(word: str, list_meaning: List[str],model: str):
    print("start")
    prompt = f"""
    จากรายการข้อความความหมาย : {list_meaning} 
    ให้เก็บข้อมูลเฉพาะข้อมูลของคำที่สนใจ นั่นคือ {word} ในแต่ละข้อความความหมาย
    ให้เป็นโครงสร้างดังต่อไปนี้:
    ```json
    {json.dumps(WordDatas.model_json_schema())}
    ```
    ให้ตอบกลับมาในรูปแบบ A JSON List ที่เพียง 1 key นั่นคือ datas เท่านั้น
    """
    if model == "gemini":
        structure_list = gemini_model.generate_content(prompt)
        time.sleep(1)
        structure_list = structure_list.text
    elif model == "typhoon":        
        client = OpenAI(
        api_key=openai_api_key,
        base_url='https://api.opentyphoon.ai/v1'
        )
        
        chat_completion = client.chat.completions.create(
            model="typhoon-v2-70b-instruct",
            messages=[{"role": "system", "content": f"{prompt}"}],
            temperature=0.2
        )
        time.sleep(1)
        # print(chat_completion)
        structure_list = chat_completion.choices[0].message.content
        
        
    print(f"After: {structure_list}")
    # print("done!")
    print("------------")
    try:
        return json.loads(structure_list.replace("json", "").strip("```"))
    except json.decoder.JSONDecodeError:
        return None

def to_excel_list(words, raws, structure_meanings_list, filename="word_data.xlsx"):
    all_data = []
    for word, raw, structure_meaning in zip(words,raws, structure_meanings_list):
        for i,r in enumerate(raw):
            if i < len(structure_meaning["datas"]):
                data = structure_meaning["datas"][i]
                meaning = data["Meaning"]
                pos = data["PartOfSpeech"]
                example = data["Example"]
            else:
                meaning = pos = example = None

            all_data.append({
                "Word": word,
                "Raw": r,
                "Meaning": meaning,
                "PartOfSpeech": pos,
                "Example": example  
            })

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Export to Excel
    df.to_excel(filename, index=False)

    print(f"Excel file '{filename}' saved successfully!")

def excel_to_list(filename: str):
    try:
        df = pd.read_excel(filename)
        data_list = df.to_dict(orient="records")
        return data_list
    except Exception as e:
        print("Error reading Excel file:", e)
        return []
    

def bunch_sturcture_source_scrape():
    results = []
    raws=[]
    words = [ "ตำ","ฉีดยา","อ้อย","ฉีดยา","เอือด","บูด","บิด","เกาเหลา","จึ้ง","ฉ่ำ",
              "หวาน","นอย","อ่อม","โฮ่ง","ลำไย","เงาะ","ส้ม","มะนาว","ละมุด","แตงโม"]
            #   "ฟาด","มะม่วง","ปัง","เยี่ยว","แกง","โป๊ะ","ตุ้บ","ยม","เฉียบ",
            #   "แหก","สลวน","ราชนิกุล","อวย","รั่ว","ดือ","เม็ด","แก้วมังกร","มู่ลี่","ตะโกน"]
            #   "นาตาชา","ดอทคอม","บ้ง","ป้ายยา","เชอร์รี่","สตอเบอรี่","บีทรูท","ติดแกลม","ปั๊ว","จ้อจี้",
            #   "ต๊าซ","ช็อตฟีล","เทส","โดนตก","กี่โมง","ชายแท้","หญิงแท้","ทำถึง","ใจฟู","ปลาหมึกแถวบน"]
    for word in words:
        list_meaning = scrape(slang=word,num="20")[1]
        # list_meaning = [s.replace('\\', " ") for s in list_meaning]
        # print(word)
        # print(f"bunch: {list_meaning}")
        raws.append(list_meaning)
        result = structure_scrape_meaning_02(word,list_meaning)
        while result == None:
            result = structure_scrape_meaning_02(word,list_meaning)
        results.append(result)
        # print(result)d
        # print("////////////////////")
    return words,raws,results

def bunch_sturcture_source_excel(excel_file_name:str,model:str):
    results = []
    raws = []
    data = excel_to_list(excel_file_name)

    # Step 1: Create a map from word to its raw meanings
    word_to_raws = {}
    for row in data:
        word = row["Word"]
        raw = row["Raw"]
        raw = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9\s]', '', raw)
        if word not in word_to_raws:
            word_to_raws[word] = []
        word_to_raws[word].append(raw)

    # Step 2: Process each unique word only once
    words_unique = list(word_to_raws.keys())
    for word in words_unique:
        raw_list = word_to_raws[word]
        raws.append(raw_list)
        result = structure_scrape_meaning_02(word,raw_list,model)
        while result == None:
            result = structure_scrape_meaning_02(word,raw_list,model)
        results.append(result)

    return words_unique, raws, results

# print(f"raws:{raws}")
# to_excel_list(words,raws,meanings,"20word_scrape.xlsx")
wordsxl,rawsxl,meaningsxl = bunch_sturcture_source_excel("20word_scrape.xlsx",model="typhoon")
# to_excel_list(wordsxl,rawsxl,meaningsxl,"Typhoon_20word.xlsx")

def save_scrape_in_excel(filename="scrape.xlsx"):
    raws = []
    words = [ "ตำ","ฉีดยา","อ้อย","ฉีดยา","เอือด","บูด","บิด","เกาเหลา","จึ้ง","ฉ่ำ",
              "หวาน","นอย","อ่อม","โฮ่ง","ลำไย","เงาะ","ส้ม","มะนาว","ละมุด","แตงโม"]
            #   "ฟาด","มะม่วง","ปัง","เยี่ยว","แกง","โป๊ะ","ตุ้บ","ยม","เฉียบ",
            #   "แหก","สลวน","ราชนิกุล","อวย","รั่ว","ดือ","เม็ด","แก้วมังกร","มู่ลี่","ตะโกน"]
            #   "นาตาชา","ดอทคอม","บ้ง","ป้ายยา","เชอร์รี่","สตอเบอรี่","บีทรูท","ติดแกลม","ปั๊ว","จ้อจี้",
            #   "ต๊าซ","ช็อตฟีล","เทส","โดนตก","กี่โมง","ชายแท้","หญิงแท้","ทำถึง","ใจฟู","ปลาหมึกแถวบน"]
    for word in words:
        list_meaning = scrape(slang=word,num="20")[1]
        raws.append(list_meaning)
    
    all_data = []
    # for word, raw, structure_meaning in zip(words,raws, structure_meanings_list):
    for word, raw  in zip(words,raws):
        for r in raw:
            all_data.append({
                "Word": word,
                "Raw": r
            })

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Export to Excel
    df.to_excel(filename, index=False)

    print(f"Excel file '{filename}' saved successfully!")

# class MeaningData(BaseModel):
#     Meaning: Optional[str] = Field(description="ส่วนของข้อความที่ระบุความหมายของคำที่สนใจ")

# class MeaningDatas(BaseModel):
#     meanings: List[MeaningData]
    
# def filter_thaidict_meaning(meaning_list,dict_meaning):
#     filter_meaning = []
    
#     prompt = f"""
#     จากรายการความหมายต่อไปนี้ ให้พิจารณาว่า :

#     ```json
#     {json.dumps(WordDatas.model_json_schema())}
#     ```
#     รายการข้อความความหมาย ที่ต้องนำมาวิเคราะห์:
#     {list_meaning}

#     ให้ตอบกลับมาในรูปแบบ A JSON List โดยไม่ต้องทวนคำถามหรืออธิบายเหตุผล
#     """
    
#     response = model.generate_content(prompt)
#     time.sleep(1)
#     print(f"Before:{meaning}")
#     print(f"After:{response.text}")
#     print("-------------")
            
#     # print(f"conclude_scrape:{conclude_meaning}")
#     return filter_meaning
# # list_meaning = filter_no_meaning("ปัง")
# # print(list_meaning)
# # structure_scrape_meaning_01("ปัง",list_meaning=list_meaning)


# def conclude_each_scrape_meaning(word,num="20"):
#     word,list_meaning = scrape(slang=word,num=num)
#     conclude_meaning = []
#     for meaning in list_meaning:
#         prompt = f"""
#         จากข้อความ {meaning}
#         หากไม่มีการให้ความหมายให้ตอบว่า ""
#         หากมีการให้ความหมาย ให้วิเคราะห์และเก็บข้อมูลของเฉพาะคำว่า {word} ให้เป็นโครงสร้าง dictionary ดังต่อไปนี้ โดยไม่จำเป็นต้องมีทุกตัวแปรในโครงสร้าง หากตัวแปรตัวใดไม่มีให้แทนค่าเป็น "" และไม่ต้องทวนคำถามหรือให้เหตุผล
#         "Meaning" : "ความหมายของคำว่า {word} ที่ไม่ใช่ความหมายที่ถูกระบุว่าเป็นคว้ามหมายดั้งเดิม",
#         "PartOfSpeech" : "หน้าที่ของคำ ของคำว่า {word}",
#         "Example" : "ตัวอย่างประโยคของ {word}"
        
#         ตัวอย่างเช่น 
#         ถ้าข้อความ meaning คือ ""จึ้ง" = อึ้ง ตกใจ แต่ในแง่ดี. ตัวอย่าง : "ดูกระเป๋าใบนี้สิ จึ้งมาก!" "บ้ง" หมายถึง สิ่งที่ไม่ดี ผิดพลาด หรือไม่ได้เรื่อง เช่น "งานนี้บ้งไปหมดเลย" "นก" หมายถึง การพลาดหวัง เช่น "กะจะได้บัตรคอนเสิร์ต สุดท้ายนก!""
#         และ word คือ "จึ้ง"
#         ให้ตอบว่า "Meaning : "อึ้ง ตกใจ แต่ในแง่ดี", PartOfSpeech : "", Example : "ดูกระเป๋าใบนี้สิ จึ้งมาก!""
        
#         """
#         response = model.generate_content(prompt)
#         conclude_meaning.append(response.text.strip("\n"))
#         print(f"Before:{meaning}")
#         print(f"After:{response.text}")
#         print("------------")
#     # print(f"conclude_scrape:{conclude_meaning}")
#     return conclude_meaning
# # conclude_each_scrape_meaning("ฉ่ำ")
