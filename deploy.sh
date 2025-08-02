#!/bin/bash

# WhatsApp Bot Deployment Script
# This script helps set up and deploy the WhatsApp chatbot backend

set -e  # Exit on any error

echo "🤖 WhatsApp Bot Deployment Script"
echo "=================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_step "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if virtual environment exists
setup_virtualenv() {
    print_step "Setting up virtual environment..."
    
    if [ ! -d "whatsapp_bot_env" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv whatsapp_bot_env
    else
        print_status "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment..."
    source whatsapp_bot_env/bin/activate
    
    print_status "Upgrading pip..."
    pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Copied .env.example to .env"
            print_warning "Please edit .env file with your actual credentials before running the bot"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_status "Environment file already exists"
    fi
}

# Check ML models
check_models() {
    print_step "Checking ML models..."
    
    if [ -f "xgboost_model.pkl" ] && [ -f "scaler.pkl" ]; then
        print_status "ML models found"
    else
        print_warning "ML models not found. Bot will run without prediction functionality."
        print_warning "Make sure xgboost_model.pkl and scaler.pkl are in the project directory"
    fi
}

# Run tests
run_tests() {
    print_step "Running tests..."
    
    if [ -f "test_bot.py" ]; then
        print_status "Starting test server..."
        # Start the bot in background for testing
        python start_bot.py &
        BOT_PID=$!
        
        # Wait for server to start
        sleep 5
        
        # Run tests
        python test_bot.py --test health
        
        # Stop the test server
        kill $BOT_PID 2>/dev/null || true
        
        print_status "Tests completed"
    else
        print_warning "test_bot.py not found, skipping tests"
    fi
}

# Start the bot
start_bot() {
    print_step "Starting WhatsApp Bot..."
    
    # Check if .env has been configured
    if grep -q "your_whatsapp_access_token_here" .env 2>/dev/null; then
        print_error "Please configure your .env file with actual WhatsApp credentials"
        print_error "Edit .env and replace placeholder values with real ones"
        exit 1
    fi
    
    print_status "Starting bot server..."
    python start_bot.py
}

# Production deployment
deploy_production() {
    print_step "Preparing for production deployment..."
    
    # Set production environment
    export FLASK_ENV=production
    
    # Create systemd service file
    create_systemd_service
    
    print_status "Production deployment prepared"
    print_warning "Remember to:"
    print_warning "1. Configure HTTPS/SSL certificate"
    print_warning "2. Set up reverse proxy (nginx)"
    print_warning "3. Configure firewall rules"
    print_warning "4. Set up monitoring and logging"
}

# Create systemd service
create_systemd_service() {
    SERVICE_FILE="/etc/systemd/system/whatsapp-bot.service"
    CURRENT_DIR=$(pwd)
    
    if [ "$EUID" -eq 0 ]; then
        cat > $SERVICE_FILE << EOF
[Unit]
Description=WhatsApp Chatbot Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/whatsapp_bot_env/bin
ExecStart=$CURRENT_DIR/whatsapp_bot_env/bin/python start_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        print_status "Systemd service created at $SERVICE_FILE"
        print_status "Use 'sudo systemctl start whatsapp-bot' to start the service"
        print_status "Use 'sudo systemctl enable whatsapp-bot' to start on boot"
    else
        print_warning "Run as root to create systemd service"
    fi
}

# Display help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup      - Complete setup (default)"
    echo "  start      - Start the bot"
    echo "  test       - Run tests only"
    echo "  deploy     - Production deployment"
    echo "  help       - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0              # Complete setup and start"
    echo "  $0 setup        # Setup only"
    echo "  $0 start        # Start the bot"
    echo "  $0 test         # Run tests"
    echo "  $0 deploy       # Production deployment"
}

# Main execution
main() {
    case "${1:-setup}" in
        "setup")
            check_python
            setup_virtualenv
            install_dependencies
            setup_environment
            check_models
            print_status "Setup completed!"
            print_warning "Next steps:"
            print_warning "1. Edit .env file with your WhatsApp credentials"
            print_warning "2. Run '$0 start' to start the bot"
            ;;
        "start")
            check_python
            if [ ! -d "whatsapp_bot_env" ]; then
                print_error "Virtual environment not found. Run '$0 setup' first."
                exit 1
            fi
            source whatsapp_bot_env/bin/activate
            start_bot
            ;;
        "test")
            check_python
            if [ ! -d "whatsapp_bot_env" ]; then
                print_error "Virtual environment not found. Run '$0 setup' first."
                exit 1
            fi
            source whatsapp_bot_env/bin/activate
            run_tests
            ;;
        "deploy")
            check_python
            deploy_production
            ;;
        "help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"