import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")

logger.propagate = False
logger.setLevel(level=logging.INFO)

file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
error_handler = logging.FileHandler(
    "logs/errors.log",
    encoding="utf-8",
)
console_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

error_handler.setLevel(logging.ERROR)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.addHandler(error_handler)
