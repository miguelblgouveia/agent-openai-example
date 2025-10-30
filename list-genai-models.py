import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("genai_api_key"))

for m in genai.list_models():
    print(m.name)
