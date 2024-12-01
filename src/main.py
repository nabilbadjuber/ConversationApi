import shutil

from fastapi import FastAPI, UploadFile, File
import chatgpt as chat
import os
from fastapi.responses import FileResponse

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
audio_dir = f"{working_dir}/audio"
img_dir = f"{working_dir}/image"

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

@app.post('/llmapihistory')
async def chatHistory():
    # Getting chat history
    return chat.conv

### New API response ###
# Define paths for processed files
OUTPUT_AUDIO_PATH = "output.mp3"
OUTPUT_IMAGE_PATH = "output-img.png"

@app.post("/convreq")
async def process_audio(file: UploadFile = File(...)):
    """
    Process the uploaded audio and return a new audio file and an image.
    """
    try:
        # Save the uploaded audio file to disk
        file_ext = file.filename.split(".").pop()
        file_path = f"{audio_dir}/input.{file_ext}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        chat.conversation(f"{audio_dir}/input.mp3")
        chat.scenarioImage()

        # Return both files
        return {
            "audio_file": f"/download/audio/{OUTPUT_AUDIO_PATH}",
            "image_file": f"/download/image/{OUTPUT_IMAGE_PATH}"
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/download/audio/{filename}")
async def download_audio(filename: str):
    """
    Endpoint to download the processed audio file.
    """
    return FileResponse(path=f"{audio_dir}/{filename}", media_type="audio/mpeg", filename=filename)

@app.get("/download/image/{filename}")
async def download_image(filename: str):
    """
    Endpoint to download the processed image file.
    """
    return FileResponse(path=f"{img_dir}/{filename}", media_type="image/png", filename=filename)
