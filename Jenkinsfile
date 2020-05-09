pipeline {
    options {
        timeout(time: 30, unit: 'SECONDS')
        } 
    agent any

    stages {
        stage('Build virtualenv') {
            steps {
                sh '''
                virtualenv venv -p python3
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }
        stage('Lint') {
            steps {
                sh '''
                . venv/bin/activate
                pylint src/*.py
                '''
            }
        }
        stage('Test'){
            steps{
                sh'''
                . venv/bin/activate
                pytest
                '''
            }
        }
    }
}
