@echo off
title AI-Based College Enquiry Chatbot
echo ========================================================
echo   Launching AI-Based College Enquiry Chatbot...
echo   Open your browser at: http://localhost:8501
echo ========================================================
python -m streamlit run app.py --browser.gatherUsageStats false
pause

