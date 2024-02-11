import logging
from aiohttp import web
import lib.config as config
import lib.rechime as rechime
import lib.blrec as blrec 

#设置日志等级
logging.basicConfig(level=logging.DEBUG)



if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.post("/rechime", rechime.handle_webhook)])
    app.add_routes([web.post("/blrec", blrec.handle_webhook)])
    web.run_app(app, host=config.host, port=config.port)
