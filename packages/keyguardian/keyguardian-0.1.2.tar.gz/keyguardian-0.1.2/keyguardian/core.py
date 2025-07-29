import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_env_variables():
    return {
        "application_key": os.getenv("APPLICATION_KEY"),
        "application_use": os.getenv("APPLICATION_USE"),
        "company_key": os.getenv("COMPANY_KEY"),
        "company_name": os.getenv("COMPANY_NAME")
    }

def clock(data):
    env_vars = get_env_variables()
    concatenated_data = f"{data}_{env_vars['company_key']}"[::-1]

    response = requests.post('https://god-server.onrender.com/api/clock', json={
        'encrypted_data': concatenated_data
    })

    return response.json()['clock_task_id']

def declock(clock_task_id):
    env_vars = get_env_variables()

    response = requests.post('https://god-server.onrender.com/api/declock', json={
        'clock_task_id': clock_task_id
    })

    encrypted_data = response.json()['encrypted_data']
    decrypted_data = encrypted_data[::-1].split('_')[0]

    return decrypted_data