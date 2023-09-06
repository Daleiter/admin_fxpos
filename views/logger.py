import logging

def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[
                            logging.StreamHandler(),  # Display logs to the console
                            logging.FileHandler('app.log')  # Save logs to a file
                        ])

def get_logger(name):
    return logging.getLogger(name)
