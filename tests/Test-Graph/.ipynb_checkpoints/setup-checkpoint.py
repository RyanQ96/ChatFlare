import sys, os
from dotenv import load_dotenv
load_dotenv() 
__package_root_dir__ = "../../"
sys.path.insert(0, os.path.dirname(__package_root_dir__))
__agent_card_package_root_dir__ = "../../../"
sys.path.append(os.path.dirname(__agent_card_package_root_dir__))
os.chdir("../../")
