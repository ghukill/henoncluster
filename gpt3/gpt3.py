"""

"""

import json

import openai

with open("gpt3/gpt3_config.json", "r") as f:
    config = json.loads(f.read())

openai.api_key = config["secret_key"]

MAX_TOKENS = 128


def submit_prompt(prompt: str, temperature=1, max_tokens=MAX_TOKENS):

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response


def tldr(prompt, max_tokens=MAX_TOKENS) -> str:

    response = submit_prompt(f'"{prompt}"\n\ntl;dr\n', max_tokens=max_tokens)
    summary = response.to_dict()["choices"][0]["text"]
    return summary.strip("\n")
