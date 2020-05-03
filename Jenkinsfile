pipeline {
    agent any

    stages {
        stage('Install packages'){
            steps{
                sh'''
                sudo apt-get update \
                && sudo apt-get install -yq\
                python3-dev\
                python3-pip\
                virtualenv\
                && apt-get clean && rm -rf /var/lib/apt/lists/*
                '''
            }
        }
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
                pylint *.py src/*.py
                '''
            }
        }
    }
}
