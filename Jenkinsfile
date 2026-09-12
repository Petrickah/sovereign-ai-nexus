// Copy this file to code/<project-name>/Jenkinsfile and set IMAGE_NAME below.
// Validated end-to-end against the ci-pilot repo (Gitea push -> webhook -> this
// pipeline -> registry push -> Gitea commit-status notification), 2026-08-17.
// See templates/PROJECT_CI_SETUP.md for how to wire the Jenkins job itself.
//
// Docker-CI migration (Homelab Redux Valul 1, 2026-09-12): Kaniko/K8s agent
// retired along with the K3s cluster. Jenkins now runs as a Docker container
// on the same host as the registry, with /var/run/docker.sock mounted, so
// image builds go through the host's own Docker daemon directly instead of
// an in-pod Kaniko executor.
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

// "Build & Push: <service>" (added 2026-08-20): one Jenkinsfile, one stage per
// service, each with its own Docker build context/Dockerfile/image tag — not a
// separate Jenkins job per service. Same practical isolation (backend build
// failing doesn't touch the frontend build result) without re-paying the
// per-job setup cost (branch discovery trait, webhook registration) for a
// single-repo, two-service project. Reuse this shape (one stage per
// `<service>/Dockerfile`) if a third service is added later.

// "Test: backend"/"Test: frontend" (updated 2026-09-12, revised same day):
// first attempt reused the repo's own `docker-compose.test.yml`, but that
// broke too — Jenkins itself runs as a container with the host's
// docker.sock passed through (Docker-outside-of-Docker), so a *relative*
// bind-mount path in that compose file resolves against Jenkins' own
// filesystem view (/var/jenkins_home/...), which the host daemon can't see.
// Reverted to a plain disposable `docker run` Postgres (closer to the
// original Kaniko-sidecar shape) — schema applied via `docker exec -i psql`
// (stdin, no bind mount involved, so no path-translation problem). No
// "Docker Pipeline" plugin installed, so no `docker.image().inside()`
// either — plain `docker run`/`docker exec`, same as everywhere else.
// Absolute host paths for the Python/Node containers are constructed via
// $WORKSPACE -> /opt/homelab/jenkins/data translation (see ci-pilot's
// Jenkinsfile comment for the fuller explanation).
pipeline {
    agent { label 'built-in' }
    environment {
        REGISTRY   = '192.168.1.21:5000'
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
        stage('Test: backend') {
            steps {
                sh '''
                docker run -d --name pg-test-${BUILD_NUMBER} \
                  -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=test \
                  -p 127.0.0.1:5433:5432 postgres:18.6-trixie
                until docker exec pg-test-${BUILD_NUMBER} pg_isready -U test -d test >/dev/null 2>&1; do sleep 1; done
                docker exec -i pg-test-${BUILD_NUMBER} psql -U test -d test < backend/db/init.sql

                HOST_WS="/opt/homelab/jenkins/data${WORKSPACE#/var/jenkins_home}"
                docker run --rm --network host -v "$HOST_WS/backend":/workspace -w /workspace \
                  ghcr.io/astral-sh/uv:0.12.5-python3.14-alpine sh -c "
                    uv sync --frozen
                    DATABASE_HOST=localhost DATABASE_PORT=5433 DATABASE_USER=test DATABASE_PASSWORD=test DATABASE_NAME=test uv run pytest -v
                  "
                '''
            }
            post {
                always {
                    sh 'docker rm -f pg-test-${BUILD_NUMBER} || true'
                }
            }
        }
        stage('Test: frontend') {
            steps {
                sh '''
                HOST_WS="/opt/homelab/jenkins/data${WORKSPACE#/var/jenkins_home}"
                docker run --rm -v "$HOST_WS/frontend":/workspace -w /workspace node:22-alpine sh -c "
                  corepack enable
                  pnpm install --frozen-lockfile
                  pnpm test
                "
                '''
            }
        }
        stage('Build & Push: backend') {
            steps {
                script {
                    def tag = "${REGISTRY}/sovereign-ai-nexus-backend:${BRANCH_NAME}-${BUILD_NUMBER}"
                    sh """
                    docker build -t ${tag} backend
                    docker push ${tag}
                    """
                }
            }
        }
        stage('Build & Push: frontend') {
            steps {
                script {
                    def tag = "${REGISTRY}/sovereign-ai-nexus-frontend:${BRANCH_NAME}-${BUILD_NUMBER}"
                    sh """
                    docker build -t ${tag} frontend
                    docker push ${tag}
                    """
                }
            }
        }
    }
}
