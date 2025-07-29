# logger.py
import os
import logging

class WorkflowLogger:
    @staticmethod
    def setup_logger(name: str, output_path: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        log_file = os.path.join(output_path, 'workflow.log')
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger
