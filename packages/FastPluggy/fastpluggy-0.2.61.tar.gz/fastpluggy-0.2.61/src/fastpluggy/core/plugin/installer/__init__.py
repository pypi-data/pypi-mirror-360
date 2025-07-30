from fastapi import UploadFile

from fastpluggy.core.base_module_manager import BaseModuleManager
from fastpluggy.core.plugin.installer.zip_installer import ZipPluginInstaller
from fastpluggy.core.tools.git_tools import is_git_installed


class PluginInstaller:
    def __init__(self, plugin_manager : BaseModuleManager):
        self.plugin_manager = plugin_manager

        self.git_available= is_git_installed()
        if self.git_available:
            from fastpluggy.core.plugin.installer.git_installer import GitPluginInstaller

            self.git_installer = GitPluginInstaller(plugin_manager)
        self.zip_installer = ZipPluginInstaller(plugin_manager)

        # todo: create dir/module only when needed
        # folder_path.mkdir(parents=True, exist_ok=True)
        # create_init_file(folder)

    def install_from_git(self, plugin_name, git_url):
        if not self.git_available:
            return {"status": "error", "message": "Git is not installed"}
        return self.git_installer.install_or_update_plugin(plugin_name, git_url)

    def update_from_git(self, plugin_name, update_method):
        if not self.git_available:
            return {"status": "error", "message": "Git is not installed"}
        return self.git_installer.update_plugin(plugin_name, update_method)

    def check_all_plugin_updates(self):
        if not self.git_available:
            return {"status": "error", "message": "Git is not installed"}
        return self.git_installer.check_all_updates()

    def extract_and_install_zip(self, file: UploadFile):
        return self.zip_installer.install_from_zip(file)
