import os
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)  # Only show errors
from scrapeweb import scrape
from thaidictscrape import get_dict_meaning
from sentence_transformers import SentenceTransformer, util
from llm import conclude_each_scrape_meaning

# Load multilingual model that supports Thai
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # Free and supports Thai

def similarity_score(word):
    dict = get_dict_meaning(word)
    meaning = conclude_each_scrape_meaning(word=word,num="5")
    sentences = dict+meaning
    print(sentences)
    # Create embeddings
    embeddings = model.encode(sentences)

    # Calculate cosine similarity between first and other sentences
    for i in range(len(dict)):
        for j in range(len(meaning)):    
            similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j+len(dict)])
            print(f"Similarity: {similarity.item():.4f} - '{sentences[i]}' and '{sentences[j+len(dict)]}'")

word = "ฉ่ำ"
# sentences = [
#     "ชุ่มชื้น",
#     "มาก เยอะ",
#     "สดชื่น"
# ]
similarity_score(word=word)
