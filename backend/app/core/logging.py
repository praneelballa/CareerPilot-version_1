import logging
import sys

def setup_logging(debug: bool = False) -> logging.Logger:
    log_level = logging.DEBUG if debug else logging.INFO
    
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("careerpilot")
    logger.setLevel(log_level)
    return logger