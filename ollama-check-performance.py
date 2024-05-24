# Description ollama-check-performance.py
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

import time
import pandas as pd
import argparse
import requests
from datetime import datetime


HEADERS = {"Content-Type": "application/json"}
CSV_INPUT_FILE = 'prompts.csv'
CSV_OUTPUT_FILE = 'bench-output.csv'
HOST = 'localhost'
PORT = '11434'
API_URL = f'http://{HOST}:{PORT}/api/generate'

def read_input_csv(input_file):
    """
    Reads data from a CSV file.
    :param input_file: str, path to the input CSV file
    :return: list, file content
    """
    try:
        # Use pandas to read the CSV file
        df = pd.read_csv(input_file)
        # Convert dataframe into a list of dictionaries (each sublist is a row of the CSV)
        # to_dict method with 'records' argument is used to realize it
        data = df.to_dict('records')
        return data
    except Exception as e:
        print(f"Error occurred while reading input CSV: {e}")

def write_output_csv(output_file, data, total_time):
    """
    Writes data to a CSV file.
    :param output_file: str, path to the output CSV file
    :param data: list, data to write into the CSV file
    :param total_time: float, total execution time
    """
    # List column headers, including the new 'program run time (s)' header
    head = ["model", "prompt", "total_duration time (ms)", "load_duration time (ms)",
            "prompt eval time (ms)", "eval_count", "performance (tokens/s)", "program run time (s)"]

    try:
        # Create a pandas DataFrame from the data
        df = pd.DataFrame(data, columns=head[:-1])

        # Add the total_time to the DataFrame as a new row
        total_time_row = pd.DataFrame([['', '', '', '', '', '', '', total_time]], columns=head)
        df = pd.concat([df, total_time_row], ignore_index=True)

        # Write the DataFrame to a CSV file
        df.to_csv(output_file, index=False)

    except Exception as e:
        print(f"Error occurred while writing to bench output: {e}")



def make_request(model, prompt, options, timeout_val=30):
    """
    Make an HTTP request to a specific API.
    :param model: str, model name for HTTP request data
    :param prompt: str, prompt for HTTP request data
    :param options: dict, additional options for controlling request such as num_tokens, temperature, and seed
    :param timeout_val: int, timeout for the HTTP request. Default is 30.
    :return: dict, response from the API
    """
    data = {"model": model, "prompt": prompt, "stream": False, **options}
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

def process_request(row, timeout_val, options):
    """
    Process a row of data from CSV file.
    :param row: dict, a row from CSV file
    :param timeout_val: int, timeout for the HTTP request
    :param options: dict, additional parameters for the request
    :return: list, processed response data
    """
    model = row['Model']
    prompt = row['Prompt']
    jsonResponse = make_request(model, prompt, options, timeout_val)
    if jsonResponse is None:
        return
    return process_response(model, prompt, jsonResponse)

def main(runs=1, timeout_val=30):
    """
    Main function to read CSV, process requests and responses, and write to a CSV file.
    :param runs: int, number of runs
    :param timeout_val: int, timeout for the HTTP request
    """
    options = {
        "num_tokens": 50,
        "temperature": 0.0,
        "seed": 42
    }

    for run in range(runs):
        start_time = time.time()

        prompts = read_input_csv(CSV_INPUT_FILE)
        bench_output_data = [process_request(row, timeout_val, options) for row in prompts]

        current_time = datetime.now()  # Get the current time
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")  # Format the time
        output_file = f"bench-output-{formatted_time}-run-{run + 1}.csv"  # Append formatted time to the output file name

        total_time = round(time.time() - start_time, 2)
        write_output_csv(output_file, bench_output_data, total_time)  # Write data to the file with the new name

        print(f"\n\nTotal execution time for run {run + 1}: {total_time} seconds")


if __name__ == "__main__":
    # Create the command-line arguments parser
    parser = argparse.ArgumentParser(description='Generate Benchmarking statistics from Ollama hosted models')
    parser.add_argument('-t', '--timeout', type=int, required=False, default=30,
                        help='Timeout period in seconds. Default is 30 seconds')
    parser.add_argument('-r', '--run', type=int, required=False, default=1,
                        help='Number of itterations you want to run. Default is 1')

    # Parse command-line arguments
    args = parser.parse_args()

    # Call the main function with the values of the command-line arguments
    main(args.run, args.timeout)
