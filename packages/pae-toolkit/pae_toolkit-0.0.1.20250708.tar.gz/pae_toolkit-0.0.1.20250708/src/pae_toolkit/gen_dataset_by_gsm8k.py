import json

from rich.progress import track
from transformers import AutoTokenizer


def gen_dataset_by_gsm8k(batch_size: int, input_len: int, dataset_path: str, model_path: str):
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    dataset = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = [json.loads(line)["question"] for line in f]

    # repeat input_len
    dataset_2k = []
    for sentence in dataset:
        words = tokenizer.tokenize(sentence)
        if len(words) == 0:
            continue
        len_num = len(words) // input_len
        if len_num == 0:
            multiplier = (input_len // len(words)) + 1
            repeated_len = words * multiplier
            words = repeated_len[:input_len]
        else:
            words = words[:input_len]
        decoded_text = tokenizer.convert_tokens_to_string(words)
        dataset_2k.append(decoded_text)
    # repeat to batch_size
    batch_num = len(dataset_2k) // batch_size
    if batch_num == 0:
        multiplier = (batch_size // len(dataset_2k)) + 1
        repeated_batch = dataset_2k * multiplier
        dataset_2k = repeated_batch[:batch_size]
    else:
        dataset_2k = dataset_2k[:batch_size]
    with open(f"gsm8k-in{input_len}-bs{batch_size}.jsonl", "w", encoding="utf-8") as f:
        for i in track(range(len(dataset_2k)), description="Gen dataset"):
            f.write(json.dumps({"question": dataset_2k[i], "answer": ""}, ensure_ascii=False))
            f.write("\n")
