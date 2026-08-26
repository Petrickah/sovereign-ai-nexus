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

// "Build & Push: <service>" (added 2026-08-20): one Jenkinsfile, one stage per
// service, each with its own Kaniko context/Dockerfile/image tag — not a
// separate Jenkins job per service. Same practical isolation (backend build
// failing doesn't touch the frontend build result) without re-paying the
// per-job setup cost (branch discovery trait, webhook registration) for a
// single-repo, two-service project. Reuse this shape (one stage per
// `<service>/Dockerfile`) if a third service is added later.

// "Test: backend"/"Test: frontend" (added 2026-08-26, Task 8): run before the
// Kaniko build stages so a broken test fails the pipeline instead of just a
// local run. Both add a sidecar container to the same pod via `yaml:` merged
// with `inheritFrom 'kaniko'` — a plain extra container in the pod, not
// Docker-in-Docker, since Kaniko's whole premise is building without a
// docker daemon and testcontainers-style "spin up a container from inside
// the build" would need one. The backend test Postgres is genuinely
// disposable (no volume) and distinct from `docker-compose.test.yml`, which
// exists for the same purpose locally — same env-var contract
// (DATABASE_HOST=localhost etc.), different orchestration mechanism, so the
// test code itself doesn't care which one it's talking to.
pipeline {
    agent {
        kubernetes {
            inheritFrom 'kaniko'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: postgres-test
      image: postgres:18.6-trixie
      env:
        - name: POSTGRES_USER
          value: test
        - name: POSTGRES_PASSWORD
          value: test
        - name: POSTGRES_DB
          value: test
    - name: python
      image: ghcr.io/astral-sh/uv:0.12.5-python3.14-alpine
      command: ['cat']
      tty: true
    - name: node
      image: node:22-alpine
      command: ['cat']
      tty: true
'''
        }
    }
    environment {
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
        stage('Test: backend') {
            steps {
                container('python') {
                    dir('backend') {
                        sh '''
                        apk add --no-cache postgresql-client >/dev/null
                        until pg_isready -h localhost -p 5432 -U test; do sleep 1; done
                        # The postgres-test sidecar has no docker-entrypoint-initdb.d mount
                        # (that's a docker-compose-only mechanism), so apply the schema by hand.
                        PGPASSWORD=test psql -h localhost -U test -d test -f db/init.sql
                        uv sync --frozen
                        DATABASE_HOST=localhost DATABASE_PORT=5432 DATABASE_USER=test DATABASE_PASSWORD=test DATABASE_NAME=test \
                          uv run pytest -v
                        '''
                    }
                }
            }
        }
        stage('Test: frontend') {
            steps {
                container('node') {
                    dir('frontend') {
                        sh '''
                        corepack enable
                        pnpm install --frozen-lockfile
                        pnpm test
                        '''
                    }
                }
            }
        }
        stage('Build & Push: backend') {
            steps {
                container('kaniko') {
                    sh '''
                    /kaniko/executor                                            \
                      --context="$(pwd)/backend"                               \
                      --dockerfile=Dockerfile                                  \
                      --destination=${REGISTRY}/sovereign-ai-nexus-backend:${BRANCH_NAME}-${BUILD_NUMBER} \
                      --insecure --skip-tls-verify
                    '''
                }
            }
        }
        stage('Build & Push: frontend') {
            steps {
                container('kaniko') {
                    sh '''
                    /kaniko/executor                                            \
                      --context="$(pwd)/frontend"                              \
                      --dockerfile=Dockerfile                                  \
                      --destination=${REGISTRY}/sovereign-ai-nexus-frontend:${BRANCH_NAME}-${BUILD_NUMBER} \
                      --insecure --skip-tls-verify
                    '''
                }
            }
        }
    }
}
