"""Firestore client for structured data storage."""
import os
from datetime import datetime, timedelta
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreClient:
    """Client for Firestore operations."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not FirestoreClient._initialized:
            self._initialize_firebase()
            FirestoreClient._initialized = True

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use Application Default Credentials
                firebase_admin.initialize_app()

        self.db = firestore.client()

    def log_workout(
        self,
        workout_type: str,
        duration_mins: int,
        exercises: list[dict] | None = None,
        notes: str | None = None,
        raw_input: str | None = None,
    ) -> str:
        """Log a workout to Firestore."""
        doc_ref = self.db.collection("logs").document("workouts").collection("entries").add({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "type": workout_type,
            "duration_mins": duration_mins,
            "exercises": exercises or [],
            "notes": notes,
            "raw_input": raw_input,
        })
        return doc_ref[1].id

    def log_meal(
        self,
        meal_type: str,
        calories: int,
        protein: int,
        carbs: int,
        fat: int,
        description: str,
        raw_input: str | None = None,
    ) -> str:
        """Log a meal to Firestore."""
        doc_ref = self.db.collection("logs").document("nutrition").collection("entries").add({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "meal_type": meal_type,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "description": description,
            "raw_input": raw_input,
        })
        return doc_ref[1].id

    def get_workouts(self, days: int = 7) -> list[dict]:
        """Get workouts from the past N days."""
        cutoff = datetime.now() - timedelta(days=days)
        query = (
            self.db.collection("logs")
            .document("workouts")
            .collection("entries")
            .where("timestamp", ">=", cutoff)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]

    def get_meals(self, days: int = 1) -> list[dict]:
        """Get meals from the past N days."""
        cutoff = datetime.now() - timedelta(days=days)
        query = (
            self.db.collection("logs")
            .document("nutrition")
            .collection("entries")
            .where("timestamp", ">=", cutoff)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]

    def get_last_workout_date(self) -> datetime | None:
        """Get the date of the most recent workout."""
        query = (
            self.db.collection("logs")
            .document("workouts")
            .collection("entries")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(1)
        )
        docs = list(query.stream())
        if docs:
            return docs[0].to_dict().get("timestamp")
        return None
