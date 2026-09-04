import json
import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
bucket = os.getenv("SUPABASE_BUCKET")

if not url or not key or not bucket:
    raise Exception("Provide Supabase credentials")

supabase: Client = create_client(url, key)


def get_data(detail: str):
    """Retrieve content defined in data.json

    Args:
        detail (str): The name of the key to extract

    Returns:
        dict[str, object]: The value of the specified key
    """
    if not os.path.exists("data.json"):
        print("Downloading 'data.json'")
        file_bytes = supabase.storage.from_(bucket).download("data.json")
        with open("data.json", "wb") as f:
            f.write(file_bytes)

    with open("data.json", "r") as f:
        data = json.load(f)

        return data[detail]


def get_urls():
    """Retrieve a set of seen url"""
    if not os.path.exists("url.txt"):
        print("Downloading 'url.txt'")
        file_bytes = supabase.storage.from_(bucket).download("url.txt")

        with open("url.txt", "wb") as f:
            f.write(file_bytes)

    with open("url.txt", "r") as f:
        return {line.strip() for line in f}


def save_urls(urls: list[str]):
    """Add new urls to url.txt"""
    with open("url.txt", "a") as f:
        f.writelines(visited_url + "\n" for visited_url in urls)

    with open("url.txt", "rb") as f:
        print("Uploading 'url.txt'")
        supabase.storage.from_(bucket).upload(
            path="url.txt", file=f, file_options={"upsert": "true"}
        )
    os.remove("url.txt")
