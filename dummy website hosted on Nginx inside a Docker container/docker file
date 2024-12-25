FROM ubuntu:latest

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Set working directory
WORKDIR /var/www/html

# Copy all files from current directory to the working directory
COPY . .

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
