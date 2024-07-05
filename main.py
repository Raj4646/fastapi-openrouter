from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Define your API key
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.post("/api/completion")
async def completion(request: Request):
    try:
        # Parse the incoming JSON request
        data = await request.json()
        messages = data.get("sendingData")

        if not messages:
            raise HTTPException(status_code=400, detail="Invalid input data")

        # Prepare the payload and headers for the OpenRouter API request
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,  # Optional
            "messages": messages,
            "stream": True,  # Enable streaming
        }

        # Send the request to the OpenRouter API and stream the response
        response = requests.post(
            url, headers=headers, data=json.dumps(payload), stream=True
        )

        if response.status_code != 200:
            error_detail = response.text
            raise HTTPException(status_code=response.status_code, detail=error_detail)

        async def response_generator():
            try:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk.decode("utf-8")
            except requests.exceptions.RequestException as e:
                yield json.dumps({"error": f"Request failed: {str(e)}"})

        return StreamingResponse(response_generator(), media_type="application/json")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
