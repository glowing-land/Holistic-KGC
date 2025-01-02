# System libraries
import sys
import os

import re
from gpt4all import GPT4All
import json
from datetime import datetime
from nltk.tokenize import word_tokenize
# nltk.download('punkt') # For sentence tokenizer

import openai

openai.api_key = "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"


CONTEXT_LIMIT = 8192
PROMPT_LIMIT = 128000
RESPONSE_LIMIT = CONTEXT_LIMIT // 4


from typing import List


def initialise_llm():
    """
    Initialise the LLM model.
    """
    model = None
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
    if prompt_length > PROMPT_LIMIT:
        return None, f"Error: The token length of the prompt is too long (> {PROMPT_LIMIT}).", 'No response'

    log = ""

    # Try three times
    temps = [initial_temp, 0.7, 0.9]
    top_ps = [0.3, 0.4, 0.5]

    for i in range(1):

        responses = []

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            temperature=temps[i],
            top_p=top_ps[i],
            max_completion_tokens=RESPONSE_LIMIT,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        responses.append(response.choices[0].message.content)

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