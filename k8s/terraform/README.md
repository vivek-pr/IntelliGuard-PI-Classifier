# Terraform Skeleton

This directory contains a minimal Terraform configuration for provisioning an EKS cluster. It is **incomplete** and intended only as a starting point. You must supply your own backend configuration, AWS credentials, and networking details.

## Usage

```bash
terraform init
terraform apply -var="vpc_id=<vpc-id>" \
  -var="subnet_ids=[\"subnet-1\",\"subnet-2\"]" \
  -var="kubeconfig=$HOME/.kube/config"
```
