from exam_other_const import TOKEN_STICKER_DOWNLOAD_BOT
from src.lotuschat_sdk.control.bot import ChatBot
from src.lotuschat_sdk.utility.logger import log_verbose, log_debug, log_info, log_warning, log_error


# Test log function
def log_test(message):
    log_verbose(message)
    log_debug(message)
    log_info(message)
    log_warning(message)
    log_error(message)


# Test Log with number
log_info("test  logger with number")
log_test(123123.211)

log_info("test logger with string")
log_test("message test for log")

log_info("test logger with class ChatBot")
log_test(ChatBot(
    name="Python Bot",
    token=TOKEN_STICKER_DOWNLOAD_BOT
))
