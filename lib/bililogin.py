import requests
import time
import qrcode_terminal


headers = {
    'Accept':'application/json, text/plain, */*',
    'Origin':'https://www.bilibili.com',
    'Referer':'https://www.bilibili.com/',
    'Host':'passport.bilibili.com',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0' 
    }
# 申请二维码接口
qr_gen = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
qr_poll = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'

cookie_info = 'https://passport.bilibili.com/x/passport-login/web/cookie/info'


def qrc_gen():
    response = requests.get(qr_gen, headers=headers)
    data = response.json()['data']
    return data['qrcode_key'], data['url']

def qrc_sc(qrcode_key):
    response = requests.get(qr_poll, headers=headers,params={'qrcode_key': qrcode_key})
    try:
        data = response.json()['data']
    except Exception as e:
        print(f"解码 JSON 响应时出错：{e}")
        return None, None
    cookies = response.cookies
    return data, cookies




qrcode_key,url = qrc_gen()

print (f'登录二维码{url}')
qrcode_terminal.draw(url)


while True:
    data,cookies = qrc_sc(qrcode_key)

    code = data['code']
    message = data['message']
    refresh_token = data['refresh_token']
    timestamp = data['timestamp']

    match code:
        case 0:
            print('确认到登录状态，正在保存')
            print('登录确认，保存 cookies 和 refresh token...')
            with open('info.txt', 'w') as file:
                file.write(f'Cookies: {cookies}\n')
                file.write(f'Refresh Token: {refresh_token}\n')
            break
        case 86038:
            print('二维码已失效')
            break

        case 86090:
            print('已扫码未确认')
            time.sleep(2)
        case 86101:
            print('未扫码正在等待')
            time.sleep(2)






