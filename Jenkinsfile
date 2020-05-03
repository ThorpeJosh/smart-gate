pipeline {
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
                pylint *.py src/*.py
                '''
            }
        }
    }
}
