gcloud config set core/project fathom-8cdfe
gcloud builds submit --tag gcr.io/fathom-8cdfe/api
gcloud beta run deploy fathom-8cdfe --platform managed --image gcr.io/fathom-8cdfe/api --allow-unauthenticated