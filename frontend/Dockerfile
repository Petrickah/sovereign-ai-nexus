FROM node:22.23-alpine3.23

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

# Copy the sourcecode
COPY . .

# Backend origin baked into the static build — Vite inlines VITE_* env vars
# at build time, and there's no dev-proxy equivalent once this is served as
# a static bundle (`serve -s dist`), so the built JS needs the backend's
# real origin to call directly (see CLAUDE.md's Task 6 CORS/proxy gap).
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the application
RUN pnpm build

# Expose the port and serve the build app
EXPOSE 3000
CMD ["pnpm", "exec", "serve", "-s", "dist", "-l", "3000"]
