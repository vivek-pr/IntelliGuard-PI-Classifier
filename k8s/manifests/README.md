# Kubernetes Manifests

This directory contains example manifests for common components:

- `nginx-ingress.yaml`: Deploys the NGINX ingress controller using a Helm chart with basic SSL termination configuration.
- `istio-install.yaml`: Installs a minimal Istio control plane with mTLS enabled.
- `network-policies.yaml`: Demonstrates how to restrict pod communication with NetworkPolicies.
- `resource-quotas.yaml`: Sets resource quotas for a namespace.

All files require editing to fit your environment. Replace placeholder values (such as certificate ARNs or secret names) before applying.
