"""

"""

import json
import logging
import os.path
import uuid

import openai

logger = logging.getLogger()
logger.setLevel(logging.INFO)

with open("gpt3/gpt3_config.json", "r") as f:
    config = json.loads(f.read())

openai.api_key = config["secret_key"]

MAX_TOKENS = 128


def submit_prompt(prompt: str, temperature=1, max_tokens=MAX_TOKENS):

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response


def summarize_text(text, max_tokens=MAX_TOKENS) -> str:

    # three main points
    # full_prompt = f'Summarize the following text as three main points, in 20 words or less each:\n\n"{text}"\n'

    # tl/dr
    full_prompt = f'"{text}"\n\ntl;dr in 40 words or less\n'

    prompt_uuid = str(uuid.uuid3(uuid.NAMESPACE_OID, full_prompt))
    filename = f"tmp/{prompt_uuid}.gpt3"

    if os.path.exists(filename):
        logger.info(f"cache hit for prompt: {prompt_uuid}")
        with open(filename, "r") as f:
            return f.read()
    else:
        logger.info(f"cache miss for prompt: {prompt_uuid}")
        response = submit_prompt(full_prompt, max_tokens=max_tokens)
        summary = response.to_dict()["choices"][0]["text"]
        summary = summary.strip("\n")
        with open(filename, "w") as f:
            f.write(summary)
        return summary
