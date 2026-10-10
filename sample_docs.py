"""
Sample documents for the RAG demo.
Later, you'll replace this with real PDF loading (docker.pdf, kubernetes.pdf, etc.)
For now, this lets you test the full RAG pipeline without needing any files.
"""

SAMPLE_DOCUMENTS = [
    """Docker is a platform used to develop, ship, and run applications inside
    containers. A container packages an application together with everything
    it needs to run: code, runtime, system tools, and libraries. This means
    the application runs the same way on any machine, whether it's a
    developer's laptop or a production server.""",

    """Docker images are read-only templates used to create containers. An
    image includes the application code, a runtime, libraries, environment
    variables, and configuration files. You can build your own image using a
    Dockerfile, or pull a pre-built image from Docker Hub.""",

    """Kubernetes, often abbreviated as K8s, is a container orchestration
    platform. It automates the deployment, scaling, and management of
    containerized applications. Kubernetes groups containers into logical
    units called Pods, and manages how those Pods run across a cluster of
    machines.""",

    """A Kubernetes cluster consists of a control plane and worker nodes. The
    control plane makes global decisions about the cluster, such as
    scheduling Pods. Worker nodes run the actual application workloads
    inside Pods, managed by an agent called the kubelet.""",

    """Jenkins is an open-source automation server used to build CI/CD
    pipelines. CI stands for Continuous Integration, and CD stands for
    Continuous Delivery or Continuous Deployment. Jenkins can automatically
    build, test, and deploy code every time a developer pushes changes to a
    repository like GitHub.""",

    """A typical Jenkins pipeline is defined in a Jenkinsfile. It usually
    contains stages such as Build, Test, and Deploy. Each stage runs a set
    of steps, such as compiling code, running unit tests, building a Docker
    image, or pushing that image to a registry like AWS ECR.""",

    """AWS ECR, or Elastic Container Registry, is a managed Docker container
    registry from Amazon Web Services. It lets teams store, manage, and
    deploy Docker container images. Images pushed to ECR can then be pulled
    by services like AWS EKS to run in production.""",

    """AWS EKS, or Elastic Kubernetes Service, is a managed Kubernetes
    service from Amazon Web Services. It handles the operational burden of
    running a Kubernetes control plane, so teams can focus on deploying and
    scaling their own applications rather than managing Kubernetes
    infrastructure themselves.""",
]
