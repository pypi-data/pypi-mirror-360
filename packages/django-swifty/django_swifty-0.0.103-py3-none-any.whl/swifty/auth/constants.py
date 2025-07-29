"""Constants"""

from dataclasses import dataclass


@dataclass
class LogEvents:
    """_summary_"""

    ROTATED_NEW_TOKEN = "ROTATED_NEW_TOKEN"
    PERMISSIONS_DENIED_BY_ERROR = "PERMISSIONS_DENIED_BY_ERROR"


JWT_TOKEN = "jwt_token"
REFRESH_TOKEN = "refresh"
ACCESS_TOKEN = "access"
