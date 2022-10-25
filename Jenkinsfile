pipeline {
    agent { label 'docker && linux' }
    options {
        timeout(time: 30, unit: 'MINUTES')
        }
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_CREDS = credentials('DockerHubCredential')
        DOCKER_IMAGE = "${DOCKER_CREDS_USR}/smart-gate"
        PLATFORM = 'linux/arm/v7'
        PLATFORM_TWO = 'linux/arm64/v8'
    }
    stages {
        stage('Build Image') {
            steps {
                echo "Building Image: ${DOCKER_IMAGE}"
                sh'''
                docker build --pull --force-rm --platform "${PLATFORM}" -t "${DOCKER_IMAGE}:tmp" .
                '''
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
