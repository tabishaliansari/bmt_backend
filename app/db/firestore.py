"""Firestore implementation of the Database interface (cloud mode, or the local emulator)."""

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


class FirestoreDatabase:
    def __init__(self, project: str) -> None:
        self.client = firestore.Client(project=project)

    def put(self, collection: str, doc_id: str, data: dict) -> None:
        self.client.collection(collection).document(doc_id).set(data)

    def get(self, collection: str, doc_id: str) -> dict | None:
        snap = self.client.collection(collection).document(doc_id).get()
        return snap.to_dict() if snap.exists else None

    def list(self, collection: str, **equals: str) -> list[dict]:
        query = self.client.collection(collection)
        for field, value in equals.items():
            query = query.where(filter=FieldFilter(field, "==", value))
        return [snap.to_dict() for snap in query.stream()]

    def delete_all(self, collection: str) -> int:
        refs = [snap.reference for snap in self.client.collection(collection).stream()]
        for ref in refs:
            ref.delete()
        return len(refs)
