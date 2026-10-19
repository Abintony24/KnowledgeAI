pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        DOCKER_IMAGE = 'abintony/knowledgeai'
        SONAR_PROJECT_KEY = 'KnowledgeAI'
        GITHUB_REPO = 'https://github.com/Abintony24/KnowledgeAI.git'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh '''
                    echo "Checking project files..."

                    test -f Dockerfile
                    test -f backend/requirements_gui.txt
                    test -f backend/main.py
                    test -f k8s/deployment.yaml
                    test -f k8s/service.yaml

                    python3 --version

                    echo "Project file checks passed."
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
                              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                              -Dsonar.projectName=KnowledgeAI \
                              -Dsonar.sources=backend,frontend \
                              -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                      -t ${DOCKER_IMAGE}:latest \
                      .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        'dockerhub-credentials'
                    ) {
                        sh '''
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker push ${DOCKER_IMAGE}:latest
                        '''
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
                        set -eu

                        git config user.name "abintony24"
                        git config user.email "abintony24@gmail.com"

                        sed -i \
                          "s|image: abintony/knowledgeai:.*|image: abintony/knowledgeai:${BUILD_NUMBER}|" \
                          k8s/deployment.yaml

                        git add k8s/deployment.yaml

                        if git diff --cached --quiet; then
                            echo "No deployment file changes."
                            exit 0
                        fi

                        git commit -m "Update KnowledgeAI image to build ${BUILD_NUMBER}"

                        AUTH=$(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 -w 0)

                        git -c http.extraheader="AUTHORIZATION: basic ${AUTH}" \
                            push "$GITHUB_REPO" HEAD:main

                        unset AUTH
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'KnowledgeAI pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check Console Output for the failed stage.'
        }

        always {
            cleanWs()
        }
    }
}
