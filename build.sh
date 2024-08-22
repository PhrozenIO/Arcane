#!/bin/bash

# Jean-Pierre LESUEUR (@DarkCoderSc)
# Description: Build Arcane Viewer Package
# Date: 2024-08-12

preflight_question() {
  local question="$1"

  echo "$question ? [y/N]"

  read -r response
  response=$(echo "$response" | tr '[:upper:]' '[:lower:]')

  if [ "$response" != "y" ]; then
    echo "(!) Do it!"
    exit 1
  fi
}

# arg: --skip-tox
skip_tox=false

# arg: --skip-flake
skip_flake=false

# arg: --skip-mypy
skip_mypy=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --skip-tox)
      skip_tox=true
      shift
      ;;

    --skip-flake)
      skip_flake=true
      shift
      ;;

    --skip-mypy)
      skip_mypy=true
      shift
      ;;
    *)
      ;;
  esac
done

# Preflight checks
preflight_question "Have you updated the arcane_viewer.arcane.constants.APP_VERSION"
preflight_question "Is this version reflected on the setup.py"

# Clean up things
echo "[+] Cleaning up things..."
rm -f dist/*.tar.gz
rm -f dist/*.whl

# Tox testing
if [ "$skip_tox" = false ]; then
  echo "[+] Tox..."
  tox
  if [ $? -ne 0 ]; then
    echo "(!) Failed!"
    exit 1
  fi
fi

# Run isort
echo "[+] isort..."
isort .

# Flake8 Testing
if [ "$skip_flake" = false ]; then
  echo "[+] Flake8..."
  flake8 .
  if [ $? -ne 0 ]; then
    echo "(!) Failed!"
    exit 2
  fi
fi

# mypy Testing
if [ "$skip_mypy" = false ]; then
  echo "[+] Mypy..."
  mypy .
  if [ $? -ne 0 ]; then
    echo "(!) Failed!"
    exit 3
  fi
fi

# Build Package
echo "[+] Building Package..."
python setup.py sdist bdist_wheel
python setup.py clean --all

echo "[*] Done."