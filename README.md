Task 9: Quick Guide

    Update: Pull the latest changes using git pull origin main.

    Run: Start the server with uvicorn app.main:app --reload.

    Test: Access the API interface at http://127.0.0.1:8000/docs.

    Business Logic:

        Tax: Automatic 16% tax calculation on every order.

        Stock: Automated inventory deduction and prevention of over-ordering (400 Bad Request).
