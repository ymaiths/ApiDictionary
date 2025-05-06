import json
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report
import glob

def load_results(logs_path_pattern):
    log_files = sorted(glob.glob(logs_path_pattern), reverse=True)
    if not log_files:
        raise FileNotFoundError("No log files found.")
    
    with open(log_files[0], encoding='utf-8') as f:
        results = json.load(f)
    
    return results

def extract_labels(results):
    y_true = []
    y_pred = []

    for entry in results:
        # Actual POS
        true_pos = entry["truth"]["part_of_speech"]
        if isinstance(true_pos, str):
            # Assume string means single label
            true_labels = [true_pos.strip()]
        elif isinstance(true_pos, list):
            true_labels = [pos.strip() for pos in true_pos]
        else:
            continue  # skip if malformed

        # ----- Predicted POS
        # You must record and store predicted POS in the result during validation
        pred_pos = entry["result"].get("part_of_speech", [])
        if isinstance(pred_pos, str):
            pred_labels = [pred_pos.strip()]
        elif isinstance(pred_pos, list):
            pred_labels = [pos.strip() for pos in pred_pos]
        else:
            pred_labels = []

        y_true.append(true_labels)
        y_pred.append(pred_labels)

    return y_true, y_pred

def evaluate_pos_classification(y_true, y_pred):
    mlb = MultiLabelBinarizer()
    y_true_bin = mlb.fit_transform(y_true)
    y_pred_bin = mlb.transform(y_pred)

    print("Evaluation Report (Multi-label POS):")
    print(classification_report(y_true_bin, y_pred_bin, target_names=mlb.classes_))

if __name__ == "__main__":
    # import json
    # from pprint import pprint

    # with open('logs/validation_results_20250506_110029.json', 'r', encoding='utf-8') as json_data:
    #     d = json.load(json_data)
    #     json_data.close()
    #     pprint(d)
    
    # print(d[0]["result"]["examples"])
    results = load_results("logs/validation_results_20250506_133024.json")
    y_true, y_pred = extract_labels(results)
    for i, (true, pred) in enumerate(zip(y_true, y_pred)):
        print(f"[{i}] True: {true} | Pred: {pred}")

    evaluate_pos_classification(y_true, y_pred)
