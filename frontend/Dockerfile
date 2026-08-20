FROM node:22.23-alpine3.23

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

# Copy the sourcecode
COPY . .

# Build the application
RUN pnpm build

# Expose the port and serve the build app
EXPOSE 3000
CMD ["pnpm", "exec", "serve", "-s", "dist", "-l", "3000"]
