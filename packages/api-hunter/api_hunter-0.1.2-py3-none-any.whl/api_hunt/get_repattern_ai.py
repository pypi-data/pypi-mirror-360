from google.genai import Client
import random
import re
from pydantic import BaseModel
import dotenv
import os
import ast
from dotenv import load_dotenv
from pathlib import Path

class ResponseFormat(BaseModel):
    key_name:str
    pattern:str

env_dir = Path.home() / "api_hunt_envs"
env_dir.mkdir(parents=True,exist_ok=True)


def anonymize_digits(api_key):
    return re.sub(r'\d', lambda _: str(random.randint(0, 9)), api_key)

def set_google_api_key(api_key):

    try:
        dotenv_path = env_dir / ".api_hunt_env"

        if not os.path.exists(dotenv_path):
            open(dotenv_path, 'a').close() 
            print(".env file not found — created new one.")

        dotenv.load_dotenv(dotenv_path)
        if dotenv.set_key(dotenv_path,"GOOGLE_API_KEY",api_key)[0]:
            print("Success loading api key")
            return
        else:
            print("failed to load api key")
            return
    
    except Exception as e:
        print(f"error setting api key error- {e}")


def get_pattern_gemini(name,anon_api_key)->dict:

    try:
        dotenv_path = env_dir / ".api_hunt_env"
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        else:
            print("error getting dotenv path check if gemini api key is configured")
            return

        gemini_api_key = os.getenv("GOOGLE_API_KEY")
        if not gemini_api_key:
            print("error getting gemini api key please check if gemini api key is configured")
            return

        client = Client(api_key=gemini_api_key)

        sys_prompt = f"""
        You are an expert in generating regex patterns that match API keys.
        Given an API key, return a JSON object with:
        if key_name: {name} if given by user then use that else 
        - "key_name": a guessed type or label in underscores (e.g. "bearer","aws", "openai")
        - "pattern": a regex that matches keys of the same kind

        Respond only in JSON.

        """
        response = client.models.generate_content(model="gemini-2.0-flash",
                                                contents=sys_prompt + str(anon_api_key),
                                                config={
                                                    "response_mime_type":"application/json",
                                                    "response_schema":ResponseFormat,
                                                })

        if isinstance(response.text,str):
            response_dict = ast.literal_eval(response.text)
            if response_dict:
                print(f"found pattern {response_dict.get('pattern','')}")
                return {"key_name":response_dict.get('key_name',''),
                        "pattern":response_dict.get('pattern','')}
            else:
                print("error getting pattern try again")
                return
            
    except Exception as e:
        print(f"error getting regex pattern from gemini error -{e}")
