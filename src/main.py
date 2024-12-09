
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
import chatgpt as chat
import os
from fastapi.responses import FileResponse
from typing import List


# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: List[List[str]]):
        for connection in self.active_connections:
            await connection.send_json(message)

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
audio_dir = f"{working_dir}/audio"
img_dir = f"{working_dir}/image"

app = FastAPI()


### Old API response ###

#@app.post('/llmapi')
#async def upload(file:UploadFile = File(...)):
#
#    # Read uploaded file and write it into drive
#    file_ext = file.filename.split(".").pop()
#    file_path = f"{audio_dir}/input.{file_ext}"
#    with open(file_path, "wb") as f:
#        content = await file.read()
#        f.write(content)
#
#    # Getting an output
#    return chat.conversation(f"{audio_dir}/input.mp3")#
#
#@app.post('/llmapihistory')
#async def chatHistory():
#    # Getting chat history
#    return chat.conv

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
        chat.scenarioImage(OUTPUT_IMAGE_PATH)

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

manager = ConnectionManager()

@app.websocket("/convhist")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for a message from the client
            #data = await websocket.receive_text()
            #print(f"Received message from client: {data}")

            # Prepare the multidimensional array to send
            response_data = chat.conv

            # Broadcast the response to all connected clients
            await manager.broadcast(response_data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

@app.get("/vocabulary/")
async def get_vocabulary():
    vocabulary = [
        {
            "word": "helfen",
            "meaning": "to help",
            "status": "Learning",
            "n_learn": 10,
            "is_repeated": True
        },
        {
            "word": "kaufen",
            "meaning": "to buy",
            "status": "Skipped",
            "n_learn": 0,
            "is_repeated": False
        }
    ]
    return vocabulary

@app.get("/scenarios/")
async def get_scenarios():

    vocabulary = [
        {"id": 1, "title": "Introduction to Spanish", "image_url": "https://www.psdstamps.com/wp-content/uploads/2022/04/test-stamp-png-768x512.png"},
        {"id": 2, "title": "Ordering Food in German", "image_url": "https://www.psdstamps.com/wp-content/uploads/2022/04/test-stamp-png-768x512.png"},
    ]
    return vocabulary