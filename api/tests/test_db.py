from mockfirestore import MockFirestore # pylint: disable=import-error
from flask import current_app

def test_db_is_mocked(tester):
    db = current_app.extensions['db']
    assert isinstance(db, MockFirestore)