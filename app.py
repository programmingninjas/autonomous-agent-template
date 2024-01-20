from openai import OpenAI
from serpapi import GoogleSearch
from trafilatura import fetch_url, extract
import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
serp_key = os.getenv("SERP_API_KEY")

client = OpenAI(api_key=openai_key)
messages = [{"role":"system","content":"Take the persona of batman"},{"role":"user","content":"hello who are you?"}]
reply = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
print(reply.choices[0].message.content)