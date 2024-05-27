# Ollama Check Performance
This is a small set of tests that I created to benchmark my laptop and desktop both running Ollama. I took inspiration from @Jason TC Chung ollama-benchmark[https://github.com/aidatatools/ollama-benchmark]

The repo should be downloaded into a python virtual environment and run from there.

```
python ollama-check-performance.py 
```
Will run 1 itteration of the tests. You can specify more on the command line if needed.

```
usage: ollama-check-performance.py [-h] [-t TIMEOUT] [-r RUN]

Generate Benchmarking statistics from Ollama hosted models

options:
  -h, --help            show this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout period in seconds. Default is 30 seconds
  -r RUN, --run RUN     Number of itterations you want to run. Default is 1

```
