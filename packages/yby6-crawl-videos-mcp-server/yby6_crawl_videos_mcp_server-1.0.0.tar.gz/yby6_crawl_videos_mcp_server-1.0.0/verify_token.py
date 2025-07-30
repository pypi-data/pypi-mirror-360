import os
import sys
import jwt
from datetime import datetime

def verify_token(token_path="token.txt", public_key_path="keys/public_key.pem"):
    """验证令牌的有效性"""
    print("=== 验证Bearer Token有效性 ===")
    
    # 检查令牌文件是否存在
    if not os.path.exists(token_path):
        print(f"❌ 令牌文件 {token_path} 不存在")
        return False
    
    # 检查公钥文件是否存在
    if not os.path.exists(public_key_path):
        print(f"❌ 公钥文件 {public_key_path} 不存在")
        return False
    
    # 读取令牌
    with open(token_path, "r") as f:
        token = f.read().strip()
    
    # 读取公钥
    with open(public_key_path, "r") as f:
        public_key = f.read()
    
    try:
        # 解码令牌
        decoded = jwt.decode(
            token, 
            public_key, 
            algorithms=["RS256"],
            audience="parse-video-py",
            issuer="https://parse-video.example.com"
        )
        
        # 检查过期时间
        if "exp" in decoded:
            exp_time = datetime.fromtimestamp(decoded["exp"])
            now = datetime.now()
            
            if exp_time < now:
                print(f"❌ 令牌已过期，过期时间: {exp_time}")
                return False
            else:
                print(f"✅ 令牌有效期至: {exp_time}")
        
        # 打印令牌信息
        print("\n令牌信息:")
        print(f"  主题 (sub): {decoded.get('sub', '未指定')}")
        print(f"  发行者 (iss): {decoded.get('iss', '未指定')}")
        print(f"  受众 (aud): {decoded.get('aud', '未指定')}")
        
        if "scope" in decoded:
            scopes = decoded["scope"].split()
            print(f"  权限范围: {', '.join(scopes)}")
        
        print("\n✅ 令牌验证成功!")
        return True
    
    except jwt.ExpiredSignatureError:
        print("❌ 令牌已过期")
        return False
    except jwt.InvalidTokenError as e:
        print(f"❌ 无效的令牌: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 验证过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 可以通过命令行参数指定令牌文件和公钥文件的路径
    token_path = sys.argv[1] if len(sys.argv) > 1 else "token.txt"
    public_key_path = sys.argv[2] if len(sys.argv) > 2 else "keys/public_key.pem"
    
    success = verify_token(token_path, public_key_path)
    sys.exit(0 if success else 1) 