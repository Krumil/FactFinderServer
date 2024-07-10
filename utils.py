import json
import base64
import requests

def load_settings():
    with open("settings.json", "r") as f:
        settings = json.load(f)
    return settings


def url_to_base64(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image from URL: {url}")
    image_content = response.content
    base64_image = base64.b64encode(image_content).decode('utf-8')
    mime_type = response.headers.get('Content-Type', 'image/jpeg')  # Default to JPEG if not specified
    return f"data:{mime_type};base64,{base64_image}"