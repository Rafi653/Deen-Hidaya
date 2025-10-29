FROM node:20-alpine

WORKDIR /app

# Install wget for healthcheck
RUN apk add --no-cache wget

# Copy package files
# COPY package*.json ./

# # Install dependencies
# RUN npm install
# Copy only manifest first for better layer caching
COPY package.json package-lock.json ./

# Install exact deps per lockfile
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "run", "dev"]
