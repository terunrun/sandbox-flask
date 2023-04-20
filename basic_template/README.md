### Cloud Runへのデプロイ
```sh
gcloud run deploy basic-template \
  --platform managed \
  --region=asia-northeast1 --max-instances=1 \
  --memory=256Mi --timeout=60 \
  --service-account="sample-sa@sandbox-terunrun-dev.iam.gserviceaccount.com" \
  --project="sandbox-terunrun-dev" \
  --set-env-vars "PROJECT=sandbox-terunrun-dev"
```

ターミナルで以下のように聞かれたら「y」。
```sh
Deploying from source. To deploy a container use [--image]. See https://cloud.google.com/run/docs/deploying-source-code for more details.
Source code location (/Users/terunrun/git/github/sandbox-flask/basic_template):
```