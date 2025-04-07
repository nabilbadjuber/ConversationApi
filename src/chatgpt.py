import openai
import os
import json
import urllib.request
from datetime import datetime

from click import prompt

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
audio_dir = f"{working_dir}/audio"
img_dir = f"{working_dir}/image"
config_dir = f"{working_dir}/config"

config_data = json.load(open(f"{config_dir}/config.json"))
#OPEN_API_KEY = config_data["OPENAI_API_KEY"]
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPEN_API_KEY
conv = []
reference_url = None
role = "cashier"
place = "restaurant"
lang = "german"

def audioToText(audio_path: str):
    input_audio = open(audio_path, "rb")
    text = openai.audio.transcriptions.create(
      model="whisper-1",
      file=input_audio,
      language="de"
    )

    print("Transcribe: " + text.text)

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

    context = ("You are roleplaying as a " + role + " in a " + place + " to help a user practice " + lang + ". The conversation simulates a realistic and friendly interaction."
               "Rules: 1. The dialogue must be no more than 7 turns total (each turn = 1 user + 1 assistant message)."
               "2. Your sentences must be no longer than 30 words."
               "3. Begin with a short greeting."
               "4. End with a polite goodbye if it’s the 7th turn, even if the user hasn’t said goodbye."
               "5. Be friendly and natural, but stay on topic."
               "Scenario context: \“ I am at a " + place + " talking with you as a " + role + ".\”")

    if "start over" in input_text:
        conv.clear()
        textToAudio("The chat has now started over")
    else:
        conv.append({"role": "user", "content": input_text, "isSentByUser": True, "datetime": datetime.now().strftime("%d-%m-%Y %H:%M:%S")})

        # Sending the input text into chatgpt to get output text response
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context },
                *conv
            ]
        )

        assistant_response = response.choices[0].message.content

        conv.append({"role": "assistant", "content": assistant_response, "isSentByUser": False, "datetime": datetime.now().strftime("%d-%m-%Y %H:%M:%S")})

        # Transforming audio into text
        textToAudio(assistant_response)



def scenarioImage(OUTPUT_IMAGE_PATH):

    image_file_path = f"{img_dir}/{OUTPUT_IMAGE_PATH}"
    global reference_url  # So we can read/write it

    keywords = img_prompt_generator("keywords_gn", "")
    print(keywords)
    prompt = img_prompt_generator("img_prompt", keywords)
    print(prompt)


    img_response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )

    urllib.request.urlretrieve(img_response.data[0].url, image_file_path)
    return True

def img_prompt_generator(purpose: str, keywords: str):

    prompt = ""
    if purpose == "img_prompt":
        prompt += "I would like to create a best prompt message to generate image based on your last dialogue: " + conv[len(conv) - 1]["content"] + ". These are the keywords: " + keywords + ". The image should contain me and you as characters. You are a " + role + " in a " + place + ". style would be soft anime style. Please generate result text only. Dont put any additional sentences or symbols."
    else:
        prompt += "I would like to create an image based on your last dialogue on our role-play scenario conversation. I need your help to extract the relevant keywords and nouns out of this dialogue: " + \
                      conv[len(conv) - 1]["content"] + ". Please generate keywords result only. Dont put any additional sentences or symbols."

    gen_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )

    return gen_response.choices[0].message.content

    # prompt = "Can you generate me an image of two persons that the situation could be fit for making conversation based on the last two dialogues? "
    # for i in range(len(conv)):
    #    if i%2 == 0:
    #        prompt += "\nPerson A: " + conv[i]["content"]
    #    else:
    #        prompt += "\nPerson B: " + conv[i]["content"]

    # With interlocutor
    # subject = "man"
    # verb = "listening to"
    # object = "Beamte"
    # place = "Burgeramt"
    # dialog = "Fullen Sie dieses formular aus und unterscreiben Sie hier"

    # Alone
    # subject = "man"
    # verb = "ausfullen"
    # object = "Anmeldeformular"
    # place = "Burgeramt"
    # dialog = ""

    # With interlocutor
    # prompt = "Generate me an image of a " + subject + " " + verb + " " + object + " saying \"" + dialog + "\" in " + place + " office. Image size: 800x800. Image style: watercolor painting"

    # prompt = ("Generate me an image of your response. Your response: " + str(conv[len(conv) - 1]["content"]) +". It will be always conversation of two people. "
    #          "You as an officer is a person who talk on the right of image, and me as a listener on the left. "
    #          "Location is Citizen's Office. Please give an object hint to me in the image to give an idea of what to response you. "
    #          "Image size: 800x800. Image style: fantasy watercolor painting.")



