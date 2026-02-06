import google.generativeai as genai
import os
import streamlit as st
import toml

# Try to load secrets from .streamlit/secrets.toml
try:
    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        secrets = toml.load(secrets_path)
        api_key = secrets.get("GEMINI_KEY")
    else:
        print("secrets.toml not found")
        api_key = None
except Exception as e:
    print(f"Error loading secrets: {e}")
    api_key = None

if not api_key:
    # Fallback to env var if needed, or ask user (but we can't in script)
    api_key = os.environ.get("GEMINI_KEY")

if not api_key:
    print("CRITICAL: GEMINI_KEY not found in secrets.toml or environment variables.")
    exit(1)

print(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")

try:
    genai.configure(api_key=api_key)
    print("Listing available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
