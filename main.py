import cv2
import numpy as np
import base64
from fastapi import FastAPI, Body
from ultralytics import YOLO
from pydantic import BaseModel

app = FastAPI()

yolo_model = YOLO('yolov8n.pt')

class ImageRequest(BaseModel):
    image: str

def decode_base64_image(base64_string: str):

    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "message": "pong",
        "model_loaded": yolo_model is not None
    }

@app.post("/detect-objects")
async def detect_objects(request: ImageRequest):

    img = decode_base64_image(request.image)
    
    if img is None:
        return {"error": "Не удалось декодировать изображение"}

    results = yolo_model(img, conf=0.05, imgsz=1280, verbose=False)
    
    detections = []
    for result in results:
        for box in result.boxes:
            label = yolo_model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            detections.append({
                "object": label, 
                "confidence": round(conf, 2)
            })
            
    return {
        "found": detections,
        "is_safe": not any(d['object'] == 'person' for d in detections)
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)