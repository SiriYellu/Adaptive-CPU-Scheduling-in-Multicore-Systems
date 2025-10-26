@echo off
cd "C:\Users\siriy\Downloads\Adaptive CPU Scheduling in Multicore Systems"

echo Uploading to GitHub...
echo.

git init
git remote remove origin 2>nul
git remote add origin https://github.com/SiriYellu/Adaptive-CPU-Scheduling-in-Multicore-Systems.git
git add .
git commit -m "Upload project"
git branch -M main
git push -u origin main --force

echo.
echo Done!
echo https://github.com/SiriYellu/Adaptive-CPU-Scheduling-in-Multicore-Systems
pause

