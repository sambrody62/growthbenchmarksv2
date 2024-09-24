import pytest
import os
import json

from mockfirestore import MockFirestore # pylint: disable=import-error

from fathom.app import create_app

@pytest.fixture()
def tester():
    params = {
        'TESTING': True,
    }
    app = create_app(settings_override=params)
    with app.app_context():
        tester = app.test_client()

        mock_firestore = MockFirestore()
        tester.application.extensions["db"] = mock_firestore

        yield tester

        mock_firestore.reset()

@pytest.fixture()
def fb_response():
    file_path = os.path.join('tests', 'data', 'fb_response.json')
    with open(file_path) as json_file:
        data = json.load(json_file)
        yield data

@pytest.fixture()
def fb_processed():
    file_path = os.path.join('tests', 'data', 'fb_processed.json')
    with open(file_path) as json_file:
        data = json.load(json_file)
        yield data