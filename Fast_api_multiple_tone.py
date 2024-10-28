from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI with the API key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the base prompts for different tones
prompts = {
    "Casual": "Make the email tone casual and friendly, like a message to a friend. Keep it informal and to the point. ",
    "Professional": "Make the email tone professional and formal. Use appropriate business language and maintain a respectful tone. ",
    "Official": "Make the email tone official and authoritative, suitable for communication from higher authorities to lower authorities. Be direct and commanding. "
}

# Define the input model using Pydantic
class EmailRequest(BaseModel):
    email_content: str
    tone: str

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from https://myenexa.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myenexa.com"],  # Update with the domain you want to allow
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Generate email content based on the prompt from Google Gemini Pro
def generate_gemini_content(email_content, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + email_content)
    return response.text

@app.post("/generate-email")
async def generate_email(request: EmailRequest):
    tone_prompt = prompts.get(request.tone, "")
    if not tone_prompt:
        raise HTTPException(status_code=400, detail="Invalid tone selected")
    
    full_prompt = tone_prompt + "Please provide the email's body for the text given here: "
    email_body = generate_gemini_content(request.email_content, full_prompt)
    
    return {"email_body": email_body}
