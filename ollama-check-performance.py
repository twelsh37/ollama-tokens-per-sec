# Description ollama-check-performance.py
#
# This program was created to provide benchmarking statistics for a medium article I am writing.
# it provides a consistent set of instructions to various LLMS which are specified in the first
# column of prompts.csv
#
# This work was inspired by llm_benchmark by Jason TC Chung
# https://github.com/aidatatools/ollama-benchmark
#
#
# The images used in this program are credited to their creators and were retrieved from Unsplash.com.
# All images are credited to their original owners
# sample1 Photo by Adam Thompson on Unsplash
# sample2 Photo by NASA on Unsplash
# sample3 Photo by Jud Mackrill on Unsplash
# sample4 Photo by Aaron Huber on Unsplash
# sample5 Photo by Catrine Rasmussen on Unsplash

import csv
import time
import requests

API_URL = 'http://localhost:11434/api/generate'
HEADERS = {"Content-Type": "application/json"}
CSV_INPUT_FILE = 'prompts.csv'
CSV_OUTPUT_FILE = 'bench-output.csv'


def read_input_csv(input_file):
    """
    Reads a CSV file and returns data.

    :param input_file: str, path to the input CSV file
    :return: list, data from the CSV file as a list of dictionaries
    """
    try:
        with open(input_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
        return data
    except Exception as e:
        print(f"Error occurred while reading static CSV: {e}")
        exit(1)


def write_output_csv(output_file, data):
    """
    Writes data to a CSV file.

    :param output_file: str, path to the output CSV file
    :param data: list, data to write into the CSV file
    """
    head = ["model", "prompt", "total_duration time (ms)", "load_duration time (ms)", "prompt eval time (ms)",
            "eval_count", "performance (tokens/s)"]
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(head)
            writer.writerows(data)
    except Exception as e:
        print(f"Error occurred while writing to bench output: {e}")


def make_request(model, prompt, timeout_val=30):
    """
    Make an HTTP request to a specific API.

    :param model: str, model name for HTTP request data
    :param prompt: str, prompt for HTTP request data
    :param timeout_val: int, timeout for the HTTP request. Default is 30.
    :return: dict, response from the API
    """
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data, timeout=timeout_val)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error occurred: {error}")
        return None
    return response.json()


def process_response(model, prompt, jsonResponse):
    """
    Process a JSON response from an API.

    :param model: str, model name
    :param prompt: str, prompt
    :param jsonResponse: dict, JSON response from the API
    :return: list, processed response data
    """
    get_value_ms = lambda key: round(float(jsonResponse.get(key, 0)) / (10 ** 6), 2)
    total_duration = get_value_ms("total_duration")
    load_duration = get_value_ms("load_duration")
    prompt_eval_duration = get_value_ms("prompt_eval_duration")
    eval_duration = get_value_ms("eval_duration")
    eval_count = jsonResponse.get("eval_count", 0)
    performance = round(eval_count / eval_duration * 1000,
                        2) if eval_duration else "Undefined (No evaluation iterations)"
    print(f"\nModel: {model}\n"
          f"Prompt: {prompt}\n"
          f"Total Duration Time (ms): {total_duration}\n"
          f"Load Duration Time (ms): {load_duration}\n"
          f"Prompt Eval Time (ms): {prompt_eval_duration}\n"
          f"Performance (tokens/s): {performance}\n")
    return [model, prompt, total_duration, load_duration, prompt_eval_duration, eval_count, performance]


def process_request(row, timeout_val):
    """
    Process a row of data from CSV file.

    :param row: dict, a row from CSV file
    :param timeout_val: int, timeout for the HTTP request
    :return: list, processed response data
    """
    model = row['Model']
    prompt = row['Prompt']
    jsonResponse = make_request(model, prompt, timeout_val)
    if jsonResponse is None:
        return
    return process_response(model, prompt, jsonResponse)


def main(timeout_val=30):
    """
    Main function to read CSV, process requests and responses, and write to a CSV file.

    :param timeout_val: int, timeout for the HTTP request
    """
    start_time = time.time()
    prompts = read_input_csv(CSV_INPUT_FILE)
    bench_output_data = [process_request(row, timeout_val) for row in prompts]
    write_output_csv(CSV_OUTPUT_FILE, bench_output_data)
    total_time = round(time.time() - start_time, 2)
    print(f"\n\nTotal execution time: {total_time} seconds")


if __name__ == "__main__":
    main()
