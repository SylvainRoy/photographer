# Deploying to Google Cloud Run

The app is deployed as a container on [Cloud Run](https://cloud.google.com/run),
which scales to zero when idle and stays within the free tier for low traffic.

- **Live URL:** <https://photographer-754179442972.europe-west1.run.app>
- **GCP project:** `photographer-303420` (the same project that hosts the Maps
  JavaScript API)
- **Region:** `europe-west1`
- **Service name:** `photographer`

The `GOOGLE_MAPS_API_KEY` is **not** baked into the image. It is kept in Secret
Manager and read at runtime; the picture is processed in the browser and never
reaches the server.

## Redeploying after code changes

Once the one-time setup below is done, every later deploy is a single command
run from the repository root:

```sh
gcloud run deploy photographer \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --memory 512Mi \
  --set-secrets=GOOGLE_MAPS_API_KEY=google-maps-api-key:latest
```

`--source .` makes Cloud Build build the `Dockerfile` server-side and push the
image to Artifact Registry, then Cloud Run rolls out a new revision. Keep
`--min-instances 0` so the service scales to zero and stays free.

## One-time setup

These steps were already performed for `photographer-303420`; they are recorded
here for reproducing the setup in a fresh project.

### 1. Install and authenticate

```sh
brew install --cask google-cloud-sdk   # macOS
gcloud auth login                       # opens a browser
gcloud config set project photographer-303420
```

### 2. Enable the required APIs

```sh
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 3. Store the Maps API key in Secret Manager

```sh
# Reads the value from the local .env without printing it.
KEY=$(grep -E '^GOOGLE_MAPS_API_KEY=' .env | head -1 | cut -d= -f2-)
printf '%s' "$KEY" | gcloud secrets create google-maps-api-key \
  --data-file=- --replication-policy=automatic
```

Grant the Cloud Run runtime service account read access (replace the project
number if different):

```sh
gcloud secrets add-iam-policy-binding google-maps-api-key \
  --member="serviceAccount:754179442972-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

To rotate the key later, add a new version (the `:latest` reference picks it up
on the next deploy):

```sh
printf '%s' "NEW_KEY" | gcloud secrets versions add google-maps-api-key --data-file=-
```

### 4. Deploy

Run the redeploy command above.

### 5. Restrict the Maps API key to the live domain

The browser key must allow the Cloud Run domain as an HTTP referrer, otherwise
the map tiles are blocked. Keep `localhost` entries for local development.

```sh
KEYNAME=$(gcloud services api-keys list --format="value(name)" --filter="displayName='API key 1'")
gcloud services api-keys update "$KEYNAME" \
  --allowed-referrers="localhost:8000/*,localhost/*,https://photographer-754179442972.europe-west1.run.app/*" \
  --api-target=service=maps-backend.googleapis.com
```

Referrer changes can take a few minutes to propagate.

## Running locally (for comparison)

```sh
podman build -t photographer .
podman run -p 8000:8000 --env-file .env photographer
# open http://localhost:8000
```

The container listens on `$PORT` when set (Cloud Run provides it) and defaults
to `8000` otherwise.

## Notes

- **Cost:** effectively $0 for low traffic. The only recurring charge is the
  image stored in the `cloud-run-source-deploy` Artifact Registry repository
  (a few cents per month).
- **Cold starts:** the first request after an idle period takes a few seconds
  while a new instance starts. This is the tradeoff for scaling to zero; setting
  `--min-instances 1` removes it but leaves an instance always running (no longer
  free).
- **Logs / status:**

  ```sh
  gcloud run services describe photographer --region europe-west1
  gcloud run services logs read photographer --region europe-west1
  ```
