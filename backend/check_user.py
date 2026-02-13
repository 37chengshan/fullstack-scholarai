"""Test script to check user data in MongoDB"""
import sys
sys.path.insert(0, '.')

try:
    from config.database import init_db, get_collection
    from flask import Flask

    # 初始化数据库
    app = Flask(__name__)
    init_db(app)

    collection = get_collection('users')
    user_dict = collection.find_one({'email': 'test@example.com'})

    if user_dict:
        print('用户数据:')
        print(f'  _id: {user_dict.get("_id")}')
        print(f'  id: {user_dict.get("id")}')
        print(f'  email: {user_dict.get("email")}')
        print(f'  name: {user_dict.get("name")}')
        print(f'  完整数据: {user_dict}')
    else:
        print('用户不存在')

except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
