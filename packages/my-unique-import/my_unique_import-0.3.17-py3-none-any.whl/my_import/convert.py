import json

# 读取JSON格式的cookie文件
with open('cookies.json', 'r') as f:
    cookies = json.load(f)

# 将cookie转换为txt格式
with open('cookies.txt', 'w') as f:
    for cookie in cookies:
        f.write(f"{cookie['domain']}\t"
                f"TRUE\t"
                f"{cookie['path']}\t"
                f"{str(cookie['secure']).upper()}\t"
                f"{int(cookie['expirationDate'])}\t"
                f"{cookie['name']}\t"
                f"{cookie['value']}\n")

print("Cookies have been converted to cookies.json format.")