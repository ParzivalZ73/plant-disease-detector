pipeline {
    agent any
    environment {
        DOCKERHUB_USER = "jazzy771"
        IMAGE_NAME = "${DOCKERHUB_USER}/plant-disease"
        IMAGE_TAG = "latest"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Prepare Model') {
            steps {
                sh "docker pull jazzy771/plant-disease:latest || true"
                sh "docker create --name temp jazzy771/plant-disease:latest && docker cp temp:/app/model/plant_model.keras model/plant_model.keras && docker rm temp || true"
            }
        }
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh """
                    ssh -o StrictHostKeyChecking=no -i /var/jenkins_home/.ssh/plant-key.pem ubuntu@3.25.164.160 '
                    minikube kubectl -- apply -f /home/ubuntu/k8s/deployment.yaml &&
                    minikube kubectl -- apply -f /home/ubuntu/k8s/service.yaml &&
                    minikube kubectl -- rollout restart deployment/plant-disease-deployment
                    '
                """
            }
        }
    }
    post {
        success {
            echo 'Deployed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
