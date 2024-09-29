from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import base64
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the rate limit exceeded error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/encode-url/")
@limiter.limit("50/minute")
async def encode_url(request: Request):
    json_data = await request.json()
    url = json_data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is missing.")

    encoded_url = base64.urlsafe_b64encode(url.encode("utf-8")).decode("utf-8")
    response_url = request.url_for("redirect_to_url", encoded_url=encoded_url)
    return {"encoded_url": response_url}

@app.get("/redirect/{encoded_url}")
@limiter.limit("200/minute")
async def redirect_to_url(request: Request, encoded_url: str):
    try:
        decoded_url = base64.urlsafe_b64decode(encoded_url.encode("utf-8")).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid URL encoding.")
    return RedirectResponse(url=decoded_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
