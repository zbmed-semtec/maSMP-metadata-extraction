# Use Node.js 20 Alpine for Nuxt.js 3 compatibility
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies for native modules
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for development)
RUN npm ci

# Copy the rest of the application
COPY . .

# Run postinstall to prepare Nuxt.js
RUN npm run postinstall

# Create a non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nuxt -u 1001

# Change ownership of the app directory
RUN chown -R nuxt:nodejs /app
USER nuxt

# Expose port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
