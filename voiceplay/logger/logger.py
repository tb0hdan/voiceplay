import logging
import sys

logging.basicConfig()
logger = logging.getLogger("voiceplay")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)
