from phone_verify.backends.base import BaseBackend

import logging
logger = logging.getLogger(__name__)

class DummyBackend(BaseBackend):
    def __init__(self, **options):
        super().__init__(**options)

    def send_sms(self, number, message):
        logger.info(f"send_sms to phone {number} called: {message}")

    def send_bulk_sms(self, numbers, message):
        logger.info(f"send_bulk_sms to phone {numbers} called: {message}")
