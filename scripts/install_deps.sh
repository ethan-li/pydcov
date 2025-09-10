#!/bin/bash
# Dependency installation script for pydcov project
# Supports Linux and macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        *)          echo "unknown";;
    esac
}

# Install dependencies on Linux
install_linux_deps() {
    log_info "Installing dependencies for Linux..."
    
    # Detect package manager
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        log_info "Using apt-get package manager"
        sudo apt-get update
        sudo apt-get install -y \
            build-essential \
            gcc \
            g++ \
            clang \
            cmake \
            lcov \
            python3 \
            python3-pip \
            python3-venv
    elif command -v yum >/dev/null 2>&1; then
        # CentOS/RHEL
        log_info "Using yum package manager"
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y \
            gcc \
            gcc-c++ \
            clang \
            cmake \
            lcov \
            python3 \
            python3-pip
    elif command -v dnf >/dev/null 2>&1; then
        # Fedora
        log_info "Using dnf package manager"
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y \
            gcc \
            gcc-c++ \
            clang \
            cmake \
            lcov \
            python3 \
            python3-pip
    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        log_info "Using pacman package manager"
        sudo pacman -S --noconfirm \
            base-devel \
            gcc \
            clang \
            cmake \
            lcov \
            python \
            python-pip
    else
        log_error "No supported package manager found"
        log_error "Please install the following packages manually:"
        log_error "  - build-essential (gcc, g++, make)"
        log_error "  - clang"
        log_error "  - cmake"
        log_error "  - lcov"
        log_error "  - python3"
        log_error "  - python3-pip"
        exit 1
    fi
}

# Install dependencies on macOS
install_macos_deps() {
    log_info "Installing dependencies for macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew >/dev/null 2>&1; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Xcode command line tools if not present
    if ! xcode-select -p >/dev/null 2>&1; then
        log_info "Installing Xcode command line tools..."
        xcode-select --install
        log_warning "Please complete the Xcode command line tools installation and run this script again"
        exit 1
    fi
    
    # Install packages with Homebrew
    log_info "Installing packages with Homebrew..."
    brew install \
        gcc \
        llvm \
        cmake \
        lcov \
        python3
    
    # Add LLVM to PATH if not already there
    if ! command -v llvm-cov >/dev/null 2>&1; then
        log_info "Adding LLVM tools to PATH..."
        echo 'export PATH="/opt/homebrew/opt/llvm/bin:$PATH"' >> ~/.zshrc
        echo 'export PATH="/usr/local/opt/llvm/bin:$PATH"' >> ~/.bash_profile
        log_warning "Please restart your shell or run 'source ~/.zshrc' (zsh) or 'source ~/.bash_profile' (bash)"
    fi
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        log_warning "requirements.txt not found, installing basic packages..."
        pip install pytest pytest-cov pytest-xdist pytest-html coverage
    fi
    
    log_success "Python dependencies installed in virtual environment"
    log_info "To activate the virtual environment, run: source venv/bin/activate"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check compilers
    if command -v gcc >/dev/null 2>&1; then
        log_success "GCC found: $(gcc --version | head -n1)"
    else
        log_error "GCC not found"
        ((errors++))
    fi
    
    if command -v clang >/dev/null 2>&1; then
        log_success "Clang found: $(clang --version | head -n1)"
    else
        log_warning "Clang not found"
    fi
    
    # Check build tools
    if command -v make >/dev/null 2>&1; then
        log_success "Make found: $(make --version | head -n1)"
    else
        log_error "Make not found"
        ((errors++))
    fi
    
    if command -v cmake >/dev/null 2>&1; then
        log_success "CMake found: $(cmake --version | head -n1)"
    else
        log_warning "CMake not found"
    fi
    
    # Check coverage tools
    if command -v gcov >/dev/null 2>&1; then
        log_success "gcov found: $(gcov --version | head -n1)"
    else
        log_warning "gcov not found"
    fi
    
    if command -v lcov >/dev/null 2>&1; then
        log_success "lcov found: $(lcov --version | head -n1)"
    else
        log_warning "lcov not found"
    fi
    
    if command -v llvm-cov >/dev/null 2>&1; then
        log_success "llvm-cov found: $(llvm-cov --version | head -n1)"
    else
        log_warning "llvm-cov not found"
    fi
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        log_success "Python3 found: $(python3 --version)"
    else
        log_error "Python3 not found"
        ((errors++))
    fi
    
    if [ $errors -eq 0 ]; then
        log_success "All essential tools are available"
        return 0
    else
        log_error "$errors essential tools are missing"
        return 1
    fi
}

# Main function
main() {
    local os="$(detect_os)"
    local install_python="${1:-yes}"
    
    log_info "Dependency installation script for pydcov project"
    log_info "Operating System: $os"
    
    case "$os" in
        "linux")
            install_linux_deps
            ;;
        "macos")
            install_macos_deps
            ;;
        *)
            log_error "Unsupported operating system: $os"
            exit 1
            ;;
    esac
    
    if [ "$install_python" = "yes" ]; then
        install_python_deps
    fi
    
    verify_installation
    
    log_success "Dependency installation completed!"
    log_info "You can now build the project with: make coverage"
    log_info "Or run the full coverage workflow with: python3 coverage_tools/scripts/coverage.py full tests/"
}

# Show help
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [yes|no]"
    echo ""
    echo "Arguments:"
    echo "  yes  - Install Python dependencies (default)"
    echo "  no   - Skip Python dependencies"
    echo ""
    echo "This script installs the following dependencies:"
    echo "  - Build tools (gcc, g++, make, cmake)"
    echo "  - Clang compiler and LLVM tools"
    echo "  - Coverage tools (gcov, lcov, llvm-cov)"
    echo "  - Python 3 and pip"
    echo "  - Python testing packages (pytest, coverage, etc.)"
    exit 0
fi

# Run main function
main "$@"
