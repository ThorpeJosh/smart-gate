pipeline {
    options {
        timeout(time: 5, unit: 'MINUTES')
        } 
    agent any

    stages {
        stage('Build Environments') {
            parallel {
                stage('Python Environment') {
                    steps {
                        sh '''
                        rm -rf venv
                        virtualenv venv -p python3
                        . venv/bin/activate
                        export READTHEDOCS=True # picamera requirement
                        pip install .[dev]
                        '''
                    }
                }
                stage('Arduino Environment') {
                    steps {
                        sh '''
                        bash arduino_src/install_and_configure_arduino-cli.sh
                        '''
                    }
                }
            }
        }
        stage('Lint RPi Code') {
            steps {
                sh '''
                . venv/bin/activate
                pylint rpi_src/*.py
                '''
            }
        }
        stage('Test RPi Code'){
            steps{
                sh'''
                rm ~/.config/smart-gate/conf.ini
                . venv/bin/activate
                tox
                '''
            }
        }
        stage('Compile Arduino Code') {
            steps {
                sh '''
                bash arduino_src/verify.sh
                '''
            }
        }
    }
}
