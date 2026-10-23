# KnowledgeAI — Deployment and DevOps

This document describes the deployment architecture and DevOps workflow for KnowledgeAI, a RAG-based document question-answering application.

The deployment workflow incorporates containerization, CI/CD automation, code quality analysis, Kubernetes orchestration, GitOps-based delivery, and application monitoring.

## Technologies Used

| Category                       | Technologies              |
| ------------------------------ | ------------------------- |
| Version Control                | Git, GitHub               |
| Containerization               | Docker                    |
| CI/CD                          | Jenkins                   |
| Code Quality Analysis          | SonarQube                 |
| Container Registry             | Amazon ECR                |
| Container Orchestration        | Kubernetes                |
| Managed Kubernetes             | Amazon EKS                |
| GitOps and Continuous Delivery | Argo CD                   |
| Web Server / Reverse Proxy     | Nginx                     |
| Monitoring and Visualization   | Prometheus, Grafana       |
| Cloud Platform                 | Amazon Web Services (AWS) |

*Document only the tools and integrations actually configured and tested in your project.*

## Deployment Architecture

```text
                     Developer
                         |
                         v
                    GitHub Repo
                         |
                         v
                      Jenkins
                         |
              +----------+----------+
              |                     |
              v                     v
          Build App             SonarQube
              |
              v
         Docker Image
              |
              v
         Amazon ECR
              |
              v
        Amazon EKS Cluster <--------+
              |                      |
              v                      |
        Kubernetes Pods              |
              |                      |
              v                      |
         Application                 |
              |                      |
              v                      |
            Nginx                    |
                                     |
       Argo CD ----------------------+
          ^
          |
          |
    GitHub Repository
    (Kubernetes Manifests)


Monitoring:
Prometheus ---> Collects Metrics
Grafana ------> Visualizes Metrics
```

**Architecture note:** Jenkins and Argo CD have different responsibilities. Jenkins builds and publishes the container image, while Argo CD synchronizes Kubernetes resources from Git to the cluster. The exact integration depends on your pipeline and Argo CD configuration.

## 1. Version Control with Git and GitHub

Git is used to track changes to the application code and deployment configuration. GitHub hosts the repository and provides a central location for source code and Kubernetes manifests.

The repository contains the application source code, Docker configuration, Jenkins pipeline, and Kubernetes deployment files.

Typical workflow:

1. Develop or modify the application.
2. Commit changes using Git.
3. Push changes to GitHub.
4. Trigger the configured CI/CD workflow.
5. Update Kubernetes manifests in Git when deployment configuration changes.

## 2. Containerization with Docker

Docker packages the application and its dependencies into a container image.

Containerization helps maintain a consistent runtime environment across development, testing, and deployment.

The `Dockerfile` defines how the image is built and how the application runs inside the container.

Example commands:

```bash
docker build -t knowledgeai .
docker run -p 8000:8000 knowledgeai
```

These commands assume that the application listens on port 8000 and the Dockerfile is configured accordingly.

## 3. CI/CD Pipeline with Jenkins

Jenkins automates the continuous integration workflow and can coordinate application builds and image publishing.

A typical pipeline contains the following stages:

1. **Source Checkout:** Retrieves the latest source code from GitHub.
2. **Code Quality Analysis:** Runs SonarQube analysis.
3. **Application Build:** Builds or validates the application.
4. **Docker Build:** Creates the application container image.
5. **Image Publishing:** Pushes the image to Amazon ECR.
6. **Deployment Configuration:** Updates the image reference in the deployment manifests or triggers the configured deployment process.

The exact stages depend on the implementation in `Jenkinsfile`.

## 4. Code Quality Analysis with SonarQube

SonarQube analyzes source code to identify potential bugs, code smells, and maintainability issues.

Integrating SonarQube with Jenkins allows code quality analysis to run automatically as part of the CI pipeline.

The analysis results help developers identify code quality problems before releasing an updated application.

## 5. Container Image Storage with Amazon ECR

Amazon Elastic Container Registry (ECR) is a managed container registry that stores Docker images.

In this workflow:

1. Jenkins builds the application image.
2. Jenkins authenticates with Amazon ECR.
3. Jenkins pushes the image to the configured ECR repository.
4. Amazon EKS retrieves the image when Kubernetes needs to start application containers.

Amazon ECR provides centralized storage for the images used by the deployment process.

## 6. Kubernetes and Amazon EKS

Kubernetes manages containerized applications and provides features such as deployment management, service discovery, scaling, and recovery.

Amazon Elastic Kubernetes Service (EKS) is AWS's managed Kubernetes service.

The Kubernetes manifests define the desired state of the application, including resources such as:

* **Deployments:** Define application pods and container images.
* **Services:** Provide stable network access to application pods.
* **ConfigMaps:** Store non-sensitive configuration.
* **Secrets:** Store sensitive configuration when appropriately secured.
* **Ingress resources:** Define HTTP or HTTPS routing when an Ingress controller is configured.

