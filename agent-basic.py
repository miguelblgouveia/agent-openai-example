import os
from dotenv import load_dotenv
import google.generativeai as genai
# from openai import OpenAI

load_dotenv()  # Carrega as variáveis do ficheiro .env

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# completion = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {"role": "system", "content": "Tu és um prestável e simpático assistente."},
#         {"role": "user", "content": "Qual é a capital da França?"},
#     ],
# )

text = """System: Tu és um prestável e simpático assistente. 
          User: Podes escrever um pequeno resumo sobre a linguagem de programação python?
          Assistant:
"""

genai.configure(api_key=os.getenv("genai_api_key"))

model_name = os.getenv("model")

print("Usando o modelo:", model_name)

model = genai.GenerativeModel(model_name=model_name)

response = model.generate_content(text)

print("Resposta do Assistente:", response.text)
