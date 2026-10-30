
import json

from src.ai.ollama_client import generate_response


prompt = """
Extract the number of tattoo premises registrations.

Document:
During the financial year 2023, 18 tattoo premises
were registered. Another 64 registrations related
to individual practitioners.

Respond with JSON containing:
- year
- premises_count
- practitioner_count
"""

response = generate_response(prompt)

print("Raw AI response:")
print(response)

data = json.loads(response)

print("\nParsed Python dictionary:")
print(data)
