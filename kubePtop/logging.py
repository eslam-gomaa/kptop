from kubePtop.global_attrs import GlobalAttrs
import logging
from rich.logging import RichHandler
from datetime import datetime

class Logging:
        debug = False

        # FORMAT = "%(message)s"
        FORMAT="[%(asctime)s] [%(levelname)s] %(message)s" # "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"    
        LEVEL="INFO"

            
        logging.basicConfig(
        level=LEVEL,
        format=FORMAT, 
        # datefmt="[%X]",
        datefmt='%H:%M:%S',
        # handlers=[RichHandler()],
        filename=GlobalAttrs.log_file_path,
        filemode='a'
        )
        log = logging.getLogger("rich")
        log.info("|---------------------|")
        log.info("| New Logging Event   |")
        log.info(f"| {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
        log.info("|---------------------|")




