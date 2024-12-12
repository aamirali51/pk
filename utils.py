import logging

def setup_logger():
    logging.basicConfig(
        filename='/var/log/pk.log',
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
