"""SageMaker Studio Identity Provider Class

This extends jupyter_server IdentityProvider interface
to provide SageMaker Studio user profile name as user name in Real Time Collaboration mode

"""

from jupyter_server.auth.identity import IdentityProvider, User
from jupyter_server.base.handlers import JupyterHandler


class SagemakerIdentityProvider(IdentityProvider):
    def get_user(self, handler: JupyterHandler) -> User:
        """Get User Info
        Get SageMaker Studio user profile from cookie "studioUserProfileName" and return as a User type

        """
        studio_user_profile_name = handler.get_cookie("studioUserProfileName")

        if not studio_user_profile_name:
            studio_user_profile_name = "User"

        user_id = name = display_name = studio_user_profile_name
        initials = studio_user_profile_name[0].upper()
        color = None
        return User(user_id, name, display_name, initials, None, color)
