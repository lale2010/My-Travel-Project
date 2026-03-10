# My Travel Project

## Description
A full-featured travel web application built with Flask and SQLite.  
This app helps users plan trips, track expenses, view live news, and access multiple APIs for useful travel information.

## Features
- User authentication: Sign up and log in
- Trip management: Create, view, and search trips
- Expense tracking: See costs for hotels, food, transport, and other travel expenses
- API integrations:
  - Currency exchange rates
  - Weather updates
  - News feed
  - Expense cost lookup
- Search history: Users can search and view past trips and API queries

## Technologies
- Python 3.x
- Flask
- SQLite
- HTML / CSS / JavaScript
- External APIs for news, weather, currency, and expenses

## Installation & Usage
```bash
# Clone the repository
git clone https://github.com/lale2010/my_travel_project.git
cd my_travel_project

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
