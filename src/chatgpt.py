import openai
import os
import json
from fastapi.responses import FileResponse

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
audio_dir = f"{working_dir}/audio"
config_dir = f"{working_dir}/config"

config_data = json.load(open(f"{config_dir}/config.json"))
OPEN_API_KEY = config_data["OPENAI_API_KEY"]
#openai.api_key = OPEN_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def audioToText(audio_path: str):
    input_audio = open(audio_path, "rb")
    text = openai.audio.transcriptions.create(
      model="whisper-1",
      file=input_audio
    )

    return text.text

def textToAudio(input_text: str):
    speech_file_path = f"{audio_dir}/output.mp3"
    with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=input_text
    ) as response:
        response.stream_to_file(speech_file_path)

    return True

def conversation(audio_path: str):

    # Transforming audio into text
    input_text = audioToText(audio_path)

    # Sending the input text into chatgpt to get output text response
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": input_text}
        ]
    )

    assistant_response = response.choices[0].message.content

    # Transforming audio into text
    textToAudio(assistant_response)

    return FileResponse(f"{audio_dir}/output.mp3")


