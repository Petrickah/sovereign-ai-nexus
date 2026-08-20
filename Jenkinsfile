// Copy this file to code/<project-name>/Jenkinsfile and set IMAGE_NAME below.
// Validated end-to-end against the ci-pilot repo (Gitea push -> webhook -> this
// pipeline -> registry push -> Gitea commit-status notification), 2026-08-17.
// See templates/PROJECT_CI_SETUP.md for how to wire the Jenkins job itself.

pipeline {
    agent { kubernetes { inheritFrom 'kaniko' } }
    environment {
        IMAGE_NAME = 'sovereign-ai-nexus'
        REGISTRY   = '192.168.1.20:5000'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build & Push') {
            steps {
                container('kaniko') {
                    sh '''
                    /kaniko/executor                                            \
                      --context="$(pwd)"                                       \
                      --dockerfile=Dockerfile                                  \
                      --destination=${REGISTRY}/${IMAGE_NAME}:${BRANCH_NAME}-${BUILD_NUMBER} \
                      --insecure --skip-tls-verify
                    '''
                }
            }
        }
    }
}
