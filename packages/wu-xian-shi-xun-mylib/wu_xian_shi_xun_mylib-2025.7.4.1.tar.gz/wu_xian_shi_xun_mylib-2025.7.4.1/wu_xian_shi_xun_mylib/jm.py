import os
import sqlite3
import ctypes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# 生成一对RSA密钥
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# 使用公钥加密消息
def encrypt_message(message, public_key, salt):
    encrypted = public_key.encrypt(
        message.encode() + salt,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

# 使用私钥解密消息
def decrypt_message(encrypted_message, private_key, salt_length):
    decrypted = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted[:-salt_length].decode()

# 创建或替换数据库
def create_or_replace_db():
    conn = sqlite3.connect('encrypted_messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, message BLOB)''')
    conn.commit()
    conn.close()

# 将加密后的消息存储到数据库中
def store_encrypted_message(encrypted_message):
    conn = sqlite3.connect('encrypted_messages.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO messages (id, message) VALUES (1, ?)", (encrypted_message,))
    conn.commit()
    conn.close()

# 从数据库中检索加密后的消息
def retrieve_encrypted_message():
    conn = sqlite3.connect('encrypted_messages.db')
    c = conn.cursor()
    c.execute("SELECT message FROM messages WHERE id=1")
    encrypted_message = c.fetchone()[0]
    conn.close()
    return encrypted_message

# 检查是否是第一次运行并设置隐藏
def check_first_run_and_hide():
    first_run_file = 'first_run.flag'
    if not os.path.exists(first_run_file):
        open(first_run_file, 'w').close()
        set_file_hidden(first_run_file)
        return True
    return False

# 检查数据库是否存在
def check_db_exists(db_file):
    return os.path.exists(db_file)

# 设置文件为隐藏
def set_file_hidden(file_path):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    ret = ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_HIDDEN)
    if not ret:
        raise ctypes.WinError()

# 加密和解密消息
def encrypt_and_decrypt(message_to_encrypt):
    private_key, public_key = generate_keys()
    salt = os.urandom(16)

    encrypted_message = encrypt_message(message_to_encrypt, public_key, salt)
    store_encrypted_message(encrypted_message)

    retrieved_message = retrieve_encrypted_message()
    decrypted_message = decrypt_message(retrieved_message, private_key, len(salt))

    return decrypted_message

# 主程序
db_file_name = 'encrypted_messages.db'

first_run = check_first_run_and_hide()
db_exists = check_db_exists(db_file_name)

if not db_exists:
    if first_run:
        print("警告：数据库文件丢失，正在重新创建数据库。")
        create_or_replace_db()
        set_file_hidden(db_file_name)
    else:
        print("错误：数据库文件不存在，程序无法继续运行。")
        exit(1)

if first_run:
    print("您第一次运行程序。")
else:
    print("欢迎回来！")