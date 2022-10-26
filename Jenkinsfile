pipeline {
    agent { label 'docker && linux' }
    options {
        timeout(time: 30, unit: 'MINUTES')
        }
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_CREDS = credentials('DockerHubCredential')
        DOCKER_IMAGE = "${DOCKER_CREDS_USR}/smart-gate"
    }
    stages {
        stage('ARM Pipeline') {
            matrix {
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'linux/arm/v7', 'linux/arm64/v8'
                    }
                }
                stages {
                    stage('Build Image') {
                        steps {
                            echo "Building Image: ${DOCKER_IMAGE} for ${PLATFORM}"
                            sh'''
                            docker build --pull --force-rm --platform "${PLATFORM}" -t "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') .
                            '''
                        }
                    }
                    stage('Lint RPi Code') {
                        steps {
                            echo "PLATFORM=${PLATFORM}"
                            sh'''
                            docker run --rm --platform "${PLATFORM}" -t "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') bash -c 'uname -m && pylint rpi_src/*.py'
                            '''
                        }
                    }
                    stage('Test RPi Code'){
                        steps{
                            echo "PLATFORM=${PLATFORM}"
                            sh'''
                            docker run --rm --platform "${PLATFORM}" -t "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') bash -c 'uname -m && pytest'
                            '''
                        }
                    }
                    stage('Compile Arduino Code') {
                        steps {
                            echo "PLATFORM=${PLATFORM}"
                            sh'''
                            docker run --rm --platform "${PLATFORM}" -t "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') bash -c 'uname -m && bash arduino_src/verify.sh'
                            '''
                        }
                    }
                }
            }
        }
    }
}
