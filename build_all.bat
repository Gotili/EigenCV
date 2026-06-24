@echo off
setlocal enabledelayedexpansion

echo Building all Application Packages...

cd "%~dp0application-packages"

for /D %%d in (*) do (
    echo.
    echo ==============================================
    echo Building Package: %%d
    echo ==============================================
    cd "%%d"
    
    if exist "build_config.json" (
        echo Compiling JSON Config...
        python ../../cv/scripts/cv_compiler.py build_config.json
        if !errorlevel! neq 0 (
            echo [-] Error compiling build_config.json
        )
    )
    
    for %%f in (*.tex) do (
        pdflatex -interaction=nonstopmode -halt-on-error "%%f"
        if !errorlevel! equ 0 (
            echo [+] %%f built successfully
        ) else (
            echo [-] Error building %%f
        )
    )
    
    if exist "build_config.json" (
        echo Running ATS Check...
        python ../../check_ats_score.py .
    )
    
    cd ..
)

echo.
echo Gathering PDFs into build directory...
mkdir "%~dp0build" 2>nul
for /D %%d in (*) do (
    if exist "%%d\*.pdf" (
        copy /Y "%%d\*.pdf" "%~dp0build\" >nul
    )
)

echo.
echo All builds completed. PDFs are available in the build\ folder.
cd "%~dp0"
endlocal
