#!/bin/bash
# Exit on error
set -e

echo "Building all Application Packages..."

# Move to application packages directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$BASE_DIR/application-packages"

if [ ! -d "$APP_DIR" ]; then
    echo "Directory $APP_DIR does not exist."
    exit 1
fi

cd "$APP_DIR"

for d in */; do
    if [ -d "$d" ]; then
        # Remove trailing slash
        DIR_NAME=${d%/}
        echo ""
        echo "=============================================="
        echo "Building Package: $DIR_NAME"
        echo "=============================================="
        
        cd "$DIR_NAME"
        
        if [ -f "build_config.json" ]; then
            echo "Compiling JSON Config..."
            if ! python ../../cv/scripts/cv_compiler.py build_config.json; then
                echo "[-] Error compiling build_config.json"
                cd ..
                continue
            fi
        fi
        
        # Check if any .tex files exist
        shopt -s nullglob
        tex_files=(*.tex)
        shopt -u nullglob
        
        for f in "${tex_files[@]}"; do
            if pdflatex -interaction=nonstopmode -halt-on-error "$f"; then
                echo "[+] $f built successfully"
            else
                echo "[-] Error building $f"
            fi
        done
        
        if [ -f "build_config.json" ]; then
            echo "Running ATS Check..."
            python ../../check_ats_score.py .
        fi
        
        cd ..
    fi
done

echo ""
echo "Gathering PDFs into build directory..."
BUILD_DIR="$BASE_DIR/build"
mkdir -p "$BUILD_DIR"

# Copy all generated PDFs to the build folder
find . -name "*.pdf" -exec cp -f {} "$BUILD_DIR/" \;

echo ""
echo "All builds completed. PDFs are available in the build/ folder."
cd "$BASE_DIR"
