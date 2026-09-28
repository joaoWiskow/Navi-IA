# To run this code you need to install the following dependencies:
# pip install google-genai

import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key="",
    )

    model = "gemini-3.1-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Olá"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="MINIMAL",
        ),
        audio_transcription_config=types.AudioTranscriptionConfig(
        ),
        tools=tools,
        system_instruction=[
            types.Part.from_text(text="""Você é um revisor de código sênior da DataLakers.
Sua única função é identificar potenciais bugs e problemas de performance em código Python.
Responda sempre em exatamente três tópicos numerados, de forma técnica e direta."""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            print(text, end="")

if __name__ == "__main__":
    generate()


