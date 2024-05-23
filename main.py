import csv
import time
import pandas as pd
import requests


def process_request(row):
    model = row['Model']
    prompt = row['Prompt']
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post('http://localhost:11434/api/generate', headers=headers, json=data, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error occurred: {error}")
        return None

    jsonResponse = response.json()
    prompt_eval_count = jsonResponse.get("prompt_eval_count", 0)
    prompt_eval_duration = round(float(jsonResponse.get("prompt_eval_duration", 0)) / (10 ** 6), 2)
    total_duration = round(float(jsonResponse.get("total_duration", 0)) / (10 ** 6), 2)
    load_duration = round(float(jsonResponse.get("load_duration", 0)) / (10 ** 6), 2)
    eval_duration = round(float(jsonResponse.get("eval_duration", 0)) / (10 ** 6), 2)
    eval_count = jsonResponse.get("eval_count", 0)

    performance = round(eval_count / eval_duration * 1000,
                        2) if eval_duration else "Undefined (No evaluation iterations)"

    data_row = [model, prompt, total_duration, load_duration,
                prompt_eval_duration, eval_count, performance]

    print(f"\nModel: {model}\n"
          f"Prompt: {prompt}\n"
          f"Total Duration Time (ms): {total_duration}\n"
          f"Load Duration Time (ms): {load_duration}\n"
          f"Prompt Eval Time (ms): {prompt_eval_duration}, Eval Count: {prompt_eval_count}\n"
          f"Performance (tokens/s): {performance}\n")
    return data_row


if __name__ == "__main__":
    start_time = time.time()
    headers = {"Content-Type": "application/json"}

    try:
        prompts = pd.read_csv('prompts.csv')
    except Exception as e:
        print(f"Error occurred while reading static CSV: {e}")
        exit(1)

    head = ["model", "prompt", "total_duration time (ms)", "load_duration time (ms)",
            "prompt eval time (ms)", "eval_count", "performance (tokens/s)"]

    data_rows = [process_request(row) for _, row in prompts.iterrows()]
    try:
        with open('bench-output.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(head)
            writer.writerows(data_rows)
    except Exception as e:
        print(f"Error occurred while writing to output CSV: {e}")

    total_time = round(time.time() - start_time, 2)
    print(f"\n\nTotal execution time: {total_time} seconds")
