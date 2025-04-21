from scrapeweb import scrape
from thaidictscrape import get_dict_meaning
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import os
load_dotenv()

import google.generativeai as genai
genai.configure(api_key="AIzaSyBYHGJ2oW2wNmO784MkGtnmIfH0MjtwNcc")

def check_sentence_similarity(sentence1, sentence2):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    พิจารณาความหมายคำในภาษาไทยสองประโยคต่อไปนี้และระบุว่ามีความหมายคล้ายกันมากแค่ไหน:
    ประโยคที่ 1: {sentence1}
    ประโยคที่ 2: {sentence2}
    ตอบเป็นเลข 0-10 เท่านั้น โดยตัวเลขยิ่งมากยิ่งมีความคล้ายมาก เช่น "0","1","2","3","4","5","6","7","8","9","10" 
    """
    response = model.generate_content(prompt)
    return response.text

# test check sentence similarity function
# sentence1 = "ไปหามาครอบครอง"
# sentence2 = "ซื้อ"
# result = check_sentence_similarity(sentence1, sentence2)
# print(result)

def cut_similarity(word):
    filter_meaning = []
    dict_meaning = []
    scrape_meaning = scrape(slang=word,num="20")[1]
    dict_meaning = get_dict_meaning(word)
    # print(len(dict_meaning))
    # print(scrape_meaning)
    for i in dict_meaning:
        for j in scrape_meaning:
            # print(check_sentence_similarity(i,j))
            if int(check_sentence_similarity(i,j))<5:
                filter_meaning.append(j)
    print(f"filterd_meaning:{filter_meaning}")
    return filter_meaning

# word = "ยม"
# cut_similarity(word=word)


# def conclude_meaning(slang):
#     filtered_list_of_meaning = cut_similarity(scrape(slang=slang),get_dict_meaning(word=slang))
#     model = genai.GenerativeModel('gemini-2.0-flash')
#     prompt = f"""
#     สรุปความหมายคำว่า {slang} จากใน list {filtered_list_of_meaning} ทั้งหมดให้อยู่ในโครงสร้างดังต่อไปนี้คือ
#     "key" : {slang}
#     "value" : [
#         "หน้าที่ของคำ" : ""
#         "ความหมาย" : ""
#         "บริบท" : ""
#     ]
#     """
#     response = model.generate_content(prompt)
#     return response.text
