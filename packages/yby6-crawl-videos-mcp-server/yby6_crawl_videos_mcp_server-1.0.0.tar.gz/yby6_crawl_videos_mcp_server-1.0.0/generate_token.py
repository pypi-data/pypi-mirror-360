import os
from fastmcp.server.auth.providers.bearer import RSAKeyPair

def generate_and_save_token():
    """生成RSA密钥对和Bearer Token，并保存到文件"""
    print("=== 生成RSA密钥对和Bearer Token ===")
    
    # 生成新的密钥对
    key_pair = RSAKeyPair.generate()
    
    # 生成测试令牌
    token = key_pair.create_token(
        subject="parse-video-user",
        issuer="https://yby6.com",
        audience="parse-video-py",
        scopes=["video:parse", "platform:list"],
        # expires_in_seconds=86400  # 24小时有效期
        expires_in_seconds=2592000  # 30天有效期
    )
    
    # 保存公钥到文件
    os.makedirs("keys", exist_ok=True)
    with open("keys/public_key.pem", "w") as f:
        f.write(key_pair.public_key)
    
    # 保存私钥到文件（实际应用中应妥善保管私钥）
    # 将 SecretStr 类型转换为普通字符串
    with open("keys/private_key.pem", "w") as f:
        # 使用 get_secret_value() 方法获取 SecretStr 的实际值
        f.write(key_pair.private_key.get_secret_value())
    
    # 保存令牌到文件
    with open("token.txt", "w") as f:
        f.write(token)
    
    print("✅ RSA密钥对已生成并保存到keys目录")
    print("✅ Bearer Token已生成并保存到token.txt")
    print(f"令牌: {token[:20]}...{token[-20:]}")
    
    return key_pair, token

if __name__ == "__main__":
    generate_and_save_token() 