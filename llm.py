# from sentence_transformers import SentenceTransformer, util

# model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# sentence1 = "หามาครอบครอง"
# sentence2 = "ซื้อ"

# embedding1 = model.encode(sentence1, convert_to_tensor=True)
# embedding2 = model.encode(sentence2, convert_to_tensor=True)

# similarity_score = util.pytorch_cos_sim(embedding1, embedding2)
# print(f"Similarity Score: {similarity_score.item()}")  # ค่าใกล้ 1 คือความหมายเหมือนกัน

from scrapeweb import scrape
from thaidictscrape import dict_scrape
from dotenv import load_dotenv
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
    ตอบเป็นเลข 0-10 โดยตัวเลขยิ่งมากยิ่งมีความคล้ายมาก 
    """
    response = model.generate_content(prompt)
    return response.text

# test check sentence similarity function
sentence1 = "ไปหามาครอบครอง"
sentence2 = "ซื้อ"
result = check_sentence_similarity(sentence1, sentence2)
print(result)

def evaluation_check_similarity():
    result = []
    word = ["จึ้ง","ฉ่ำ","ตะโกน","หวาน","ตำ","ฉีดยา","บูด","บิด","เกาเหลา","ฟาด",
            "นอย","อ่อม","โฮ่ง","ลำไย","เงาะ","ส้ม","มะนาว","ละมุด","แตงโม","เชอร์รี่",
            "อ้อย","มะม่วง","ปัง","เยี่ยว","แกง","โป๊ะ","ตุ้บ","ยม","เฉียบ","เอือด",
            "แหก","สลวน","ราชนิกุล","อวย","รั่ว","ดือ","สับ","เม็ด","แก้วมังกร","มู่ลี่"]
    for i in word:
        list_meaning = scrape(slang=word[i],num="50")
        list_dict_meaning = dict_scrape(word=word[i])
        result.append(list_meaning,list_dict_meaning,check_sentence_similarity(list_meaning,list_dict_meaning))
    return result
    

def cut_similarity(list_of_meaning,dict_meaning):
    filtered_meaning = []
    boundary_num = 5 
    for i in list_of_meaning:
        if check_sentence_similarity(dict_meaning, list_of_meaning[i]) < boundary_num:
            filtered_meaning.append(list_of_meaning[i])
    return filtered_meaning


def conclude_meaning(slang):
    filtered_list_of_meaning = cut_similarity(scrape(slang=slang),dict_scrape(word=slang))
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    สรุปความหมายคำว่า {slang} จากใน list {filtered_list_of_meaning} ทั้งหมดให้อยู่ในโครงสร้างดังต่อไปนี้คือ
    "key" : {slang}
    "value" : [
        "หน้าที่ของคำ" : ""
        "ความหมาย" : ""
        "บริบท" : ""
    ]
    """
    response = model.generate_content(prompt)
    return response.text
