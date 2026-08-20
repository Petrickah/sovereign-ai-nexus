// Copy this file to code/<project-name>/Jenkinsfile and set IMAGE_NAME below.
// Validated end-to-end against the ci-pilot repo (Gitea push -> webhook -> this
// pipeline -> registry push -> Gitea commit-status notification), 2026-08-17.
// See templates/PROJECT_CI_SETUP.md for how to wire the Jenkins job itself.
//
// "Mirror to GitHub" (added 2026-08-20, sovereign-ai-nexus): Gitea's native Push
// Mirror only supports http(s)/git:// remotes (confirmed from Gitea source,
// modules/git/remote.go — ssh:// is rejected with "Invalid mirror protocol"),
// so for a project that wants SSH-key-based mirroring (one deploy key, scoped
// per-repo via GitHub Deploy Keys, not a PAT per repo) the push has to happen
// from Jenkins instead. Runs right after checkout, before the Docker build, so
// mirroring never depends on the build succeeding. Credential
// "github-mirror-<project-name>" is an SSH private key (ssh-credentials plugin),
// its public half registered as a write-access GitHub Deploy Key on that repo
// only — reuse this pattern for future projects that want the same mirror setup.

pipeline {
    agent { kubernetes { inheritFrom 'kaniko' } }
    environment {
        IMAGE_NAME = 'sovereign-ai-nexus'
        REGISTRY   = '192.168.1.20:5000'
        GITHUB_MIRROR_URL = 'git@github.com:Petrickah/sovereign-ai-nexus.git'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Mirror to GitHub') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'github-mirror-sovereign-ai-nexus', keyFileVariable: 'SSH_KEY')]) {
                    sh '''
                    export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null"
                    git push "${GITHUB_MIRROR_URL}" "HEAD:refs/heads/${BRANCH_NAME}"
                    '''
                }
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
