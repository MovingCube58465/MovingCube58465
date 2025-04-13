import hashlib
import base64
import os
import json
import platform
import uuid
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESCrypto:
    """AES加密解密工具类，参考Java实现"""
    
    @staticmethod
    def md5(data):
        """计算MD5哈希值"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def get_machine_info():
        """获取机器特定信息作为加密密钥的种子"""
        # 获取系统信息和硬件标识
        system_info = platform.system() + platform.version()
        try:
            machine_id = str(uuid.getnode())  # MAC地址的数字表示
        except:
            machine_id = "fallback_id"
            
        # 组合并返回
        return f"{system_info}:{machine_id}:MystiAide_Secret_Key"
    
    @staticmethod
    def encrypt(data, key):
        """AES加密数据"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
            
        # 确保密钥长度为16字节(128位)
        if len(key) > 16:
            key = key[:16]
        elif len(key) < 16:
            key = key + b'\0' * (16 - len(key))
            
        # 使用密钥作为IV (与Java实现保持一致)
        iv = key
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        return base64.b64encode(ct_bytes).decode('utf-8')
    
    @staticmethod
    def decrypt(encrypted_data, key):
        """AES解密数据"""
        if isinstance(encrypted_data, str):
            encrypted_data = base64.b64decode(encrypted_data)
        if isinstance(key, str):
            key = key.encode('utf-8')
            
        # 确保密钥长度为16字节(128位)
        if len(key) > 16:
            key = key[:16]
        elif len(key) < 16:
            key = key + b'\0' * (16 - len(key))
            
        # 使用密钥作为IV (与Java实现保持一致)
        iv = key
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return pt
    
    @staticmethod
    def encrypt_string(data, key):
        """加密字符串，使用MD5处理密钥"""
        md5_key = AESCrypto.md5(key)[16:]  # 取MD5后16位
        return AESCrypto.encrypt(data, md5_key)
    
    @staticmethod
    def decrypt_string(encrypted_data, key):
        """解密字符串，使用MD5处理密钥"""
        md5_key = AESCrypto.md5(key)[16:]  # 取MD5后16位
        decrypted = AESCrypto.decrypt(encrypted_data, md5_key)
        return decrypted.decode('utf-8')
    
    @staticmethod
    def encrypt_login_data(login_data):
        """加密登录数据"""
        try:
            # 准备登录数据
            json_data = json.dumps(login_data)
            
            # 生成密钥 (使用机器特定信息作为种子)
            machine_info = AESCrypto.get_machine_info()
            key = hashlib.sha256(machine_info.encode()).digest()[:16]
            
            # 加密数据
            cipher = AES.new(key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(json_data.encode(), AES.block_size))
            iv = base64.b64encode(cipher.iv).decode('utf-8')
            ct = base64.b64encode(ct_bytes).decode('utf-8')
            
            # 计算校验和
            checksum = hashlib.sha256((json_data + machine_info).encode()).hexdigest()
            
            # 返回加密数据
            return {
                "iv": iv,
                "data": ct,
                "checksum": checksum
            }
        except Exception as e:
            print(f"加密登录数据时出错: {str(e)}")
            return None
    
    @staticmethod
    def decrypt_login_data(encrypted_data):
        """解密登录数据"""
        try:
            # 检查数据格式
            if not all(k in encrypted_data for k in ("iv", "data", "checksum")):
                print("登录数据格式错误")
                return None
            
            # 生成解密密钥
            machine_info = AESCrypto.get_machine_info()
            key = hashlib.sha256(machine_info.encode()).digest()[:16]
            
            # 解密数据
            iv = base64.b64decode(encrypted_data["iv"])
            ct = base64.b64decode(encrypted_data["data"])
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            login_data = json.loads(pt.decode('utf-8'))
            
            # 验证校验和
            json_data = json.dumps(login_data)
            checksum = hashlib.sha256((json_data + machine_info).encode()).hexdigest()
            if checksum != encrypted_data["checksum"]:
                print("登录数据校验失败，可能被篡改")
                return None
            
            return login_data
        except Exception as e:
            print(f"解密登录数据失败: {str(e)}")
            return None

    @staticmethod
    def encrypt_file(file_path, save_path=None):
        """对整个文件进行加密"""
        import os
        
        try:
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return False
                
            # 如果未指定保存路径，则使用原文件路径
            if save_path is None:
                save_path = file_path + ".enc"
                
            # 读取文件内容
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            # 生成密钥
            machine_info = AESCrypto.get_machine_info()
            key = hashlib.sha256(machine_info.encode()).digest()[:16]
            
            # 加密数据
            cipher = AES.new(key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(file_data, AES.block_size))
            
            # 保存IV和加密数据
            with open(save_path, 'wb') as f:
                f.write(cipher.iv)  # 先写入16字节的IV
                f.write(ct_bytes)   # 再写入加密数据
                
            print(f"文件已加密并保存到: {save_path}")
            return True
            
        except Exception as e:
            print(f"加密文件时出错: {str(e)}")
            return False
            
    @staticmethod
    def decrypt_file(file_path, save_path=None):
        """解密已加密的文件"""
        import os
        
        try:
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return False
                
            # 如果未指定保存路径，则使用原文件路径(去掉.enc后缀)
            if save_path is None:
                if file_path.endswith('.enc'):
                    save_path = file_path[:-4]
                else:
                    save_path = file_path + ".dec"
                    
            # 读取文件内容
            with open(file_path, 'rb') as f:
                iv = f.read(16)  # 读取前16字节作为IV
                ct_bytes = f.read()  # 读取剩余部分作为加密数据
                
            # 生成密钥
            machine_info = AESCrypto.get_machine_info()
            key = hashlib.sha256(machine_info.encode()).digest()[:16]
            
            # 解密数据
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct_bytes), AES.block_size)
            
            # 保存解密数据
            with open(save_path, 'wb') as f:
                f.write(pt)
                
            print(f"文件已解密并保存到: {save_path}")
            return True
            
        except Exception as e:
            print(f"解密文件时出错: {str(e)}")
            return False