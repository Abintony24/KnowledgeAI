pipeline {
    agent any

    environment {
        DOCKER_IMAGE  = "abintony/knowledgeai"
        GIT_REPO_NAME = "KnowledgeAI"
        GIT_USER_NAME = "Abintony24"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        stage('Checkout') {
            steps {
                sh 'echo "Checkout successful"'
                sh 'ls -la'
            }
        }

        stage('Build and Test') {
            steps {
                sh '''
                    echo "Checking KnowledgeAI project files"

                    test -f Dockerfile
                    test -f backend/requirements.txt
                    test -f k8s/deployment.yaml
                    test -f k8s/service.yaml

                    python3 --version
                    echo "KnowledgeAI application is ready for packaging"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('KnowledgeAI') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=KnowledgeAI \
                            -Dsonar.projectName='KnowledgeAI' \
                            -Dsonar.sources=backend,frontend \
                            -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    sh '''
                        docker build \
                            -t ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                            -t ${DOCKER_IMAGE}:latest .
                    '''

                    def dockerImage = docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}")

                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        'dockerhub-credentials'
                    ) {
                        dockerImage.push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }

        stage('Update Deployment File') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'github-token',
                        variable: 'GITHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        git config user.email "abintony24@gmail.com"
                        git config user.name "${GIT_USER_NAME}"

                        sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" k8s/deployment.yaml

                        git add k8s/deployment.yaml

                        git commit -m "Update KnowledgeAI image tag to ${BUILD_NUMBER} [skip ci]" || echo "No changes to commit"

                        git push https://${GITHUB_TOKEN}@github.com/${GIT_USER_NAME}/${GIT_REPO_NAME}.git HEAD:main
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }

        success {
            echo 'KnowledgeAI image pushed to Docker Hub and deployment YAML updated!'
        }

        failure {
            echo 'Pipeline failed. Check the Jenkins Console Output for the failed stage.'
        }
    }
}
