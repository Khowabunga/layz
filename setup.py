"""Interactive setup wizard for Layz."""
import json
import os
import sys
from pathlib import Path


def main():
    print("\n Layz - Fitness Accountability Agent Setup\n")

    env_vars = {}

    # Step 1: OpenAI
    print("Step 1/5: OpenAI")
    api_key = input("  Enter your OpenAI API key: ").strip()
    if not api_key.startswith("sk-"):
        print("  Warning: API key doesn't look like an OpenAI key")
    env_vars["OPENAI_API_KEY"] = api_key
    print("  OpenAI configured\n")

    # Step 2: Twilio
    print("Step 2/5: Twilio")
    env_vars["TWILIO_ACCOUNT_SID"] = input("  Enter Account SID: ").strip()
    env_vars["TWILIO_AUTH_TOKEN"] = input("  Enter Auth Token: ").strip()
    env_vars["TWILIO_PHONE_NUMBER"] = input("  Enter your Twilio phone number (e.g., +1234567890): ").strip()
    print("  Twilio configured\n")

    # Step 3: Firebase
    print("Step 3/5: Firebase")
    env_vars["GOOGLE_CLOUD_PROJECT"] = input("  Enter GCP Project ID: ").strip()
    cred_path = input("  Path to service account JSON (or press Enter to use ADC): ").strip()
    if cred_path:
        env_vars["FIREBASE_SERVICE_ACCOUNT"] = cred_path
    print("  Firebase configured\n")

    # Step 4: Mem0
    print("Step 4/5: Mem0")
    mem0_key = input("  Enter Mem0 API key (or press Enter for self-hosted): ").strip()
    if mem0_key:
        env_vars["MEM0_API_KEY"] = mem0_key
    print("  Mem0 configured\n")

    # Step 5: User Info
    print("Step 5/5: Your Info")
    env_vars["USER_PHONE_NUMBER"] = input("  Your phone number (e.g., +1234567890): ").strip()
    env_vars["USER_NAME"] = input("  Your name: ").strip()
    env_vars["USER_TIMEZONE"] = input("  Timezone (default: America/Los_Angeles): ").strip() or "America/Los_Angeles"
    print("  User info configured\n")

    # Write .env file
    env_path = Path(".env")
    with open(env_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print(f"Configuration saved to {env_path}")

    # Seed Firestore
    print("\nSeeding Firestore with default configs...")
    try:
        from scripts.seed_firestore import seed_defaults
        seed_defaults()
        print("Firestore seeded with default configs")
    except Exception as e:
        print(f"Could not seed Firestore: {e}")
        print("   Run 'python scripts/seed_firestore.py' manually after setting up credentials")

    print("\n" + "="*50)
    print("Setup complete!")
    print("\nNext steps:")
    print("  Run locally:     uvicorn src.main:app --reload")
    print("  Run with Docker: docker-compose up")
    print("  Deploy:          ./scripts/deploy.sh")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
