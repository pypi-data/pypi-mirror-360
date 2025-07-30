import importlib
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from contextlib import contextmanager
from typing import Callable, Generator, List


class ModuleImportManager:
    """Module operation utilities for QoreClient"""

    def __init__(
        self,
        get_file_method: Callable,
        upload_file_method: Callable,
    ):
        """
        Initialize with required methods from the parent client

        :param request_method: The _request method from QoreClient
        :param get_file_list_method: Method to get file list from folder
        :param get_file_method: Method to download file content
        :param upload_file_method: Method to upload file from path
        """
        self._get_file = get_file_method
        self._upload_file = upload_file_method

    #
    # Public module import methods
    #

    @contextmanager
    def get_module(
        self,
        wheel_file_id: str,
    ) -> Generator[pathlib.Path, None, None]:
        """
        Context manager that downloads and installs a wheel file from drive to a temporary directory.
        The wheel file and installed packages will be automatically deleted when the context exits.

        Usage example:
        with client.import_wheel(wheel_file_id) as wheel_dir:
            import my_package  # Use temporarily installed wheel package
            # Use my_package
        # Here, the package is uninstalled and temporary files are deleted

        :param wheel_file_id: Drive ID of the wheel file
        :return: Path to the wheel installation directory
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            download_dir = temp_path / "download"
            install_dir = temp_path / "install"

            # Create directories
            download_dir.mkdir(exist_ok=True)
            install_dir.mkdir(exist_ok=True)

            # Download wheel file
            wheel_path = download_dir / f"{wheel_file_id}.whl"
            wheel_path.write_bytes(self._get_file(wheel_file_id).getvalue())

            # Install wheel file
            module_dir = install_dir / wheel_file_id
            module_dir.mkdir(exist_ok=True)
            installed_modules = self._install_wheel(wheel_path, module_dir)

            # Temporarily add to sys.path
            original_path = sys.path.copy()
            sys.path.insert(0, str(module_dir))

            try:
                # Reset cache for installed modules
                self._reload_modules(installed_modules)
                yield module_dir
            finally:
                # Restore sys.path - temporary directory will be auto-deleted
                sys.path = original_path

    #
    # Public module building methods
    #

    def build_module(self, module_path, output_dir=None, version="0.1.0"):
        """
        Build a single file or simple module into a wheel package.

        :param module_path: Path to the file or directory to build
        :param output_dir: Directory where wheel file will be saved (default: current directory)
        :param version: Package version (default: 0.1.0)
        :return: Path to the generated wheel file
        """
        module_path = pathlib.Path(module_path)

        if not module_path.exists():
            raise FileNotFoundError(f"Path not found: {module_path}")

        package_name = self._get_valid_package_name(module_path)

        # Set output directory
        output_dir = self._prepare_output_dir(output_dir)

        # Create temporary project directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            pkg_dir = temp_path / package_name
            pkg_dir.mkdir()

            # Create pyproject.toml
            self._create_pyproject_toml(temp_path, package_name, version)

            # Copy file or directory
            self._copy_module_files(module_path, pkg_dir)

            # Build wheel
            wheel_path = self._build_wheel(temp_path, output_dir, package_name, version)

            return wheel_path

    def build_and_upload_module(self, module_path, folder_id, version="0.1.0"):
        """
        Build a single file or simple module into a wheel package and upload to Qore drive.

        :param module_path: Path to the file or directory to build
        :param folder_id: Qore drive folder ID to upload to
        :param version: Package version (default: 0.1.0)
        :return: Response info for the uploaded wheel file
        """
        # Build wheel in a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            wheel_path = self.build_module(module_path, temp_dir, version)

            # Upload file using upload_file method
            upload_response = self._upload_file(str(wheel_path), folder_id=folder_id)

            wheel_file_id = upload_response.get("id")
            if wheel_file_id is None:
                raise RuntimeError("Failed to upload wheel file")

            package_name = self._get_valid_package_name(pathlib.Path(module_path))

            module_path = pathlib.Path(module_path)
            if module_path.is_file():
                import_line = f"from {package_name} import your_function"
            else:
                # 폴더 내 첫 번째 .py 파일명 (init 제외)
                py_files = [f.stem for f in module_path.glob("*.py") if f.name != "__init__.py"]
                first_file = py_files[0] if py_files else "your_module"
                import_line = f"from {package_name}.{first_file} import your_function"

            print(
                f"""
================================================================================
Module uploaded successfully!
You can use your module in your code as follows:

<Example usage>
with qc.get_module("{wheel_file_id}"):
    {import_line}
