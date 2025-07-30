from importlib.metadata import version

import structlog

logger = structlog.getLogger(__name__)


class VersionResolver:
    @staticmethod
    def get_version_for_package(package_name: str) -> str | None:
        try:
            return version(package_name)
        except (ImportError, ValueError) as e:
            logger.warning(
                "failed to get version for package",
                package_name=package_name,
                error_detail=str(e),
                error_type=type(e).__name__,
            )
        return None
