import os
import requests
from dotenv import load_dotenv

def setup():
    application_use = input("Enter the application use: ")
    company_name = input("Enter the company name: ")

    # Simulate server interaction to get keys
    response = requests.post('https://god-server.onrender.com/api/generate_keys', json={
        'application_use': application_use,
        'company_name': company_name
    })
    data = response.json()
    
    with open('.env', 'w') as f:
        f.write(f"APPLICATION_KEY={data['application_key']}\n")
        f.write(f"APPLICATION_USE={application_use}\n")
        f.write(f"COMPANY_KEY={data['company_key']}\n")
        f.write(f"COMPANY_NAME={company_name}\n")
    
    print("Setup complete. Keys stored in .env file.")

if __name__ == '__main__':
    setup()