================================================================================
"""
            )
            return upload_response

    #
    # Internal helper methods for importing
    #

    def _install_wheel(self, wheel_file: pathlib.Path, target_dir: pathlib.Path) -> List[str]:
        """
        Install a wheel file to the specified directory

        :param wheel_file: Path to the wheel file
        :param target_dir: Target directory for installation
        :return: List of installed module names
        """
        installed_modules = set()
        with zipfile.ZipFile(wheel_file, "r") as wheel_zip:
            wheel_zip.extractall(target_dir)
            for path in wheel_zip.namelist():
                if path.endswith("__init__.py"):
                    pkg_dir = path.rsplit("/", 1)[0]
                    if pkg_dir and not pkg_dir.endswith(".dist-info"):
                        installed_modules.add(pkg_dir)
        return list(installed_modules)

    def _reload_modules(self, module_names: List[str]) -> None:
        """
        Reload modules if they exist in sys.modules

        :param module_names: List of module names to reload
        """
        for module_name in module_names:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])

    #
    # Internal helper methods for building
    #

    def _get_valid_package_name(self, module_path: pathlib.Path) -> str:
        """
        Generate a valid package name from a file or directory path

        :param module_path: Path to the file or directory
        :return: Valid package name
        """
        package_name = module_path.stem if module_path.is_file() else module_path.name

        # Remove invalid characters from package name
        package_name = "".join(c if c.isalnum() or c == "_" else "_" for c in package_name)
        if package_name[0].isdigit():
            package_name = f"module_{package_name}"

        return package_name

    def _prepare_output_dir(self, output_dir) -> pathlib.Path:
        """
        Prepare the output directory for wheel files

        :param output_dir: Specified output directory or None
        :return: Path object for the output directory
        """
        if output_dir is None:
            output_dir = pathlib.Path.cwd() / "dist"
        else:
            output_dir = pathlib.Path(output_dir)

        output_dir.mkdir(exist_ok=True, parents=True)
        return output_dir

    def _create_pyproject_toml(
        self, temp_path: pathlib.Path, package_name: str, version: str
    ) -> None:
        """
        Create a pyproject.toml file for the package

        :param temp_path: Path to the temporary directory
        :param package_name: Package name
        :param version: Package version
        """
        with open(temp_path / "pyproject.toml", "w") as f:
            f.write(f"""
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "{version}"
description = "Automatically generated package"
requires-python = ">=3.7"
            """)

    def _copy_module_files(self, module_path: pathlib.Path, pkg_dir: pathlib.Path) -> None:
        """
        Copy files from the source module to the package directory

        :param module_path: Path to the source file or directory
        :param pkg_dir: Path to the target package directory
        """
        if module_path.is_file():
            self._copy_file_to_package(module_path, pkg_dir)
        else:
            self._copy_directory_to_package(module_path, pkg_dir)

    def _copy_file_to_package(self, file_path: pathlib.Path, pkg_dir: pathlib.Path) -> None:
        """
        Copy a single file to a package directory

        :param file_path: Path to the file
        :param pkg_dir: Path to the target package directory
        """
        if file_path.suffix == ".py":
            # Create __init__.py that imports everything from the module
            with open(pkg_dir / "__init__.py", "w") as f:
                f.write(f"from .{file_path.stem} import *\n")
            shutil.copy(file_path, pkg_dir / file_path.name)
        else:
            # Copy other files as-is
            shutil.copy(file_path, pkg_dir / file_path.name)

    def _copy_directory_to_package(self, dir_path: pathlib.Path, pkg_dir: pathlib.Path) -> None:
        """
        Copy a directory to a package directory

        :param dir_path: Path to the source directory
        :param pkg_dir: Path to the target package directory
        """
        # Copy directory contents
        for item in dir_path.glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to(dir_path)
                target = pkg_dir / rel_path
                target.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy(item, target)

        # Create __init__.py if it doesn't exist
        if not (pkg_dir / "__init__.py").exists():
            with open(pkg_dir / "__init__.py", "w") as f:
                f.write("# Auto-generated __init__.py\n")

    def _build_wheel(
        self, temp_path: pathlib.Path, output_dir: pathlib.Path, package_name: str, version: str
    ) -> pathlib.Path:
        """
        Build a wheel file from the package

        :param temp_path: Path to the temporary directory with package files
        :param output_dir: Output directory for the wheel file
        :param package_name: Package name
        :param version: Package version
        :return: Path to the built wheel file
        """
        # Build wheel
        cmd = [sys.executable, "-m", "build", "--wheel", "--outdir", str(output_dir)]
        result = subprocess.run(cmd, cwd=temp_path, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Wheel build failed: {result.stderr}")

        # Find generated wheel file
        wheel_files = list(output_dir.glob(f"{package_name.replace('-', '_')}-{version}-*.whl"))
        if not wheel_files:
            raise FileNotFoundError("Wheel file not found")

        return wheel_files[0]
