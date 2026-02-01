"""Seed Firestore with default configuration."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def seed_defaults():
    """Seed Firestore with defaults from configs/defaults.json."""
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Initialize Firebase
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()

    db = firestore.client()

    # Load defaults
    defaults_path = Path(__file__).parent.parent / "configs" / "defaults.json"
    with open(defaults_path) as f:
        defaults = json.load(f)

    # Seed each config
    for config_name, config_value in defaults.items():
        doc_ref = db.collection("config").document(config_name)

        # Check if already exists
        if doc_ref.get().exists:
            print(f"  Config '{config_name}' already exists, skipping")
            continue

        doc_ref.set(config_value)
        print(f"  Seeded '{config_name}'")

    # Update user config with env vars if present
    user_phone = os.getenv("USER_PHONE_NUMBER")
    user_name = os.getenv("USER_NAME")
    if user_phone or user_name:
        db.collection("config").document("user").update({
            **({"phone": user_phone} if user_phone else {}),
            **({"name": user_name} if user_name else {}),
        })
        print("  Updated user config with env vars")


if __name__ == "__main__":
    print("Seeding Firestore with default configs...")
    seed_defaults()
    print("Done!")
