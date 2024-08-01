#!/bin/bash

# Jean-Pierre LESUEUR (@DarkCoderSc)
# Description: Build Arcane Viewer Package
# Date: 2024-08-01

# arg: --skip-tox
skip_tox=false

# arg: --skip-flake
skip_flake=false

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
    *)
      ;;
  esac
done

# Clean up things
echo "Cleaning up things..."
rm -f dist/*.tar.gz
rm -f dist/*.whl

# Tox testing
if [ "$skip_tox" = false ]; then
  echo "Running Tox Testing..."
  tox
  if [ $? -ne 0 ]; then
    echo "(!) Tox Testing Failed!"
    exit 1
  fi
fi

# Active Python 3.12 Virtual Environment
source venv/312/bin/activate

# Run isort
echo "Running isort..."
isort .

# Flake8 Testing
if [ "$skip_flake" = false ]; then
  flake8 .
  if [ $? -ne 0 ]; then
    echo "(!) Flake8 Testing Failed!"
    exit 2
  fi
fi

# Build Package
echo "Building Package..."
python setup.py sdist bdist_wheel
python setup.py clean --all

deactivate

echo "Done."