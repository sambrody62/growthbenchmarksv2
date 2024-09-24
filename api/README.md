# Flask API for Fathom

Running Locally (Windows):

1. `cd api`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Mac: `source ./venv/bin/activate`)
4. `pip install -r requirements.txt`
5. `flask run`
6. `http://127.0.0.1:5000/`

Calling Facebook locally:

1. Get an (access token) and account id [https://developers.facebook.com/tools/explorer/?method=GET&path=me%2Fadaccounts%3Ffields%3Damount_spent%2Cname&version=v12.0] (ladder is 1075908215767703)
2. Call fetch facebook: `/facebook/fetch_metrics?account_id=<account_id>&access_token=<access_token>`

Running Tests locally:

1. `cd api`
2. `venv\Scripts\activate` (Mac: `source ./venv/bin/activate`)
3. `pytest`
4. `pytest -v -s` - This provides print statements and a verbose version of pytest.
5. `pytest tests/test_fb.py::test_init_fb_api -vv -s` runs a specific test

Running tests on Docker:

1. `docker-compose up`
2. `docker-compose exec web pytest fathom`
3. `docker-compose exec web pytest fathom -v -s` - This provides print statements and a verbose version of pytest.
4. `docker-compose exec web pytest --cov-report term-missing --cov fathom`

Running on Docker:

1. `cd api`
2. `docker-compose up --build`
3. `http://localhost:8000/`

Deploy on Cloud Run:

1. `gcloud config set core/project fathom-8cdfe`
2. `gcloud builds submit --tag gcr.io/fathom-8cdfe/api`
3. `gcloud beta run deploy fathom-8cdfe --platform managed --image gcr.io/fathom-8cdfe/api --allow-unauthenticated`
