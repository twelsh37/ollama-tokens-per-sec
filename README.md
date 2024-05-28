# Ollama Check Performance
A method to benchmark throughput via local LLMs hosted on Ollama.
I took inspiration from @Jason TC Chung [ollama-benchmark](https://github.com/aidatatools/ollama-benchmark)
This program was written to enable me to capture throughput statistics for Ollama. The medium article is [here](https://medium.com/@twelsh37/taking-the-pc-and-laptop-for-a-walk-down-the-ollama-highway-1dcb362bfdd8) 
## Installation
1. Create a Poetry environment
2. download the repo into the Poetry environment
3. Run Poetry install
```python
poetry install --no-root
```
4. Enable the Poetry Environment
```python
poetry shell
```
5. Run the program

```
python ollama-check-performance.py 
```
When the program executes it will compare the models in the prompts.csv file to the models you have installed in ollama.
If there is a model missing, the program will exit and inform the user of the missing model.
It is up to the user to install the missing model using the ollama command 'ollama pull <model Name>'

If the program executes it will run a total of 1 iteration and exit unless you specify more runs on the cli.


You can specify more iterations or increase the timeout via the command line if needed.
I had to increase the timeout to 900 seconds to enable the program to execute successfully 10 times on my laptop.

```
usage: ollama-check-performance.py [-h] [-t TIMEOUT] [-r RUN]

Generate Benchmarking statistics from Ollama hosted models

options:
  -h, --help            show this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout period in seconds. Default is 30 seconds
  -r RUN, --run RUN     Number of iterations you want to run. Default is 1
```
Bear in mind that the program will run incredibly slowly on a system without a GPU. The chart below was executed on my desktop and laptop. laptop timings are in orange, desktop in blue.



## Program output
When the program is running, it will post output to the console.
When the program completes, it will write out a csv file to whatever path you have defined in 'CSV_OUTPUT_FILE'

![td2](https://github.com/twelsh37/ollama-tokens-per-sec/assets/4956770/bcaa49f9-febf-4552-ae74-403357ae47ed)

## Language Models and Prompts
The prompt.csv file is what the program uses to run its tests.
it is a simple file with two columns.
Model and Prompt

Currently the following models are defined in the file; 

| Model Name       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mistral:7b       | Mistral 7B is a powerful open-source language model developed by Mistral AI. Mistral is a 7B parameter model distributed with the Apache license. It is available in both instruct (instruction following) and text completion.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| llama3:8b        | A family of models developed by Meta Inc. are new state-of-the-art  available in both 8B and 70B parameter sizes (pre-trained or instruction-tuned).Llama3 instruction-tuned models are fine-tuned and optimized for dialogue/chat use cases and outperform many of the available open-source chat models on common benchmarks.                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| phi3:3.8b        | Phi-3 is a family of open AI models developed by Microsoft.Phi-3 Mini is a 3.8B parameters lightweight state-of-the-art open model trained with the Phi-3 datasets that includes both synthetic data and the filtered publicly available websites data with a focus on high-quality and reasoning dense properties. The model has underwent a post-training process that incorporates both supervised fine-tuning and direct preference optimization to ensure precise instruction adherence and robust safety measures. When assessed against benchmarks testing common sense - language understanding - math - code - long context and logical reasoning Phi-3 Mini-4K-Instruct showcased a robust and state-of-the-art performance among models with less than 13 billion parameters. |
| gemma:2b and 7b  | Gemma is a new open model developed by Google and its DeepMind team. It’s inspired by Gemini models at Google. The models undergo training on a diverse dataset of web documents to expose them to a wide range of linguistic styles - topics - and vocabularies. This includes code to learn syntax and patterns of programming languages as well as mathematical text to grasp logical reasoning. To ensure the safety of the model the team employed various data cleaning and filtering techniques including rigorous filtering for CSAM (child sexual abuse material) sensitive data filtering and filtering based on content quality in compliance with Google’s policies.                                                                                                         |
| gemma:7b         | Gemma 7B was created by Google.it is great at text generation tasks like question answering summarisation and reasoning                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| llava:7b and 13B | LLaVA is a multimodal model that combines a vision encoder and Vicuna for general-purpose visual and language understanding achieving impressive chat capabilities mimicking spirits of the multimodal GPT-4.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

You can easily add or remove models or questions to the prompt.csv file. 
