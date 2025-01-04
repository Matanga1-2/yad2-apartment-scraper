import logging

def setup_logging(level=logging.WARNING, log_file=None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        
        handlers = [stream_handler]
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            handlers.append(file_handler)
            
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler) 