# Description ollama-check-performance.py
# Author twelsh37@gmail.com
# Licence MIT Licence
#
# This program was created to provide benchmarking statistics for a medium article I am writing.
# it provides a consistent set of instructions to various LLMS which are specified in the first
# column of prompts.csv
#
# This work was inspired by llm_benchmark by Jason TC Chung
# https://github.com/aidatatools/ollama-benchmark
#
# The program is hardcoded to run against localhost on port 11434. if you run a different configuration
# then you will need to update the HOST and PORT settings
#
# The images used in this program are credited to their creators and were retrieved from Unsplash.com.
# All images are credited to their original owners
# sample1 Photo by Adam Thompson on Unsplash
# sample2 Photo by NASA on Unsplash
# sample3 Photo by Jud Mackrill on Unsplash
# sample4 Photo by Aaron Huber on Unsplash
# sample5 Photo by Catrine Rasmussen on Unsplash
import argparse
import csv
import subprocess
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional, Union

import pandas as pd
import requests


HEADERS: Dict[str, str] = {"Content-Type": "application/json"}
CSV_INPUT_FILE: str = 'prompts.csv'
CSV_OUTPUT_FILE: str = 'bench-output.csv'
HOST: str = 'localhost'
PORT: str = '11434'
API_URL: str = f'http://{HOST}:{PORT}/api/generate'


def check_models():
    models = []
    with open("prompts.csv", "r") as file:
        reader = csv.DictReader(file)
        models = [row['Model'] for row in reader]  # take model names from each row
    process = subprocess.Popen(["ollama", "list"], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    installed_models = output.decode("utf-8").split()
    for model in models:
        if model not in installed_models:
            print(f"Model {model} is not installed. Please install it and re-run the program.")
            sys.exit(2)  # exit with an error code of 2


def read_input_csv(input_file: str) -> List[Dict[str, Union[str, int, float]]]:
    try:
        df = pd.read_csv(input_file)
        data = df.to_dict('records')
        return data
    except Exception as e:
        print(f"Error occurred while reading input CSV: {e}")


def write_output_csv(output_file: str, data: List[Dict[str, Union[str, int, float]]], total_time: float) -> None:
    head = ["model", "prompt", "total_duration time (ms)", "load_duration time (ms)", "prompt eval time (ms)",
            "eval_count", "eval_duration", "performance (tokens/s)", "program run time (s)"]
    try:
        df = pd.DataFrame(data, columns=head[:-1])
        total_time_row = pd.DataFrame([['', '', '', '', '', '', '', '', total_time]], columns=head)
        df = pd.concat([df, total_time_row], ignore_index=True)
        df.to_csv(output_file, index=False)
    except Exception as e:
        print(f"Error occurred while writing to bench output: {e}")


def make_request(model: str, prompt: str, options: Dict[str, Union[int, float]], timeout_val: int = 30) \
        -> Optional[Dict]:
    data = {"model": model, "prompt": prompt, "stream": False, **options}
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data, timeout=timeout_val)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error occurred: {error}")
        return None
    return response.json()


def process_response(model: str, prompt: str, jsonresponse: Dict) -> List[Union[str, int, float]]:
    get_value_ms = lambda key: round(float(jsonresponse.get(key, 0)) / (10 ** 6), 2)
    total_duration = get_value_ms("total_duration")
    load_duration = get_value_ms("load_duration")
    prompt_eval_duration = get_value_ms("prompt_eval_duration")
    eval_duration = get_value_ms("eval_duration")
    eval_count = jsonresponse.get("eval_count", 0)
    performance = round(eval_count / eval_duration * 1000,
                        2) if eval_duration else "Undefined (No evaluation iterations)"
    print(
        f"\nModel: {model}\n Prompt: {prompt}\n Total Duration Time (ms): {total_duration}\n Load Duration Time (ms):"
        f" {load_duration}\n Prompt Eval Time (ms): {prompt_eval_duration}\n Response Generation Time (ms): "
        f"{eval_duration}\n Performance (tokens/s): {performance}\n")
    return [model, prompt, total_duration, load_duration, prompt_eval_duration, eval_count, eval_duration, performance]


def process_request(row: Dict, timeout_val: int, options: Dict[str, Union[int, float]]) -> List[Union[str, int, float]]:
    model = row['Model']
    prompt = row['Prompt']
    jsonresponse = make_request(model, prompt, options, timeout_val)
    if jsonresponse is None:
        return
    return process_response(model, prompt, jsonresponse)


def main(runs: int = 1, timeout_val: int = 30) -> None:
    options: Dict[str, Union[int, float]] = {
        "num_tokens": 50,
        "temperature": 0.0,
        "seed": 42
    }

    for run in range(runs):
        start_time = time.time()
        prompts = read_input_csv(CSV_INPUT_FILE)
        bench_output_data = [process_request(row, timeout_val, options) for row in prompts]
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")
        output_file = f"bench-output-{formatted_time}-run-{run + 1}.csv"
        total_time = round(time.time() - start_time, 2)
        write_output_csv(output_file, bench_output_data, total_time)
        print(f"\n\nTotal execution time for run {run + 1}: {total_time} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Benchmarking statistics from Ollama hosted models')
    parser.add_argument('-t', '--timeout', type=int, required=False, default=30,
                        help='Timeout period in seconds. Default is 30 seconds')
    parser.add_argument('-r', '--run', type=int, required=False, default=1,
                        help='Number of itterations you want to run. Default is 1')
    args = parser.parse_args()

    check_models()

    main(args.run, args.timeout)
