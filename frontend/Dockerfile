# Stage 1: Build
FROM node:20-slim AS builder

# Install pnpm
RUN npm install -g pnpm

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
# Note: For production, consider switching to @sveltejs/adapter-node in svelte.config.js
RUN pnpm run build

# Stage 2: Runtime
FROM node:20-slim

WORKDIR /app

# Install pnpm for running
RUN npm install -g pnpm

# Copy the built app and dependencies
COPY --from=builder /app /app

# Expose SvelteKit port (default for preview/node)
EXPOSE 4173

# Command to run (using preview for now as adapter-auto might not output a direct build/index.js without adapter-node)
CMD ["pnpm", "run", "preview", "--host", "0.0.0.0"]
