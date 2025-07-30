#!/bin/bash

# Vocals SDK Python Examples Runner
# This script helps run the example scripts with proper setup and error checking

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_info "Checking Python version..."
    if command_exists python3; then
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_info "Python version: $python_version"
        
        # Check if Python >= 3.8
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        print_error "Python3 is not installed"
        exit 1
    fi
}

# Function to check and install dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/upgrade dependencies
    print_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Dependencies installed"
}

# Function to check environment variables
check_environment() {
    print_info "Checking environment variables..."
    
    # Check for .env file
    if [ -f ".env" ]; then
        print_info "Found .env file, loading..."
        export $(cat .env | xargs)
    fi
    
    # Check for required environment variables
    if [ -z "$VOCALS_DEV_API_KEY" ]; then
        print_warning "VOCALS_DEV_API_KEY not set"
        print_info "Please set your API key:"
        print_info "export VOCALS_DEV_API_KEY='your_api_key_here'"
        print_info "Or create a .env file with: VOCALS_DEV_API_KEY=your_api_key_here"
        exit 1
    fi
    
    if [ -z "$VOCALS_WS_ENDPOINT" ]; then
        print_warning "VOCALS_WS_ENDPOINT not set, using default"
        export VOCALS_WS_ENDPOINT="ws://192.168.1.46:8000/v1/stream/conversation"
    fi
    
    print_success "Environment variables configured"
    print_info "API Key: ${VOCALS_DEV_API_KEY:0:10}..."
    print_info "WebSocket Endpoint: $VOCALS_WS_ENDPOINT"
}

# Function to check audio file for file example
check_audio_file() {
    if [ ! -f "test_audio.wav" ]; then
        print_warning "test_audio.wav not found"
        print_info "The file playback example requires test_audio.wav"
        print_info "Please provide a WAV file in the project root"
        return 1
    fi
    
    print_success "Audio file found: test_audio.wav"
    return 0
}

# Function to run file playback example
run_file_example() {
    print_info "Running File Playback Example..."
    
    if ! check_audio_file; then
        print_error "Cannot run file example without test_audio.wav"
        return 1
    fi
    
    if [ ! -f "example_file_playback.py" ]; then
        print_error "example_file_playback.py not found"
        return 1
    fi
    
    print_info "Starting file playback example..."
    print_info "Press Ctrl+C to stop"
    
    python3 example_file_playback.py
}

# Function to run microphone example
run_microphone_example() {
    print_info "Running Microphone Streaming Example..."
    
    if [ ! -f "example_microphone_streaming.py" ]; then
        print_error "example_microphone_streaming.py not found"
        return 1
    fi
    
    print_info "Starting microphone streaming example..."
    print_info "Press Ctrl+C to stop"
    print_warning "Make sure your microphone is working and permissions are granted"
    
    python3 example_microphone_streaming.py
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  file        Run the file playback example"
    echo "  mic         Run the microphone streaming example"
    echo "  setup       Setup environment and dependencies only"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 file     # Run file playback example"
    echo "  $0 mic      # Run microphone streaming example"
    echo "  $0 setup    # Setup environment only"
}

# Function to setup environment
setup_environment() {
    print_info "Setting up Vocals SDK Python Examples..."
    
    check_python_version
    check_dependencies
    check_environment
    
    print_success "Setup completed successfully!"
    print_info "You can now run the examples:"
    print_info "  $0 file    # File playback example"
    print_info "  $0 mic     # Microphone streaming example"
}

# Main script logic
main() {
    echo "🎵 Vocals SDK Python Examples Runner"
    echo "===================================="
    
    # Check if running from correct directory
    if [ ! -f "vocals/__init__.py" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    case "${1:-}" in
        "file")
            setup_environment
            run_file_example
            ;;
        "mic")
            setup_environment
            run_microphone_example
            ;;
        "setup")
            setup_environment
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        "")
            print_info "No option specified. Showing usage..."
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 