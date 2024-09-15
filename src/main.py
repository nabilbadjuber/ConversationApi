from fastapi import FastAPI, UploadFile, File
import chatgpt as chat
import os

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
audio_dir = f"{working_dir}/audio"

app = FastAPI()

@app.post('/llmapi')
async def upload(file:UploadFile = File(...)):

    # Read uploaded file and write it into drive
    file_ext = file.filename.split(".").pop()
    file_path = f"{audio_dir}/input.{file_ext}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Getting an output
    return chat.conversation(f"{audio_dir}/input.mp3")
