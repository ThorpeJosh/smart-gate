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
        stage('Pre-Build Environment') {
            steps {
                echo "Name: ${env.BRANCH_NAME}"
                echo "Change: ${env.CHANGE_ID}"
                echo "Source branch: ${env.CHANGE_BRANCH}"
                echo "Target branch: ${env.CHANGE_TARGET}"
                echo "Branch is primary: ${env.BRANCH_IS_PRIMARY}"
                echo "Tag name: ${env.TAG_NAME}"
                echo "Tag date: ${env.TAG_DATE}"
                echo "Commit: ${env.GIT_COMMIT}"
                sh 'git status'
                sh 'git show'
                sh 'git log'
                sh 'git fetch --tags'
                sh 'git describe --tags'
            }
        }
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
                            docker build --pull --force-rm --build-arg VERSION=$(git describe --tags) --platform "${PLATFORM}" -t "${DOCKER_IMAGE}":$(echo "${PLATFORM}" | sed 's/\\//_/g') .
                            '''
                        }
                    }
                    stage('Lint RPi Code') {
                        when {
                            environment name: 'PLATFORM', value: 'linux/amd64'
                        }
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
