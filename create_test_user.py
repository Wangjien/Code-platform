import requests

# 测试账户信息
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}

# 调用注册API创建测试账户
def create_test_account():
    api_url = "http://localhost:5001/api/register"
    print(f"创建测试账户: {test_user['username']}")
    
    try:
        response = requests.post(api_url, json=test_user)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            print("\n[OK] 测试账户创建成功！")
            print(f"用户名: {test_user['username']}")
            print(f"邮箱: {test_user['email']}")
            print(f"密码: {test_user['password']}")
            print("\n可以使用以上账户登录 http://localhost:5173")
        elif response.status_code == 400:
            print("\n[INFO] 测试账户已存在")
            print(f"用户名: {test_user['username']}")
            print(f"邮箱: {test_user['email']}")
            print(f"密码: {test_user['password']}")
            print("\n可以使用以上账户登录 http://localhost:5173")
        else:
            print("\n[ERROR] 测试账户创建失败")
            
    except Exception as e:
        print(f"\n[ERROR] 创建测试账户时出错: {e}")

if __name__ == "__main__":
    create_test_account()
