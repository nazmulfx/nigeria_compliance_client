import base64
import json
import time
from io import BytesIO

import frappe
import qrcode
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def before_validate(doc, method):
    pass
    




