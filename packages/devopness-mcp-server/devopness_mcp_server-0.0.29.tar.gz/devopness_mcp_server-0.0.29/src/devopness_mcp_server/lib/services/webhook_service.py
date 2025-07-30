from fastmcp import Context as ServerContext

from devopness.models import Hook, HookPipelineCreate, HookTypeParam

from ..auth import get_credentials
from ..devopness_api import devopness, ensure_authenticated


class WebHookService:
    @staticmethod
    async def tool_create_webhook(
        ctx: ServerContext,
        pipeline_id: int,
        hook_type: HookTypeParam,
        hook_settings: HookPipelineCreate,
    ) -> Hook:
        await ensure_authenticated(get_credentials(ctx))
        response = await devopness.hooks.add_pipeline_hook(
            hook_type,
            pipeline_id,
            hook_settings,
        )

        return response.data
