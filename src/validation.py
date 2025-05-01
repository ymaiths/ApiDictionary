from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from sklearn.metrics import precision_score, recall_score, f1_score
import torch
from transformers import BertTokenizer, BertModel
from bert_score import BERTScorer


class Truth(BaseModel):
    word: str
    part_of_speech: str
    meaning: str
    example: str


class TruthReader:
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.data = self.data.to_dict(orient='records')
        self.data = [Truth(word=row['word'], part_of_speech=row['part_of_speech'],
                           meaning=row['meaning'], example=row['example']) for row in self.data]


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

    def calculate_semantic_textual_similarity(self, text1: str, text2: str) -> float:
        """Calculate Semantic Textual Similarity between two texts"""
        # For simplicity, we'll use the same BERT-based approach but could be extended
        return self.calculate_bertscore(text1, text2)

    def calculate_part_of_speech_metrics(self, actual_pos: str, predicted_pos: str) -> bool:
        """Calculate precision, recall, and F1 score for part of speech"""
        # For part of speech validation, we're checking exact matches
        is_correct = 1 if actual_pos.strip() == predicted_pos.strip() else 0
        return is_correct

    def calculate_perplexity(self, example: str, reference_example: str) -> float:
        """Calculate perplexity-like score for example sentences"""
        # Since true perplexity requires a language model, we'll use semantic similarity as a proxy
        similarity = self.calculate_semantic_textual_similarity(
            example, reference_example)
        # Convert similarity to a perplexity-like score (lower is better for perplexity)
        # Adding small constant to avoid division by zero
        return 1.0 / (similarity + 0.0001)

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
                "perplexity": self.calculate_perplexity(example, truth.example),
                "meaning_matrix": self.calculate_meaning_matrix(meaning, truth.meaning, example, truth.example)
            }
        }

        return results
