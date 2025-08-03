# Test de la fonction normalize_frontend_url

def normalize_frontend_url(frontend_url: str) -> str:
    """Normalize frontend URL to ensure it has proper protocol"""
    if not frontend_url:
        return 'https://localhost:8000'
    
    # If already has protocol, return as-is
    if frontend_url.startswith(('http://', 'https://')):
        return frontend_url
    
    # Add https:// protocol for production domains
    return f'https://{frontend_url}'

# Test cases
test_cases = [
    ('jeromeiavarone.fr', 'https://jeromeiavarone.fr'),
    ('https://jeromeiavarone.fr', 'https://jeromeiavarone.fr'),
    ('http://localhost:8000', 'http://localhost:8000'),
    ('localhost:3000', 'https://localhost:3000'),
    ('', 'https://localhost:8000'),
]

print('🧪 Testing normalize_frontend_url function:')
for input_url, expected in test_cases:
    result = normalize_frontend_url(input_url)
    status = '✅' if result == expected else '❌'
    print(f'{status} Input: "{input_url}" → Output: "{result}"')
    if result \!= expected:
        print(f'   Expected: "{expected}"')

print()
print('🔗 Testing session link generation:')

# Test Railway production case
frontend_url = 'jeromeiavarone.fr'
normalized = normalize_frontend_url(frontend_url)
session_link = f'{normalized}/frontend/public/training.html?token=TEST123&profile=required'

print(f'✅ Input FRONTEND_URL: "{frontend_url}"')
print(f'✅ Normalized URL: "{normalized}"')
print(f'✅ Final session link: "{session_link}"')

expected_link = 'https://jeromeiavarone.fr/frontend/public/training.html?token=TEST123&profile=required'
print(f'✅ Expected result: "{expected_link}"')
print(f'✅ Match: {session_link == expected_link}')
