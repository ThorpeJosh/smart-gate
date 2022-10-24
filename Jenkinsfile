pipeline {
    agent { dockerfile true }
    options {
        timeout(time: 5, unit: 'MINUTES')
        }
    environment {
        DOCKER_IMAGE = 'thorpejosh/smart-gate'
        PROD_TAG = 'latest'
        DEV_TAG = 'latest-dev'
    }
    stages {
        stage('Build Image') {
            steps {
                echo "built image"
            }
        }
        stage('Lint RPi Code') {
            steps {
                sh "pylint rpi_src/*.py"
            }
        }
        stage('Test RPi Code'){
            steps{
                sh "pytest"
            }
        }
        stage('Compile Arduino Code') {
            steps {
                sh "bash arduino_src/verify.sh"
            }
        }
    }
}
