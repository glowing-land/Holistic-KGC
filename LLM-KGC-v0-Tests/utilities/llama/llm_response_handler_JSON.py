# System libraries
import sys
import os

import re
from gpt4all import GPT4All
import json
from datetime import datetime
from nltk.tokenize import word_tokenize
# nltk.download('punkt') # For sentence tokenizer

CONTEXT_LIMIT = 8192
PROMPT_LIMIT = 7000
RESPONSE_LIMIT = CONTEXT_LIMIT // 4


from typing import List


def initialise_llm():
    """
    Initialise the LLM model.
    """
    model = GPT4All(
    model_name="Meta-Llama-3-8B-Instruct.Q4_0.gguf",
    device="cuda",
    n_ctx=CONTEXT_LIMIT) # downloads / loads a 4.66GB LLM
    return model


def call_llm_and_return_JSON(model, prompt, check_messages=[], initial_temp=0.2):
    """
    Call the LLM model with the given prompt and return the response as a list.

    args:
    - model: the LLM model
    - prompt: the prompt to be used

    """
    assert isinstance(prompt, str), "Prompt must be a string"
    assert len(prompt.strip()) > 0, "Prompt must not be empty"

    # Check the token length of the prompt
    prompt_length = len(word_tokenize(prompt))
    if prompt_length > CONTEXT_LIMIT / 2:
        return None, f"Error: The token length of the prompt is too long (> {PROMPT_LIMIT}).", "No response"

    log = ""

    # Try three times
    temps = [initial_temp, 0.7, 0.9]
    top_ps = [0.3, 0.4, 0.5]

    for i in range(1):

        responses = []

        # Call the LLM model
        with model.chat_session():
            responses.append(model.generate(prompt, max_tokens=RESPONSE_LIMIT, temp=temps[i], top_p=top_ps[i]))
            for message in check_messages:
                responses.append(model.generate(message, max_tokens=RESPONSE_LIMIT, temp=0.7, top_p=0.4))
        

        response_length = 0
        list_parsed = None

        if responses[-1]:
            response_length = len(word_tokenize(responses[-1]))
            match = re.search(r'{.*}', responses[-1], re.DOTALL)
            if match:
                json_string = match.group(0)
                try:
                    list_parsed = json.loads(json_string)
                except json.JSONDecodeError as e:
                    list_parsed = None
                
        # Generate a log
        log += f"Prompt ({prompt_length}/{PROMPT_LIMIT}):\n" + "-"*40 + '\n' + prompt + "\n" + "-"*40 + '\n\n'
        for response in responses:
            log += f"Response ({response_length}/{RESPONSE_LIMIT}):\n" + "-"*40 + '\n' + str(response) + "\n" + "-"*40 + '\n\n'
        if list_parsed is None:
            log += "Parsed List:\n" + "-"*40 + '\n' + "Parsing Error Detected!" + "\n" + "-"*40 + '\n\n'
        else:
            log += "Parsed List:\n" + "-"*40 + '\n' + str(json.dumps(list_parsed, indent=2)) + "\n" + "-"*40 + '\n\n'

        if list_parsed is not None:
            break
    
    # Return the parsed list and the log
    return list_parsed, log, responses[-1]



if __name__ == "__main__":

    # Tests

    model = initialise_llm()

    prompt = 'List some fruits in JSON format'
    list_parsed, log = call_llm_and_return_JSON(model, prompt)
    print(log)
    print("\n\n\n\n")

    prompt = "List some fruits in JSON format"
    list_parsed, log = call_llm_and_return_JSON(model, prompt)
    print(log)
    print("\n\n\n\n")