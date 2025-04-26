from dotenv import load_dotenv
load_dotenv()

from google.cloud import firestore

class FirestoreDatabase:
    def __init__(self):
        self.db = firestore.Client()

    def add_document(self, collection_name, document_id, data):
        """
        Add a document to a Firestore collection.
        """
        try:
            self.db.collection(collection_name).document(document_id).set(data)
            print(f"Document {document_id} added to {collection_name} collection.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_document(self, collection_name, document_id):
        """
        Retrieve a document from a Firestore collection.
        """
        try:
            doc = self.db.collection(collection_name).document(document_id).get()
            if doc.exists:
                print(f"Document data: {doc.to_dict()}")
                return doc.to_dict()
            else:
                print(f"No document found with ID {document_id}.")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")

    def update_document(self, collection_name, document_id, data):
        """
        Update a document in a Firestore collection.
        """
        try:
            self.db.collection(collection_name).document(document_id).update(data)
            print(f"Document {document_id} updated in {collection_name} collection.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_document(self, collection_name, document_id):
        """
        Delete a document from a Firestore collection.
        """
        try:
            self.db.collection(collection_name).document(document_id).delete()
            print(f"Document {document_id} deleted from {collection_name} collection.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_all_documents(self, collection_name):
        """
        Retrieve all documents from a Firestore collection.
        """
        try:
            docs = self.db.collection(collection_name).stream()
            all_docs = {doc.id: doc.to_dict() for doc in docs}
            print(f"All documents in {collection_name}: {all_docs}")
            return all_docs
        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage:
# db = FirestoreDatabase()
# db.add_document("users", "user1", {"name": "John Doe", "email": "john.doe@example.com"})
# db.get_document("users", "user1")
# db.update_document("users", "user1", {"email": "new.email@example.com"})
# db.delete_document("users", "user1")
# db.get_all_documents("users")