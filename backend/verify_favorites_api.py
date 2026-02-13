"""
验证收藏夹API实现

简单检查favorites.py路由文件是否正确实现。
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_imports():
    """验证必要的模块是否可以导入"""
    print("🔍 验证模块导入...")

    try:
        from models.favorites import Favorite, Folder
        print("  ✅ models.favorites")
    except Exception as e:
        print(f"  ❌ models.favorites: {e}")
        return False

    try:
        from middleware.auth import generate_token, jwt_required_custom
        print("  ✅ middleware.auth")
    except Exception as e:
        print(f"  ❌ middleware.auth: {e}")
        return False

    try:
        from config.database import get_collection
        print("  ✅ config.database")
    except Exception as e:
        print(f"  ❌ config.database: {e}")
        return False

    try:
        from routes.favorites import favorites_bp
        print("  ✅ routes.favorites")
    except Exception as e:
        print(f"  ❌ routes.favorites: {e}")
        return False

    try:
        from app import create_app
        print("  ✅ app")
    except Exception as e:
        print(f"  ❌ app: {e}")
        return False

    return True


def verify_models():
    """验证数据模型"""
    print("\n🔍 验证数据模型...")

    try:
        from models.favorites import Favorite, Folder

        # 测试Folder模型
        print("\n测试 Folder 模型:")
        folder = Folder(name="测试文件夹", created_by="user-123")
        print(f"  ✅ 创建文件夹: {folder.name}")
        print(f"  ✅ 颜色: {folder.color}")
        print(f"  ✅ ID: {folder.id}")

        folder_dict = folder.to_dict()
        print(f"  ✅ 序列化成功: {len(folder_dict)} 个字段")

        # 测试Favorite模型
        print("\n测试 Favorite 模型:")
        favorite = Favorite(
            user_id="user-123",
            paper_id="2301.00001",
            title="测试论文",
            authors=["作者1", "作者2"]
        )
        print(f"  ✅ 创建收藏项: {favorite.title}")
        print(f"  ✅ 论文ID: {favorite.paper_id}")
        print(f"  ✅ ID: {favorite.id}")

        favorite_dict = favorite.to_dict()
        print(f"  ✅ 序列化成功: {len(favorite_dict)} 个字段")

        return True

    except Exception as e:
        print(f"  ❌ 数据模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_blueprint():
    """验证蓝图配置"""
    print("\n🔍 验证蓝图配置...")

    try:
        from routes.favorites import favorites_bp

        print(f"  ✅ 蓝图名称: {favorites_bp.name}")
        print(f"  ✅ URL前缀: {favorites_bp.url_prefix}")

        # 列出所有路由
        print("\n  📋 注册的路由:")
        for rule in favorites_bp.deferred_functions:
            print(f"     - {rule}")

        return True

    except Exception as e:
        print(f"  ❌ 蓝图验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_app_registration():
    """验证应用中是否注册了蓝图"""
    print("\n🔍 验证应用注册...")

    try:
        from app import create_app

        app = create_app()

        # 检查蓝图是否已注册
        blueprint_names = [bp.name for bp in app.blueprints.values()]

        print(f"  已注册的蓝图: {blueprint_names}")

        if 'favorites' in blueprint_names:
            print("  ✅ favorites 蓝图已注册")
            return True
        else:
            print("  ❌ favorites 蓝图未注册")
            return False

    except Exception as e:
        print(f"  ❌ 应用注册验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_endpoints():
    """验证API端点"""
    print("\n🔍 验证API端点...")

    try:
        from app import create_app

        app = create_app()

        # 获取所有以/api/favorites开头的路由
        favorites_routes = [
            rule for rule in app.url_map.iter_rules()
            if str(rule).startswith('/api/favorites')
        ]

        print(f"  找到 {len(favorites_routes)} 个收藏夹相关端点:")

        expected_endpoints = [
            ('GET', '/api/favorites'),
            ('POST', '/api/favorites/toggle'),
            ('PUT', '/api/favorites/<favorite_id>'),
            ('DELETE', '/api/favorites/<favorite_id>'),
            ('GET', '/api/favorites/folders'),
            ('POST', '/api/favorites/folders'),
            ('PUT', '/api/folders/<folder_id>'),
            ('DELETE', '/api/folders/<folder_id>')
        ]

        for route in favorites_routes:
            methods = sorted(list(route.methods - {'HEAD', 'OPTIONS'}))
            print(f"     {methods} {route.rule}")

        # 检查关键端点是否存在
        routes_str = [str(route.rule) for route in favorites_routes]

        missing = []
        for method, endpoint in expected_endpoints:
            if endpoint not in routes_str:
                missing.append(f"{method} {endpoint}")

        if missing:
            print(f"\n  ⚠️  缺少端点: {missing}")
            return False
        else:
            print(f"\n  ✅ 所有关键端点已实现")
            return True

    except Exception as e:
        print(f"  ❌ 端点验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("ScholarAI - 收藏夹API验证")
    print("="*60)

    results = []

    # 运行验证测试
    results.append(("模块导入", verify_imports()))
    results.append(("数据模型", verify_models()))
    results.append(("蓝图配置", verify_blueprint()))
    results.append(("应用注册", verify_app_registration()))
    results.append(("API端点", verify_endpoints()))

    # 打印结果
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n🎉 所有验证通过！收藏夹API实现正确。")
        return 0
    else:
        print("\n❌ 部分验证失败，请检查实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
