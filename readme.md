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

### Running tests

```bash
pytest
```
