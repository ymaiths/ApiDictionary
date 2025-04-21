
import serpapi
import os


from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('SERPAPI_KEY')
client = serpapi.Client(api_key=api_key)
list_slang = [
    "นาตาชา", "เบอร์", "จึ้ง", "ฉ่ำ", "ตะโกน", "หวาน", "จะแล้วไหม", "ดอทคอม", "ตำ", "ฉีดยา",
    "มู่ลี่", "บ้ง", "บูด", "บิด", "ป้ายยา", "เกาเหลา", "เฟียสกี", "ฟาด", "มองบน", "นอย",
    "อ่อม", "โฮ่ง", "ตัวพ่อ", "ตัวแม่", "วาป", "ลำไย", "เงาะ", "ส้ม", "มะนาว", "กล้วย",
    "ละมุด", "แตงโม", "เชอร์รี่", "อ้อย", "สตอเบอรี่", "มะม่วง", "บีทรูท", "ปัง", "ติดแกลม", "เยี่ยว"
]
clarify_search = " ภาษาวัยรุ่น"
organic_fields = [
    "position", "title", "snippet", "snippet_highlighted_words", "source",
    "link", "redirect_link", "displayed_link","favicon"
]
for index,slang in enumerate(list_slang[0:1]):
    result = client.search(
        q=slang+clarify_search,
        engine="google",
        hl="th",
        gl="th",
        num="2",
        filter=0
    )
    # print(result["organic_results"])
    for item in result.get("organic_results", []):  # Loop through search results
        for field in organic_fields[0:5]:
            if field in item:
                print(f"{field}: {item[field]}")
            else:
                print(f"{field}: No data available")
    print("-----------------------")  # Separator for readability