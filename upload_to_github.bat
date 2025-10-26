@echo off
echo ====================================================================
echo    UPLOAD PROJECT TO GITHUB
echo ====================================================================
echo.
echo Repository: https://github.com/SiriYellu/Adaptive-CPU-Scheduling-in-Multicore-Systems
echo.
echo ====================================================================
echo    Step 1: Initializing Git Repository
echo ====================================================================
git init
echo.

echo ====================================================================
echo    Step 2: Adding Remote Repository
echo ====================================================================
git remote remove origin 2>nul
git remote add origin https://github.com/SiriYellu/Adaptive-CPU-Scheduling-in-Multicore-Systems.git
echo.

echo ====================================================================
echo    Step 3: Adding All Files
echo ====================================================================
git add .
echo.

echo ====================================================================
echo    Step 4: Committing Files
echo ====================================================================
git commit -m "Complete Adaptive CPU Scheduling project - All algorithms, documentation, and working demos"
echo.

echo ====================================================================
echo    Step 5: Pushing to GitHub
echo ====================================================================
echo.
echo Note: You may be asked for GitHub credentials.
echo Use your GitHub username and Personal Access Token (not password)
echo.
git branch -M main
git push -u origin main --force
echo.

echo ====================================================================
echo    UPLOAD COMPLETE!
echo ====================================================================
echo.
echo Your project is now live at:
echo https://github.com/SiriYellu/Adaptive-CPU-Scheduling-in-Multicore-Systems
echo.
echo ====================================================================
pause

