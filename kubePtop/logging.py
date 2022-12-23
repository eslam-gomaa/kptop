from kubePtop.global_attrs import GlobalAttrs
from kubePtop.read_env import ReadEnv
import logging
# from rich.logging import RichHandler
from datetime import datetime

class Logging:
   debug = False

   log_dir = GlobalAttrs.log_dir
   log_file = GlobalAttrs.log_file
   if log_dir[-1] != "/":
      log_dir = log_dir + "/"

   try:
      # FORMAT = "%(message)s"
      FORMAT="[%(asctime)s] [%(levelname)s] %(message)s" # "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"    
      LEVEL="INFO"

      logging.basicConfig(
      level=LEVEL,
      format=FORMAT, 
      # datefmt="[%X]",
      datefmt='%H:%M:%S',
      # handlers=[RichHandler()],
      filename=log_dir + log_file,
      filemode='a'
      )
      log = logging.getLogger("rich")
      log.info("|---------------------|")
      log.info("| New Logging Event   |")
      log.info(f"| {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
      log.info("|---------------------|")
   except Exception as e:
      print(f"ERROR -- Logging dir does NOT exist\n{e}")
      exit(1)




