terraform {
  required_version = ">= 1.5"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.25"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig
}

module "cluster" {
  source = "terraform-aws-modules/eks/aws"
  version = "19.10.0"

  cluster_name    = var.cluster_name
  cluster_version = var.k8s_version
  subnet_ids      = var.subnet_ids
  vpc_id          = var.vpc_id

  eks_managed_node_groups = {
    default = {
      desired_capacity = 5
      min_capacity     = 5
      max_capacity     = 10
      instance_types   = ["t3.large"]
    }
  }
}
