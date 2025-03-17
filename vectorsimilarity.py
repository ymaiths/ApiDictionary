# from sentence_transformers import SentenceTransformer, util

# model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# sentence1 = "หามาครอบครอง"
# sentence2 = "ซื้อ"

# embedding1 = model.encode(sentence1, convert_to_tensor=True)
# embedding2 = model.encode(sentence2, convert_to_tensor=True)

# similarity_score = util.pytorch_cos_sim(embedding1, embedding2)
# print(f"Similarity Score: {similarity_score.item()}")  # ค่าใกล้ 1 คือความหมายเหมือนกัน

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

# ตัวอย่างการใช้งาน
sentence1 = "ไปหามาครอบครอง"
sentence2 = "ซื้อ"
result = check_sentence_similarity(sentence1, sentence2)
print(result)