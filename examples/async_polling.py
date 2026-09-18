"""Fire-and-poll: submit without blocking, do other work, then collect the result."""
import time
from bagel_api import Client

client = Client()  # reads SYNEXA_API_KEY
prediction = client.run({"prompt": "Make this a 90s cartoon", "input_image": "https://example.com/input.png"}, wait=False)
print("submitted", prediction["id"], prediction["status"])
while prediction["status"] not in ("succeeded", "failed"):
    time.sleep(2)
    prediction = client.get(prediction["id"])
print(prediction["status"], prediction.get("output"))
