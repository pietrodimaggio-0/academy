# ---------------------
# Stage 1: Builder
# ---------------------
FROM node:20 AS builder

WORKDIR /app

# Copy and install dependencies
COPY package*.json ./
RUN npm install --production

# Copy source code
COPY . .

# ---------------------
# Stage 2: Runtime
# ---------------------
FROM node:20-alpine AS runtime

WORKDIR /app

# Copy only what’s needed from the builder stage
COPY --from=builder /app ./

# Expose the application port
EXPOSE 3000

# Run the app
CMD ["npm", "start"]
