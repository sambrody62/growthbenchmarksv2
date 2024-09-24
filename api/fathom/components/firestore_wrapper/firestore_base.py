from .errors import PlatformNotDefined
from flask import current_app

class FireStoreWrapper():
    """FireStore wrapper."""

    def __init__(self, client=None, platform_prefix:str=None):
        self.client = client
        # Adding in fault tolerance for initialised firestore wrappers:
        if self.client is None:
            self.db = current_app.extensions["db"]

        # Set the platform prefix:
        self.platform_prefix = platform_prefix

    def get_document_data(self, doc_ref):
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return data
        else:
            return "Failed to retrieve the document"

    # Default CRUD Operations:
    def create(self, collection: str, document: str, data: dict):
        doc_ref = self.client.collection(u'{}'.format(collection)).document(u'{}'.format(document))
        doc_ref.set(data)

    def read_single_document(self, collection: str, document: str):
        doc_ref = self.client.collection(u'{}'.format(collection)).document(u'{}'.format(document))
        return doc_ref.get().to_dict()

    def delete_single_collection_document(self, collection: str, document: str):
        doc_ref = self.client.collection(u'{}'.format(collection)).document(u'{}'.format(document))
        return doc_ref.delete()

    def update_single_collection_document(self, collection: str, document: str, data: dict):
        doc_ref = self.client.collection(u'{}'.format(collection)).document(u'{}'.format(document))
        return doc_ref.update(data)

    # Custom CRUD Operations:
    def get_account_list(self, account_ids_platform:str) -> list:
        # Get all of the users in the database:
        posts_ref = self.db.collection(u'users')
        results = posts_ref.stream()

        # Scan over all of the accounts:
        accounts = list()
        for doc in results:
            user = doc.to_dict()
            account_ids = user.get(account_ids_platform)
            refresh_token = user.get(f'{self.platform_prefix}_refresh_token', "")
            access_token = user.get(f'{self.platform_prefix}_access_token', "")

            # Only include accounts that have account ids and either a refresh_token or access_token:
            if account_ids and (refresh_token != "" or access_token != ""):
                user_accounts = dict()
                user_accounts['refresh_token'] = refresh_token
                user_accounts['access_token'] = access_token
                user_accounts['account_ids'] = account_ids
                accounts.append(user_accounts)
                
        return accounts

    def read_account_document(self, account_id:str) -> dict:
        """Reads a unique FireStore account document.

        Args:
            account_id (str): The id of the fb/google account etc.
            platform (str): This platform is defined within the config.py under each conntectors as PREFIX.

        Returns:
            dict: Returns the account FireStore document.
        """        
        accounts_collection = self.db.collection(u'Accounts')
        account_ref = accounts_collection.where(u'account_id', u'==', account_id)
        doc = list(account_ref.stream())[0]

        if doc and self.platform_prefix in doc.id:
            return doc.to_dict()
        else:
            return None
