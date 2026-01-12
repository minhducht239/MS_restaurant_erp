#!/bin/bash

# DEPLOYMENT SCRIPT FOR DIGITALOCEAN DROPLET
# Tự động setup environment và deploy microservices

set -e

echo "🚀 Restaurant ERP Microservices Deployment Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Please don't run this script as root"
   exit 1
fi

# Check if domain is provided
if [[ $# -eq 0 ]]; then
    print_error "Usage: $0 <your-domain.com>"
    print_info "Example: $0 restaurant.yourdomain.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

print_info "Domain: $DOMAIN"
print_info "Email: $EMAIL"

# Step 1: Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install Docker and Docker Compose
print_status "Installing Docker and Docker Compose..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install -y docker-compose

# Step 3: Install Nginx and Certbot
print_status "Installing Nginx and SSL certificates..."
sudo apt install -y nginx certbot python3-certbot-nginx

# Step 4: Clone repository
print_status "Cloning repository..."
if [[ ! -d "MS_restaurant_erp" ]]; then
    git clone https://github.com/minhducht239/MS_restaurant_erp.git
fi
cd MS_restaurant_erp/restaurant-microservices

# Step 5: Setup environment file
print_status "Creating environment file..."
cp env-droplet.example .env
sed -i "s/yourdomain.com/$DOMAIN/g" .env
sed -i "s/your-email@example.com/$EMAIL/g" .env

# Generate random secret key
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(50))')
sed -i "s/your-very-secure-django-secret-key-here/$SECRET_KEY/g" .env

# Generate random MySQL password
MYSQL_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
sed -i "s/your-mysql-password/$MYSQL_PASSWORD/g" .env

print_status "Environment file created with random secrets"

# Step 6: Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Frontend (React build)
    location / {
        root /var/www/restaurant-frontend;
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # API Routes
    location /api/auth/ {
        proxy_pass http://localhost:8001/api/auth/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/menu/ {
        proxy_pass http://localhost:8002/api/menu/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/billing/ {
        proxy_pass http://localhost:8003/api/billing/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/customers/ {
        proxy_pass http://localhost:8004/api/customers/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/tables/ {
        proxy_pass http://localhost:8005/api/tables/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/staff/ {
        proxy_pass http://localhost:8006/api/staff/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/reservations/ {
        proxy_pass http://localhost:8007/api/reservations/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/dashboard/ {
        proxy_pass http://localhost:8008/api/dashboard/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/restaurant-static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/restaurant-media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Step 7: Start services
print_status "Starting Docker services..."
docker-compose down
docker-compose up --build -d

print_status "Waiting for services to start..."
sleep 30

# Step 8: Setup SSL
print_status "Setting up SSL certificate..."
sudo systemctl reload nginx
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL

# Step 9: Build and deploy frontend
print_status "Building and deploying frontend..."
cd ../../MS_restaurant_erp_FE

# Create production environment file for React
cat > .env.production <<EOF
REACT_APP_AUTH_API_URL=https://$DOMAIN/api/auth
REACT_APP_MENU_API_URL=https://$DOMAIN/api/menu
REACT_APP_BILLING_API_URL=https://$DOMAIN/api/billing
REACT_APP_CUSTOMER_API_URL=https://$DOMAIN/api/customers
REACT_APP_TABLES_API_URL=https://$DOMAIN/api/tables
REACT_APP_STAFF_API_URL=https://$DOMAIN/api/staff
REACT_APP_RESERVATION_API_URL=https://$DOMAIN/api/reservations
REACT_APP_DASHBOARD_API_URL=https://$DOMAIN/api/dashboard
EOF

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

npm install
npm run build

# Deploy frontend
sudo mkdir -p /var/www/restaurant-frontend
sudo cp -r build/* /var/www/restaurant-frontend/
sudo chown -R www-data:www-data /var/www/restaurant-frontend

# Step 10: Final checks
print_status "Running final checks..."
cd ../restaurant-microservices

# Check if all containers are running
if [[ $(docker-compose ps -q | wc -l) -eq 0 ]]; then
    print_error "No containers are running!"
    exit 1
fi

# Test API endpoints
print_status "Testing API endpoints..."
if curl -f -s https://$DOMAIN/api/auth/health/ > /dev/null; then
    print_status "Auth service is responding"
else
    print_warning "Auth service is not responding"
fi

print_status "Deployment completed!"
print_info "Your application is available at: https://$DOMAIN"
print_info ""
print_info "Next steps:"
print_info "1. Update your Google OAuth redirect URIs to: https://$DOMAIN/auth/google/callback"
print_info "2. Update your DNS A record to point to this server's IP"
print_info "3. Run 'docker-compose logs' to check for any errors"
print_info ""
print_info "Useful commands:"
print_info "- Monitor logs: docker-compose logs -f"
print_info "- Restart services: docker-compose restart"
print_info "- Update code: git pull && docker-compose up --build -d"