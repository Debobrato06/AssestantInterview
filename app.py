from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import json
import os
from speech_processor import SpeechProcessor
from chat_gpt import ChatGPTAssistant

app = FastAPI()

# Initialize AI and Speech Processor
processor = SpeechProcessor()
ai = ChatGPTAssistant()

# Serve static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Lock for concurrent websocket writes
ws_lock = asyncio.Lock()

async def safe_send(websocket: WebSocket, data: dict):
    async with ws_lock:
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"Send Error: {e}")

async def process_text_task(websocket: WebSocket, text: str, source: str):
    if not text or len(text.strip()) < 3:
        return

    print(f"Processing ({source}): {text[:50]}...")

    # Send the detected speech to frontend (feedback)
    await safe_send(websocket, {
        "type": "question",
        "content": text,
        "source": source
    })
    
    # Show "Thinking" status
    await safe_send(websocket, {
        "type": "status",
        "content": f"Thinking ({source})..."
    })
    
    # Get answer from AI (offload to thread to keep websocket responsive)
    loop = asyncio.get_event_loop()
    try:
        answer = await loop.run_in_executor(None, ai.get_answer, text, source)
        
        # Check for error in structured response
        if "Error" in answer.get("main_answer", ""):
            await safe_send(websocket, {
                "type": "status",
                "content": f"⚠️ AI Error: {answer.get('main_answer')}"
            })
            # Also send as an AI message so it's visible in chat
            await safe_send(websocket, {
                "type": "answer",
                "content": {
                    "main_answer": f"Bot Error: {answer.get('main_answer')}",
                    "talking_points": ["Check API Key", "Check Credits"],
                    "keywords": ["Error"],
                    "interviewer_question": "Please verify your OpenAI settings."
                }
            })
        else:
            await safe_send(websocket, {
                "type": "answer",
                "content": answer
            })
    except Exception as e:
        print(f"Task Error: {e}")
    
    await safe_send(websocket, {
        "type": "status",
        "content": "Listening..."
    })

@app.get("/")
async def get():
    with open("frontend/index_v2.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Websocket connected")
    
    try:
        while True:
            # 1. Check for incoming messages
            try:
                # Wait for message (either JSON or Binary)
                msg_raw = await asyncio.wait_for(websocket.receive(), timeout=0.05)
                
                if "text" in msg_raw:
                    msg = json.loads(msg_raw["text"])
                    if msg.get("type") == "transcription":
                        frontend_text = msg.get("content")
                        print(f"Frontend Text: {frontend_text}")
                        asyncio.create_task(process_text_task(websocket, frontend_text, "Candidate"))
                
                elif "bytes" in msg_raw:
                    # Received raw audio chunk from interviewer feed (System Audio)
                    audio_data = msg_raw["bytes"]
                    print("Processing System Audio Chunk (Interviewer)...")
                    # Offload transcription to avoid blocking the loop
                    loop = asyncio.get_event_loop()
                    text = await loop.run_in_executor(None, ai.transcribe_audio, audio_data)
                    if text:
                        asyncio.create_task(process_text_task(websocket, text, "Interviewer"))

            except asyncio.TimeoutError:
                pass
            
            # 2. Check for backend-only detection (legacy/fallback)
            backend_text = processor.get_latest_text()
            if backend_text:
                asyncio.create_task(process_text_task(websocket, backend_text, "Interviewer"))

            await asyncio.sleep(0.01) 
            
    except WebSocketDisconnect:
        print("Websocket disconnected")
    except Exception as e:
        print(f"Websocket error: {e}")

@app.post("/toggle-listening")
async def toggle_listening():
    if not processor.is_listening:
        processor.start_listening()
        return {"status": "listening"}
    else:
        processor.stop_listening()
        return {"status": "idle"}

@app.get("/status")
async def get_status():
    return {"is_listening": processor.is_listening}

@app.get("/devices")
async def get_devices():
    return processor.list_devices()

@app.post("/select-device")
async def select_device(request: Request):
    data = await request.json()
    device_index = data.get("index")
    processor.set_device(device_index)
    return {"status": "success", "device_index": device_index}

@app.post("/update-key")
async def update_key(request: Request):
    data = await request.json()
    new_key = data.get("key")
    provider = data.get("provider", "openai")
    if new_key:
        ai.update_key(new_key, provider)
        return {"status": "success", "provider": provider}
    return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
