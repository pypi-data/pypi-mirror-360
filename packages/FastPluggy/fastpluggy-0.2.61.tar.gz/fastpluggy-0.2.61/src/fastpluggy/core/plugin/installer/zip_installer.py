import os
import zipfile
from fastapi import UploadFile
from loguru import logger

from fastpluggy.core.tools.fs_tools import extract_zip


class ZipPluginInstaller:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.install_folder = plugin_manager.fast_pluggy.get_folder_by_module_type('plugin')

    def install_from_zip(self, file: UploadFile):
        if not file.filename.endswith(".zip"):
            return {"status": "error", "message": "The file must be a ZIP archive"}

        try:
            extract_zip(file, target_folder=self.install_folder)

            plugin_name = os.path.splitext(file.filename)[0]
            if not self.plugin_manager.module_directory_exists(plugin_name):
                return {"status": "error", "message": f"Plugin '{plugin_name}' was not installed correctly"}

            return {
                "status": "success",
                "message": f"Plugin '{plugin_name}' installed from ZIP successfully",
                "plugin_name": plugin_name,
            }

        except zipfile.BadZipFile:
            return {"status": "error", "message": "The ZIP file is corrupt or invalid"}

        except Exception as e:
            logger.exception(f"[ZipInstaller] Error installing plugin: {e}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
