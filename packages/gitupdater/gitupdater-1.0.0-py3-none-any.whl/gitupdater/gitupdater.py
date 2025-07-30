from revoltlogger import Logger
from revoltutils import AsyncTempdir, ProgressBar, FileUtils
import asyncio
import httpx
from rich.console import Console
from rich.markdown import Markdown
import shutil
import os
import aiofiles
import sys
from colorama import Fore,Style,init
init(autoreset=True)

class GitUpdater:
    def __init__(self, repository: str, current_version: str,toolname:str) -> None:
        self.logger = Logger()
        self.repo = repository
        self.current_version = current_version
        self.tempdir = AsyncTempdir()
        self.dirpath = None
        self.console = Console()
        self.fileutils = FileUtils()
        self.red = Fore.RED
        self.green = Fore.GREEN
        self.yellow = Fore.YELLOW
        self.blue = Fore.BLUE
        self.magenta = Fore.MAGENTA
        self.cyan = Fore.CYAN
        self.white = Fore.WHITE
        self.bold = Style.BRIGHT
        self.reset = Style.RESET_ALL
        self.toolname = toolname

    async def __aenter__(self):
        self.dirpath = await self.tempdir.create()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.tempdir.close()

    def detect_installer(self) -> str | None:
        for tool in ["uv", "pipx", "pip"]:
            if shutil.which(tool):
                return tool
        return None

    async def fetch_latest_release_info(self):
        url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching release info: {e}")
        return None

    async def install_zip(self, zip_path: str, installer: str) -> bool:
        self.logger.info(f"Installing using {installer}...")
        cmd = []

        if installer == "uv":
            cmd = ["uv", "tool", "install", zip_path, "--force"]
        elif installer == "pipx":
            cmd = ["pipx", "install", zip_path, "--force"]
        elif installer == "pip":
            cmd = ["pip", "install", "--break-system-packages", "-U", zip_path]
        else:
            self.logger.error("No installer found.")
            return False

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()
        return process.returncode == 0

    async def download_zipball(self, zip_url: str, tag: str) -> str:
        filepath = os.path.join(self.dirpath, f"{self.repo.replace('/', '_')}_{tag}.zip")
        try:
            self.progress = ProgressBar(total=None, title="Downloading...")
            self.progress.start()
            async with httpx.AsyncClient(timeout=30,follow_redirects=True) as client:
                async with client.stream("GET", zip_url) as response:
                    if response.status_code == 200:
                        async with aiofiles.open(filepath, "wb") as f:
                            async for chunk in response.aiter_bytes():
                                await f.write(chunk)
                                self.progress.update()
            self.progress.close()
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to download zipball: {e}")
            return ""

    async def show_update_log(self):
        info = await self.fetch_latest_release_info()
        if info:
            body = info.get("body", "")
            if body:
                self.console.print(Markdown(body))
            else:
                self.logger.info("No changelog found.")
        else:
            self.logger.error("Could not fetch changelog.")

    async def update(self) -> bool:
        if self.dirpath is None:
            self.dirpath = await self.tempdir.create()

        info = await self.fetch_latest_release_info()
        if not info:
            self.logger.error("Could not fetch latest release.")
            return False

        latest_tag = info.get("tag_name", "")
        if not latest_tag:
            self.logger.error("No release tag found.")
            return False

        if self.current_version and self.current_version == latest_tag:
            self.logger.info(f"{self.toolname} Already in the latest version")
            return True

        zip_url = info.get("zipball_url")
        if not zip_url:
            self.logger.error("No zipball URL found.")
            return False

        installer = self.detect_installer()
        if not installer:
            self.logger.error("No supported installer found (uv, pipx, pip).")
            return False

        zip_path = await self.download_zipball(zip_url, latest_tag)
        if not zip_path or not await self.fileutils.file_exist(zip_path):
            return False

        success = await self.install_zip(zip_path, installer)
        if self.tempdir:
            await self.tempdir.close()

        if success:
            self.logger.success(f"Successfully updated {self.toolname} from {self.current_version} → {latest_tag}")
            return True
        else:
            self.logger.error("Installation failed.")
            return False

    async def versionlog(self) -> None:
        info = await self.fetch_latest_release_info()
        if not info:
            self.logger.warn("Could not fetch latest release.")
            return None

        latest = info.get("tag_name", "")
        if not latest:
            self.logger.warn("Could not fetch latest release.")
            return None
        if self.current_version == latest:
            print(
                f"[{self.blue}{self.bold}version{self.reset}]:{self.bold}{self.white}{self.toolname} current version {self.current_version} ({self.green}latest{self.reset}{self.bold}{self.white}){self.reset}",
                file=sys.stderr
            )
        else:
            print(
                f"[{self.blue}{self.bold}version{self.reset}]:{self.bold}{self.white}{self.toolname} current version {self.current_version} ({self.red}outdated{self.reset}{self.bold}{self.white}){self.reset}",
            file=sys.stderr
            )
        return None