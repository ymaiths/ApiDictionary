from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from sklearn.metrics import precision_score, recall_score, f1_score
import torch
from transformers import BertTokenizer, BertModel
from bert_score import BERTScorer
from sentence_transformers import SentenceTransformer, util
import re
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import math


model = SentenceTransformer('all-MiniLM-L6-v2')
class Truth(BaseModel):
    word: str
    part_of_speech: List[str]
    meaning: str
    example: str


class TruthReader:
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.data = self.data.to_dict(orient='records')
        self.data = [
            Truth(
                word=row['word'],
                part_of_speech=[p.strip() for p in row['part_of_speech'].split(';')],
                meaning=row['meaning'],
                example=row['example']
            ) for row in self.data
        ]

class Validation:
    def __init__(self, truths: List[Truth]):
        self.truths = truths
        # Initialize BERT model for semantic similarity calculations
        self.tokenizer = None
        self.model = None
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')

    def calculate_bertscore(self, text1: str, text2: str) -> float:
        """Calculate BERTScore between two texts"""
        scorer = BERTScorer(model_type="bert-base-uncased")
        P, R, F1 = scorer.score([text1], [text2])
        return F1

    def calculate_semantic_textual_similarity(self, sentence1: str, sentence2: str) -> float:

        # Encode sentences into embeddings
        embedding1 = model.encode(sentence1, convert_to_tensor=True)
        embedding2 = model.encode(sentence2, convert_to_tensor=True)
        
        # Compute cosine similarity
        similarity_score = util.pytorch_cos_sim(embedding1, embedding2).item()
        return similarity_score

    def calculate_part_of_speech_metrics(self, actual_pos: List[str], predicted_pos: Union[str, List[str]]) -> bool:
        if isinstance(predicted_pos, str):
            predicted_pos = [predicted_pos]
        return any(p in actual_pos for p in predicted_pos)
    
    def calculate_perplexity_transformers(self, sentence, model_name='gpt2'):
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)
        model.eval()

        inputs = tokenizer(sentence, return_tensors='pt')
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            perplexity = torch.exp(loss)
        return perplexity.item()


    def calculate_perplexity(self, meaning, example, word) -> float:
        """Calculate perplexity-like score for example sentences"""
        # Since true perplexity requires a language model, we'll use semantic similarity as a proxy
        meanings = re.split('; |, ', meaning)
        for i in meanings[::-1]:
            result = example.replace(word, i)
        similarity = self.calculate_perplexity_transformers(result)
        # Convert similarity to a perplexity-like score (lower is better for perplexity)
        # Adding small constant to avoid division by zero
        return similarity

    def calculate_meaning_matrix(self, meaning: str, reference_meaning: str, example: str, reference_example: str) -> float:
        """Calculate meaning matrix that reflects minimum semantic correspondence"""
        meaning_similarity = self.calculate_semantic_textual_similarity(
            meaning, reference_meaning)
        example_similarity = self.calculate_semantic_textual_similarity(
            example, reference_example)
        return min(meaning_similarity, example_similarity)

    def validate(self, word: str, meaning: str, part_of_speech: str, example: str) -> Dict[str, Any]:
        """Validate the word definition against ground truth"""
        # Find the matching truth data
        truth = next((t for t in self.truths if t.word == word), None)
        if not truth:
            return {"error": f"Word '{word}' not found in truth data"}

        results = {
            "word": word,
            "word_meaning_metrics": {
                "bertscore": self.calculate_bertscore(meaning, truth.meaning),
                "semantic_textual_similarity": self.calculate_semantic_textual_similarity(meaning, truth.meaning)
            },
            "part_of_speech_metrics": self.calculate_part_of_speech_metrics(truth.part_of_speech, part_of_speech),
            "example_metrics": {
                "perplexity": self.calculate_perplexity(meaning, example, word),
                "meaning_matrix": self.calculate_meaning_matrix(meaning, truth.meaning, example, truth.example)
            }
        }

        return results
