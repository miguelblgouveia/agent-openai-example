import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests


def get_weather(latitude, longitude):
    """This is a publically available weather API for demonstration purposes."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    )
    data = response.json()
    return data["current_weather"]


# Define a function that the model can call to control smart lights
get_weather_declaration = {
    "name": "get_weather",
    "description": "Gets the current weather for a specific location.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number", "description": "Latitude of the location."},
            "longitude": {
                "type": "number",
                "description": "Longitude of the location.",
            },
        },
        "required": ["latitude", "longitude"],
    },
}

load_dotenv()  # Carrega as variáveis do ficheiro .env

model_name = os.getenv("model")
api_key = os.getenv("genai_api_key")

client = genai.Client(api_key=api_key)

tools = types.Tool(function_declarations=[get_weather_declaration])
config = types.GenerateContentConfig(tools=[tools])

# text = "Qual é a previsão do tempo para Lisboa, Portugal hoje? (localização: latitude 32.7607, longitude -16.9595)"
text = """System: Tu és um assistente que pode chamar funções para obter informações adicionais. Tenta sempre chamar a função apropriada quando necessário.
        Se não tiveres a informação tenta obter-la através do teu conhecimento interno. Deves responder em português de Portugal.
        User: Qual é a previsão do tempo para Madeira, Portugal hoje?"""

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

if tool_call.name == "get_weather":
    result = get_weather(**tool_call.args)
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

    client = genai.Client(api_key=api_key)
    final_response = client.models.generate_content(
        model=model_name,
        config=config,
        contents=contents,
    )

    print("Final response after function execution:")
    print(final_response.text)
