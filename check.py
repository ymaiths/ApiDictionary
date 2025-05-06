from src.validation import TruthReader, Validation
from main import main
from rich.console import Console
import json
import os
from datetime import datetime
import torch


def tensor_to_native(obj):
    if isinstance(obj, torch.Tensor):
        return obj.item()
    elif isinstance(obj, dict):
        return {key: tensor_to_native(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [tensor_to_native(item) for item in obj]
    return obj


if __name__ == "__main__":
    console = Console()
    print("Processing...")
    with console.status("Processing..."):
        truth_reader = TruthReader("src/truth-demo.csv")

    # print(truth_reader.data)
    validation = Validation(truth_reader.data)

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/validation_results_{timestamp}.json"

    results = []
    for i in truth_reader.data:
        result = main(i.word)
        print(result)
        verdict = validation.validate(
            result.word, result.meaning, result.part_of_speed.value, result.examples)
        print(verdict)

        # Convert tensors to native Python types
        verdict_native = tensor_to_native(verdict)

        # Add to results list
        results.append({
            "word": i.word,
            "result": {
                "word": result.word,
                "meaning": result.meaning,
                "part_of_speech": result.part_of_speed.value,
                "examples": result.examples
            },
            "truth": {
                "word": i.word,
                "meaning": i.meaning,
                "part_of_speech": i.part_of_speech,
                "examples": i.example
            },
            "validation": verdict_native
        })

    # Save results to log file
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Validation results saved to {log_file}")
