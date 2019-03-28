import os

from rmatics import create_app
from rmatics.config import CONFIG_MODULE

application = create_app(config=CONFIG_MODULE)

if __name__ == '__main__':
    application.run()