from sentry_sdk import init
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sanic import SanicIntegration
from decouple import config
from sanic.log import logger


def get_unsampled_status_list() -> set[int]:
    return set(config("SENTRY_UNSAMPLED_STATUS", cast=str, default="").split(","))

def version():
    print("VERSION TEST")


def activate_sentry():
    if config("SENTRY_IS_ACTIVE", cast=bool, default=False):
        sentry_dsn = config("SENTRY_DSN", cast=str, default=None)

        if not sentry_dsn:
            logger.warn("Sentry DSN not configured")
            return

        init(
            dsn=config("SENTRY_DSN"),
            send_default_pii=True,
            traces_sample_rate=1.0,
            integrations=[
                AsyncioIntegration(),
                SanicIntegration(
                    unsampled_statuses=get_unsampled_status_list()
                ),
            ],
        )
        return

    logger.warn("Sentry is not activated")
