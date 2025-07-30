import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from nacwrap import nacwrap

fr = datetime.now() - timedelta(hours=3)
to = datetime.now()

res = nacwrap.instances_list(workflow_name="Form 279", from_datetime=fr, to_datetime=to)

pass
