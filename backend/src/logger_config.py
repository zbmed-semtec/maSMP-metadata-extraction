import logging

# Configure logging
log_file = "app.log"

logging.basicConfig(
    filename=log_file, 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO 
)

# Get a logger instance
logger = logging.getLogger("RepositoryProcessor")

