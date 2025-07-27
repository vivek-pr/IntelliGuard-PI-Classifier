variable "kubeconfig" {
  type        = string
  description = "Path to kubeconfig file"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name"
  default     = "pi-classifier-cluster"
}

variable "k8s_version" {
  type        = string
  description = "Kubernetes version"
  default     = "1.28"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for node groups"
}
