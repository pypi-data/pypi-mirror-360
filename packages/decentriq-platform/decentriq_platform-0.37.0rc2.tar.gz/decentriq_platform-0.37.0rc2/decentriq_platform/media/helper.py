from datetime import datetime
import uuid


def generate_id() -> str:
    return str(uuid.uuid4())

def current_iso_standard_utc_time() -> str:
    return str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"))[:-3] + "Z"