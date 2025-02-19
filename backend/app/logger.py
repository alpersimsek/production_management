import logging
import uvicorn.logging

logger = logging.getLogger("gdpr")
logger.setLevel(logging.INFO)
formatter = uvicorn.logging.DefaultFormatter(
    "%(levelprefix)s %(message)s",
    # datefmt="%Y-%m-%d %H:%M:%S",
    use_colors=True
)
# formatter.datefmt = "%Y-%m-%d %H:%M:%S"
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False
