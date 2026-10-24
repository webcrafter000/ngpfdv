# ---- Build stage ---------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies – using npm install because we don't have a lockfile
COPY package.json ./
RUN npm install

# Accept Vite base URL at build time
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy source files and build the app
COPY . .
RUN npm run build

# ---- Runtime stage -------------------------------------------------------
FROM node:20-alpine AS runtime

WORKDIR /app

# Install a tiny static file server (serve) – used only at runtime
RUN npm install -g serve

# Copy the built assets from the builder stage
COPY --from=builder /app/dist ./dist

ENV NODE_ENV=production
EXPOSE 5173

# Serve the static build on the default Vite preview port
CMD ["serve", "-s", "dist", "-l", "5173"]
