import logging
import subprocess
from eo4eu_api_utils import Client

logger = logging.getLogger("test")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

development =  'https://umm-api.dev.wekeo.apps.eo4eu.eu'
username_dev = subprocess.check_output(["pass", "eo4eu/openeo-username-dev"], text=True).strip()
password_dev = subprocess.check_output(["pass", "eo4eu/openeo-password-dev"], text=True).strip()

if __name__ == "__main__":
    client = Client(development, username_dev, password_dev)
    status = "PUBLISHING"
    cfs = "FALSE"
    workflows = client.list_workflows(status, cfs)
    print(workflows)
