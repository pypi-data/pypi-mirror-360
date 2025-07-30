from fastmcp import Context as ServerContext

from devopness.models import UserMe

from ..auth import get_credentials
from ..devopness_api import devopness, ensure_authenticated


class UserService:
    @staticmethod
    async def tool_get_user_profile(
        ctx: ServerContext,
    ) -> UserMe:
        await ensure_authenticated(get_credentials(ctx))
        current_user = await devopness.users.get_user_me()

        return current_user.data
