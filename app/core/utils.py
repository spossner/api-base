import base64
import uuid


def create_id():
    random_bytes = uuid.uuid4().bytes
    return base64.urlsafe_b64encode(random_bytes).decode("ascii").rstrip("=")
