from google import genai

client = genai.Client(api_key="AIzaSyA4Ll9mA-wodm2MZv_8MWDo2NSk8gbBwi4")

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents="Give me best project idea for hackophobia gemini api.Technical/Best Use of API "
)

print(response.text)