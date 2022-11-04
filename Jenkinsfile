pipeline {
    agent { label 'docker && linux' }
    options {
        timeout(time: 60, unit: 'MINUTES')
        }
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_CREDS = credentials('DockerHubCredential')
        DOCKER_IMAGE = "${DOCKER_CREDS_USR}/smart-gate"
    }
    stages {
        stage('ARM & x86 Pipeline') {
            matrix {
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'linux/arm/v7', 'linux/arm64/v8', 'linux/amd64'
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
                            docker run --rm -t --platform "${PLATFORM}" "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') bash -c 'uname -m && pylint rpi_src/*.py'
                            '''
                        }
                    }
                    stage('Test RPi Code'){
                        steps{
                            echo "PLATFORM=${PLATFORM}"
                            sh'''
                            docker run --rm -t --platform "${PLATFORM}" "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') bash -c 'uname -m && pytest'
                            '''
                        }
                    }
                    stage('Compile Arduino Code') {
                        steps {
                            echo "PLATFORM=${PLATFORM}"
                            sh'''
                            docker run --rm -t --platform "${PLATFORM}" "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') bash -c 'uname -m && bash arduino_src/verify.sh'
                            '''
                        }
                    }
                }
            }
        }
        stage('Publish Images') {
            when {
                environment name: 'BRANCH_IS_PRIMARY', value: 'true'
            }
            steps {
                sh'''
                echo $DOCKER_CREDS_PSW | docker login $DOCKER_REGISTRY --username $DOCKER_CREDS_USR --password-stdin
                docker push --all-tags "${DOCKER_IMAGE}"
                docker manifest create "${DOCKER_IMAGE}:${BUILD_NUMBER}" \
                    "${DOCKER_IMAGE}":linux_arm_v7 \
                    "${DOCKER_IMAGE}":linux_arm64_v8 \
                    "${DOCKER_IMAGE}":linux_amd64
                docker manifest inspect "${DOCKER_IMAGE}:${BUILD_NUMBER}"
                docker manifest push --purge "${DOCKER_IMAGE}:${BUILD_NUMBER}"
                docker logout
                '''
            }
        }
    }
    post {
        always {
            cleanWs(cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    notFailBuild: true,
                    patterns: [[pattern: '.gitignore', type: 'INCLUDE'],
                               [pattern: '.propsfile', type: 'EXCLUDE']])
        }
    }
}
