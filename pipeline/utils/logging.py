import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configura le impostazioni di logging per l'applicazione con rotazione file.
    """
    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    # Impostazione della rotazione per i log file
    rotating_file_handler = RotatingFileHandler(
        os.path.join(log_folder, 'pipeline.log'),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=3               # Numero di file di backup da mantenere
    )

    rotating_file_handler.setLevel(logging.INFO)
    rotating_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Configura il logger con il gestore di rotazione file e lo stream console
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            rotating_file_handler,
            logging.StreamHandler()
        ]
    )