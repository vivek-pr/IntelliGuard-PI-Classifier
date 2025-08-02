# IntelliGuard PI Classifier Infrastructure

This repository contains infrastructure configuration samples for running the IntelliGuard PI Classifier on Kubernetes. The provided manifests and Terraform snippets are **not** production ready but illustrate the general approach for setting up common components such as an ingress controller, service mesh, security policies, and resource limits.

```
NOTE: These files are incomplete examples. They are meant as a starting point and require significant customization and testing before use in any environment.
```

## Layout

- `k8s/manifests/` – Sample Kubernetes manifests (ingress controller, Istio, network policies, resource quotas).
- `k8s/terraform/` – Skeleton Terraform configuration for bootstrapping a cluster.

## Usage

1. Review the sample manifests and Terraform files.
2. Adjust values for your environment (domain names, SSL certificates, node counts, etc.).
3. Use `kubectl` and `helm` to deploy resources once a Kubernetes cluster is provisioned.

These examples do **not** satisfy the comprehensive production requirements outlined in the project description. They merely provide a starting framework.

## API Gateway

This repository now includes a minimal FastAPI-based API gateway for the PI classifier.

### Running locally

```bash
pip install -r requirements.txt
python -m app
```

The API will be available at `http://localhost:8000` and the OpenAPI docs at `/docs`.

### Database setup (development)

The sample application uses SQLAlchemy with an async PostgreSQL engine. By default
it stores data in a local SQLite file `app.db`. To use PostgreSQL, set the
`DATABASE_URL` environment variable before running the app:

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/dbname"
python -m app
```

On startup the tables defined in `app/models.py` will be created automatically.

### Running tests

```bash
pytest
```

## PI Classification Engine

The API gateway bundles a lightweight personal information (PI) classifier. It
uses regular expressions for structured entities (email, phone, SSN, credit
card, IP addresses, URLs, dates and generic government IDs) and a tiny
HuggingFace BERT model for free‑form entities like names or locations. The
model is loaded lazily on first use and falls back to the regex detectors if the
model cannot be loaded.

Example usage from Python:

```python
from app.pii_classifier import PIIClassifier

clf = PIIClassifier()
print(clf.classify_text("Email me at user@example.com"))
```

The `/api/v1/classify/text` endpoint accepts a JSON body `{"text": "..."}` and
returns a list of detected entities with confidence scores. Batch processing is
available via `/api/v1/classify/batch`.
