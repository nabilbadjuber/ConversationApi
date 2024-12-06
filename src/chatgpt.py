import openai
import os
import json
import urllib.request
from datetime import datetime

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
audio_dir = f"{working_dir}/audio"
img_dir = f"{working_dir}/image"
config_dir = f"{working_dir}/config"

config_data = json.load(open(f"{config_dir}/config.json"))
#OPEN_API_KEY = config_data["OPENAI_API_KEY"]
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPEN_API_KEY
conv = []

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

    if "start over" in input_text:
        conv.clear()
        textToAudio("The chat has now started over")
    else:
        conv.append({"role": "user", "content": input_text, "isSentByUser": True, "datetime": datetime.now().strftime("%d-%m-%Y %H:%M:%S")})

        # Sending the input text into chatgpt to get output text response
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "I am a beginner in learning german. I would like to learn german conversation based on role-play. "
                                              "My current german is A1 based according to CEFR Framework. "
                                              "Please do not correct my grammar when you answer me and please do not give me suggestion on your replies."
                                              },
                *conv
            ]
        )

        assistant_response = response.choices[0].message.content

        conv.append({"role": "assistant", "content": assistant_response, "isSentByUser": False, "datetime": datetime.now().strftime("%d-%m-%Y %H:%M:%S")})

        # Transforming audio into text
        textToAudio(assistant_response)

def scenarioImage(OUTPUT_IMAGE_PATH):

    image_file_path = f"{img_dir}/{OUTPUT_IMAGE_PATH}"

    prompt = "Can you generate me an image of two persons that the situation could be fit for making conversation based on the last two dialogues? "

    for i in range(len(conv)):
        if i%2 == 0:
            prompt += "\nPerson A: " + conv[i]["content"]
        else:
            prompt += "\nPerson B: " + conv[i]["content"]

    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    urllib.request.urlretrieve(response.data[0].url, image_file_path)
    return True


