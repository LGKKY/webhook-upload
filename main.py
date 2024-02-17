import logging
from aiohttp import web
from tomlkit import parse

import lib.rechime as rechime
import lib.blrec as blrec
from lib.bililogin import run_cookies_schedule


# 设置日志等级
logging.basicConfig(level=logging.DEBUG)

with open("lib/config.toml", 'r', encoding='utf-8') as f:
    config = parse(f.read()).unwrap()

if __name__ == "__main__":
    run_cookies_schedule()

    app = web.Application()
    app.add_routes([web.post("/rechime", rechime.handle_webhook)])
    app.add_routes([web.post("/blrec", blrec.handle_webhook)])
    host, port = config["server"]["host"], config["server"]["port"]
    web.run_app(app, host=host, port=port)

