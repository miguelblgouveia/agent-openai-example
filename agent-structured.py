import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()  # Carrega as variáveis do ficheiro .env

model_name = os.getenv("model")
api_key = os.getenv("genai_api_key")

client = genai.Client(api_key=api_key)


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


text = """System: Tu és um prestável e simpático assistente. Podes obter o evento de calendário para o utilizador.
          User: O João e a Maria têm uma reunião no dia 25 de dezembro de 2024 para discutir o projeto de implementação da nova funcionalidade para a aplicação móvel. 
          A reunião começará às 10h00 e terminará às 11h30. Participarão também o Pedro e a Ana.
          Assistant:
"""

response = client.models.generate_content(
    model=model_name,
    contents=text,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=CalendarEvent,
    ),
)

# A resposta já vem validada e convertida em instância de CalendarEvent
print(response.parsed)  # Objeto CalendarEvent
print(response.parsed.name)  # Acede diretamente aos atributos
print(response.text)  # JSON original, se quiseres ver
