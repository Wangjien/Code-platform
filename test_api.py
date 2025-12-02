'''
Author: Wangjien2 1569399536@qq.com
Date: 2025-12-02 00:06:21
LastEditors: Wangjien2 1569399536@qq.com
LastEditTime: 2025-12-02 00:30:15
FilePath: /代码分享平台/test_api.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import requests

# 测试API端点
api_url = 'http://localhost:5001/api'

def test_api_endpoint(endpoint, method='get', data=None):
    url = f'{api_url}/{endpoint}'
    print(f'\nTesting {url} ({method.upper()})...')
    try:
        if method == 'get':
            response = requests.get(url)
        elif method == 'post':
            response = requests.post(url, json=data)
        else:
            response = requests.request(method, url, json=data)
        
        print(f'Status Code: {response.status_code}')
        print(f'Response: {response.text[:500]}...')
        return response
    except Exception as e:
        print(f'Error: {e}')
        return None

# 测试各个API端点
test_api_endpoint('categories')
test_api_endpoint('tags')
test_api_endpoint('codes')
test_api_endpoint('register', 'post', {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'password123'
})
