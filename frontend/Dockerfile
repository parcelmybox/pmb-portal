# Development stage
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --force

# Copy the rest of the application
COPY . .

# Expose port 3000
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV WDS_SOCKET_PORT=0
ENV BROWSER=none

# Start development server with explicit host and port
CMD ["npm", "start", "--host", "0.0.0.0", "--port", "3000"]
