"""The same client drives every hosted model listed in bagel_api.MODELS."""
from bagel_api import Client, MODELS

client = Client()
for slug, info in MODELS.items():
    print(slug, "->", info["category"], "required:", info["required"])
# pick one explicitly
output = client.run({"prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"}, model="openai/gpt-image-2")
print(output)
