from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import base64
import urllib.parse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/encode-url/")
async def encode_url(request: Request):
    json_data = await request.json()
    url = json_data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is missing.")

    # Base64 encode the URL
    encoded_url = base64.urlsafe_b64encode(url.encode("utf-8")).decode("utf-8")

    # Generate a new endpoint to access it
    response_url = request.url_for("redirect_to_url", encoded_url=encoded_url)

    return {"encoded_url": response_url}


@app.get("/redirect/{encoded_url}")
async def redirect_to_url(encoded_url: str):
    # Decode the base64 URL
    try:
        decoded_url = base64.urlsafe_b64decode(encoded_url.encode("utf-8")).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid URL encoding.")

    # Redirect to the original URL
    return RedirectResponse(url=decoded_url)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)