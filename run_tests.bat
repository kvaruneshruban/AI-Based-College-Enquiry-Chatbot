@echo off
title AI-Based College Enquiry Chatbot - Test Suite
echo ========================================================
echo   Running Pytest Automated Verification Suite...
echo ========================================================
python -m pytest tests/test_chatbot.py -v
echo ========================================================
pause

