from pathlib import Path

from git import Repo, GitCommandError
from loguru import logger

from fastpluggy.core.base_module_manager import BaseModuleManager
from fastpluggy.core.models import ModuleRepository
from fastpluggy.core.plugin.repository import save_or_update_plugin_git_info
from fastpluggy.core.plugin.service import PluginService
from fastpluggy.core.tools.git_tools import get_git_info_for_module


class GitPluginInstaller:
    def __init__(self, plugin_manager: BaseModuleManager):
        self.plugin_manager = plugin_manager
        self.install_folder = plugin_manager.fast_pluggy.get_folder_by_module_type('plugin')

    def _apply_git_update(self, plugin_name: str, plugin_path: Path, update_method: str = "pull", git_url: str = None):
        """
        Core logic to clone or update a plugin. `update_method` can be:
        - "clone" = clone if path doesn't exist
        - "pull" = regular update
        - "stash" / "discard" = handle dirty state
        """
        action = "installed" if update_method == "clone" else "updated"
        stashed = False

        try:
            if update_method == "clone":
                Repo.clone_from(git_url, str(plugin_path))
                repo = Repo(str(plugin_path))
            else:
                repo = Repo(str(plugin_path))
                is_dirty = repo.is_dirty(untracked_files=True)

                if is_dirty:
                    if update_method == "stash":
                        repo.git.stash('save')
                        stashed = True
                        logger.info(f"[GitInstaller] Stashed changes in '{plugin_name}' before pull.")
                    elif update_method == "discard":
                        repo.git.reset('--hard')
                        repo.git.clean('-fd')
                        logger.info(f"[GitInstaller] Discarded local changes in '{plugin_name}'.")
                    elif update_method == "none":
                        return {"status": "error", "message": f"Local changes in '{plugin_name}', cannot continue."}

                repo.git.pull()
                if stashed:
                    repo.git.stash('pop')

            PluginService.enable_plugin(plugin_name, fast_pluggy=self.plugin_manager.fast_pluggy)
            logger.info(
                f"Plugin '{plugin_name}' {action} from Git successfully. "
                f"Plugin '{plugin_name}' is now enabled."
            )
            git_info, version = None, None
            plugin_state = self.plugin_manager.modules.get(plugin_name)
            if plugin_state:
                git_info = get_git_info_for_module(plugin_state)
                save_or_update_plugin_git_info(git_info=git_info, plugin_name=plugin_name,db=self.plugin_manager.db_session)
                version = git_info.current_version[:8] if git_info.current_version else None

            self.plugin_manager.refresh_plugins_states()

            return {
                "status": "success",
                "action": action,
                "plugin_name": plugin_name,
                "version": version,
                "git_info": git_info,
                "message": f"Plugin '{plugin_name}' {action} from Git successfully"
            }

        except GitCommandError as e:
            logger.exception(f"[GitInstaller] Git command failed for '{plugin_name}': {e}")
            return {"status": "error", "message": f"Git command failed: {e}"}
        except Exception as e:
            logger.exception(f"[GitInstaller] Failed to update plugin '{plugin_name}': {e}")
            return {"status": "error", "message": f"Unexpected error: {e}"}

    def install_or_update_plugin(self, plugin_name: str, git_url: str):
        plugin_path = Path(self.install_folder) / plugin_name
        if not plugin_path.exists():
            result = self._apply_git_update(plugin_name, plugin_path, update_method="clone", git_url=git_url)
        else:
            result = self._apply_git_update(plugin_name, plugin_path, update_method="pull")

        if result["status"] == "success":
            PluginService.enable_plugin(plugin_name, fast_pluggy=self.plugin_manager.fast_pluggy)
            logger.info(f"Plugin '{plugin_name}' is now enabled.")

        return result

    def update_plugin(self, plugin_name: str, update_method: str):
        db = self.plugin_manager.db_session
        plugin_repo = db.query(ModuleRepository).filter_by(name=plugin_name).first()
        if not plugin_repo:
            return {"status": "error", "message": f"Plugin '{plugin_name}' not found in DB"}

        module_info = self.plugin_manager.modules.get(plugin_name)
        plugin_path = Path(module_info.path)

        result = self._apply_git_update(plugin_name, plugin_path, update_method=update_method)
        return result

    def check_all_updates(self):
        updates = []
        db = self.plugin_manager.db_session

        for name, module in self.plugin_manager.modules.items():
            try:
                info = get_git_info_for_module(module)
                if info and info.have_update:
                    updates.append({
                        "plugin": name,
                        "current_version": info.current_version,
                        "latest_version": info.latest_version
                    })

                    save_or_update_plugin_git_info(
                        db=db,
                        plugin_name=name,
                        git_info=info,
                    )
            except Exception as e:
                logger.warning(f"[GitInstaller] Failed to check update for {name}: {e}")

        return updates
