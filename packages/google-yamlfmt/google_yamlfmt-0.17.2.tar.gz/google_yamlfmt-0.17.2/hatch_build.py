from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

PY_PLATFORM_MAPPING = {
    ("Linux", "x86_64"): ("musllinux_1_2", "x86_64"),
    ("Linux", "i686"): ("musllinux_1_2", "i686"),
    ("Linux", "armv7l"): ("musllinux_1_2", "armv7l"),
    ("Linux", "aarch64"): ("musllinux_1_2", "aarch64"),
    ("Darwin", "x86_64"): ("macosx_10_12", "x86_64"),
    ("Darwin", "arm64"): ("macosx_11_0", "arm64"),
    ("Windows", "AMD64"): ("win", "amd64"),
    ("Windows", "ARM64"): ("win", "arm64"),
}

# key 为 pypi 分发的系统和架构组合
BUILD_TARGET = {
    ("musllinux_1_2", "x86_64"): ("linux", "amd64"),
    ("musllinux_1_2", "i686"): ("linux", "386"),
    ("musllinux_1_2", "armv7l"): ("linux", "arm"),
    ("musllinux_1_2", "aarch64"): ("linux", "arm64"),
    ("manylinux_2_17", "x86_64"): ("linux", "amd64"),
    ("manylinux_2_17", "aarch64"): ("linux", "arm64"),
    ("macosx_10_12", "x86_64"): ("darwin", "amd64"),
    ("macosx_11_0", "arm64"): ("darwin", "arm64"),
    ("win", "amd64"): ("windows", "amd64"),
    ("win", "arm64"): ("windows", "arm64"),
}


class SpecialBuildHook(BuildHookInterface):
    BIN_NAME = "yamlfmt"
    YAMLFMT_REPO = "https://github.com/google/yamlfmt.git"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp_dir = Path(tempfile.mkdtemp())

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        # 仅在构建 Wheel 文件时执行此逻辑
        if self.target_name != "wheel":
            return

        # 获取系统信息
        system_info = get_system_info()
        default_os_mapping = (None, None)

        # 获取目标架构和平台信息
        target_arch = os.environ.get("CIBW_ARCHS") or PY_PLATFORM_MAPPING.get(system_info, default_os_mapping)[1]
        target_os_info = os.environ.get("CIBW_PLATFORM") or PY_PLATFORM_MAPPING.get(system_info, default_os_mapping)[0]

        # 确保目标架构和平台信息有效
        assert target_arch is not None, (
            f"CIBW_ARCHS not set and no mapping found in PY_PLATFORM_MAPPING for: {system_info}"
        )
        assert target_os_info is not None, (
            f"CIBW_PLATFORM not set and no mapping found in PY_PLATFORM_MAPPING for: {system_info}"
        )

        assert (target_os_info, target_arch) in BUILD_TARGET, f"Unsupported target: {target_os_info}, {target_arch}"

        # 构建完整的 Wheel 标签
        full_wheel_tag = f"py3-none-{target_os_info}_{target_arch}"
        build_data["tag"] = full_wheel_tag

        # 构建 yamlfmt 二进制文件
        self.build_yamlfmt(target_os_info, target_arch)

        # 将构建好的二进制文件添加到 wheel 中
        bin_path = self.temp_dir / self.BIN_NAME

        assert bin_path.is_file(), f"{self.BIN_NAME} not found after build"
        build_data["force_include"][str(bin_path.resolve())] = f"yamlfmt/{self.BIN_NAME}"

    def build_yamlfmt(self, target_os_info: str, target_arch: str) -> None:
        """Build the yamlfmt binary for the specified OS and architecture."""
        # 确认环境安装
        for command in ["go", "make", "git"]:
            assert shutil.which(command), f"{command} is not installed or not found in PATH"

        build_target = BUILD_TARGET[(target_os_info, target_arch)]

        # 编译逻辑可以在这里添加
        version = re.sub(
            r"(?:a|b|rc)\d+|\.post\d+|\.dev\d+$", "", self.metadata.version
        )  # 去掉版本号中的后缀, alpha/beta/rc/post/dev

        # clone repo
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                f"v{version}",
                self.YAMLFMT_REPO,
                str(self.temp_dir / f"yamlfmt-{version}"),
            ],
            check=True,
        )

        # 编译
        env = os.environ.copy()
        env.update({"GOOS": build_target[0], "GOARCH": build_target[1]})
        if target_arch == "armv7l":
            env.update({"GOARM": "7"})

        # 检查工作目录是否存在
        work_dir = self.temp_dir / f"yamlfmt-{version}"
        assert work_dir.exists(), f"Working directory {work_dir} does not exist"

        subprocess.run(
            ["make", "build"],
            env=env,
            cwd=work_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        # 检查生成的二进制文件是否存在
        bin_path = work_dir / "dist" / self.BIN_NAME
        assert bin_path.exists(), f"Binary file {bin_path} was not created"

        # 将二进制文件复制到临时目录的根目录，供后续使用
        shutil.copy2(bin_path, self.temp_dir / self.BIN_NAME)

    def finalize(self, version, build_data, artifact_path):
        # 清理临时目录
        try:
            shutil.rmtree(self.temp_dir)
        except (OSError, PermissionError) as e:
            print(f"Warning: Failed to remove temp directory {self.temp_dir}: {e}")
        super().finalize(version, build_data, artifact_path)


def get_system_info():
    system = platform.system()
    machine = platform.machine()
    return system, machine
