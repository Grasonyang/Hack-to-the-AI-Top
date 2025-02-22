from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import json

client = genai.Client(api_key="AIzaSyAmbyz82j6ORj6eto1lNJg30sNTvLi_Eag")
model_id = "gemini-2.0-flash"

google_search_tool = Tool(
    google_search=GoogleSearch()
)

response = client.models.generate_content(
    model=model_id,
    contents="蒐集到台積電的最新消息",
    config=GenerateContentConfig(
        tools=[google_search_tool],
        response_modalities=["TEXT"],
    )
)

# print(response)
for each in response.candidates:
    result_text = []
    result_url = []
    for part in each.content.parts:
        result_text.append(part.text)
        print(f"Text: {part.text}")

    for url in each.grounding_metadata.grounding_chunks:
        result_url.append({
            "title": url.web.title,
            "url": url.web.uri
        })
        print(f"title: {url.web.title}, url: {url.web.uri}")
