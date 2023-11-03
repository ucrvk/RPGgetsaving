from httpx import get, post

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                  ' x64) AppleWebKit/537.36 (KHTML, like'
                  ' Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'app-version-code': '65535',
}

def logIn(username: str, password: str):
    json = {"username": username, "password": password}
    ans = post('https://rpg.heimaoo.com/api/app/login',
               json=json, headers=header)
    if not ans.status_code == 200:
        return -1
    if ans.json()["code"] == 0:
        return ans.json()["token"]
    else:
        return ans.json()["code"]


def getActivity(token):
    tempHeader = header
    tempHeader.update(token=token)
    ans = get('http://rpg.heimaoo.com/api/app/activity/currentDay',
              headers=tempHeader)
    if not ans.status_code == 200:
        return -1
    else:
        if ans.json()["code"] == 0:
            if not ans.json()["data"]:
                return 0
            else:
                return ans.json()["data"]
        else:
            return ans.json()["code"]
        
def loginErrorCompose(errorCode):
    if errorCode == 500:
        return "登录失败，原因：密码错误\n如果需要token登录，请保证账号栏为空。如果忘记了密码，请联系keyang或拾柒\n错误代码：500    错误阶段：1.1"
    elif errorCode == -1:
        return "登录失败，原因：无法连接到服务器\n请检查您的网络，并尝试重新接档，当然，也可能是服务器炸了\n错误代码：-1    错误阶段：1.1"
    elif errorCode == 401:
        return "登录失败，原因：token错误或过期\n请尝试重新用密码登录，如果使用密码登录出现此问题，请联系制作者\n错误代码：401    错误阶段：1.2"
    else:
        return "登录失败，原因：我也不知道\n请将下方错误代码和阶段告知制作者以帮助优化\n错误代码"+errorCode+"    错误阶段：1"
