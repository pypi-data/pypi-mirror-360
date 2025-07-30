import requests

def chat_with_liberty_gpt(prompt, cortex_token):
    use_case = 'testing'
    api_version = '2024-10-21'
    model_name = 'gpt-4o-latest'

    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {cortex_token}',
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

    response = requests.post(
        f'https://cortex.aws.lmig.com/rest/v2/azure/openai/deployments/{model_name}/chat/completions',
        params=params, headers=headers, json=json_data
    )

    try:
        data = response.json()
    except Exception as e:
        print("Failed to decode JSON:", e)
        print("Raw response text:", response.text)
        return f"# README Generation Failed\n\nError: Failed to decode JSON: {e}"

    # Print the full data for debugging
    print("API response:", data)

    if response.status_code != 200:
        return f"# README Generation Failed\n\nError: {data.get('error', data)}"

    if 'choices' in data and data['choices']:
        return data['choices'][0]['message']['content']
    else:
        return f"# README Generation Failed\n\nError: {data.get('error', data)}"



def validate_liberty_gpt_token(cortex_token):
    """
    Checks if the provided cortex_token is valid for Liberty GPT API.
    Returns (is_valid, message)
    """
    api_version = '2024-10-21'
    model_name = 'gpt-4o-latest'
    url = f'https://cortex.aws.lmig.com/rest/v2/azure/openai/deployments/{model_name}/chat/completions'
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {cortex_token}',
    }
    params = {
        'api-version': api_version,
    }
    # Use a trivial harmless prompt
    json_data = {
        'messages': [
            {
                'content': 'Hello',
                'role': 'user',
            },
        ],
        'use_case': 'testing'
    }

    try:
        response = requests.post(url, params=params, headers=headers, json=json_data)
        # Try to decode JSON response for error detail
        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}
        if response.status_code == 200 and 'choices' in data:
            return True, "Token is valid."
        else:
            # Common error: {'error': 'Unauthorized'} or similar
            # For debugging, pass the error message back
            error_message = data.get('error', data)
            return False, f"Token is invalid: {error_message}"
    except Exception as e:
        return False, f"Exception occurred while checking token: {e}"