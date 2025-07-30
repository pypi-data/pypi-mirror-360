from typing import Dict, Optional

from loguru import logger
from sqlalchemy.orm import Session

from fastpluggy.core.models import ModuleRepository
from fastpluggy.core.tools.git_tools import GitInfo


def update_plugin_status(db: Session, plugin_name: str, status: bool) -> bool:
    """
    Update the status of a plugin in the database.

    :param db: The database session.
    :param plugin_name: The name of the plugin.
    :param status: The new status of the plugin (True for enabled, False for disabled).
    :return: True if the plugin's status was updated successfully, False otherwise.
    """
    # Check if the plugin exists in the database
    plugin = db.query(ModuleRepository).filter_by(name=plugin_name).first()

    if plugin is None:
        logger.error(f"Plugin '{plugin_name}' does not exist in the database.")
        plugin = ModuleRepository(name=plugin_name)

    # Update the plugin status
    plugin.active = status
    db.add(plugin)
    db.commit()

    logger.info(f"Plugin '{plugin_name}' status updated to {status}.")
    return True


def get_all_modules_status(db: Session) -> Dict[str, bool]:
    """
    Retrieves plugin status from the database and populates the plugin_states dictionary.
    """
    plugin_states = {}
    if not db:
        logger.warning("Database session is not set for PluginManager.")
        return plugin_states

    module_records = db.query(ModuleRepository).all()
    if module_records:
        plugin_states = {module.name: module.active for module in module_records}

    logger.info(f"Loaded plugin states: {plugin_states}")

    return plugin_states

def save_or_update_plugin_git_info(
    db: Session,
    plugin_name: str,
    git_info: Optional[GitInfo]
):
    """
    Save a new plugin or update an existing one based on GitInfo, only if values differ.

    :param db: SQLAlchemy session.
    :param plugin_name: The name of the plugin.
    :param git_info: GitInfo instance containing current and latest version info.
    """
    existing_plugin = db.query(ModuleRepository).filter_by(name=plugin_name).first()
    updated = False

    current_version = git_info.current_version if git_info else None
    last_version = git_info.latest_version if git_info else None
    git_url = git_info.remote_branch if git_info else None

    if existing_plugin:
        if git_url is not None and existing_plugin.git_url != git_url:
            existing_plugin.git_url = git_url
            updated = True

        if current_version is not None and existing_plugin.current_version != current_version:
            existing_plugin.current_version = current_version
            updated = True

        if last_version is not None and existing_plugin.last_version != last_version:
            existing_plugin.last_version = last_version
            updated = True

        if updated:
            db.add(existing_plugin)
            logger.info(f"Updated plugin '{plugin_name}' in the database.")
        else:
            logger.debug(f"No changes detected for plugin '{plugin_name}' — skipping update.")
    else:
        new_plugin = ModuleRepository(
            name=plugin_name,
            git_url=git_url,
            current_version=current_version,
            last_version=last_version
        )
        db.add(new_plugin)
        logger.info(f"Added new plugin '{plugin_name}' to the database.")
        updated = True

    if updated:
        db.commit()
