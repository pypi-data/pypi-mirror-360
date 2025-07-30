import logging
import os
import uvicorn
from intelliw.utils.colorlog import ColoredFormatter
from intelliw.utils.logger import _get_framework_logger, TraceIDFilter


def default_config(bind, workers=None):
    config = {
        'bind': bind,
        'accesslog': '-', 'errorlog': '-',
        'timeout': 6000,
        'workers': workers or 1,
        'worker_class': 'intelliw.feature.IntelliwWorker',
        'logger_class': CustomLogger
    }
    return config


try:
    import gunicorn.app.base
    from gunicorn import glogging


    class CustomLogger(glogging.Logger):
        """Custom logger for Gunicorn log messages."""

        def __set_handler(self, logger, formatter, handler):
            h = self._get_gunicorn_handler(logger)
            if h:
                logger.handlers.remove(h)
            h.setFormatter(formatter)
            h._gunicorn = True
            logger.addHandler(h)
            logger.addHandler(handler)

        def setup(self, cfg):
            """Configure Gunicorn application logging configuration."""
            super().setup(cfg)

            format_string = '%(log_color)s[%(process)d] -System Log-  %(asctime)s | %(levelname)4s | %(message)4s'
            formatter = ColoredFormatter(format_string)

            framework_handler = _get_framework_logger().handlers[0]

            # Override Gunicorn's `error_log` configuration.
            self.__set_handler(self.error_log, formatter, framework_handler)
            self.__set_handler(self.access_log, formatter, framework_handler)


    class GunServer(gunicorn.app.base.BaseApplication):

        def __init__(self, app, options=None, logger=None, limit_concurrency=100):
            self.options = options or {}
            self.application = app
            self.logger = logger

            super().__init__()
            # self.cfg.set('max_requests', limit_concurrency)

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

        def run(self):
            super().run()
except Exception as e:
    _get_framework_logger().warning('Windows can not use Gunicorn, Uvicorn service import')


class UvicornServer:

    def __init__(self, app, host='0.0.0.0', port=8888, workers=None, limit_concurrency=9999):
        config = uvicorn.Config(
            app,
            host=host,
            port=int(port),
            workers=workers,
            limit_concurrency=limit_concurrency
        )
        self.server = uvicorn.Server(config)

    def run(self):
        class NoMsgFilter(logging.Filter):
            def filter(self, record):
                return record.getMessage().find('/healthcheck') < 0

        logger = logging.getLogger("uvicorn.error")
        logger.handlers = logging.getLogger().handlers
        logger.addFilter(TraceIDFilter())
        logger.addFilter(NoMsgFilter())
        logger.propagate = False

        logger = logging.getLogger("uvicorn.access")
        logger.handlers = logging.getLogger().handlers
        logger.addFilter(TraceIDFilter())
        logger.addFilter(NoMsgFilter())
        logger.propagate = False

        self.server.run()


if __name__ == '__main__':
    # options = {
    #     'bind': '%s:%s' % ('127.0.0.1', '8080'),
    #     'workers': number_of_workers(),
    # }
    # StandaloneApplication(handler_app, options).run()
    pass
