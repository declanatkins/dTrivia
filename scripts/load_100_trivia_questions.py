import os
import requests


DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', '100-trivia-questions.txt')
with open(DATA_FILE, 'r') as f:
    lines = [line.strip() for line in f.readlines()]

questions = {}
active_question = None
categories = [
    {
        'name': 'general-knowledge',
        'description': 'General knowledge'
    },
    {
        'name': 'literature',
        'description': 'Literature'
    },
    {
        'name': 'history',
        'description': 'History'
    },
    {
        'name': 'sports',
        'description': 'Sports'
    },
    {
        'name': 'art',
        'description': 'Art'
    },
    {
        'name': 'entertainment',
        'description': 'Entertainment'
    },
    {
        'name': 'geography',
        'description': 'Geography'
    }
]

for line in lines:
    if not line:
        active_question = None
        continue

    if len(questions) < 100 and not active_question:
        active_question, category = line.split('?')
        active_question = active_question.strip()
        category = category.strip()
        questions[active_question] = {'category': category, 'answers': []}
    elif active_question:
        questions[active_question]['answers'].append(line)
    else:
        question, answer = line.split('?')
        question = question.strip()
        answer = answer.strip()
        questions[question]['correct_answer'] = questions[question]['answers'].index(answer)


user_name = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')
base_url = os.environ.get('BASE_URL')

if not user_name or not password or not base_url:
    print('You must set the USER_NAME, PASSWORD and BASE_URL environment variables')
    exit(1)

login_response = requests.post(f'{base_url}/users/login', json={'user_name': user_name, 'password': password})
if login_response.status_code != 200:
    print(f'Failed to login: {login_response.json()["detail"]}')
    exit(1)

session_id = login_response.json()['session_id']

for category in categories:
    response = requests.post(
        f'{base_url}/questions/categories/',
        json={
            'name': category['name'],
            'description': category['description']
        }, 
        headers={
            'session-id': session_id
        }
    )
    if response.status_code != 201:
        print(response.text)
        print(f'Failed to create category: {response.json()["detail"]}')

for question, data in questions.items():
    response = requests.post(
        f'{base_url}/questions/',
        json={
            'question': question,
            'category_name': data['category'],
            'answers': data['answers'],
            'correct_answer': data['correct_answer']
        },
        headers={
            'session-id': session_id
        }
    )
    if response.status_code != 201:
        print(f'Failed to create question: {response.json()["detail"]}')