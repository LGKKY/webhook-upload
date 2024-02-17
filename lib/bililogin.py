import logging
from tomlkit import parse, dumps
import time
import qrcode_terminal
import schedule
from threading import Thread

from html.parser import HTMLParser
from http.cookiejar import DefaultCookiePolicy
from requests import Session
from requests.utils import dict_from_cookiejar

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import binascii


logger = logging.getLogger(__name__)

config_path = "lib/config.toml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = parse(f.read()).unwrap()


def run_cookies_schedule():
    def inner():
        while True:
            schedule.run_pending()
            time.sleep(1)
    bili_login = BiliLogin()
    check_time = config["cookie_refresh"]["check_time"]
    schedule.every().day.at(check_time).do(bili_login.check_and_update)
    Thread(name="cookies_schedule", target=inner).start()


class BiliLogin:
    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        self.session = Session()
        self.session.headers.update(headers)

        self.login_if_needed()
        cookies = config["cookie_refresh"]["cookies"]
        self.session.cookies.update(cookies)

        # 禁止通过 _refresh_cookies 中的响应更新 cookies，需要等到 _confirm 完成后手动更新
        self.session.cookies.set_policy(DefaultCookiePolicy(allowed_domains=[]))

    def login_if_needed(self):
        # 如果配置文件中没有 cookies 信息，则扫码登录
        if "cookies" not in config["cookie_refresh"].keys():
            self._login()

    def _qrc_gen(self):
        """
        生成登录用二维码所需信息
        """
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
        response = self.session.get(url)
        data = response.json()['data']
        return data['qrcode_key'], data['url']

    def _qrc_sc(self, qrcode_key):
        """
        登录并获取cookies
        """
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        response = self.session.get(url, params={'qrcode_key': qrcode_key})
        try:
            data = response.json()['data']
        except Exception as e:
            print(f"解码 JSON 响应时出错：{e}")
            return None, None
        cookies = response.cookies
        return data, cookies

    def _login(self):
        """
        扫码登录
        """
        qrcode_key, url = self._qrc_gen()

        print(f'登录二维码{url}')
        qrcode_terminal.draw(url, version=3)

        while True:
            data, cookies = self._qrc_sc(qrcode_key)

            code = data['code']
            message = data['message']
            refresh_token = data['refresh_token']
            timestamp = data['timestamp']

            match code:
                case 0:
                    print('确认到登录状态，正在保存')
                    print('登录确认，保存 cookies 和 refresh token...')
                    config["cookie_refresh"]["cookies"] = dict_from_cookiejar(cookies)
                    config["cookie_refresh"]["refresh_token"] = refresh_token
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(dumps(config))
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

    def _check(self):
        """
        检查是否需要刷新cookie
        :return: (是否需要刷新 Cookie, 当前时间戳)
        """
        url = "https://passport.bilibili.com/x/passport-login/web/cookie/info"
        response = self.session.get(url).json()
        if response["code"] == 0:
            logger.info("check成功")
            need_refresh = response["data"]["refresh"]
            timestamp = response["data"]["timestamp"]
            return need_refresh, timestamp
        else:
            msg = response["message"]
            logger.error(msg)

    @staticmethod
    def _get_correspond_path(timestamp):
        """
        获取 correspond_path
        :param timestamp: check() 返回的时间戳
        :return: correspond_path
        """
        key = RSA.importKey('''\
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg
Uc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71
nzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40
JNrRuoEUXpabUzGB8QIDAQAB
-----END PUBLIC KEY-----
''')
        cipher = PKCS1_OAEP.new(key, SHA256)
        encrypted = cipher.encrypt(f'refresh_{timestamp}'.encode())
        return binascii.b2a_hex(encrypted).decode()

    def _get_refresh_csrf(self, correspond_path):
        """
        获取 refresh_csrf
        :param correspond_path: get_correspond_path() 的返回值
        :return: refresh_csrf
        """
        url = "https://www.bilibili.com/correspond/1/" + correspond_path
        html = self.session.get(url).text

        class MyHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.recording = False
                self.data = ''

            def handle_starttag(self, tag, attrs):
                if tag == 'div':
                    for attr in attrs:
                        if attr == ('id', '1-name'):
                            self.recording = True

            def handle_endtag(self, tag):
                if tag == 'div' and self.recording:
                    self.recording = False

            def handle_data(self, data):
                if self.recording:
                    self.data += data

        parser = MyHTMLParser()
        parser.feed(html)
        refresh_csrf = parser.data
        return refresh_csrf

    def _refresh_cookies(self, refresh_csrf):
        """
        刷新 cookies
        :param refresh_csrf: get_refresh_csrf() 的返回值
        :return: 新的 cookies 和 refresh_token
        """
        url = "https://passport.bilibili.com/x/passport-login/web/cookie/refresh"
        data = {
            "csrf": config["cookie_refresh"]["cookies"]["bili_jct"],
            "refresh_csrf": refresh_csrf,
            "source": "main_web",
            "refresh_token": config["cookie_refresh"]["refresh_token"]
        }
        response = self.session.post(url, data)
        new_cookies = response.cookies.get_dict()
        response = response.json()
        if response["code"] == 0:
            logger.info("refresh_cookies成功")
            new_refresh_token = response["data"]["refresh_token"]
            return new_cookies, new_refresh_token
        else:
            msg = response["message"]
            logger.error(msg)

    def _confirm(self, new_cookies, new_refresh_token):
        """
        确认更新，使旧的 refresh_token 对应的 cookies 失效
        """
        url = "https://passport.bilibili.com/x/passport-login/web/confirm/refresh"
        data = {
            "csrf": config["cookie_refresh"]["cookies"]["bili_jct"],
            "refresh_token": config["cookie_refresh"]["refresh_token"]
        }
        response = self.session.post(url, data).json()
        if response["code"] == 0:
            logger.info("confirm成功")
            self.session.cookies.update(new_cookies)
            config["cookie_refresh"]["cookies"] = new_cookies
            config["cookie_refresh"]["refresh_token"] = new_refresh_token
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(dumps(config))
        else:
            msg = response["message"]
            logger.error(msg)

    def update_recorder_settings(self, recorders=("rechime", "blrec")):
        """
        更新录播工具设置中的cookies
        :param recorders: 进行更新的录播工具
        """
        cookies = config["cookie_refresh"]["cookies"]
        cookies_str = ";".join(f"{k}={v}" for k, v in cookies.items())

        if "rechime" in recorders:
            url = f"http://{config['server']['host']}:{config['rechime']['port']}/api/config/global"
            data = {
                "optionalCookie": {
                    "hasValue": True,
                    "value": cookies_str
                }
            }
            response = self.session.post(url, json=data)
            status = response.status_code
            body = response.json()
            if status == 200 and body["optionalCookie"]["value"] == cookies_str:
                logger.info("rechime: cookies更新成功")
            else:
                logger.error(f"rechime: cookies更新失败")

        if "blrec" in recorders:
            url = f"http://{config['server']['host']}:{config['blrec']['port']}/api/v1/settings"
            data = {
                "header": {
                    "cookie": cookies_str
                }
            }
            response = self.session.patch(url, json=data)
            status = response.status_code
            body = response.json()
            if status == 200 and "header" in body and body["header"]["cookie"] == cookies_str:
                logger.info("cookies更新成功")
            else:
                logger.error(f"cookies更新失败")

    def check_and_update(self):
        """
        检查并更新 cookies 的完整流程
        """
        need_refresh, timestamp = self._check()
        if need_refresh:
            logger.info("需要更新cookies")
            correspond_path = self._get_correspond_path(timestamp)
            refresh_csrf = self._get_refresh_csrf(correspond_path)
            new_cookies, new_refresh_token = self._refresh_cookies(refresh_csrf)
            self._confirm(new_cookies, new_refresh_token)
            self.update_recorder_settings()
        else:
            logger.info("无需更新cookies")