Example commands:

```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get deployments
kubectl get services
```

These commands assume that the `k8s/` directory contains valid manifests and `kubectl` is configured to access the correct EKS cluster.

## 7. GitOps and Continuous Delivery with Argo CD

Argo CD is a GitOps continuous-delivery tool for Kubernetes. It uses a Git repository as the source of truth for the desired application configuration.

In this project architecture, Argo CD manages the synchronization of Kubernetes manifests with the Amazon EKS cluster.

### How Argo CD Works

1. Kubernetes deployment manifests are stored in GitHub.
2. Argo CD monitors the configured repository and application path.
3. When the manifests change, Argo CD detects the difference between the desired configuration and the cluster's current state.
4. Argo CD synchronizes the cluster when automatic synchronization is enabled, or when synchronization is initiated manually.
5. Kubernetes applies the resulting desired state.

### Jenkins vs. Argo CD

| Jenkins                                                            | Argo CD                                                              |
| ------------------------------------------------------------------ | -------------------------------------------------------------------- |
| Automates CI tasks.                                                | Implements GitOps-based delivery to Kubernetes.                      |
| Builds and tests application code.                                 | Monitors Kubernetes manifests stored in Git.                         |
| Runs code quality analysis through integrations such as SonarQube. | Synchronizes the desired application configuration with the cluster. |
| Builds and pushes container images.                                | Applies deployment configuration through Kubernetes.                 |

**Important:** Publishing a new Docker image to Amazon ECR does not automatically mean Argo CD will deploy it. The Kubernetes manifests must reference the intended image, and the configured GitOps workflow must synchronize that change.

## 8. Nginx

Nginx is a web server that can also act as a reverse proxy.

Depending on the application architecture, Nginx can receive HTTP requests and forward them to the appropriate application service.

Its exact role depends on the deployment configuration. For example, Nginx may run inside the cluster or operate as a separate component.

The application must be configured so that traffic reaches the appropriate backend endpoint.

## 9. Monitoring with Prometheus and Grafana

Prometheus and Grafana provide monitoring and visualization capabilities.

### Prometheus

Prometheus collects and stores time-series metrics from configured targets.

Depending on the monitoring setup, these targets may include application instrumentation, infrastructure exporters, or Kubernetes-related metrics endpoints.

### Grafana

Grafana connects to Prometheus and displays collected metrics through dashboards.

Dashboards can help visualize resource usage, application performance, and other metrics exposed by the configured monitoring targets.

### Monitoring Workflow

1. Configure the metrics endpoints or exporters.
2. Configure Prometheus scrape targets.
3. Verify that metrics are being collected.
4. Connect Grafana to Prometheus.
5. Create dashboards to visualize the collected data.
6. Configure alerting if alert rules and notification channels are required.

The available metrics depend on the exporters and instrumentation actually configured in the project.

## 10. Configuration and Secrets Management

KnowledgeAI uses external services such as the Groq API and Amazon S3. These integrations require appropriate configuration and credentials.

Recommended practices include:

* Store API keys and credentials outside source control.
* Use environment variables or an appropriate secrets-management mechanism.
* Apply least-privilege access to AWS resources.
* Avoid committing plaintext credentials in Kubernetes manifests.
* Rotate credentials if they are exposed.
* Ensure the application can access the required S3 bucket and objects.

The application should receive its configuration through the mechanism supported by the actual deployment.

## 11. End-to-End Workflow

The deployment workflow can be summarized as follows:

1. The developer pushes application changes to GitHub.
2. Jenkins retrieves the source code.
3. Jenkins runs the configured build and SonarQube analysis.
4. Jenkins builds the Docker image.
5. Jenkins pushes the image to Amazon ECR.
6. The deployment configuration is updated to reference the intended image.
7. The updated Kubernetes manifests are pushed to GitHub.
8. Argo CD detects and synchronizes the desired configuration with Amazon EKS.
9. Kubernetes runs the application containers.
10. Nginx routes traffic according to its configuration.
11. Prometheus collects metrics from configured targets, and Grafana visualizes them.

The exact workflow may vary depending on whether Jenkins updates the Kubernetes manifests directly, whether image updates are automated separately, and whether Argo CD synchronization is automatic or manual.

## Conclusion

KnowledgeAI combines a RAG-based application with a cloud-native deployment workflow.

Docker packages the application, Jenkins automates CI tasks, SonarQube supports code quality analysis, Amazon ECR stores container images, and Amazon EKS runs the application on Kubernetes. Argo CD provides GitOps-based synchronization, while Prometheus and Grafana support monitoring and visualization.

For the application's RAG architecture, document processing, embeddings, FAISS retrieval, Groq integration, and S3 storage, refer to `README.md`.
