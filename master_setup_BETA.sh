#!/bin/bash

# Function to check and install Homebrew (macOS/Linux)
install_homebrew() {
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Homebrew is already installed."
    fi
}

# Function to install pyenv
install_pyenv() {
    if ! command -v pyenv &> /dev/null; then
        echo "Installing pyenv..."
        if [ "$OS" == "Darwin" ]; then
            brew install pyenv
        elif [ "$OS" == "Linux" ]; then
            curl https://pyenv.run | bash
            # Add pyenv to the shell configuration
            export PATH="$HOME/.pyenv/bin:$PATH"
            eval "$(pyenv init --path)"
            eval "$(pyenv virtualenv-init -)"
        fi
    else
        echo "pyenv is already installed."
    fi
}

# Function to install dependencies with pyenv and pip
setup_environment() {
    echo "Installing Python versions with pyenv..."
    pyenv install -s 3.11.9
    pyenv install -s 3.12.5

    echo "Setting global Python version to 3.12.5..."
    pyenv global 3.12.5

    echo "Setting local Python version to 3.11.9..."
    pyenv local 3.11.9

    echo "Creating a virtual environment..."
    python -m venv .venv

    echo "Activating the virtual environment and installing dependencies..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install matplotlib psycopg2 pandas python-dotenv ipykernel

    echo "Setting up Jupyter kernel for the virtual environment..."
    python -m ipykernel install --user --name=.venv --display-name "Python (.venv)"

    echo "Environment setup complete."
}

# Main script execution
OS=$(uname)
echo "Detected operating system: $OS"

if [[ "$OS" == "Darwin" ]]; then
    echo "Setting up for macOS..."
    install_homebrew
    install_pyenv
elif [[ "$OS" == "Linux" ]]; then
    echo "Setting up for Linux..."
    sudo apt update
    sudo apt install -y build-essential curl zlib1g-dev libssl-dev libreadline-dev libbz2-dev libsqlite3-dev libffi-dev
    install_pyenv
elif [[ "$OS" == "WSL" || "$OS" == "Linux" && -n "$(grep Microsoft /proc/version)" ]]; then
    echo "Setting up for Windows Subsystem for Linux (WSL)..."
    sudo apt update
    sudo apt install -y build-essential curl zlib1g-dev libssl-dev libreadline-dev libbz2-dev libsqlite3-dev libffi-dev
    install_pyenv
else
    echo "Unsupported operating system. Exiting..."
    exit 1
fi

setup_environment
