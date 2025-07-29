# ---- Stage 1: Build ----
# Use a Node.js image to build the Vite/React application
FROM node:18-alpine as builder

WORKDIR /app

# Copy package.json and package-lock.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application source code
COPY . .


# Build the application
RUN npm run build

# ---- Stage 2: Serve ----
# Use a lightweight Nginx image to serve the static files
FROM nginx:1.25-alpine

# Copy the built application from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the custom Nginx configuration
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for Nginx
EXPOSE 80

# The default Nginx command will run automatically