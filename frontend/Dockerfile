# Stage 1: Build
FROM node:20-slim AS builder

# Install pnpm
RUN npm install -g pnpm

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies (allow lockfile updates for new packages)
RUN pnpm install --no-frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN pnpm run build

# Stage 2: Runtime
FROM node:20-slim

WORKDIR /app

# Copy only the built output (adapter-node bundles everything)
COPY --from=builder /app/build ./build

# Expose SvelteKit adapter-node default port
EXPOSE 3000

# Set default port and host for adapter-node
ENV PORT=3000
ENV HOST=0.0.0.0

CMD ["node", "build"]
