from pathlib import Path
from typing import Optional, Union, List
try:
    from backend.app.core.logging import logger
except ImportError:
    from app.core.logging import logger


class CleanupService:
    """
    Manages deterministic, privacy-first deletion of temporary files.
    Guarantees no residual customer document artifacts linger on the host filesystem.
    """

    @staticmethod
    def cleanup_file(filepath: Optional[Union[str, Path]]) -> bool:
        if not filepath:
            return False

        path = Path(filepath)
        try:
            if path.exists() and path.is_file():
                path.unlink(missing_ok=True)
                logger.info(f"Temporary document file securely deleted: {path.name}")
                return True
        except Exception as e:
            logger.error(f"Error deleting temporary file {path.name}: {str(e)}")
            return False

        return False

    @staticmethod
    def cleanup_files(filepaths: List[Union[str, Path]]) -> None:
        for fp in filepaths:
            CleanupService.cleanup_file(fp)


cleanup_service = CleanupService()
