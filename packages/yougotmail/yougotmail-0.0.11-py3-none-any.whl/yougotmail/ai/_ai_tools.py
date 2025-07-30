from yougotmail.send.send import Send


TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
    }
]


class AI_TOOLS:
    def get_weather(self, location):
        return "Weather retrieved"
