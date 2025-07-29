"""Token Manager"""

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from swifty.auth.constants import LogEvents, ACCESS_TOKEN, REFRESH_TOKEN
from swifty.logging.logger import SwiftyLoggerMixin


class AccessTokenManager(SwiftyLoggerMixin):
    """Manages JWT access token operations including rotation and validation"""

    def __init__(self, token_data: dict[str, str]) -> None:
        self.token_data = token_data

    def rotate_new_token(self, refresh_token: str) -> str:
        """Generates new access token using refresh token

        Args:
            refresh_token: JWT refresh token string
        Returns:
            New access token string
        """
        self.token_data[ACCESS_TOKEN] = str(RefreshToken(refresh_token).access_token)
        self.logger.info(LogEvents.ROTATED_NEW_TOKEN)
        return self.token_data[ACCESS_TOKEN]

    @property
    def access_token(self) -> str:
        """Validates and returns access token, rotating if necessary

        Raises:
            AuthenticationFailed: When access token is missing
            TokenError: When token validation fails
        """
        if not (token := self.token_data.get(ACCESS_TOKEN)):
            raise AuthenticationFailed

        try:
            return str(AccessToken(token=token, verify=True))
        except (TokenError, InvalidToken):
            return self.rotate_new_token(self.token_data[REFRESH_TOKEN])
