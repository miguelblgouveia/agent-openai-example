import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


def search_kb(question: str):
    """Simula uma pesquisa numa base de conhecimento."""
    with open("kb.json", "r", encoding="utf-8") as f:
        return json.load(f)


def call_function(name: str, args: dict):
    if name == "search_kb":
        return search_kb(**args)
    else:
        raise ValueError(f"Função desconhecida: {name}")


class KBResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    source: int = Field(description="The record id of the answer.")


search_kb_declaration = {
    "name": "search_kb",
    "description": "Searches the knowledge base for a specific question.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question to search for.",
            },
        },
        "required": ["question"],
    },
}

load_dotenv()  # Carrega as variáveis do ficheiro .env

model_name = os.getenv("model")
api_key = os.getenv("genai_api_key")

client = genai.Client(api_key=api_key)

tools = types.Tool(function_declarations=[search_kb_declaration])
config = types.GenerateContentConfig(tools=[tools])

# text = "Qual é a previsão do tempo para Lisboa, Portugal hoje? (localização: latitude 32.7607, longitude -16.9595)"
text = """System: Tu és um assistente que responde a perguntas com base numa base de conhecimento sobre a lei do trabalho em Portugal.
        User: Quantos dias de férias tenho direito?"""

# Define user prompt
contents = [types.Content(role="user", parts=[types.Part(text=text)])]

# Send request with function declarations
response = client.models.generate_content(
    model=model_name,
    contents=contents,
    config=config,
)

print("Function call response:")
print(response.candidates[0].content.parts[0].function_call)

# Extract tool call details, it may not be in the first part.
tool_call = response.candidates[0].content.parts[0].function_call

if tool_call.name == "search_kb":
    result = call_function(tool_call.name, tool_call.args)
    print(f"Function execution result: {result}")

    # Create a function response part
    function_response_part = types.Part.from_function_response(
        name=tool_call.name,
        response={"result": result},
    )

    # Append function call and result of the function execution to contents
    contents.append(
        response.candidates[0].content
    )  # Append the content from the model's response.
    contents.append(
        types.Content(role="user", parts=[function_response_part])
    )  # Append the function response

    config2 = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=KBResponse,
    )

    client = genai.Client(api_key=api_key)
    final_response = client.models.generate_content(
        model=model_name,
        config=config2,
        contents=contents,
    )

    print("Final response after function execution:")
    print(final_response.parsed)  # Objeto KBResponse
    print(final_response.parsed.source)  # Acede diretamente aos atributos
    print(final_response.parsed.answer)  # Acede diretamente aos atributos
