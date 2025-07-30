import requests
from decouple import config


def chat_with_liberty_gpt(USER_ACCESS_TOKEN,prompt):
    
    
    use_case = 'testing'  # Limited to 255 characters
    api_version = '2024-10-21'
    model_name = 'gpt-4o-latest'

    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {USER_ACCESS_TOKEN}',
    }

    params = {
        'api-version': api_version,
    }

    json_data = {
        'messages': [
            {
                'content': f'{prompt}.',
                'role': 'user',
            },
        ],
        'use_case': use_case
    }

    response = requests.post(f'https://cortex.aws.lmig.com/rest/v2/azure/openai/deployments/{model_name}/chat/completions', params=params, headers=headers, json=json_data)
    print(response.json()['choices'][0]['message']['content'])
    return response.json()['choices'][0]['message']['content']