import os
from dotenv import load_dotenv

def check_env(required: list[str], load_dotenv_file: bool = True) -> list[str]:
    if load_dotenv_file:
        load_dotenv()

    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
    else:
        print("✅ All required environment variables are set.")

    return missing
