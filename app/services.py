import base64
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from typing import Optional
from fastapi import Header, Depends, HTTPException

import requests
from app.db import SessionLocal
from app.core.config import (ALG, JWKS_URL, BACKEND_AUDIENCE, IDP_ISS)
import logging


from .auth import get_claims, get_principal, require_role
