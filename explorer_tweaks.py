#!/usr/bin/env python3
"""
ExplorerTweaks v2.6.0 - Windows File Explorer Configuration Utility
Pixel-accurate Windows 11 File Explorer and Taskbar simulation.

Author: SysAdminDoc
License: MIT
"""

import multiprocessing
multiprocessing.freeze_support()

import ctypes
import customtkinter as ctk
from tkinter import messagebox
import winreg
import platform
import subprocess
import json
import sys
import os
import argparse
import base64
import glob as glob_module
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import Optional, Callable, List, Any, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

APP_NAME = "ExplorerTweaks"
APP_VERSION = "2.6.0"
DARKMODE_TASK_NAME = r"\ExplorerTweaks\DarkModeAutoSwitch"
DARKMODE_SCRIPT_NAME = "darkmode_auto_switch.ps1"

# Global dry-run flag
DRY_RUN = False

REFRESH_NONE = "none"
REFRESH_SHELL_NOTIFY = "shell_notify"
REFRESH_THEME_BROADCAST = "theme_broadcast"
REFRESH_EXPLORER_RESTART = "explorer_restart"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# App UI Colors
UI = {
    "bg": "#0a0a0a", "sidebar": "#0f0f0f", "card": "#161616",
    "hover": "#1f1f1f", "accent": "#1DB954", "accent_hover": "#1ed760",
    "text": "#ffffff", "text_sec": "#b0b0b0", "text_dim": "#707070",
    "border": "#2a2a2a", "on": "#4ade80", "off": "#f87171",
}

# Windows 11 Explorer Colors (Dark)
EXP_DARK = {
    "window_bg": "#202020",
    "titlebar": "#1f1f1f", "titlebar_text": "#ffffff", "titlebar_inactive": "#2d2d2d",
    "toolbar": "#2d2d2d", "toolbar_text": "#ffffff", "toolbar_icon": "#ffffff",
    "command_bar": "#2d2d2d",
    "nav_pane": "#1f1f1f", "nav_text": "#ffffff", "nav_hover": "#383838", "nav_selected": "#0078d4",
    "address_bg": "#383838", "address_text": "#ffffff", "address_icon": "#999999",
    "content_bg": "#1f1f1f", "content_text": "#ffffff", "content_dim": "#999999",
    "header_bg": "#2d2d2d", "header_text": "#999999", "header_border": "#383838",
    "row_hover": "#2d2d2d", "row_selected": "#0078d4", "row_selected_text": "#ffffff",
    "status_bg": "#1f1f1f", "status_text": "#999999",
    "scrollbar": "#555555", "scrollbar_bg": "#2d2d2d",
    "hidden": "#666666", "encrypted": "#00b050", "compressed": "#0078d4",
    "border": "#3d3d3d",
}

# Windows 11 Explorer Colors (Light)
EXP_LIGHT = {
    "window_bg": "#f3f3f3",
    "titlebar": "#f3f3f3", "titlebar_text": "#000000", "titlebar_inactive": "#f9f9f9",
    "toolbar": "#f9f9f9", "toolbar_text": "#000000", "toolbar_icon": "#000000",
    "command_bar": "#f9f9f9",
    "nav_pane": "#f3f3f3", "nav_text": "#000000", "nav_hover": "#e5e5e5", "nav_selected": "#cce8ff",
    "address_bg": "#ffffff", "address_text": "#000000", "address_icon": "#666666",
    "content_bg": "#ffffff", "content_text": "#000000", "content_dim": "#666666",
    "header_bg": "#f9f9f9", "header_text": "#666666", "header_border": "#e5e5e5",
    "row_hover": "#f5f5f5", "row_selected": "#cce8ff", "row_selected_text": "#000000",
    "status_bg": "#f3f3f3", "status_text": "#666666",
    "scrollbar": "#c0c0c0", "scrollbar_bg": "#f0f0f0",
    "hidden": "#999999", "encrypted": "#008000", "compressed": "#0066cc",
    "border": "#e5e5e5",
}

# Windows 11 Taskbar Colors
TASKBAR = {
    "bg": "#1c1c1c", "bg_glass": "#1c1c1c",
    "item_hover": "#ffffff1a", "item_active": "#ffffff26",
    "indicator": "#0078d4", "indicator_inactive": "#ffffff4d",
    "text": "#ffffff", "text_dim": "#999999",
    "search_bg": "#2c2c2c", "search_border": "#454545", "search_text": "#999999",
    "tray_hover": "#ffffff1a",
}


class OSVersion(Enum):
    WINDOWS_10 = "10"
    WINDOWS_11_21H2 = "11_21H2"
    WINDOWS_11_22H2 = "11_22H2"
    WINDOWS_11_23H2 = "11_23H2"
    WINDOWS_11_24H2 = "11_24H2"
    UNKNOWN = "unknown"


@dataclass
class PreviewState:
    show_extensions: bool = False
    show_hidden: bool = False
    show_system: bool = False
    show_checkboxes: bool = False
    colored_encrypted: bool = False
    compact_mode: bool = False
    show_thumbnails: bool = True
    show_type_overlay: bool = True
    show_status_bar: bool = True
    full_row_select: bool = True
    show_tooltips: bool = True
    full_path_title: bool = False
    full_path_address: bool = False
    launch_to_thispc: bool = False
    expand_to_folder: bool = False
    show_all_folders: bool = False
    separate_process: bool = False
    restore_folders: bool = False
    use_sharing_wizard: bool = True
    show_recent: bool = True
    show_frequent: bool = True
    track_docs: bool = True
    track_apps: bool = True
    sync_notifications: bool = True
    silent_installs: bool = True
    bing_search: bool = True
    cortana: bool = True
    search_history: bool = True
    taskview_button: bool = True
    widgets_button: bool = True
    center_taskbar: bool = True
    end_task: bool = False
    search_mode: int = 2
    taskbar_animations: bool = True
    aero_peek: bool = True
    disable_thumb_cache: bool = False
    snap_assist: bool = True
    snap_layouts: bool = True
    dark_mode: bool = True
    show_gallery: bool = True
    classic_context_menu: bool = False


@dataclass
class RegistrySetting:
    id: str
    name: str
    description: str
    category: str
    subcategory: str
    reg_path: str
    reg_name: str
    reg_type: str
    enable_value: Any
    disable_value: Any
    default_value: Any
    min_os: Optional[OSVersion] = None
    max_os: Optional[OSVersion] = None
    warning: Optional[str] = None
    inverted: bool = False
    preview_key: Optional[str] = None
    info: Optional[str] = None  # "Why it matters" explanation
    refresh_strategy: str = REFRESH_SHELL_NOTIFY


# ============================================================================
# WINDOWS UTILITIES
# ============================================================================

def get_windows_version() -> OSVersion:
    try:
        build = int(platform.version().split('.')[2])
        if build < 22000: return OSVersion.WINDOWS_10
        elif build < 22621: return OSVersion.WINDOWS_11_21H2
        elif build < 22631: return OSVersion.WINDOWS_11_22H2
        elif build < 26100: return OSVersion.WINDOWS_11_23H2
        else: return OSVersion.WINDOWS_11_24H2
    except: return OSVersion.UNKNOWN

@dataclass
class ShellRefreshReport:
    label: str
    dry_run: bool
    strategies: List[str]
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    restart_available: bool = True

    @property
    def success(self) -> bool:
        return not self.errors


def unique_refresh_strategies(strategies: List[str]) -> List[str]:
    ordered = []
    for strategy in strategies:
        if not strategy or strategy == REFRESH_NONE:
            continue
        if strategy not in ordered:
            ordered.append(strategy)
    return ordered


def shell_change_notify() -> None:
    shcne_assocchanged = 0x08000000
    shcnf_idlist = 0x0000
    ctypes.windll.shell32.SHChangeNotify(shcne_assocchanged, shcnf_idlist, None, None)


def broadcast_setting_change(area: str, timeout_ms: int = 5000) -> bool:
    hwnd_broadcast = 0xFFFF
    wm_settingchange = 0x001A
    smto_abortifhung = 0x0002
    result = ctypes.c_ulong()
    response = ctypes.windll.user32.SendMessageTimeoutW(
        hwnd_broadcast,
        wm_settingchange,
        0,
        area,
        smto_abortifhung,
        timeout_ms,
        ctypes.byref(result),
    )
    return bool(response)


def refresh_registry_strategies(
    strategies: List[str],
    label: str = "registry changes",
    dry_run: Optional[bool] = None,
) -> ShellRefreshReport:
    effective_dry_run = DRY_RUN if dry_run is None else dry_run
    ordered = unique_refresh_strategies(strategies)
    report = ShellRefreshReport(label, effective_dry_run, ordered)

    if not ordered:
        return report

    if effective_dry_run:
        print(f"[DRY-RUN] REFRESH {label}: {', '.join(ordered)}")
        if REFRESH_EXPLORER_RESTART in ordered:
            print("[DRY-RUN]   Explorer restart would remain an explicit fallback.")
        return report

    if REFRESH_SHELL_NOTIFY in ordered:
        try:
            shell_change_notify()
            if broadcast_setting_change(r"Software\Microsoft\Windows\CurrentVersion\Explorer"):
                report.messages.append("Sent shell change notification and Explorer settings broadcast.")
            else:
                report.errors.append("Explorer settings broadcast timed out or was not acknowledged.")
        except Exception as exc:
            report.errors.append(f"Shell notification failed: {exc}")

    if REFRESH_THEME_BROADCAST in ordered:
        try:
            if broadcast_setting_change("ImmersiveColorSet"):
                report.messages.append("Sent theme settings broadcast.")
            else:
                report.errors.append("Theme settings broadcast timed out or was not acknowledged.")
        except Exception as exc:
            report.errors.append(f"Theme broadcast failed: {exc}")

    if REFRESH_EXPLORER_RESTART in ordered:
        report.messages.append("Explorer restart is available as an explicit fallback.")

    for message in report.messages:
        print(f"Refresh: {message}")
    for error in report.errors:
        print(f"Refresh warning: {error} Restart Explorer remains available as an explicit fallback.")
    return report


def refresh_registry_changes(
    operations: List["RegistryOperation"],
    label: str = "registry changes",
    dry_run: Optional[bool] = None,
) -> ShellRefreshReport:
    return refresh_registry_strategies([operation.refresh_strategy for operation in operations], label, dry_run)


def refresh_shell_now(dry_run: Optional[bool] = None) -> ShellRefreshReport:
    return refresh_registry_strategies(
        [REFRESH_SHELL_NOTIFY, REFRESH_THEME_BROADCAST],
        label="manual shell refresh",
        dry_run=dry_run,
    )


def restart_explorer() -> bool:
    if DRY_RUN:
        print("[DRY-RUN] RESTART Explorer fallback")
        return True
    try:
        result = subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode != 0 and "not found" not in (result.stderr + result.stdout).lower():
            print(f"Explorer restart warning: {(result.stderr or result.stdout).strip()}")
        subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
        print("Explorer restarted.")
        return True
    except Exception as exc:
        print(f"Explorer restart failed: {exc}")
        return False

def get_registry_value(path: str, name: str, hive: int = winreg.HKEY_CURRENT_USER) -> Optional[Any]:
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except: return None


@dataclass
class RegistryValueSnapshot:
    exists: bool
    value: Any = None
    reg_type: Optional[int] = None


@dataclass
class RegistryValueRecord:
    path: str
    name: str
    value: Any
    reg_type: int


@dataclass
class RegistryTreeSnapshot:
    exists: bool
    keys: List[str] = field(default_factory=list)
    values: List[RegistryValueRecord] = field(default_factory=list)


@dataclass
class RegistryOperation:
    action: str
    hive: int
    path: str
    name: str = ""
    value: Any = None
    reg_type: Any = "DWORD"
    label: str = ""
    refresh_strategy: str = REFRESH_SHELL_NOTIFY


@dataclass
class RegistryOperationResult:
    operation: RegistryOperation
    snapshot: Any
    applied: bool = False
    verified: bool = False
    error: Optional[str] = None


@dataclass
class RegistryPlanReport:
    label: str
    dry_run: bool
    operations: List[RegistryOperation]
    results: List[RegistryOperationResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    rollback_errors: List[str] = field(default_factory=list)
    rolled_back: int = 0
    refresh: Optional[ShellRefreshReport] = None

    @property
    def success(self) -> bool:
        return not self.errors and not self.rollback_errors

    @property
    def planned(self) -> int:
        return len(self.operations)

    @property
    def applied(self) -> int:
        return sum(1 for result in self.results if result.applied)

    @property
    def verified(self) -> int:
        return sum(1 for result in self.results if result.verified)


class RegistryOperationError(RuntimeError):
    """Raised when a registry operation cannot be applied, verified, or rolled back."""


HIVE_DISPLAY_NAMES = {
    winreg.HKEY_CURRENT_USER: "HKCU",
    winreg.HKEY_LOCAL_MACHINE: "HKLM",
    winreg.HKEY_USERS: "HKU",
}

REGISTRY_TYPE_NAMES = {
    winreg.REG_DWORD: "DWORD",
    winreg.REG_SZ: "String",
    winreg.REG_EXPAND_SZ: "ExpandString",
    winreg.REG_BINARY: "Binary",
    winreg.REG_MULTI_SZ: "MultiString",
    winreg.REG_QWORD: "QWORD",
}

LAST_REGISTRY_PLAN_REPORTS: List[RegistryPlanReport] = []


def registry_type_code(reg_type: Any) -> int:
    if isinstance(reg_type, int):
        return reg_type
    normalized = str(reg_type).replace("REG_", "").replace("-", "").replace("_", "").upper()
    type_map = {
        "DWORD": winreg.REG_DWORD,
        "STRING": winreg.REG_SZ,
        "SZ": winreg.REG_SZ,
        "EXPANDSTRING": winreg.REG_EXPAND_SZ,
        "EXPANDSZ": winreg.REG_EXPAND_SZ,
        "BINARY": winreg.REG_BINARY,
    }
    if normalized not in type_map:
        raise RegistryOperationError(f"Unsupported registry value type: {reg_type}")
    return type_map[normalized]


def registry_type_name(reg_type: Any) -> str:
    try:
        return REGISTRY_TYPE_NAMES.get(registry_type_code(reg_type), str(reg_type))
    except RegistryOperationError:
        return str(reg_type)


def hive_display_name(hive: int) -> str:
    return HIVE_DISPLAY_NAMES.get(hive, f"HIVE_{hive}")


def registry_value_target(hive: int, path: str, name: str = "") -> str:
    leaf = "(Default)" if name == "" else name
    return f"{hive_display_name(hive)}\\{path}\\{leaf}"


def registry_operation_target(operation: RegistryOperation) -> str:
    if operation.action == "delete_tree":
        return f"{hive_display_name(operation.hive)}\\{operation.path}"
    return registry_value_target(operation.hive, operation.path, operation.name)


def registry_set_operation(
    path: str,
    name: str,
    value: Any,
    reg_type: Any,
    hive: int = winreg.HKEY_CURRENT_USER,
    label: str = "",
    refresh_strategy: str = REFRESH_SHELL_NOTIFY,
) -> RegistryOperation:
    return RegistryOperation("set_value", hive, path, name, value, reg_type, label, refresh_strategy)


def registry_delete_value_operation(
    path: str,
    name: str,
    hive: int = winreg.HKEY_CURRENT_USER,
    label: str = "",
    refresh_strategy: str = REFRESH_SHELL_NOTIFY,
) -> RegistryOperation:
    return RegistryOperation("delete_value", hive, path, name, None, "DWORD", label, refresh_strategy)


def registry_delete_tree_operation(
    path: str,
    hive: int = winreg.HKEY_CURRENT_USER,
    label: str = "",
    refresh_strategy: str = REFRESH_SHELL_NOTIFY,
) -> RegistryOperation:
    return RegistryOperation("delete_tree", hive, path, "", None, "DWORD", label, refresh_strategy)


def read_registry_value_snapshot(hive: int, path: str, name: str) -> RegistryValueSnapshot:
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        try:
            value, reg_type = winreg.QueryValueEx(key, name)
            return RegistryValueSnapshot(True, value, reg_type)
        finally:
            winreg.CloseKey(key)
    except FileNotFoundError:
        return RegistryValueSnapshot(False)
    except OSError:
        return RegistryValueSnapshot(False)


def write_registry_value(hive: int, path: str, name: str, value: Any, reg_type: Any) -> None:
    key = winreg.CreateKeyEx(hive, path, 0, winreg.KEY_WRITE)
    try:
        winreg.SetValueEx(key, name, 0, registry_type_code(reg_type), value)
    finally:
        winreg.CloseKey(key)


def delete_registry_value(hive: int, path: str, name: str) -> None:
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return
    try:
        try:
            winreg.DeleteValue(key, name)
        except FileNotFoundError:
            pass
        except OSError:
            pass
    finally:
        winreg.CloseKey(key)


def capture_registry_tree_snapshot(hive: int, path: str) -> RegistryTreeSnapshot:
    snapshot = RegistryTreeSnapshot(False)

    def walk(current_path: str) -> None:
        key = winreg.OpenKey(hive, current_path, 0, winreg.KEY_READ)
        snapshot.keys.append(current_path)
        try:
            index = 0
            while True:
                try:
                    name, value, reg_type = winreg.EnumValue(key, index)
                except OSError:
                    break
                snapshot.values.append(RegistryValueRecord(current_path, name, value, reg_type))
                index += 1

            index = 0
            while True:
                try:
                    child = winreg.EnumKey(key, index)
                except OSError:
                    break
                walk(current_path + "\\" + child)
                index += 1
        finally:
            winreg.CloseKey(key)

    try:
        walk(path)
        snapshot.exists = True
    except OSError:
        snapshot.exists = False
    return snapshot


def restore_registry_tree_snapshot(hive: int, snapshot: RegistryTreeSnapshot) -> None:
    if not snapshot.exists:
        return
    for key_path in sorted(snapshot.keys, key=lambda item: item.count("\\")):
        key = winreg.CreateKeyEx(hive, key_path, 0, winreg.KEY_WRITE)
        winreg.CloseKey(key)
    for record in snapshot.values:
        write_registry_value(hive, record.path, record.name, record.value, record.reg_type)


def capture_registry_operation_snapshot(operation: RegistryOperation) -> Any:
    if operation.action in ("set_value", "delete_value"):
        return read_registry_value_snapshot(operation.hive, operation.path, operation.name)
    if operation.action == "delete_tree":
        return capture_registry_tree_snapshot(operation.hive, operation.path)
    raise RegistryOperationError(f"Unsupported registry operation: {operation.action}")


def registry_values_equal(actual: Any, expected: Any, reg_type: Any) -> bool:
    kind = registry_type_code(reg_type)
    if kind in (winreg.REG_DWORD, winreg.REG_QWORD):
        return int(actual) == int(expected)
    if kind == winreg.REG_BINARY:
        return bytes(actual) == bytes(expected)
    if kind == winreg.REG_MULTI_SZ:
        return list(actual) == list(expected)
    return str(actual) == str(expected)


def apply_registry_operation(operation: RegistryOperation) -> None:
    if operation.action == "set_value":
        write_registry_value(operation.hive, operation.path, operation.name, operation.value, operation.reg_type)
        return
    if operation.action == "delete_value":
        delete_registry_value(operation.hive, operation.path, operation.name)
        return
    if operation.action == "delete_tree":
        delete_registry_tree(operation.hive, operation.path)
        return
    raise RegistryOperationError(f"Unsupported registry operation: {operation.action}")


def verify_registry_operation(operation: RegistryOperation) -> bool:
    if operation.action == "set_value":
        snapshot = read_registry_value_snapshot(operation.hive, operation.path, operation.name)
        return (
            snapshot.exists
            and snapshot.reg_type == registry_type_code(operation.reg_type)
            and registry_values_equal(snapshot.value, operation.value, operation.reg_type)
        )
    if operation.action == "delete_value":
        return not read_registry_value_snapshot(operation.hive, operation.path, operation.name).exists
    if operation.action == "delete_tree":
        return not registry_key_exists(operation.path, operation.hive)
    raise RegistryOperationError(f"Unsupported registry operation: {operation.action}")


def rollback_registry_operation(result: RegistryOperationResult) -> None:
    operation = result.operation
    snapshot = result.snapshot
    if operation.action in ("set_value", "delete_value"):
        if snapshot and snapshot.exists:
            write_registry_value(operation.hive, operation.path, operation.name, snapshot.value, snapshot.reg_type)
        else:
            delete_registry_value(operation.hive, operation.path, operation.name)
        return
    if operation.action == "delete_tree":
        delete_registry_tree(operation.hive, operation.path)
        restore_registry_tree_snapshot(operation.hive, snapshot)
        return
    raise RegistryOperationError(f"Unsupported registry operation: {operation.action}")


def summarize_registry_snapshot(snapshot: Any) -> str:
    if isinstance(snapshot, RegistryValueSnapshot):
        if not snapshot.exists:
            return "missing"
        return f"{snapshot.value!r} ({registry_type_name(snapshot.reg_type)})"
    if isinstance(snapshot, RegistryTreeSnapshot):
        if not snapshot.exists:
            return "missing tree"
        return f"{len(snapshot.keys)} key(s), {len(snapshot.values)} value(s)"
    return "unknown"


def format_registry_operation_error(operation: RegistryOperation, error: str) -> str:
    action = operation.action.replace("_", " ")
    return (
        f"{action} failed for {registry_operation_target(operation)}: {error}. "
        "Recovery hint: captured previous registry values were restored where possible."
    )


def execute_registry_plan(
    operations: List[RegistryOperation],
    label: str = "registry plan",
    dry_run: Optional[bool] = None,
    rollback_on_failure: bool = True,
) -> RegistryPlanReport:
    effective_dry_run = DRY_RUN if dry_run is None else dry_run
    report = RegistryPlanReport(label, effective_dry_run, list(operations))

    if not operations:
        LAST_REGISTRY_PLAN_REPORTS.append(report)
        return report

    if effective_dry_run:
        print(f"[DRY-RUN] PLAN {label}: {len(operations)} registry operation(s)")
        for operation in operations:
            try:
                snapshot = capture_registry_operation_snapshot(operation)
            except Exception as exc:
                snapshot = None
                message = format_registry_operation_error(operation, str(exc))
                report.errors.append(message)
            result = RegistryOperationResult(operation, snapshot)
            report.results.append(result)
            value_suffix = ""
            if operation.action == "set_value":
                value_suffix = f" = {operation.value!r} ({registry_type_name(operation.reg_type)})"
            print(f"[DRY-RUN]   {operation.action.upper()} {registry_operation_target(operation)}{value_suffix}")
            print(f"[DRY-RUN]     previous: {summarize_registry_snapshot(snapshot)}")
        report.refresh = refresh_registry_changes(operations, label, dry_run=True)
        LAST_REGISTRY_PLAN_REPORTS.append(report)
        return report

    for operation in operations:
        try:
            snapshot = capture_registry_operation_snapshot(operation)
            result = RegistryOperationResult(operation, snapshot)
            apply_registry_operation(operation)
            result.applied = True
            if not verify_registry_operation(operation):
                raise RegistryOperationError("post-write verification did not observe the requested state")
            result.verified = True
            report.results.append(result)
        except Exception as exc:
            if "result" not in locals() or result.operation is not operation:
                result = RegistryOperationResult(operation, None)
            if not any(item is result for item in report.results):
                report.results.append(result)
            result.error = str(exc)
            report.errors.append(format_registry_operation_error(operation, str(exc)))
            if rollback_on_failure:
                for applied_result in reversed([item for item in report.results if item.applied]):
                    try:
                        rollback_registry_operation(applied_result)
                        report.rolled_back += 1
                    except Exception as rollback_exc:
                        report.rollback_errors.append(
                            f"rollback failed for {registry_operation_target(applied_result.operation)}: {rollback_exc}"
                        )
            LAST_REGISTRY_PLAN_REPORTS.append(report)
            return report

    report.refresh = refresh_registry_changes(operations, label)
    LAST_REGISTRY_PLAN_REPORTS.append(report)
    return report


def set_registry_value(path: str, name: str, value: Any, reg_type: str, hive: int = winreg.HKEY_CURRENT_USER) -> bool:
    report = execute_registry_plan([registry_set_operation(path, name, value, reg_type, hive)], label="set registry value")
    return report.success

def registry_key_exists(path: str, hive: int = winreg.HKEY_CURRENT_USER) -> bool:
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except: return False

def is_policy_locked(reg_path: str, reg_name: str) -> bool:
    """Check if a setting is locked by Group Policy (HKLM\\...\\Policies)."""
    policy_paths = []
    # Build potential policy paths from the HKCU path
    if "Explorer\\Advanced" in reg_path:
        policy_paths.append(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
        policy_paths.append(r"Software\Policies\Microsoft\Windows\Explorer")
    elif "Search" in reg_path:
        policy_paths.append(r"Software\Policies\Microsoft\Windows\Windows Search")
    elif "Themes\\Personalize" in reg_path:
        policy_paths.append(r"Software\Policies\Microsoft\Windows\Personalization")
    elif "ContentDeliveryManager" in reg_path:
        policy_paths.append(r"Software\Policies\Microsoft\Windows\CloudContent")

    # Also check the exact same path under HKLM Policies
    if "Software\\Microsoft\\" in reg_path:
        policy_variant = reg_path.replace("Software\\Microsoft\\", "Software\\Policies\\Microsoft\\")
        if policy_variant not in policy_paths:
            policy_paths.append(policy_variant)

    for pp in policy_paths:
        val = get_registry_value(pp, reg_name, winreg.HKEY_LOCAL_MACHINE)
        if val is not None:
            return True
        # Also check HKCU policies
        val = get_registry_value(pp, reg_name, winreg.HKEY_CURRENT_USER)
        if val is not None:
            return True
    return False


# ============================================================================
# .REG FILE EXPORT
# ============================================================================

def export_reg_file(settings: List, filepath: str):
    """Export current settings as a .reg file for easy undo/deployment."""
    lines = ["Windows Registry Editor Version 5.00", ""]
    lines.append("; Generated by ExplorerTweaks v" + APP_VERSION)
    lines.append("; Import this file to restore these settings")
    lines.append("")

    # Group by registry path
    by_path: Dict[str, list] = {}
    for s in settings:
        by_path.setdefault(s.reg_path, []).append(s)

    for path, slist in by_path.items():
        lines.append(f"[HKEY_CURRENT_USER\\{path}]")
        for s in slist:
            val = get_registry_value(s.reg_path, s.reg_name)
            if val is None:
                val = s.default_value
            if s.reg_type == "DWORD":
                lines.append(f'"{s.reg_name}"=dword:{val:08x}')
            elif s.reg_type == "String":
                escaped = str(val).replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'"{s.reg_name}"="{escaped}"')
        lines.append("")

    with open(filepath, 'w', encoding='utf-16') as f:
        f.write('\r\n'.join(lines))


# ============================================================================
# POWERSHELL DEPLOYMENT / MULTI-USER HELPERS
# ============================================================================

SID_PATTERN = re.compile(r"^S-\d-\d+-(?:\d+-)+\d+$")


def ps_quote(value: Any) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def windows_cmd_quote(value: str) -> str:
    return '"' + value.replace('"', r'\"') + '"'


def setting_to_registry_value(setting: RegistrySetting, target_value: Any) -> Any:
    if isinstance(target_value, bool):
        return setting.enable_value if target_value else setting.disable_value
    return target_value


def is_setting_supported(setting: RegistrySetting, os_version: OSVersion) -> bool:
    order = [
        OSVersion.WINDOWS_10,
        OSVersion.WINDOWS_11_21H2,
        OSVersion.WINDOWS_11_22H2,
        OSVersion.WINDOWS_11_23H2,
        OSVersion.WINDOWS_11_24H2,
    ]
    if os_version not in order:
        return True
    idx = order.index(os_version)
    if setting.min_os and idx < order.index(setting.min_os):
        return False
    if setting.max_os and idx > order.index(setting.max_os):
        return False
    return True


def current_registry_entries(settings: List[RegistrySetting]) -> List[Dict[str, Any]]:
    entries = []
    for setting in settings:
        value = get_registry_value(setting.reg_path, setting.reg_name)
        if value is None:
            value = setting.default_value
        entries.append({
            "path": setting.reg_path,
            "name": setting.reg_name,
            "type": setting.reg_type,
            "value": value,
        })
    return entries


def profile_registry_entries(profile_settings: dict, settings: List[RegistrySetting]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    settings_map = {s.id: s for s in settings}
    entries = []
    special = {}

    for setting_id, target_value in profile_settings.items():
        if setting_id in ("_classic", "classic_context_menu"):
            special["classic_context_menu"] = bool(target_value)
            continue
        if setting_id in ("_search", "search_mode"):
            special["search_mode"] = int(target_value)
            continue

        setting = settings_map.get(setting_id)
        if not setting:
            continue
        entries.append({
            "path": setting.reg_path,
            "name": setting.reg_name,
            "type": setting.reg_type,
            "value": setting_to_registry_value(setting, target_value),
        })

    return entries, special


def build_powershell_script(entries: List[Dict[str, Any]], special: Optional[Dict[str, Any]] = None, default_all_users: bool = False) -> str:
    special = special or {}
    param_block = "param([switch]$CurrentUserOnly)" if default_all_users else "param([switch]$AllUsers)"
    apply_line = "$ApplyAllUsers = -not $CurrentUserOnly.IsPresent" if default_all_users else "$ApplyAllUsers = $AllUsers.IsPresent"

    lines = [
        f"# Generated by ExplorerTweaks v{APP_VERSION}",
        "# Applies Explorer, taskbar, search, and shell registry preferences.",
        "[CmdletBinding()]",
        param_block,
        "$ErrorActionPreference = 'Stop'",
        apply_line,
        "",
        "function Get-ExplorerTweaksTargets {",
        "    param([bool]$ForAllUsers)",
        "    if (-not $ForAllUsers) { return @('HKCU:') }",
        "    $targets = @('Registry::HKEY_USERS\\.DEFAULT')",
        "    Get-ChildItem -Path 'Registry::HKEY_USERS' | ForEach-Object {",
        "        $sid = Split-Path $_.Name -Leaf",
        "        if ($sid -match '^S-\\d-\\d+-(\\d+-)+\\d+$') {",
        "            $targets += \"Registry::HKEY_USERS\\$sid\"",
        "        }",
        "    }",
        "    return $targets | Select-Object -Unique",
        "}",
        "",
        "function Set-ExplorerTweaksValue {",
        "    param([string]$HiveRoot, [string]$SubPath, [string]$Name, [string]$Type, [object]$Value)",
        "    $targetPath = Join-Path $HiveRoot $SubPath",
        "    if (-not (Test-Path -LiteralPath $targetPath)) { New-Item -Path $targetPath -Force | Out-Null }",
        "    if ($Name -eq '') {",
        "        (Get-Item -LiteralPath $targetPath).SetValue('', [string]$Value, [Microsoft.Win32.RegistryValueKind]::String)",
        "    } elseif ($Type -eq 'DWORD') {",
        "        New-ItemProperty -Path $targetPath -Name $Name -PropertyType DWord -Value ([int]$Value) -Force | Out-Null",
        "    } else {",
        "        New-ItemProperty -Path $targetPath -Name $Name -PropertyType String -Value ([string]$Value) -Force | Out-Null",
        "    }",
        "}",
        "",
        "$Settings = @(",
    ]

    for entry in entries:
        value = int(entry["value"]) if str(entry["type"]).upper() == "DWORD" else ps_quote(entry["value"])
        lines.append(
            "    @{ Path = "
            + ps_quote(entry["path"])
            + "; Name = "
            + ps_quote(entry["name"])
            + "; Type = "
            + ps_quote(str(entry["type"]).upper())
            + f"; Value = {value} }},"
        )

    lines.extend([
        ")",
        "$Targets = Get-ExplorerTweaksTargets -ForAllUsers:$ApplyAllUsers",
        "foreach ($target in $Targets) {",
        "    foreach ($setting in $Settings) {",
        "        Set-ExplorerTweaksValue -HiveRoot $target -SubPath $setting.Path -Name $setting.Name -Type $setting.Type -Value $setting.Value",
        "    }",
    ])

    if "search_mode" in special:
        lines.append(
            "    Set-ExplorerTweaksValue -HiveRoot $target -SubPath "
            + ps_quote(r"Software\Microsoft\Windows\CurrentVersion\Search")
            + " -Name 'SearchboxTaskbarMode' -Type 'DWORD' -Value "
            + str(int(special["search_mode"]))
        )

    if "classic_context_menu" in special:
        classic_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
        inproc_path = classic_path + r"\InprocServer32"
        if special["classic_context_menu"]:
            lines.append(
                "    Set-ExplorerTweaksValue -HiveRoot $target -SubPath "
                + ps_quote(inproc_path)
                + " -Name '' -Type 'String' -Value ''"
            )
        else:
            lines.extend([
                "    $classicPath = Join-Path $target " + ps_quote(classic_path),
                "    Remove-Item -LiteralPath $classicPath -Recurse -Force -ErrorAction SilentlyContinue",
            ])

    lines.extend([
        "}",
        "Write-Host \"Applied ExplorerTweaks settings to $($Targets.Count) registry hive(s).\"",
        "",
    ])
    return "\r\n".join(lines)


def export_ps1_file(settings: List[RegistrySetting], filepath: str, all_users: bool = False):
    special = {
        "classic_context_menu": SpecialSettings.get_classic_context_menu(),
        "search_mode": SpecialSettings.get_search_mode(),
    }
    script = build_powershell_script(current_registry_entries(settings), special, default_all_users=all_users)
    with open(filepath, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write(script)


def export_profile_ps1(profile_path: str, filepath: str, all_users: bool = False):
    data = load_preset_from_file(profile_path)
    if not data:
        raise ValueError(f"Could not parse profile: {profile_path}")
    profile_settings = data.get("settings", data)
    entries, special = profile_registry_entries(profile_settings, get_all_settings())
    script = build_powershell_script(entries, special, default_all_users=all_users)
    with open(filepath, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write(script)


def remote_apply_profile(profile_path: str, computers: List[str], all_users: bool = False, dry_run: bool = False) -> int:
    data = load_preset_from_file(profile_path)
    if not data:
        raise ValueError(f"Could not parse profile: {profile_path}")
    if not computers:
        raise ValueError("At least one remote computer is required.")

    profile_settings = data.get("settings", data)
    entries, special = profile_registry_entries(profile_settings, get_all_settings())
    script = build_powershell_script(entries, special, default_all_users=all_users)
    encoded_script = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    computer_literal = "@(" + ",".join(ps_quote(c) for c in computers) + ")"
    ps_command = "\r\n".join([
        "$ErrorActionPreference = 'Stop'",
        f"$Computers = {computer_literal}",
        f"$ScriptText = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{encoded_script}'))",
        "$ScriptBlock = [ScriptBlock]::Create($ScriptText)",
        "Invoke-Command -ComputerName $Computers -ScriptBlock $ScriptBlock",
    ])

    if dry_run:
        print(f"[DRY-RUN] Remote apply profile: {profile_path}")
        print(f"[DRY-RUN] Targets: {', '.join(computers)}")
        print(f"[DRY-RUN] All users: {all_users}")
        return 0

    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Remote apply failed."
        raise RuntimeError(message)
    return result.returncode


def get_loaded_user_roots() -> List[str]:
    roots = [".DEFAULT"]
    try:
        key = winreg.OpenKey(winreg.HKEY_USERS, "")
        index = 0
        while True:
            try:
                subkey = winreg.EnumKey(key, index)
            except OSError:
                break
            index += 1
            if subkey.endswith("_Classes"):
                continue
            if SID_PATTERN.match(subkey):
                roots.append(subkey)
        winreg.CloseKey(key)
    except OSError:
        pass
    return list(dict.fromkeys(roots))


def set_user_registry_value(user_root: Optional[str], path: str, name: str, value: Any, reg_type: str) -> bool:
    if user_root is None:
        return set_registry_value(path, name, value, reg_type)
    return set_registry_value(f"{user_root}\\{path}", name, value, reg_type, winreg.HKEY_USERS)


def classic_context_menu_operations(enable: bool, hive: int = winreg.HKEY_CURRENT_USER, user_root: Optional[str] = None) -> List[RegistryOperation]:
    path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
    parent = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
    if user_root:
        path = f"{user_root}\\{path}"
        parent = f"{user_root}\\{parent}"
    if enable:
        return [registry_set_operation(path, "", "", "String", hive, "classic context menu")]
    return [registry_delete_tree_operation(parent, hive, "classic context menu")]


def set_classic_context_menu_for_user(enable: bool, user_root: Optional[str] = None) -> bool:
    if user_root is None:
        return SpecialSettings.set_classic_context_menu(enable)

    report = execute_registry_plan(
        classic_context_menu_operations(enable, winreg.HKEY_USERS, user_root),
        label=f"classic context menu HKU\\{user_root}",
    )
    return report.success


def apply_profile_values(profile_settings: dict, all_settings: List[RegistrySetting], os_version: OSVersion, multi_user: bool = False) -> int:
    settings_map = {s.id: s for s in all_settings}
    user_roots: List[Optional[str]] = get_loaded_user_roots() if multi_user else [None]
    applied = 0

    for user_root in user_roots:
        target_label = "HKCU" if user_root is None else f"HKU\\{user_root}"
        hive = winreg.HKEY_CURRENT_USER if user_root is None else winreg.HKEY_USERS
        if multi_user:
            print(f"Target: {target_label}")

        operations: List[RegistryOperation] = []

        for setting_id, target_value in profile_settings.items():
            if setting_id in ("classic_context_menu", "_classic"):
                print(f"  Classic context menu: {target_value}")
                operations.extend(classic_context_menu_operations(bool(target_value), hive, user_root))
                continue
            if setting_id in ("search_mode", "_search"):
                print(f"  Search mode: {target_value}")
                path = r"Software\Microsoft\Windows\CurrentVersion\Search"
                if user_root:
                    path = f"{user_root}\\{path}"
                operations.append(registry_set_operation(path, "SearchboxTaskbarMode", int(target_value), "DWORD", hive, "search mode"))
                continue

            setting = settings_map.get(setting_id)
            if not setting:
                continue
            if not is_setting_supported(setting, os_version):
                print(f"  {setting.name}: skipped on {os_version.value}")
                continue

            reg_value = setting_to_registry_value(setting, target_value)
            locked = is_policy_locked(setting.reg_path, setting.reg_name)
            lock_str = " [GP-LOCKED]" if locked else ""
            print(f"  {setting.name}: {target_value}{lock_str}")
            path = setting.reg_path if user_root is None else f"{user_root}\\{setting.reg_path}"
            operations.append(
                registry_set_operation(
                    path,
                    setting.reg_name,
                    reg_value,
                    setting.reg_type,
                    hive,
                    setting.name,
                    setting.refresh_strategy,
                )
            )

        report = execute_registry_plan(operations, label=f"apply profile to {target_label}")
        if report.success:
            applied += report.planned if report.dry_run else report.verified
        else:
            for error in report.errors + report.rollback_errors:
                print(f"  Error: {error}")

    return applied


# ============================================================================
# SEND-TO FOLDER MANAGER
# ============================================================================

def get_sendto_entries() -> List[Dict[str, str]]:
    """List entries in the shell:sendto folder."""
    sendto = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "SendTo")
    entries = []
    if os.path.isdir(sendto):
        for item in os.listdir(sendto):
            full = os.path.join(sendto, item)
            entry = {"name": item, "path": full, "is_link": item.lower().endswith(".lnk")}
            entries.append(entry)
    return entries

def remove_sendto_entry(path: str) -> bool:
    """Remove a Send To entry."""
    if DRY_RUN:
        print(f"[DRY-RUN] DELETE Send To entry: {path}")
        return True
    try:
        os.remove(path)
        return True
    except:
        return False


# ============================================================================
# RECENT ITEMS WIPE
# ============================================================================

def wipe_recent_items() -> Dict[str, int]:
    """Clear Jump Lists, AutomaticDestinations, CustomDestinations, and Recent."""
    results = {"deleted": 0, "errors": 0}
    targets = [
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent", "AutomaticDestinations"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent", "CustomDestinations"),
    ]

    if DRY_RUN:
        for d in targets:
            if os.path.isdir(d):
                count = len(os.listdir(d))
                print(f"[DRY-RUN] Would delete {count} files in {d}")
                results["deleted"] += count
        return results

    for d in targets:
        if os.path.isdir(d):
            for item in os.listdir(d):
                fp = os.path.join(d, item)
                if os.path.isfile(fp):
                    try:
                        os.remove(fp)
                        results["deleted"] += 1
                    except:
                        results["errors"] += 1
    return results


# ============================================================================
# CLASSIC PHOTO VIEWER RESTORE
# ============================================================================

PHOTO_VIEWER_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".ico"]

def is_photo_viewer_registered() -> bool:
    """Check if Windows Photo Viewer is registered for image files."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\.jpg\OpenWithProgids",
            0, winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, "PhotoViewer.FileAssoc.Tiff")
            winreg.CloseKey(key)
            return True
        except:
            winreg.CloseKey(key)
            return False
    except:
        return False

def set_photo_viewer(enable: bool) -> bool:
    """Register or unregister Windows Photo Viewer for common image types."""
    progid = "PhotoViewer.FileAssoc.Tiff"
    operations: List[RegistryOperation] = []

    if enable:
        for ext in PHOTO_VIEWER_EXTENSIONS:
            path = rf"Software\Classes\{ext}\OpenWithProgids"
            operations.append(registry_set_operation(path, progid, b"", "Binary", label="Windows Photo Viewer"))
    else:
        for ext in PHOTO_VIEWER_EXTENSIONS:
            path = rf"Software\Classes\{ext}\OpenWithProgids"
            operations.append(registry_delete_value_operation(path, progid, label="Windows Photo Viewer"))

    report = execute_registry_plan(operations, label="Windows Photo Viewer association")
    return report.success


# ============================================================================
# BACKUP / RESTORE BUNDLES
# ============================================================================

EXTRA_BACKUP_REGISTRY_PATHS = [
    r"Software\Microsoft\Windows\CurrentVersion\Search",
    r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}",
    r"Control Panel\Desktop",
]
BACKUP_MANIFEST_FILE = "manifest.json"
BACKUP_ALLOWED_DIRS = {"registry", "wallpaper", "taskbar_pins"}
REGISTRY_HIVE_ALIASES = {
    "HKEY_CURRENT_USER": "HKCU",
    "HKEY_LOCAL_MACHINE": "HKLM",
    "HKEY_USERS": "HKU",
}
REGISTRY_HIVE_VALUES = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKU": winreg.HKEY_USERS,
}


class BackupBundleValidationError(ValueError):
    """Raised when a backup bundle is unsafe or does not match the expected schema."""


def backup_registry_paths(settings: List[RegistrySetting]) -> List[str]:
    paths = [s.reg_path for s in settings]
    paths.extend(EXTRA_BACKUP_REGISTRY_PATHS)
    return list(dict.fromkeys(paths))


def safe_backup_name(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", path).strip("_") or "root"


def normalize_backup_member_name(name: str) -> str:
    normalized = name.replace("\\", "/").strip()
    if not normalized:
        raise BackupBundleValidationError("Backup archive contains an empty member name.")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        raise BackupBundleValidationError(f"Backup archive contains an absolute path: {name}")
    parts = normalized.rstrip("/").split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise BackupBundleValidationError(f"Backup archive contains an unsafe relative path: {name}")
    return "/".join(parts)


def allowed_backup_registry_keys() -> List[str]:
    return [f"HKCU\\{path}" for path in backup_registry_paths(get_all_settings())]


def normalize_registry_key(key: str) -> str:
    normalized = key.strip().replace("/", "\\")
    for long_name, short_name in REGISTRY_HIVE_ALIASES.items():
        if normalized.casefold() == long_name.casefold():
            return short_name
        prefix = long_name + "\\"
        if normalized.casefold().startswith(prefix.casefold()):
            return short_name + normalized[len(long_name):]
    return normalized


def is_allowed_backup_registry_key(key: str, allowed_keys: List[str]) -> bool:
    normalized = normalize_registry_key(key).casefold()
    for allowed in allowed_keys:
        allowed_normalized = allowed.casefold()
        if normalized == allowed_normalized or normalized.startswith(allowed_normalized + "\\"):
            return True
    return False


def decode_reg_file(raw: bytes) -> str:
    for encoding in ("utf-16", "utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise BackupBundleValidationError("Registry export could not be decoded.")


def validate_reg_file_content(raw: bytes, allowed_keys: List[str], member_name: str) -> None:
    text = decode_reg_file(raw)
    headers = re.findall(r"^\s*\[-?([^\]]+)\]", text, flags=re.MULTILINE)
    if not headers:
        raise BackupBundleValidationError(f"Registry export has no registry key headers: {member_name}")
    for key in headers:
        if not is_allowed_backup_registry_key(key, allowed_keys):
            raise BackupBundleValidationError(f"Registry export contains a non-whitelisted key: {key}")


def reg_logical_lines(text: str) -> List[str]:
    lines = []
    pending = ""
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            if pending:
                continue
            lines.append("")
            continue
        pending += stripped
        if pending.endswith("\\"):
            pending = pending[:-1]
            continue
        lines.append(pending)
        pending = ""
    if pending:
        lines.append(pending)
    return lines


def unescape_reg_string(value: str) -> str:
    chars = []
    escaped = False
    for char in value:
        if escaped:
            chars.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        else:
            chars.append(char)
    if escaped:
        chars.append("\\")
    return "".join(chars)


def parse_reg_hex_bytes(payload: str, member_name: str) -> bytes:
    hex_text = re.sub(r"[^0-9A-Fa-f]", "", payload)
    if len(hex_text) % 2:
        raise BackupBundleValidationError(f"Registry export has malformed hex payload: {member_name}")
    return bytes.fromhex(hex_text)


def decode_reg_utf16_payload(payload: bytes) -> str:
    text = payload.decode("utf-16-le", errors="replace")
    return text.rstrip("\x00")


def parse_reg_value_payload(payload: str, member_name: str) -> Tuple[str, Any, Any]:
    payload = payload.strip()
    if payload == "-":
        return "delete_value", None, "DWORD"
    if payload.lower().startswith("dword:"):
        return "set_value", int(payload.split(":", 1)[1], 16), "DWORD"
    if payload.lower().startswith("hex(b):"):
        raw = parse_reg_hex_bytes(payload.split(":", 1)[1], member_name)
        return "set_value", int.from_bytes(raw, "little"), winreg.REG_QWORD
    if payload.lower().startswith("hex(2):"):
        raw = parse_reg_hex_bytes(payload.split(":", 1)[1], member_name)
        return "set_value", decode_reg_utf16_payload(raw), winreg.REG_EXPAND_SZ
    if payload.lower().startswith("hex(7):"):
        raw = parse_reg_hex_bytes(payload.split(":", 1)[1], member_name)
        decoded = decode_reg_utf16_payload(raw)
        return "set_value", [item for item in decoded.split("\x00") if item], winreg.REG_MULTI_SZ
    if payload.lower().startswith("hex:"):
        return "set_value", parse_reg_hex_bytes(payload.split(":", 1)[1], member_name), "Binary"
    hex_match = re.match(r"^hex\(([0-9A-Fa-f]+)\):(.*)$", payload, flags=re.IGNORECASE)
    if hex_match:
        type_id = hex_match.group(1)
        raw = parse_reg_hex_bytes(hex_match.group(2), member_name)
        return "set_value", raw, int(type_id, 16)
    if payload.lower().startswith("hex("):
        raise BackupBundleValidationError(f"Registry export has malformed hex payload type in {member_name}: {payload[:40]}")
    if payload.startswith('"') and payload.endswith('"'):
        return "set_value", unescape_reg_string(payload[1:-1]), "String"
    raise BackupBundleValidationError(f"Registry export has an unsupported value payload in {member_name}: {payload[:40]}")


def parse_reg_value_line(line: str, member_name: str) -> Tuple[str, str, Any, Any]:
    if line.startswith("@="):
        name = ""
        payload = line[2:]
    else:
        match = re.match(r'^"((?:\\.|[^"\\])*)"=(.+)$', line)
        if not match:
            raise BackupBundleValidationError(f"Registry export has malformed value line in {member_name}: {line[:80]}")
        name = unescape_reg_string(match.group(1))
        payload = match.group(2)
    action, value, reg_type = parse_reg_value_payload(payload, member_name)
    return action, name, value, reg_type


def parse_reg_header(header: str, member_name: str) -> Tuple[str, int, str]:
    action = "set"
    if header.startswith("-"):
        action = "delete_tree"
        header = header[1:]
    normalized = normalize_registry_key(header)
    if "\\" not in normalized:
        raise BackupBundleValidationError(f"Registry export header has no subkey path in {member_name}: {header}")
    hive_alias, path = normalized.split("\\", 1)
    hive = REGISTRY_HIVE_VALUES.get(hive_alias.upper())
    if hive is None:
        raise BackupBundleValidationError(f"Registry export uses an unsupported hive in {member_name}: {header}")
    return action, hive, path


def parse_reg_file_operations(raw: bytes, member_name: str) -> List[RegistryOperation]:
    text = decode_reg_file(raw)
    operations: List[RegistryOperation] = []
    current_hive: Optional[int] = None
    current_path: Optional[str] = None

    for line in reg_logical_lines(text):
        if not line or line.startswith(";") or line.lower().startswith("windows registry editor"):
            continue
        header_match = re.match(r"^\[([^\]]+)\]$", line)
        if header_match:
            action, hive, path = parse_reg_header(header_match.group(1), member_name)
            if action == "delete_tree":
                operations.append(registry_delete_tree_operation(path, hive, member_name))
                current_hive = None
                current_path = None
            else:
                current_hive = hive
                current_path = path
            continue
        if current_hive is None or current_path is None:
            raise BackupBundleValidationError(f"Registry export has a value outside a key header: {member_name}")
        action, name, value, reg_type = parse_reg_value_line(line, member_name)
        if action == "delete_value":
            operations.append(registry_delete_value_operation(current_path, name, current_hive, member_name))
        else:
            operations.append(registry_set_operation(current_path, name, value, reg_type, current_hive, member_name))

    if not operations:
        raise BackupBundleValidationError(f"Registry export has no restorable values: {member_name}")
    return operations


def validate_manifest_file_path(value: Any, required_prefix: str, required_suffix: Optional[str] = None) -> str:
    if not isinstance(value, str):
        raise BackupBundleValidationError("Backup manifest contains a non-string file path.")
    normalized = normalize_backup_member_name(value)
    if not normalized.startswith(required_prefix + "/"):
        raise BackupBundleValidationError(f"Backup manifest file path is not under {required_prefix}: {value}")
    leaf = normalized.split("/")[-1]
    if not leaf:
        raise BackupBundleValidationError(f"Backup manifest file path has no filename: {value}")
    if required_suffix and not leaf.lower().endswith(required_suffix):
        raise BackupBundleValidationError(f"Backup manifest file path has the wrong extension: {value}")
    if "/" in normalized[len(required_prefix) + 1:]:
        raise BackupBundleValidationError(f"Backup manifest file path is nested too deeply: {value}")
    return normalized


def expected_taskbar_pins_suffix() -> str:
    return r"\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar".casefold()


def validate_backup_manifest(metadata: Any, zip_files: Dict[str, zipfile.ZipInfo], zf: zipfile.ZipFile) -> Tuple[Dict[str, Any], set]:
    if not isinstance(metadata, dict):
        raise BackupBundleValidationError("Backup manifest must be a JSON object.")
    if metadata.get("app") != APP_NAME:
        raise BackupBundleValidationError("Backup manifest was not created by ExplorerTweaks.")
    if not isinstance(metadata.get("version"), str) or not metadata["version"]:
        raise BackupBundleValidationError("Backup manifest is missing a version string.")

    allowed_files = {BACKUP_MANIFEST_FILE}
    allowed_registry_keys = allowed_backup_registry_keys()
    registry_exports = metadata.get("registry_exports", [])
    if not isinstance(registry_exports, list):
        raise BackupBundleValidationError("Backup manifest registry_exports must be a list.")

    seen_export_files = set()
    for export in registry_exports:
        if not isinstance(export, dict):
            raise BackupBundleValidationError("Backup manifest registry export must be an object.")
        key = export.get("key")
        if not isinstance(key, str) or not is_allowed_backup_registry_key(key, allowed_registry_keys):
            raise BackupBundleValidationError(f"Backup manifest references a non-whitelisted registry key: {key}")
        export_file = validate_manifest_file_path(export.get("file"), "registry", ".reg")
        if export_file in seen_export_files:
            raise BackupBundleValidationError(f"Backup manifest references a duplicate registry file: {export_file}")
        if export_file not in zip_files:
            raise BackupBundleValidationError(f"Backup manifest references a missing registry file: {export_file}")
        validate_reg_file_content(zf.read(zip_files[export_file]), allowed_registry_keys, export_file)
        seen_export_files.add(export_file)
        allowed_files.add(export_file)

    missing_registry_paths = metadata.get("missing_registry_paths", [])
    if missing_registry_paths is not None:
        if not isinstance(missing_registry_paths, list) or not all(isinstance(item, str) for item in missing_registry_paths):
            raise BackupBundleValidationError("Backup manifest missing_registry_paths must be a list of strings.")

    wallpaper = metadata.get("wallpaper")
    if wallpaper is not None:
        if not isinstance(wallpaper, dict):
            raise BackupBundleValidationError("Backup manifest wallpaper entry must be an object.")
        wallpaper_file = validate_manifest_file_path(wallpaper.get("file"), "wallpaper")
        original_path = wallpaper.get("original_path")
        if not isinstance(original_path, str) or not re.match(r"^[A-Za-z]:\\", original_path):
            raise BackupBundleValidationError("Backup manifest wallpaper original_path must be an absolute Windows path.")
        if Path(original_path).name != Path(wallpaper_file).name:
            raise BackupBundleValidationError("Backup manifest wallpaper filename does not match original_path.")
        if wallpaper_file not in zip_files:
            raise BackupBundleValidationError(f"Backup manifest references a missing wallpaper file: {wallpaper_file}")
        allowed_files.add(wallpaper_file)

    pins = metadata.get("taskbar_pins")
    if pins is not None:
        if not isinstance(pins, dict):
            raise BackupBundleValidationError("Backup manifest taskbar_pins entry must be an object.")
        folder = pins.get("folder")
        if folder != "taskbar_pins":
            raise BackupBundleValidationError("Backup manifest taskbar_pins folder must be taskbar_pins.")
        original_path = pins.get("original_path")
        if not isinstance(original_path, str) or not original_path.replace("/", "\\").casefold().endswith(expected_taskbar_pins_suffix()):
            raise BackupBundleValidationError("Backup manifest taskbar_pins original_path is not a TaskBar pins folder.")
        for member_name in zip_files:
            if member_name.startswith("taskbar_pins/"):
                if "/" in member_name[len("taskbar_pins/"):]:
                    raise BackupBundleValidationError(f"Backup taskbar pin file is nested too deeply: {member_name}")
                allowed_files.add(member_name)

    for member_name in zip_files:
        if member_name not in allowed_files:
            raise BackupBundleValidationError(f"Backup archive contains an unexpected payload entry: {member_name}")

    return metadata, allowed_files


def validate_backup_zip(zf: zipfile.ZipFile) -> Tuple[Dict[str, Any], set]:
    zip_files: Dict[str, zipfile.ZipInfo] = {}
    directory_names = set()
    manifest_count = 0

    for info in zf.infolist():
        normalized = normalize_backup_member_name(info.filename)
        if info.is_dir():
            if normalized not in BACKUP_ALLOWED_DIRS:
                raise BackupBundleValidationError(f"Backup archive contains an unexpected directory: {info.filename}")
            directory_names.add(normalized)
            continue
        if normalized in zip_files:
            raise BackupBundleValidationError(f"Backup archive contains a duplicate file: {normalized}")
        zip_files[normalized] = info
        if normalized == BACKUP_MANIFEST_FILE:
            manifest_count += 1

    if manifest_count != 1:
        raise BackupBundleValidationError("Backup archive must contain exactly one manifest.json file.")

    try:
        metadata = json.loads(zf.read(zip_files[BACKUP_MANIFEST_FILE]).decode("utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BackupBundleValidationError(f"Backup manifest is not valid JSON: {exc}") from exc

    return validate_backup_manifest(metadata, zip_files, zf)


def validate_backup_bundle(filepath: str) -> Dict[str, Any]:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)
    with zipfile.ZipFile(filepath, "r") as zf:
        metadata, _ = validate_backup_zip(zf)
    return metadata


def extract_validated_backup_zip(zf: zipfile.ZipFile, temp_path: Path, allowed_files: set) -> None:
    for info in zf.infolist():
        if info.is_dir():
            continue
        normalized = normalize_backup_member_name(info.filename)
        if normalized not in allowed_files:
            raise BackupBundleValidationError(f"Backup archive contains an unexpected payload entry: {normalized}")
        target = temp_path / normalized
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(info, "r") as source, open(target, "wb") as dest:
            shutil.copyfileobj(source, dest)


def create_backup_bundle(filepath: str) -> Dict[str, Any]:
    """Create a zip containing ExplorerTweaks registry subtrees, wallpaper, and taskbar pins."""
    settings = get_all_settings()
    metadata: Dict[str, Any] = {
        "app": APP_NAME,
        "version": APP_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "registry_exports": [],
        "missing_registry_paths": [],
        "wallpaper": None,
        "taskbar_pins": None,
    }

    if DRY_RUN:
        print(f"[DRY-RUN] CREATE backup bundle: {filepath}")
        for path in backup_registry_paths(settings):
            print(f"[DRY-RUN] EXPORT HKCU\\{path}")
        return metadata

    with tempfile.TemporaryDirectory(prefix="ExplorerTweaksBackup_") as temp_dir:
        temp_path = Path(temp_dir)
        registry_dir = temp_path / "registry"
        registry_dir.mkdir(parents=True, exist_ok=True)

        for path in backup_registry_paths(settings):
            export_name = safe_backup_name(path) + ".reg"
            export_path = registry_dir / export_name
            result = subprocess.run(
                ["reg", "export", f"HKCU\\{path}", str(export_path), "/y"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                metadata["registry_exports"].append({"key": f"HKCU\\{path}", "file": f"registry/{export_name}"})
            else:
                metadata["missing_registry_paths"].append(f"HKCU\\{path}")

        wallpaper_path = get_registry_value(r"Control Panel\Desktop", "WallPaper")
        if wallpaper_path and os.path.isfile(wallpaper_path):
            wallpaper_dir = temp_path / "wallpaper"
            wallpaper_dir.mkdir(parents=True, exist_ok=True)
            dest = wallpaper_dir / Path(wallpaper_path).name
            shutil.copy2(wallpaper_path, dest)
            metadata["wallpaper"] = {"original_path": wallpaper_path, "file": f"wallpaper/{dest.name}"}

        pins_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Internet Explorer" / "Quick Launch" / "User Pinned" / "TaskBar"
        if pins_dir.is_dir():
            pins_dest = temp_path / "taskbar_pins"
            shutil.copytree(pins_dir, pins_dest)
            metadata["taskbar_pins"] = {"original_path": str(pins_dir), "folder": "taskbar_pins"}

        metadata_path = temp_path / "manifest.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path.unlink()
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in temp_path.rglob("*"):
                if item.is_file():
                    zf.write(item, item.relative_to(temp_path).as_posix())

    return metadata


def restore_backup_bundle(filepath: str) -> Dict[str, int]:
    """Restore an ExplorerTweaks backup bundle."""
    results = {"registry_imported": 0, "files_restored": 0, "errors": 0}
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)

    if DRY_RUN:
        print(f"[DRY-RUN] RESTORE backup bundle: {filepath}")
        with zipfile.ZipFile(filepath, "r") as zf:
            metadata, _ = validate_backup_zip(zf)
            for export in metadata.get("registry_exports", []):
                export_file = export.get("file", "")
                operations = parse_reg_file_operations(zf.read(export_file), export_file)
                execute_registry_plan(operations, label=f"restore {export_file}", dry_run=True)
        return results

    with tempfile.TemporaryDirectory(prefix="ExplorerTweaksRestore_") as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(filepath, "r") as zf:
            metadata, allowed_files = validate_backup_zip(zf)
            extract_validated_backup_zip(zf, temp_path, allowed_files)

        for export in metadata.get("registry_exports", []):
            reg_file = temp_path / export.get("file", "")
            if not reg_file.is_file():
                results["errors"] += 1
                continue
            operations = parse_reg_file_operations(reg_file.read_bytes(), str(reg_file))
            report = execute_registry_plan(operations, label=f"restore {export.get('file', '')}")
            if report.success:
                results["registry_imported"] += 1
            else:
                results["errors"] += len(report.errors) or 1

        wallpaper = metadata.get("wallpaper")
        if wallpaper:
            source = temp_path / wallpaper.get("file", "")
            original = wallpaper.get("original_path")
            if source.is_file() and original:
                original_dir = os.path.dirname(original)
                if os.path.isdir(original_dir):
                    shutil.copy2(source, original)
                    set_registry_value(r"Control Panel\Desktop", "WallPaper", original, "String")
                    results["files_restored"] += 1

        pins = metadata.get("taskbar_pins")
        if pins:
            source = temp_path / pins.get("folder", "")
            original = pins.get("original_path")
            if source.is_dir() and original:
                os.makedirs(original, exist_ok=True)
                for item in source.iterdir():
                    if item.is_file():
                        shutil.copy2(item, Path(original) / item.name)
                        results["files_restored"] += 1

    return results


# ============================================================================
# CONTEXT MENU SHELL INTEGRATION
# ============================================================================

CONTEXT_MENU_TARGETS = [
    {
        "path": r"Software\Classes\Directory\Background\shell\ExplorerTweaks",
        "label": "ExplorerTweaks: Folder Background",
        "focus": "Navigation",
    },
    {
        "path": r"Software\Classes\Directory\shell\ExplorerTweaks",
        "label": "ExplorerTweaks: Folder Settings",
        "focus": "Navigation",
    },
    {
        "path": r"Software\Classes\Drive\shell\ExplorerTweaks",
        "label": "ExplorerTweaks: Drive Settings",
        "focus": "Navigation",
    },
    {
        "path": r"Software\Classes\DesktopBackground\Shell\ExplorerTweaks",
        "label": "ExplorerTweaks: Desktop Shell Settings",
        "focus": "Appearance",
    },
    {
        "path": r"Software\Classes\CLSID\{645FF040-5081-101B-9F08-00AA002F954E}\shell\ExplorerTweaks",
        "label": "ExplorerTweaks: Recycle Bin Settings",
        "focus": "Privacy",
    },
]


def app_launch_command(focus: str) -> str:
    if getattr(sys, "frozen", False):
        parts = [sys.executable]
    else:
        parts = [sys.executable, str(Path(__file__).resolve())]
    parts.extend(["--focus", focus])
    return " ".join(windows_cmd_quote(part) for part in parts)


def delete_registry_tree(hive: int, path: str):
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except OSError:
        return
    try:
        while True:
            try:
                child = winreg.EnumKey(key, 0)
            except OSError:
                break
            delete_registry_tree(hive, path + "\\" + child)
    finally:
        winreg.CloseKey(key)
    try:
        winreg.DeleteKey(hive, path)
    except OSError:
        pass


def is_context_menu_installed() -> bool:
    return registry_key_exists(CONTEXT_MENU_TARGETS[0]["path"] + r"\command")


def set_context_menu_integration(enable: bool) -> bool:
    operations: List[RegistryOperation] = []
    if enable:
        icon_path = sys.executable if getattr(sys, "frozen", False) else str(Path(__file__).resolve())
        for target in CONTEXT_MENU_TARGETS:
            operations.append(registry_set_operation(target["path"], "MUIVerb", target["label"], "String", label="context menu"))
            operations.append(registry_set_operation(target["path"], "Icon", icon_path, "String", label="context menu"))
            operations.append(
                registry_set_operation(
                    target["path"] + r"\command",
                    "",
                    app_launch_command(target["focus"]),
                    "String",
                    label="context menu",
                )
            )
    else:
        for target in CONTEXT_MENU_TARGETS:
            operations.append(registry_delete_tree_operation(target["path"], label="context menu"))

    report = execute_registry_plan(operations, label="ExplorerTweaks context menu integration")
    return report.success


# ============================================================================
# DARK MODE AUTO-SWITCH
# ============================================================================

def explorer_tweaks_appdata_dir() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / APP_NAME
    return Path.home() / "AppData" / "Roaming" / APP_NAME


def darkmode_auto_switch_script_path() -> Path:
    return explorer_tweaks_appdata_dir() / DARKMODE_SCRIPT_NAME


def ps_number_or_null(value: Optional[float]) -> str:
    return "$null" if value is None else f"{float(value):.8f}"


def build_darkmode_auto_switch_script(latitude: Optional[float] = None, longitude: Optional[float] = None) -> str:
    lines = [
        f"# Generated by ExplorerTweaks v{APP_VERSION}",
        "# Switches Windows app/system theme to light during daylight and dark after sunset.",
        "[CmdletBinding()]",
        "param()",
        "$ErrorActionPreference = 'Stop'",
        f"$ConfiguredLatitude = {ps_number_or_null(latitude)}",
        f"$ConfiguredLongitude = {ps_number_or_null(longitude)}",
        "$LogDir = Join-Path $env:LOCALAPPDATA 'ExplorerTweaks'",
        "New-Item -Path $LogDir -ItemType Directory -Force | Out-Null",
        "$LogPath = Join-Path $LogDir 'darkmode_auto_switch.log'",
        "",
        "function Write-ExplorerTweaksLog {",
        "    param([string]$Message)",
        "    $stamp = (Get-Date).ToString('s')",
        "    Add-Content -Path $LogPath -Value \"$stamp $Message\" -Encoding UTF8",
        "}",
        "",
        "function Get-ExplorerTweaksLocation {",
        "    if ($null -ne $ConfiguredLatitude -and $null -ne $ConfiguredLongitude) {",
        "        return [pscustomobject]@{ Latitude = [double]$ConfiguredLatitude; Longitude = [double]$ConfiguredLongitude; Source = 'configured' }",
        "    }",
        "    try {",
        "        Add-Type -AssemblyName System.Runtime.WindowsRuntime",
        "        $null = [Windows.Devices.Geolocation.Geolocator,Windows.Devices.Geolocation,ContentType=WindowsRuntime]",
        "        $geolocator = [Windows.Devices.Geolocation.Geolocator]::new()",
        "        $geolocator.DesiredAccuracy = [Windows.Devices.Geolocation.PositionAccuracy]::Default",
        "        $operation = $geolocator.GetGeopositionAsync()",
        "        $task = [System.WindowsRuntimeSystemExtensions]::AsTask($operation)",
        "        $position = $task.GetAwaiter().GetResult()",
        "        return [pscustomobject]@{ Latitude = $position.Coordinate.Point.Position.Latitude; Longitude = $position.Coordinate.Point.Position.Longitude; Source = 'Windows Location API' }",
        "    } catch {",
        "        throw \"Location unavailable. Enable Windows location access or reinstall with --darkmode-lat and --darkmode-lon. $($_.Exception.Message)\"",
        "    }",
        "}",
        "",
        "function ConvertTo-Radians { param([double]$Degrees) return $Degrees * [Math]::PI / 180.0 }",
        "function ConvertTo-Degrees { param([double]$Radians) return $Radians * 180.0 / [Math]::PI }",
        "function Normalize-Degrees {",
        "    param([double]$Degrees)",
        "    while ($Degrees -lt 0) { $Degrees += 360 }",
        "    while ($Degrees -ge 360) { $Degrees -= 360 }",
        "    return $Degrees",
        "}",
        "function Normalize-Hours {",
        "    param([double]$Hours)",
        "    while ($Hours -lt 0) { $Hours += 24 }",
        "    while ($Hours -ge 24) { $Hours -= 24 }",
        "    return $Hours",
        "}",
        "",
        "function Get-SunEvent {",
        "    param([datetime]$Date, [double]$Latitude, [double]$Longitude, [bool]$Sunrise)",
        "    $day = $Date.DayOfYear",
        "    $lngHour = $Longitude / 15.0",
        "    $t = if ($Sunrise) { $day + ((6.0 - $lngHour) / 24.0) } else { $day + ((18.0 - $lngHour) / 24.0) }",
        "    $m = (0.9856 * $t) - 3.289",
        "    $l = $m + (1.916 * [Math]::Sin((ConvertTo-Radians $m))) + (0.020 * [Math]::Sin((ConvertTo-Radians (2.0 * $m)))) + 282.634",
        "    $l = Normalize-Degrees $l",
        "    $ra = ConvertTo-Degrees ([Math]::Atan(0.91764 * [Math]::Tan((ConvertTo-Radians $l))))",
        "    $ra = Normalize-Degrees $ra",
        "    $lQuadrant = [Math]::Floor($l / 90.0) * 90.0",
        "    $raQuadrant = [Math]::Floor($ra / 90.0) * 90.0",
        "    $ra = ($ra + ($lQuadrant - $raQuadrant)) / 15.0",
        "    $sinDec = 0.39782 * [Math]::Sin((ConvertTo-Radians $l))",
        "    $cosDec = [Math]::Cos([Math]::Asin($sinDec))",
        "    $cosH = ([Math]::Cos((ConvertTo-Radians 90.833)) - ($sinDec * [Math]::Sin((ConvertTo-Radians $Latitude)))) / ($cosDec * [Math]::Cos((ConvertTo-Radians $Latitude)))",
        "    if ($cosH -gt 1 -or $cosH -lt -1) { return $null }",
        "    $h = if ($Sunrise) { 360.0 - (ConvertTo-Degrees ([Math]::Acos($cosH))) } else { ConvertTo-Degrees ([Math]::Acos($cosH)) }",
        "    $h = $h / 15.0",
        "    $localMeanTime = $h + $ra - (0.06571 * $t) - 6.622",
        "    $utcHour = Normalize-Hours ($localMeanTime - $lngHour)",
        "    return ([datetime]::SpecifyKind($Date.Date, [DateTimeKind]::Utc)).AddHours($utcHour).ToLocalTime()",
        "}",
        "",
        "function Set-ExplorerTweaksTheme {",
        "    param([bool]$UseLight)",
        "    $themePath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'",
        "    if (-not (Test-Path -LiteralPath $themePath)) { New-Item -Path $themePath -Force | Out-Null }",
        "    $value = if ($UseLight) { 1 } else { 0 }",
        "    New-ItemProperty -Path $themePath -Name 'AppsUseLightTheme' -PropertyType DWord -Value $value -Force | Out-Null",
        "    New-ItemProperty -Path $themePath -Name 'SystemUsesLightTheme' -PropertyType DWord -Value $value -Force | Out-Null",
        "    try {",
        "        Add-Type @'",
        "using System;",
        "using System.Runtime.InteropServices;",
        "public static class ExplorerTweaksNative {",
        "  [DllImport(\"user32.dll\", SetLastError=true, CharSet=CharSet.Auto)]",
        "  public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint flags, uint timeout, out UIntPtr result);",
        "}",
        "'@ -ErrorAction SilentlyContinue",
        "        $result = [UIntPtr]::Zero",
        "        [ExplorerTweaksNative]::SendMessageTimeout([IntPtr]0xffff, 0x001A, [UIntPtr]::Zero, 'ImmersiveColorSet', 0x0002, 5000, [ref]$result) | Out-Null",
        "    } catch {}",
        "}",
        "",
        "try {",
        "    $location = Get-ExplorerTweaksLocation",
        "    $now = Get-Date",
        "    $sunrise = Get-SunEvent -Date $now -Latitude $location.Latitude -Longitude $location.Longitude -Sunrise $true",
        "    $sunset = Get-SunEvent -Date $now -Latitude $location.Latitude -Longitude $location.Longitude -Sunrise $false",
        "    if ($null -eq $sunrise -or $null -eq $sunset) { throw 'Sunrise/sunset unavailable for this latitude today.' }",
        "    $useLight = ($now -ge $sunrise -and $now -lt $sunset)",
        "    Set-ExplorerTweaksTheme -UseLight:$useLight",
        "    $mode = if ($useLight) { 'light' } else { 'dark' }",
        "    Write-ExplorerTweaksLog \"Set $mode mode using $($location.Source); sunrise=$sunrise sunset=$sunset\"",
        "} catch {",
        "    Write-ExplorerTweaksLog \"ERROR $($_.Exception.Message)\"",
        "    exit 1",
        "}",
    ]
    return "\r\n".join(lines)


def install_darkmode_auto_switch(latitude: Optional[float] = None, longitude: Optional[float] = None, interval_minutes: int = 15) -> Path:
    script_path = darkmode_auto_switch_script_path()
    if DRY_RUN:
        print(f"[DRY-RUN] INSTALL dark mode auto-switch task: {DARKMODE_TASK_NAME}")
        print(f"[DRY-RUN] Script: {script_path}")
        return script_path

    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(build_darkmode_auto_switch_script(latitude, longitude), encoding="utf-8-sig", newline="\r\n")
    task_command = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{script_path}"'
    result = subprocess.run(
        ["schtasks", "/Create", "/F", "/TN", DARKMODE_TASK_NAME, "/SC", "MINUTE", "/MO", str(interval_minutes), "/TR", task_command],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Could not create scheduled task.")
    subprocess.run(["schtasks", "/Run", "/TN", DARKMODE_TASK_NAME], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return script_path


def uninstall_darkmode_auto_switch() -> bool:
    if DRY_RUN:
        print(f"[DRY-RUN] UNINSTALL dark mode auto-switch task: {DARKMODE_TASK_NAME}")
        return True

    subprocess.run(["schtasks", "/Delete", "/F", "/TN", DARKMODE_TASK_NAME], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    script_path = darkmode_auto_switch_script_path()
    try:
        if script_path.exists():
            script_path.unlink()
        if script_path.parent.exists() and not any(script_path.parent.iterdir()):
            script_path.parent.rmdir()
    except OSError:
        return False
    return True


def is_darkmode_auto_switch_installed() -> bool:
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", DARKMODE_TASK_NAME],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return result.returncode == 0


# ============================================================================
# PRESETS
# ============================================================================

BUILTIN_PRESETS = {
    "Minimal": {
        "description": "Clean, distraction-free Explorer. Hides clutter, disables ads.",
        "settings": {
            "show_extensions": True, "show_hidden": False, "show_system": False,
            "colored_encrypted": False, "show_checkboxes": False, "compact_mode": True,
            "show_thumbnails": True, "status_bar": False, "full_path_title": False,
            "show_recent": False, "show_frequent": False, "sync_notifications": False,
            "silent_installs": False, "bing_search": False, "widgets_button": False,
            "taskview_button": False, "show_gallery": False,
        }
    },
    "Privacy": {
        "description": "Maximum privacy. Disables tracking, telemetry, and ads.",
        "settings": {
            "show_recent": False, "show_frequent": False, "track_docs": False,
            "track_apps": False, "sync_notifications": False, "silent_installs": False,
            "bing_search": False, "cortana": False, "search_history": False,
            "widgets_button": False,
        }
    },
    "Power User": {
        "description": "Show everything. Extensions, hidden files, full paths, classic menus.",
        "settings": {
            "show_extensions": True, "show_hidden": True, "show_system": False,
            "colored_encrypted": True, "show_checkboxes": True, "compact_mode": True,
            "show_thumbnails": True, "type_overlay": True, "status_bar": True,
            "full_path_title": True, "full_path_address": True,
            "launch_to_thispc": True, "expand_to_folder": True,
            "show_all_folders": True, "end_task": True,
            "classic_context_menu": True,
        }
    },
}

def apply_preset(preset_settings: dict, all_settings: List, os_version) -> int:
    """Apply a preset's settings. Returns count of settings applied."""
    return apply_profile_values(preset_settings, all_settings, os_version)

def save_preset_to_file(name: str, description: str, settings: List, filepath: str):
    """Save current settings as a user preset JSON file."""
    preset = {
        "name": name,
        "description": description,
        "version": APP_VERSION,
        "settings": {}
    }
    for s in settings:
        val = get_registry_value(s.reg_path, s.reg_name)
        if val is not None:
            enabled = (val == s.enable_value)
            preset["settings"][s.id] = enabled

    preset["settings"]["classic_context_menu"] = SpecialSettings.get_classic_context_menu()
    preset["settings"]["search_mode"] = SpecialSettings.get_search_mode()

    with open(filepath, 'w', encoding="utf-8") as f:
        json.dump(preset, f, indent=2)

def load_preset_from_file(filepath: str) -> Optional[dict]:
    """Load a user preset from a JSON file."""
    try:
        with open(filepath, 'r', encoding="utf-8-sig") as f:
            data = json.load(f)
        return data
    except:
        return None


# ============================================================================
# SETTINGS DEFINITIONS
# ============================================================================

def get_all_settings() -> List[RegistrySetting]:
    ADV = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    EXP = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
    CAB = r"Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState"
    SEARCH = r"Software\Microsoft\Windows\CurrentVersion\Search"
    CDM = r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
    THEME = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    DWM = r"Software\Microsoft\Windows\DWM"
    
    return [
        RegistrySetting("show_extensions", "Show File Extensions", "Display .txt, .exe, .pdf after filenames.", "Appearance", "File Display", ADV, "HideFileExt", "DWORD", 0, 1, 1, inverted=True, preview_key="show_extensions",
            info="Security best-practice. Hidden extensions let malware disguise 'invoice.pdf.exe' as a PDF."),
        RegistrySetting("show_hidden", "Show Hidden Files", "Display hidden files and folders.", "Appearance", "File Display", ADV, "Hidden", "DWORD", 1, 2, 2, preview_key="show_hidden",
            info="Reveals dotfiles and items with the Hidden attribute. Useful for devs and troubleshooting."),
        RegistrySetting("show_system", "Show System Files", "Display protected OS files.", "Appearance", "File Display", ADV, "ShowSuperHidden", "DWORD", 1, 0, 0, warning="!", preview_key="show_system",
            info="Shows critical OS files like bootmgr and pagefile.sys. Deleting these can break Windows."),
        RegistrySetting("colored_encrypted", "Colored Encrypted/Compressed", "Green=encrypted, Blue=compressed.", "Appearance", "File Display", ADV, "ShowEncryptCompressedColor", "DWORD", 1, 0, 0, preview_key="colored_encrypted",
            info="Visual indicator: green filenames are EFS-encrypted, blue are NTFS-compressed."),
        RegistrySetting("show_checkboxes", "Selection Checkboxes", "Checkboxes for multi-select.", "Appearance", "File Display", ADV, "AutoCheckSelect", "DWORD", 1, 0, 0, preview_key="show_checkboxes",
            info="Adds checkboxes for selecting multiple files without holding Ctrl. Good for touchscreens."),
        RegistrySetting("compact_mode", "Compact View", "Reduce spacing between items.", "Appearance", "View Options", ADV, "UseCompactMode", "DWORD", 1, 0, 0, min_os=OSVersion.WINDOWS_11_21H2, preview_key="compact_mode",
            info="Windows 11 added extra padding for touch targets. This restores Win10-density spacing."),
        RegistrySetting("show_thumbnails", "Show Thumbnails", "Image previews instead of icons.", "Appearance", "View Options", ADV, "IconsOnly", "DWORD", 0, 1, 0, inverted=True, preview_key="show_thumbnails",
            info="Shows image/video previews in Explorer. Disabling speeds up folders with many media files."),
        RegistrySetting("type_overlay", "Type Overlay", "Badge on thumbnails (W, X, P).", "Appearance", "View Options", ADV, "ShowTypeOverlay", "DWORD", 1, 0, 1, preview_key="show_type_overlay",
            info="Small letter badges on thumbnails indicating file type (W=Word, X=Excel, P=PowerPoint)."),
        RegistrySetting("status_bar", "Status Bar", "Item count at bottom.", "Appearance", "View Options", ADV, "ShowStatusBar", "DWORD", 1, 0, 1, preview_key="show_status_bar",
            info="Shows item count and selection size at the bottom of Explorer windows."),
        RegistrySetting("full_row_select", "Full Row Selection", "Highlight entire row.", "Appearance", "View Options", ADV, "FullRowSelect", "DWORD", 1, 0, 1, preview_key="full_row_select",
            info="In Details view, highlights the entire row instead of just the filename."),
        RegistrySetting("tooltips", "Tooltips", "Show details on hover.", "Appearance", "View Options", ADV, "ShowInfoTip", "DWORD", 1, 0, 1, preview_key="show_tooltips",
            info="Shows file details (size, date, dimensions) when hovering over items."),
        RegistrySetting("full_path_title", "Full Path in Title", "C:\\Users\\... in title bar.", "Appearance", "Title Bar", CAB, "FullPath", "DWORD", 1, 0, 0, preview_key="full_path_title",
            info="Shows the full directory path in the title bar instead of just the folder name."),
        RegistrySetting("full_path_address", "Full Path in Address", "Text path vs breadcrumbs.", "Appearance", "Title Bar", CAB, "FullPathAddress", "DWORD", 1, 0, 0, preview_key="full_path_address",
            info="Shows a text path (C:\\Users\\...) instead of clickable breadcrumbs in the address bar."),
        RegistrySetting("launch_to_thispc", "Open to This PC", "Start at drives view.", "Navigation", "Startup", ADV, "LaunchTo", "DWORD", 1, 2, 2, preview_key="launch_to_thispc",
            info="Opens Explorer to the This PC view showing drives, instead of Quick Access/Home."),
        RegistrySetting("expand_to_folder", "Expand to Folder", "Auto-expand nav tree.", "Navigation", "Nav Pane", ADV, "NavPaneExpandToCurrentFolder", "DWORD", 1, 0, 0, preview_key="expand_to_folder",
            info="The navigation pane tree automatically expands to show the current folder's location."),
        RegistrySetting("show_all_folders", "Show All Folders", "Recycle Bin, Control Panel.", "Navigation", "Nav Pane", ADV, "NavPaneShowAllFolders", "DWORD", 1, 0, 0, preview_key="show_all_folders",
            info="Adds Recycle Bin, Control Panel, and other shell folders to the navigation pane tree."),
        RegistrySetting("separate_process", "Separate Process", "Independent windows.", "Navigation", "Windows", ADV, "SeparateProcess", "DWORD", 1, 0, 0, preview_key="separate_process",
            info="Each Explorer window runs in its own process. If one crashes, others stay open."),
        RegistrySetting("restore_folders", "Restore at Logon", "Reopen after restart.", "Navigation", "Windows", ADV, "PersistBrowsers", "DWORD", 1, 0, 0, preview_key="restore_folders",
            info="Reopens the Explorer windows you had open before signing out or restarting."),
        RegistrySetting("sharing_wizard", "Sharing Wizard", "Simple vs advanced.", "Navigation", "Windows", ADV, "SharingWizardOn", "DWORD", 1, 0, 1, preview_key="use_sharing_wizard",
            info="Uses a simplified sharing dialog. Disabling shows the advanced Security tab instead."),
        RegistrySetting("show_recent", "Recent Files", "Recently opened files.", "Privacy", "Quick Access", EXP, "ShowRecent", "DWORD", 1, 0, 1, preview_key="show_recent",
            info="Shows recently opened files in Quick Access / Home. Disabling improves privacy."),
        RegistrySetting("show_frequent", "Frequent Folders", "Often used folders.", "Privacy", "Quick Access", EXP, "ShowFrequent", "DWORD", 1, 0, 1, preview_key="show_frequent",
            info="Shows frequently accessed folders in Quick Access / Home."),
        RegistrySetting("track_docs", "Track Documents", "Remember opened docs.", "Privacy", "Tracking", ADV, "Start_TrackDocs", "DWORD", 1, 0, 1, preview_key="track_docs",
            info="Windows tracks which documents you open for Jump Lists and recent files."),
        RegistrySetting("track_apps", "Track Apps", "Remember launched apps.", "Privacy", "Tracking", ADV, "Start_TrackProgs", "DWORD", 1, 0, 1, preview_key="track_apps",
            info="Windows tracks which apps you launch for the Start menu's 'Most used' section."),
        RegistrySetting("sync_notifications", "OneDrive Notifications", "Sync provider promos.", "Privacy", "Ads", ADV, "ShowSyncProviderNotifications", "DWORD", 1, 0, 1, preview_key="sync_notifications",
            info="Disabling removes OneDrive and other sync provider promotional banners from Explorer."),
        RegistrySetting("silent_installs", "Silent App Installs", "Auto-install apps.", "Privacy", "Ads", CDM, "SilentInstalledAppsEnabled", "DWORD", 1, 0, 1, preview_key="silent_installs",
            info="Windows silently installs suggested apps (Candy Crush, etc.). Disabling stops this."),
        RegistrySetting("bing_search", "Bing Web Search", "Web results in search.", "Search", "Web", SEARCH, "BingSearchEnabled", "DWORD", 1, 0, 1, preview_key="bing_search",
            info="Start menu search includes Bing web results. Disabling makes search local-only and faster."),
        RegistrySetting("cortana", "Cortana", "Voice assistant.", "Search", "Cortana", SEARCH, "CortanaConsent", "DWORD", 1, 0, 1, preview_key="cortana",
            info="Enables Cortana voice assistant integration. Deprecated in Windows 11 23H2+."),
        RegistrySetting("search_history", "Search History", "Remember searches.", "Search", "Cortana", SEARCH, "HistoryViewEnabled", "DWORD", 1, 0, 1, preview_key="search_history",
            info="Shows your recent search queries in the search panel. Disabling improves privacy."),
        RegistrySetting("taskview_button", "Task View", "Virtual desktops button.", "Taskbar", "Buttons", ADV, "ShowTaskViewButton", "DWORD", 1, 0, 1, preview_key="taskview_button",
            info="The Task View button opens virtual desktops. You can still use Win+Tab without the button."),
        RegistrySetting("widgets_button", "Widgets", "News/weather button.", "Taskbar", "Buttons", ADV, "TaskbarDa", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_21H2, preview_key="widgets_button",
            info="The Widgets panel shows news, weather, and other feeds. Often considered distracting."),
        RegistrySetting("center_taskbar", "Center Icons", "Center vs left align.", "Taskbar", "Layout", ADV, "TaskbarAl", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_21H2, preview_key="center_taskbar",
            info="Windows 11 centers taskbar icons by default. Disabling moves them to the left like Win10."),
        RegistrySetting("end_task", "End Task Menu", "Add End Task option.", "Taskbar", "Menu", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings", "TaskbarEndTask", "DWORD", 1, 0, 0, min_os=OSVersion.WINDOWS_11_22H2, preview_key="end_task",
            info="Adds 'End task' to the right-click menu on taskbar app icons. Quick way to kill frozen apps."),
        RegistrySetting("taskbar_animations", "Animations", "Animate taskbar.", "Performance", "Animations", ADV, "TaskbarAnimations", "DWORD", 1, 0, 1, preview_key="taskbar_animations",
            info="Enables slide/fade animations on the taskbar. Disabling can feel snappier on slow hardware."),
        RegistrySetting("aero_peek", "Aero Peek", "Desktop preview.", "Performance", "Effects", DWM, "EnableAeroPeek", "DWORD", 1, 0, 1, preview_key="aero_peek",
            info="Hovering over the far-right taskbar corner makes windows transparent to show the desktop."),
        RegistrySetting("disable_thumb_cache", "Disable Thumb Cache", "No thumbnail storage.", "Performance", "Thumbnails", ADV, "DisableThumbnailCache", "DWORD", 1, 0, 0, preview_key="disable_thumb_cache",
            info="Stops caching thumbnails to disk. Saves space but slows browsing image-heavy folders."),
        RegistrySetting("disable_network_thumbs", "No Network Thumbs", "No thumbs.db on network.", "Performance", "Thumbnails", ADV, "DisableThumbsDBOnNetworkFolders", "DWORD", 1, 0, 0,
            info="Prevents creating thumbs.db cache files on network drives. Avoids lock/permission issues."),
        RegistrySetting("snap_assist", "Snap Assist", "Window suggestions.", "Performance", "Snapping", ADV, "SnapAssist", "DWORD", 1, 0, 1, preview_key="snap_assist",
            info="After snapping a window, suggests other windows to fill the remaining space."),
        RegistrySetting("snap_layouts", "Snap Layouts", "Layout grid.", "Performance", "Snapping", ADV, "EnableSnapBar", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_21H2, preview_key="snap_layouts",
            info="Hovering over the maximize button shows layout options for arranging windows."),
        RegistrySetting("dark_system", "Dark System", "Dark taskbar/Start.", "Theme", "Mode", THEME, "SystemUsesLightTheme", "DWORD", 0, 1, 1, inverted=True, preview_key="dark_mode",
            info="Applies dark theme to Windows chrome: taskbar, Start menu, Action Center, and notifications.", refresh_strategy=REFRESH_THEME_BROADCAST),
        RegistrySetting("dark_apps", "Dark Apps", "Dark app windows.", "Theme", "Mode", THEME, "AppsUseLightTheme", "DWORD", 0, 1, 1, inverted=True, preview_key="dark_mode",
            info="Applies dark theme to app windows (Settings, Explorer, UWP apps). Independent of system theme.", refresh_strategy=REFRESH_THEME_BROADCAST),
        RegistrySetting("show_gallery", "Gallery", "Photo gallery in nav.", "Windows 11", "Nav Pane", ADV, "ShowGallery", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_23H2, preview_key="show_gallery",
            info="Shows the Gallery view in the navigation pane for quick access to your photos."),
    ]


class SpecialSettings:
    @staticmethod
    def get_classic_context_menu() -> bool:
        return registry_key_exists(r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32")
    
    @staticmethod
    def set_classic_context_menu(enable: bool) -> bool:
        report = execute_registry_plan(
            classic_context_menu_operations(enable),
            label="classic context menu",
        )
        return report.success
    
    @staticmethod
    def get_search_mode() -> int:
        val = get_registry_value(r"Software\Microsoft\Windows\CurrentVersion\Search", "SearchboxTaskbarMode")
        return val if val is not None else 2
    
    @staticmethod
    def set_search_mode(mode: int) -> bool:
        return set_registry_value(r"Software\Microsoft\Windows\CurrentVersion\Search", "SearchboxTaskbarMode", mode, "DWORD")


# ============================================================================
# WINDOWS 11 FILE EXPLORER SIMULATION
# ============================================================================

class Win11Explorer(ctk.CTkFrame):
    """Pixel-accurate Windows 11 File Explorer simulation."""
    
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, fg_color="transparent", corner_radius=8)
        self.state = state
        self._build()
    
    def _c(self, key):
        """Get color from theme."""
        return (EXP_DARK if self.state.dark_mode else EXP_LIGHT).get(key, "#ff00ff")
    
    def _build(self):
        # Window frame with border
        self.window = ctk.CTkFrame(self, fg_color=self._c("window_bg"), corner_radius=8, border_width=1, border_color=self._c("border"))
        self.window.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Title bar
        self._build_titlebar()
        # Toolbar/Command bar
        self._build_toolbar()
        # Main content (nav pane + file list)
        self._build_content()
        # Status bar
        self._build_statusbar()
    
    def _build_titlebar(self):
        self.titlebar = ctk.CTkFrame(self.window, fg_color=self._c("titlebar"), height=32, corner_radius=0)
        self.titlebar.pack(fill="x")
        self.titlebar.pack_propagate(False)
        
        # Left side - icon and title
        left = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        left.pack(side="left", padx=12, pady=8)
        
        ctk.CTkLabel(left, text="📁", font=ctk.CTkFont(size=14)).pack(side="left")
        self.title_label = ctk.CTkLabel(left, text="Documents", font=ctk.CTkFont(size=11), text_color=self._c("titlebar_text"))
        self.title_label.pack(side="left", padx=(8, 0))
        
        # Right side - window controls
        controls = ctk.CTkFrame(self.titlebar, fg_color="transparent")
        controls.pack(side="right")
        
        for symbol, w in [("─", 46), ("□", 46), ("✕", 46)]:
            btn = ctk.CTkFrame(controls, fg_color="transparent", width=w, height=32)
            btn.pack(side="left")
            btn.pack_propagate(False)
            ctk.CTkLabel(btn, text=symbol, font=ctk.CTkFont(size=10), text_color=self._c("titlebar_text")).pack(expand=True)
    
    def _build_toolbar(self):
        # Command bar
        self.toolbar = ctk.CTkFrame(self.window, fg_color=self._c("command_bar"), height=48, corner_radius=0)
        self.toolbar.pack(fill="x")
        self.toolbar.pack_propagate(False)
        
        # Navigation buttons
        nav = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        nav.pack(side="left", padx=8, pady=8)
        
        for sym in ["  <  ", "  >  ", "  ^  "]:
            btn = ctk.CTkFrame(nav, fg_color="transparent")
            btn.pack(side="left", padx=1)
            ctk.CTkLabel(btn, text=sym, font=ctk.CTkFont(size=11, weight="bold"), text_color=self._c("toolbar_icon")).pack(padx=4, pady=4)
        
        # Address bar
        self.address_bar = ctk.CTkFrame(self.toolbar, fg_color=self._c("address_bg"), corner_radius=4, height=32)
        self.address_bar.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.address_bar.pack_propagate(False)
        
        self.address_content = ctk.CTkFrame(self.address_bar, fg_color="transparent")
        self.address_content.pack(side="left", fill="both", expand=True, padx=8)
        
        # Search box
        search = ctk.CTkFrame(self.toolbar, fg_color=self._c("address_bg"), corner_radius=4, width=140, height=32)
        search.pack(side="right", padx=8, pady=8)
        search.pack_propagate(False)
        
        sf = ctk.CTkFrame(search, fg_color="transparent")
        sf.pack(expand=True)
        ctk.CTkLabel(sf, text="O", font=ctk.CTkFont(size=11), text_color=self._c("address_icon")).pack(side="left", padx=(8, 4))
        ctk.CTkLabel(sf, text="Search Documents", font=ctk.CTkFont(size=10), text_color=self._c("address_icon")).pack(side="left")
    
    def _build_content(self):
        content = ctk.CTkFrame(self.window, fg_color=self._c("content_bg"), corner_radius=0)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Navigation pane
        self.nav_pane = ctk.CTkFrame(content, fg_color=self._c("nav_pane"), width=180, corner_radius=0)
        self.nav_pane.grid(row=0, column=0, sticky="nsew")
        self.nav_pane.grid_propagate(False)
        
        self.nav_content = ctk.CTkFrame(self.nav_pane, fg_color="transparent")
        self.nav_content.pack(fill="both", expand=True, padx=4, pady=8)
        
        # Separator
        ctk.CTkFrame(content, fg_color=self._c("border"), width=1).grid(row=0, column=0, sticky="nse")
        
        # File list area
        file_area = ctk.CTkFrame(content, fg_color=self._c("content_bg"), corner_radius=0)
        file_area.grid(row=0, column=1, sticky="nsew")
        
        # Column headers
        self.headers = ctk.CTkFrame(file_area, fg_color=self._c("header_bg"), height=28)
        self.headers.pack(fill="x")
        self.headers.pack_propagate(False)
        
        # File list
        self.filelist = ctk.CTkFrame(file_area, fg_color=self._c("content_bg"))
        self.filelist.pack(fill="both", expand=True)
    
    def _build_statusbar(self):
        self.statusbar = ctk.CTkFrame(self.window, fg_color=self._c("status_bg"), height=26, corner_radius=0)
        self.statusbar.pack(fill="x")
        self.statusbar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self.statusbar, text="8 items", font=ctk.CTkFont(size=10), text_color=self._c("status_text"))
        self.status_label.pack(side="left", padx=16, pady=4)
    
    def _render_nav_pane(self):
        for w in self.nav_content.winfo_children():
            w.destroy()
        
        # Build navigation items
        items = []
        items.append({"icon": "🏠", "text": "Home", "level": 0, "selected": not self.state.launch_to_thispc})
        
        if self.state.show_gallery:
            items.append({"icon": "🖼", "text": "Gallery", "level": 0})
        
        items.append({"icon": "☁", "text": "OneDrive - Personal", "level": 0})
        
        # This PC section
        expanded = self.state.expand_to_folder or self.state.launch_to_thispc
        items.append({"icon": "💻", "text": "This PC", "level": 0, "expanded": expanded, "selected": self.state.launch_to_thispc and not expanded})
        
        if expanded:
            items.append({"icon": "📁", "text": "Desktop", "level": 1})
            items.append({"icon": "📁", "text": "Documents", "level": 1, "selected": True})
            items.append({"icon": "📁", "text": "Downloads", "level": 1})
            items.append({"icon": "📁", "text": "Music", "level": 1})
            items.append({"icon": "📁", "text": "Pictures", "level": 1})
            items.append({"icon": "📁", "text": "Videos", "level": 1})
            items.append({"icon": "💿", "text": "Local Disk (C:)", "level": 1})
        
        items.append({"icon": "🌐", "text": "Network", "level": 0})
        
        if self.state.show_all_folders:
            items.append({"icon": "🗑", "text": "Recycle Bin", "level": 0})
            items.append({"icon": "⚙", "text": "Control Panel", "level": 0})
        
        # Render items
        for item in items:
            level = item.get("level", 0)
            selected = item.get("selected", False)
            expanded = item.get("expanded", False)
            
            row = ctk.CTkFrame(self.nav_content, fg_color=self._c("nav_selected") if selected else "transparent", height=28, corner_radius=4)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            
            indent = level * 20 + 8
            
            # Expand arrow for top-level items
            if level == 0:
                arrow = "v" if expanded else ">"
                ctk.CTkLabel(row, text=arrow, font=ctk.CTkFont(size=8), text_color=self._c("nav_text"), width=12).pack(side="left", padx=(indent, 0))
            else:
                ctk.CTkLabel(row, text="", width=12).pack(side="left", padx=(indent, 0))
            
            # Icon and text
            ctk.CTkLabel(row, text=item["icon"], font=ctk.CTkFont(size=12)).pack(side="left", padx=(4, 6))
            
            text_color = "#ffffff" if selected else self._c("nav_text")
            ctk.CTkLabel(row, text=item["text"], font=ctk.CTkFont(size=11), text_color=text_color).pack(side="left")
    
    def _render_address_bar(self):
        for w in self.address_content.winfo_children():
            w.destroy()
        
        if self.state.full_path_address:
            ctk.CTkLabel(self.address_content, text="C:\\Users\\User\\Documents", font=ctk.CTkFont(size=11), text_color=self._c("address_text")).pack(side="left", pady=6)
        else:
            # Breadcrumb style
            parts = [("💻", "This PC"), (">", ""), ("📁", "Documents")]
            for icon, text in parts:
                if icon == ">":
                    ctk.CTkLabel(self.address_content, text="  >  ", font=ctk.CTkFont(size=10), text_color=self._c("address_icon")).pack(side="left")
                else:
                    f = ctk.CTkFrame(self.address_content, fg_color="transparent")
                    f.pack(side="left", pady=6)
                    ctk.CTkLabel(f, text=icon, font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 4))
                    ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=11), text_color=self._c("address_text")).pack(side="left")
    
    def _render_headers(self):
        for w in self.headers.winfo_children():
            w.destroy()
        
        hf = ctk.CTkFrame(self.headers, fg_color="transparent")
        hf.pack(fill="x", padx=8, pady=4)
        
        if self.state.show_checkboxes:
            ctk.CTkLabel(hf, text="☐", font=ctk.CTkFont(size=11), text_color=self._c("header_text"), width=28).pack(side="left")
        
        ctk.CTkLabel(hf, text="", width=28).pack(side="left")  # Icon space
        
        headers_data = [("Name", 150), ("Date modified", 130), ("Type", 100), ("Size", 70)]
        for text, width in headers_data:
            ctk.CTkLabel(hf, text=text, font=ctk.CTkFont(size=10), text_color=self._c("header_text"), width=width, anchor="w").pack(side="left", padx=4)
    
    def _render_files(self):
        for w in self.filelist.winfo_children():
            w.destroy()
        
        files = [
            {"name": "Work Projects", "ext": "", "type": "File folder", "date": "1/26/2026 3:45 PM", "size": "", "icon": "📁", "folder": True},
            {"name": "Vacation Photos", "ext": "", "type": "File folder", "date": "1/25/2026 10:30 AM", "size": "", "icon": "📁", "folder": True},
            {"name": "Annual Report", "ext": ".docx", "type": "Microsoft Word", "date": "1/24/2026 4:45 PM", "size": "2.4 MB", "icon": "📄", "overlay": "W"},
            {"name": "Budget 2026", "ext": ".xlsx", "type": "Microsoft Excel", "date": "1/23/2026 2:15 PM", "size": "156 KB", "icon": "📊", "overlay": "X"},
            {"name": "Family Photo", "ext": ".jpg", "type": "JPG File", "date": "1/22/2026 6:00 PM", "size": "4.2 MB", "icon": "🖼"},
            {"name": "Presentation", "ext": ".pptx", "type": "PowerPoint", "date": "1/21/2026 11:00 AM", "size": "8.1 MB", "icon": "📽", "overlay": "P"},
            {"name": "Backup Archive", "ext": ".zip", "type": "Compressed", "date": "1/20/2026 9:30 AM", "size": "500 MB", "icon": "📦", "compressed": True},
            {"name": "Encrypted Notes", "ext": ".docx", "type": "Microsoft Word", "date": "1/19/2026 1:00 PM", "size": "50 KB", "icon": "🔒", "encrypted": True, "overlay": "W"},
            {"name": "desktop", "ext": ".ini", "type": "Configuration", "date": "12/15/2025", "size": "1 KB", "icon": "⚙", "hidden": True},
            {"name": "pagefile", "ext": ".sys", "type": "System File", "date": "9/1/2025", "size": "4.0 GB", "icon": "⚙", "hidden": True, "system": True},
        ]
        
        row_height = 24 if self.state.compact_mode else 32
        selected_idx = 2
        visible = 0
        
        for idx, f in enumerate(files):
            if f.get("hidden") and not self.state.show_hidden:
                continue
            if f.get("system") and not self.state.show_system:
                continue
            
            visible += 1
            is_selected = (idx == selected_idx)
            
            # Row background
            if is_selected and self.state.full_row_select:
                bg = self._c("row_selected")
            else:
                bg = "transparent"
            
            row = ctk.CTkFrame(self.filelist, fg_color=bg, height=row_height, corner_radius=4 if is_selected else 0)
            row.pack(fill="x", padx=4, pady=1)
            row.pack_propagate(False)
            
            rf = ctk.CTkFrame(row, fg_color="transparent")
            rf.pack(fill="x", padx=4)
            
            # Checkbox
            if self.state.show_checkboxes:
                cb = "☑" if is_selected else "☐"
                ctk.CTkLabel(rf, text=cb, font=ctk.CTkFont(size=11), text_color=self._c("content_text"), width=28).pack(side="left")
            
            # Icon with optional overlay
            icon_f = ctk.CTkFrame(rf, fg_color="transparent", width=28)
            icon_f.pack(side="left")
            icon_f.pack_propagate(False)
            
            if self.state.show_thumbnails and f.get("overlay"):
                tf = ctk.CTkFrame(icon_f, fg_color="transparent")
                tf.pack(expand=True)
                ctk.CTkLabel(tf, text=f["icon"], font=ctk.CTkFont(size=14)).pack(side="left")
                if self.state.show_type_overlay:
                    ctk.CTkLabel(tf, text=f["overlay"], font=ctk.CTkFont(size=8, weight="bold"), text_color="#0078d4").pack(side="left")
            else:
                ctk.CTkLabel(icon_f, text=f["icon"], font=ctk.CTkFont(size=14)).pack(expand=True)
            
            # File name
            name = f["name"]
            if self.state.show_extensions and f.get("ext"):
                name += f["ext"]
            
            # Text color
            if f.get("hidden"):
                tc = self._c("hidden")
            elif self.state.colored_encrypted and f.get("encrypted"):
                tc = self._c("encrypted")
            elif self.state.colored_encrypted and f.get("compressed"):
                tc = self._c("compressed")
            elif is_selected and self.state.full_row_select:
                tc = self._c("row_selected_text")
            else:
                tc = self._c("content_text")
            
            dim_tc = self._c("row_selected_text") if (is_selected and self.state.full_row_select) else self._c("content_dim")
            
            ctk.CTkLabel(rf, text=name, font=ctk.CTkFont(size=11), text_color=tc, width=150, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=f.get("date", ""), font=ctk.CTkFont(size=10), text_color=dim_tc, width=130, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=f.get("type", ""), font=ctk.CTkFont(size=10), text_color=dim_tc, width=100, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=f.get("size", ""), font=ctk.CTkFont(size=10), text_color=dim_tc, width=70, anchor="e").pack(side="left", padx=4)
        
        self._visible_count = visible
    
    def _update_colors(self):
        self.window.configure(fg_color=self._c("window_bg"), border_color=self._c("border"))
        self.titlebar.configure(fg_color=self._c("titlebar"))
        self.toolbar.configure(fg_color=self._c("command_bar"))
        self.address_bar.configure(fg_color=self._c("address_bg"))
        self.nav_pane.configure(fg_color=self._c("nav_pane"))
        self.headers.configure(fg_color=self._c("header_bg"))
        self.filelist.configure(fg_color=self._c("content_bg"))
        self.statusbar.configure(fg_color=self._c("status_bg"))
    
    def update(self):
        self._update_colors()
        
        # Title
        title = "C:\\Users\\User\\Documents" if self.state.full_path_title else "Documents"
        self.title_label.configure(text=title, text_color=self._c("titlebar_text"))
        
        self._render_address_bar()
        self._render_nav_pane()
        self._render_headers()
        self._render_files()
        
        # Status bar
        if self.state.show_status_bar:
            self.statusbar.pack(fill="x")
            self.status_label.configure(text=f"{getattr(self, '_visible_count', 8)} items | 1 item selected", text_color=self._c("status_text"))
        else:
            self.statusbar.pack_forget()


# ============================================================================
# WINDOWS 11 TASKBAR SIMULATION
# ============================================================================

class Win11Taskbar(ctk.CTkFrame):
    """Pixel-accurate Windows 11 Taskbar simulation."""
    
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, fg_color=TASKBAR["bg"], height=48, corner_radius=0)
        self.state = state
        self.pack_propagate(False)
        self._build()
    
    def _build(self):
        # System tray (right side)
        self.tray = ctk.CTkFrame(self, fg_color="transparent")
        self.tray.pack(side="right", padx=12, pady=8)
        
        # Tray icons
        tray_frame = ctk.CTkFrame(self.tray, fg_color="transparent")
        tray_frame.pack(side="right")
        
        ctk.CTkLabel(tray_frame, text="^", font=ctk.CTkFont(size=10), text_color=TASKBAR["text"]).pack(side="left", padx=4)
        ctk.CTkLabel(tray_frame, text="🔊", font=ctk.CTkFont(size=12)).pack(side="left", padx=4)
        ctk.CTkLabel(tray_frame, text="📶", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
        ctk.CTkLabel(tray_frame, text="🔋", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
        
        # Date/Time
        dt_frame = ctk.CTkFrame(self.tray, fg_color="transparent")
        dt_frame.pack(side="right", padx=8)
        ctk.CTkLabel(dt_frame, text="10:30 AM", font=ctk.CTkFont(size=10), text_color=TASKBAR["text"]).pack()
        ctk.CTkLabel(dt_frame, text="1/27/2026", font=ctk.CTkFont(size=10), text_color=TASKBAR["text"]).pack()
        
        # Main icons container
        self.icons_container = ctk.CTkFrame(self, fg_color="transparent")
    
    def update(self):
        self.icons_container.pack_forget()
        for w in self.icons_container.winfo_children():
            w.destroy()
        
        # Position based on alignment
        if self.state.center_taskbar:
            self.icons_container.pack(expand=True)
        else:
            self.icons_container.pack(side="left", padx=4)
        
        icons = ctk.CTkFrame(self.icons_container, fg_color="transparent")
        icons.pack(pady=4)
        
        # Start button
        start = ctk.CTkFrame(icons, fg_color="transparent", width=44, height=40)
        start.pack(side="left", padx=2)
        start.pack_propagate(False)
        ctk.CTkLabel(start, text="⊞", font=ctk.CTkFont(size=22), text_color=TASKBAR["text"]).pack(expand=True)
        
        # Search
        if self.state.search_mode == 2:
            # Full search box
            search = ctk.CTkFrame(icons, fg_color=TASKBAR["search_bg"], corner_radius=20, width=200, height=36, border_width=1, border_color=TASKBAR["search_border"])
            search.pack(side="left", padx=4)
            search.pack_propagate(False)
            sf = ctk.CTkFrame(search, fg_color="transparent")
            sf.pack(expand=True)
            ctk.CTkLabel(sf, text="🔍", font=ctk.CTkFont(size=13)).pack(side="left", padx=(16, 6))
            ctk.CTkLabel(sf, text="Search", font=ctk.CTkFont(size=12), text_color=TASKBAR["search_text"]).pack(side="left")
        elif self.state.search_mode == 1:
            # Search icon only
            si = ctk.CTkFrame(icons, fg_color="transparent", width=44, height=40)
            si.pack(side="left", padx=2)
            si.pack_propagate(False)
            ctk.CTkLabel(si, text="🔍", font=ctk.CTkFont(size=16), text_color=TASKBAR["text"]).pack(expand=True)
        
        # Task View
        if self.state.taskview_button:
            tv = ctk.CTkFrame(icons, fg_color="transparent", width=44, height=40)
            tv.pack(side="left", padx=2)
            tv.pack_propagate(False)
            ctk.CTkLabel(tv, text="⧉", font=ctk.CTkFont(size=16), text_color=TASKBAR["text"]).pack(expand=True)
        
        # Widgets
        if self.state.widgets_button:
            wg = ctk.CTkFrame(icons, fg_color="transparent", width=44, height=40)
            wg.pack(side="left", padx=2)
            wg.pack_propagate(False)
            ctk.CTkLabel(wg, text="☀", font=ctk.CTkFont(size=18), text_color=TASKBAR["text"]).pack(expand=True)
        
        # Separator
        ctk.CTkFrame(icons, fg_color="#444444", width=1, height=24).pack(side="left", padx=8, pady=8)
        
        # Pinned apps
        apps = [("📁", True, "File Explorer"), ("🌐", False, "Edge"), ("📝", False, "Notepad"), ("🎵", False, "Spotify")]
        
        for emoji, active, name in apps:
            app = ctk.CTkFrame(icons, fg_color=TASKBAR["item_active"] if active else "transparent", width=44, height=40, corner_radius=4)
            app.pack(side="left", padx=2)
            app.pack_propagate(False)
            
            ctk.CTkLabel(app, text=emoji, font=ctk.CTkFont(size=16)).pack(expand=True)
            
            # Active indicator
            if active:
                ind = ctk.CTkFrame(app, fg_color=TASKBAR["indicator"], width=20, height=3, corner_radius=1)
                ind.place(relx=0.5, rely=0.92, anchor="center")


# ============================================================================
# PREVIEW PANELS
# ============================================================================

class BasePreview(ctk.CTkScrollableFrame):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, fg_color=UI["card"], corner_radius=8)
        self.state = state


class AppearancePreview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="File Explorer Preview", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        self.explorer = Win11Explorer(self, self.state)
        self.explorer.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        
        # Settings summary
        ctk.CTkLabel(self, text="Active Settings", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).pack(anchor="w", padx=10, pady=(6, 4))
        self.status = ctk.CTkFrame(self, fg_color="transparent")
        self.status.pack(fill="x", padx=6, pady=(0, 10))
    
    def _render_status(self):
        for w in self.status.winfo_children():
            w.destroy()
        
        settings = [
            ("Extensions", self.state.show_extensions), ("Hidden", self.state.show_hidden),
            ("System", self.state.show_system), ("Checkboxes", self.state.show_checkboxes),
            ("Colored", self.state.colored_encrypted), ("Compact", self.state.compact_mode),
            ("Thumbnails", self.state.show_thumbnails), ("Overlay", self.state.show_type_overlay),
            ("Status Bar", self.state.show_status_bar), ("Full Row", self.state.full_row_select),
            ("Path Title", self.state.full_path_title), ("Path Addr", self.state.full_path_address),
        ]
        
        for i, (name, val) in enumerate(settings):
            f = ctk.CTkFrame(self.status, fg_color=UI["hover"], corner_radius=4)
            f.grid(row=i//4, column=i%4, padx=2, pady=2, sticky="ew")
            self.status.grid_columnconfigure(i%4, weight=1)
            
            ctk.CTkLabel(f, text=name, font=ctk.CTkFont(size=9), text_color=UI["text_dim"]).pack(padx=4, pady=(3, 0))
            ctk.CTkLabel(f, text="ON" if val else "OFF", font=ctk.CTkFont(size=9, weight="bold"), text_color=UI["on"] if val else UI["off"]).pack(padx=4, pady=(0, 3))
    
    def update(self):
        self.explorer.state = self.state
        self.explorer.update()
        self._render_status()


class NavigationPreview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="Navigation Pane Preview", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        self.explorer = Win11Explorer(self, self.state)
        self.explorer.pack(fill="x", padx=6, pady=(0, 6))
        
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).pack(anchor="w", padx=10, pady=(6, 4))
        self.info = ctk.CTkFrame(self, fg_color=UI["hover"], corner_radius=6)
        self.info.pack(fill="x", padx=6, pady=(0, 10))
    
    def _render_info(self):
        for w in self.info.winfo_children():
            w.destroy()
        c = ctk.CTkFrame(self.info, fg_color="transparent")
        c.pack(fill="x", padx=10, pady=8)
        
        for label, val in [
            ("Opens to", "This PC" if self.state.launch_to_thispc else "Home"),
            ("Expand to folder", "ON" if self.state.expand_to_folder else "OFF"),
            ("Show all folders", "ON" if self.state.show_all_folders else "OFF"),
            ("Separate process", "ON" if self.state.separate_process else "OFF"),
            ("Sharing", "Simple" if self.state.use_sharing_wizard else "Advanced"),
        ]:
            r = ctk.CTkFrame(c, fg_color="transparent")
            r.pack(fill="x", pady=1)
            ctk.CTkLabel(r, text=label + ":", font=ctk.CTkFont(size=10), text_color=UI["text_sec"]).pack(side="left")
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=10, weight="bold"), text_color=UI["text"]).pack(side="right")
    
    def update(self):
        self.explorer.state = self.state
        self.explorer.update()
        self._render_info()


class TaskbarPreview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="Taskbar Preview", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        self.taskbar = Win11Taskbar(self, self.state)
        self.taskbar.pack(fill="x", padx=6, pady=(0, 10))
        
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).pack(anchor="w", padx=10, pady=(6, 4))
        self.info = ctk.CTkFrame(self, fg_color=UI["hover"], corner_radius=6)
        self.info.pack(fill="x", padx=6, pady=(0, 6))
        
        ctk.CTkLabel(self, text="Right-Click Menu", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).pack(anchor="w", padx=10, pady=(6, 4))
        self.menu = ctk.CTkFrame(self, fg_color=UI["hover"], corner_radius=6)
        self.menu.pack(fill="x", padx=6, pady=(0, 10))
    
    def _render_info(self):
        for w in self.info.winfo_children():
            w.destroy()
        c = ctk.CTkFrame(self.info, fg_color="transparent")
        c.pack(fill="x", padx=10, pady=8)
        
        for label, val in [
            ("Alignment", "Center" if self.state.center_taskbar else "Left"),
            ("Search", ["Hidden", "Icon", "Box"][self.state.search_mode]),
            ("Task View", "Shown" if self.state.taskview_button else "Hidden"),
            ("Widgets", "Shown" if self.state.widgets_button else "Hidden"),
        ]:
            r = ctk.CTkFrame(c, fg_color="transparent")
            r.pack(fill="x", pady=1)
            ctk.CTkLabel(r, text=label + ":", font=ctk.CTkFont(size=10), text_color=UI["text_sec"]).pack(side="left")
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=10, weight="bold"), text_color=UI["text"]).pack(side="right")
    
    def _render_menu(self):
        for w in self.menu.winfo_children():
            w.destroy()
        c = ctk.CTkFrame(self.menu, fg_color="transparent")
        c.pack(fill="x", padx=10, pady=8)
        
        items = ["Pin to taskbar", "Maximize", "Minimize", "Close window"]
        if self.state.end_task:
            items.extend(["---", "End task"])
        
        for item in items:
            if item == "---":
                ctk.CTkFrame(c, fg_color=UI["border"], height=1).pack(fill="x", pady=4)
            else:
                tc = UI["off"] if item == "End task" else UI["text_sec"]
                ctk.CTkLabel(c, text=item, font=ctk.CTkFont(size=10), text_color=tc).pack(anchor="w", pady=1)
    
    def update(self):
        self.taskbar.state = self.state
        self.taskbar.update()
        self._render_info()
        self._render_menu()


class PrivacyPreview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="Privacy Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        self.content = ctk.CTkFrame(self, fg_color=UI["hover"], corner_radius=6)
        self.content.pack(fill="x", padx=6, pady=(0, 10))
    
    def update(self):
        for w in self.content.winfo_children():
            w.destroy()
        c = ctk.CTkFrame(self.content, fg_color="transparent")
        c.pack(fill="x", padx=10, pady=8)
        
        for label, val in [
            ("Frequent Folders", self.state.show_frequent),
            ("Recent Files", self.state.show_recent),
            ("Track Documents", self.state.track_docs),
            ("Track Apps", self.state.track_apps),
            ("OneDrive Promos", self.state.sync_notifications),
            ("Auto App Install", self.state.silent_installs),
        ]:
            r = ctk.CTkFrame(c, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=11), text_color=UI["text_sec"]).pack(side="left")
            ctk.CTkLabel(r, text="ON" if val else "OFF", font=ctk.CTkFont(size=11, weight="bold"), text_color=UI["on"] if val else UI["off"]).pack(side="right")


class SearchPreview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="Search Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        self.content = ctk.CTkFrame(self, fg_color=UI["hover"], corner_radius=6)
        self.content.pack(fill="x", padx=6, pady=(0, 10))
    
    def update(self):
        for w in self.content.winfo_children():
            w.destroy()
        c = ctk.CTkFrame(self.content, fg_color="transparent")
        c.pack(fill="x", padx=10, pady=8)
        
        for label, val in [("Bing Web Search", self.state.bing_search), ("Cortana", self.state.cortana), ("Search History", self.state.search_history)]:
            r = ctk.CTkFrame(c, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=11), text_color=UI["text_sec"]).pack(side="left")
            ctk.CTkLabel(r, text="ON" if val else "OFF", font=ctk.CTkFont(size=11, weight="bold"), text_color=UI["on"] if val else UI["off"]).pack(side="right")


class PerformancePreview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="Performance Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        self.content = ctk.CTkFrame(self, fg_color=UI["hover"], corner_radius=6)
        self.content.pack(fill="x", padx=6, pady=(0, 10))
    
    def update(self):
        for w in self.content.winfo_children():
            w.destroy()
        c = ctk.CTkFrame(self.content, fg_color="transparent")
        c.pack(fill="x", padx=10, pady=8)
        
        for label, val in [
            ("Taskbar Animations", self.state.taskbar_animations),
            ("Aero Peek", self.state.aero_peek),
            ("Thumbnail Cache", not self.state.disable_thumb_cache),
            ("Snap Assist", self.state.snap_assist),
            ("Snap Layouts", self.state.snap_layouts),
        ]:
            r = ctk.CTkFrame(c, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=11), text_color=UI["text_sec"]).pack(side="left")
            ctk.CTkLabel(r, text="ON" if val else "OFF", font=ctk.CTkFont(size=11, weight="bold"), text_color=UI["on"] if val else UI["off"]).pack(side="right")


class ThemePreview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="Theme Preview", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        
        comp = ctk.CTkFrame(self, fg_color="transparent")
        comp.pack(fill="x", padx=6, pady=(0, 6))
        comp.grid_columnconfigure(0, weight=1)
        comp.grid_columnconfigure(1, weight=1)
        
        # Dark
        dark = ctk.CTkFrame(comp, fg_color=EXP_DARK["content_bg"], corner_radius=6)
        dark.grid(row=0, column=0, sticky="nsew", padx=(0, 3), pady=4)
        ctk.CTkFrame(dark, fg_color=EXP_DARK["titlebar"], height=20, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(dark, text="📁 Folder", font=ctk.CTkFont(size=10), text_color=EXP_DARK["content_text"]).pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(dark, text="📄 File.txt", font=ctk.CTkFont(size=10), text_color=EXP_DARK["content_text"]).pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(dark, text="DARK", font=ctk.CTkFont(size=10, weight="bold"), text_color="#fff").pack(pady=4)
        
        # Light
        light = ctk.CTkFrame(comp, fg_color=EXP_LIGHT["content_bg"], corner_radius=6)
        light.grid(row=0, column=1, sticky="nsew", padx=(3, 0), pady=4)
        ctk.CTkFrame(light, fg_color=EXP_LIGHT["titlebar"], height=20, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(light, text="📁 Folder", font=ctk.CTkFont(size=10), text_color=EXP_LIGHT["content_text"]).pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(light, text="📄 File.txt", font=ctk.CTkFont(size=10), text_color=EXP_LIGHT["content_text"]).pack(anchor="w", padx=8, pady=2)
        ctk.CTkLabel(light, text="LIGHT", font=ctk.CTkFont(size=10, weight="bold"), text_color="#000").pack(pady=4)
        
        self.status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.status.pack(pady=(6, 10))
    
    def update(self):
        self.status.configure(text="Current: DARK MODE" if self.state.dark_mode else "Current: LIGHT MODE", text_color=UI["accent"] if self.state.dark_mode else UI["text"])


class Windows11Preview(BasePreview):
    def __init__(self, parent, state: PreviewState):
        super().__init__(parent, state)
        ctk.CTkLabel(self, text="Windows 11 Features", font=ctk.CTkFont(size=14, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=10, pady=(10, 6))
        self.explorer = Win11Explorer(self, self.state)
        self.explorer.pack(fill="x", padx=6, pady=(0, 6))
        
        ctk.CTkLabel(self, text="Context Menu Style", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).pack(anchor="w", padx=10, pady=(6, 4))
        self.status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11, weight="bold"))
        self.status.pack(anchor="w", padx=10, pady=(0, 10))
    
    def update(self):
        self.explorer.state = self.state
        self.explorer.update()
        self.status.configure(
            text="CLASSIC (Full Win10 Menu)" if self.state.classic_context_menu else "MODERN (Win11 Simplified)",
            text_color=UI["on"] if self.state.classic_context_menu else UI["text"]
        )


# ============================================================================
# UI COMPONENTS
# ============================================================================

class SettingCard(ctk.CTkFrame):
    def __init__(self, parent, setting: RegistrySetting, on_change: Callable = None):
        super().__init__(parent, fg_color=UI["card"], corner_radius=8)
        self.setting, self.on_change = setting, on_change
        self._policy_locked = is_policy_locked(setting.reg_path, setting.reg_name)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
        header.grid_columnconfigure(0, weight=1)

        nf = ctk.CTkFrame(header, fg_color="transparent")
        nf.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(nf, text=setting.name, font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["text"]).pack(side="left")
        if setting.warning:
            ctk.CTkLabel(nf, text=" ⚠", font=ctk.CTkFont(size=10), text_color=UI["off"]).pack(side="left")
        if self._policy_locked:
            ctk.CTkLabel(nf, text=" (GP)", font=ctk.CTkFont(size=9), text_color="#ff9800").pack(side="left")
        if setting.info:
            info_btn = ctk.CTkLabel(nf, text=" (?)", font=ctk.CTkFont(size=9), text_color=UI["accent"], cursor="hand2")
            info_btn.pack(side="left")
            info_btn.bind("<Button-1>", lambda e: self._show_info())

        self.switch_var = ctk.BooleanVar()
        self.switch = ctk.CTkSwitch(header, text="", variable=self.switch_var, command=self._toggle, width=40, height=20, switch_width=36, switch_height=18, progress_color=UI["accent"], button_color="#fff", fg_color=UI["hover"])
        self.switch.grid(row=0, column=1, sticky="e")

        desc_text = setting.description
        if self._policy_locked:
            desc_text += " [Locked by Group Policy]"
        ctk.CTkLabel(self, text=desc_text, font=ctk.CTkFont(size=10), text_color="#ff9800" if self._policy_locked else UI["text_sec"], wraplength=320, justify="left", anchor="w").grid(row=1, column=0, sticky="w", padx=12, pady=(0, 2))

        # Info text area (hidden by default)
        self.info_label = None
        self._info_visible = False

        # Bottom padding
        self._bottom_pad = ctk.CTkFrame(self, fg_color="transparent", height=8)
        self._bottom_pad.grid(row=3, column=0)

        self._load_state()
    
    def _show_info(self):
        if not self.setting.info:
            return
        if self._info_visible and self.info_label:
            self.info_label.grid_forget()
            self.info_label.destroy()
            self.info_label = None
            self._info_visible = False
        else:
            self.info_label = ctk.CTkLabel(
                self, text=self.setting.info,
                font=ctk.CTkFont(size=9, slant="italic"),
                text_color=UI["accent"], wraplength=310, justify="left", anchor="w"
            )
            self.info_label.grid(row=2, column=0, sticky="w", padx=12, pady=(2, 4))
            self._info_visible = True

    def _load_state(self):
        val = get_registry_value(self.setting.reg_path, self.setting.reg_name)
        if val is None: val = self.setting.default_value
        enabled = (val == self.setting.enable_value)
        self.switch_var.set(enabled)

    def _toggle(self):
        if self._policy_locked:
            messagebox.showwarning(
                "Group Policy Lock",
                f'"{self.setting.name}" is managed by Group Policy.\n\n'
                "The change may not persist or take effect. Contact your IT administrator."
            )
        enabled = self.switch_var.get()
        val = self.setting.enable_value if enabled else self.setting.disable_value
        set_registry_value(self.setting.reg_path, self.setting.reg_name, val, self.setting.reg_type)
        if self.on_change: self.on_change(self.setting, enabled)


class SpecialCard(ctk.CTkFrame):
    def __init__(self, parent, name, desc, get_fn, set_fn, on_change=None, preview_key=None):
        super().__init__(parent, fg_color=UI["card"], corner_radius=8)
        self.get_fn, self.set_fn, self.on_change, self.preview_key = get_fn, set_fn, on_change, preview_key
        self.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header, text=name, font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["text"]).grid(row=0, column=0, sticky="w")
        
        self.switch_var = ctk.BooleanVar(value=self.get_fn())
        self.switch = ctk.CTkSwitch(header, text="", variable=self.switch_var, command=self._toggle, width=40, height=20, switch_width=36, switch_height=18, progress_color=UI["accent"], button_color="#fff", fg_color=UI["hover"])
        self.switch.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(self, text=desc, font=ctk.CTkFont(size=10), text_color=UI["text_sec"], wraplength=320, justify="left", anchor="w").grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))
    
    def _toggle(self):
        self.set_fn(self.switch_var.get())
        if self.on_change: self.on_change(self.preview_key, self.switch_var.get())


class SearchModeCard(ctk.CTkFrame):
    def __init__(self, parent, on_change=None):
        super().__init__(parent, fg_color=UI["card"], corner_radius=8)
        self.on_change = on_change
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Taskbar Search", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["text"]).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        
        rf = ctk.CTkFrame(self, fg_color="transparent")
        rf.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))
        self.mode_var = ctk.IntVar(value=SpecialSettings.get_search_mode())
        for v, t in [(0, "Hidden"), (1, "Icon"), (2, "Box")]:
            ctk.CTkRadioButton(rf, text=t, variable=self.mode_var, value=v, command=self._change, font=ctk.CTkFont(size=10), text_color=UI["text_sec"], fg_color=UI["accent"]).pack(side="left", padx=(0, 10))
    
    def _change(self):
        SpecialSettings.set_search_mode(self.mode_var.get())
        if self.on_change: self.on_change("search_mode", self.mode_var.get())


class NavButton(ctk.CTkButton):
    def __init__(self, parent, text, emoji, command, selected=False):
        self.selected = selected
        super().__init__(parent, text=f"{emoji}  {text}", command=command, font=ctk.CTkFont(size=11), text_color=UI["text"] if selected else UI["text_sec"], fg_color=UI["hover"] if selected else "transparent", hover_color=UI["hover"], anchor="w", height=32, corner_radius=6)
    
    def set_selected(self, selected):
        self.selected = selected
        self.configure(text_color=UI["text"] if selected else UI["text_sec"], fg_color=UI["hover"] if selected else "transparent")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class App(ctk.CTk):
    def __init__(self, initial_focus: Optional[str] = None):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1500x850")
        self.minsize(1300, 750)
        self.configure(fg_color=UI["bg"])
        
        self.os_version = get_windows_version()
        self.preview_state = PreviewState()
        self._load_preview_state()
        
        self.all_settings = get_all_settings()
        self.settings = self._filter_os(self.all_settings)
        self.categories = self._get_categories()
        self.current_cat = self._resolve_focus(initial_focus) or (self.categories[0] if self.categories else None)
        self.nav_buttons = {}
        self.previews = {}
        
        self._build_ui()
        self._create_previews()
        if self.current_cat: self._show_category(self.current_cat)

    def _resolve_focus(self, focus: Optional[str]) -> Optional[str]:
        if not focus:
            return None
        normalized = focus.strip().lower().replace("-", "_")
        for category in self.categories:
            if normalized == category.lower().replace(" ", "_"):
                return category
        for setting in self.settings:
            if normalized in (setting.id.lower(), setting.name.lower().replace(" ", "_")):
                return setting.category
        if normalized == "tools":
            return "Tools"
        return None
    
    def _load_preview_state(self):
        adv = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        exp = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
        cab = r"Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState"
        theme = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        
        def gb(path, name, ev, default, inv=False):
            v = get_registry_value(path, name)
            r = (v == ev) if v is not None else default
            return not r if inv else r
        
        self.preview_state.show_extensions = gb(adv, "HideFileExt", 0, False, True)
        self.preview_state.show_hidden = gb(adv, "Hidden", 1, False)
        self.preview_state.show_system = gb(adv, "ShowSuperHidden", 1, False)
        self.preview_state.show_checkboxes = gb(adv, "AutoCheckSelect", 1, False)
        self.preview_state.colored_encrypted = gb(adv, "ShowEncryptCompressedColor", 1, False)
        self.preview_state.compact_mode = gb(adv, "UseCompactMode", 1, False)
        self.preview_state.show_thumbnails = gb(adv, "IconsOnly", 0, True, True)
        self.preview_state.show_type_overlay = gb(adv, "ShowTypeOverlay", 1, True)
        self.preview_state.show_status_bar = gb(adv, "ShowStatusBar", 1, True)
        self.preview_state.full_row_select = gb(adv, "FullRowSelect", 1, True)
        self.preview_state.show_tooltips = gb(adv, "ShowInfoTip", 1, True)
        self.preview_state.full_path_title = gb(cab, "FullPath", 1, False)
        self.preview_state.full_path_address = gb(cab, "FullPathAddress", 1, False)
        self.preview_state.launch_to_thispc = gb(adv, "LaunchTo", 1, False)
        self.preview_state.expand_to_folder = gb(adv, "NavPaneExpandToCurrentFolder", 1, False)
        self.preview_state.show_all_folders = gb(adv, "NavPaneShowAllFolders", 1, False)
        self.preview_state.separate_process = gb(adv, "SeparateProcess", 1, False)
        self.preview_state.restore_folders = gb(adv, "PersistBrowsers", 1, False)
        self.preview_state.use_sharing_wizard = gb(adv, "SharingWizardOn", 1, True)
        self.preview_state.show_recent = gb(exp, "ShowRecent", 1, True)
        self.preview_state.show_frequent = gb(exp, "ShowFrequent", 1, True)
        self.preview_state.track_docs = gb(adv, "Start_TrackDocs", 1, True)
        self.preview_state.track_apps = gb(adv, "Start_TrackProgs", 1, True)
        self.preview_state.sync_notifications = gb(adv, "ShowSyncProviderNotifications", 1, True)
        self.preview_state.silent_installs = True
        self.preview_state.bing_search = True
        self.preview_state.cortana = True
        self.preview_state.search_history = True
        self.preview_state.taskview_button = gb(adv, "ShowTaskViewButton", 1, True)
        self.preview_state.widgets_button = gb(adv, "TaskbarDa", 1, True)
        self.preview_state.center_taskbar = gb(adv, "TaskbarAl", 1, True)
        self.preview_state.end_task = False
        self.preview_state.search_mode = SpecialSettings.get_search_mode()
        self.preview_state.taskbar_animations = gb(adv, "TaskbarAnimations", 1, True)
        self.preview_state.aero_peek = True
        self.preview_state.disable_thumb_cache = gb(adv, "DisableThumbnailCache", 1, False)
        self.preview_state.snap_assist = gb(adv, "SnapAssist", 1, True)
        self.preview_state.snap_layouts = gb(adv, "EnableSnapBar", 1, True)
        light = get_registry_value(theme, "AppsUseLightTheme")
        self.preview_state.dark_mode = (light == 0) if light is not None else True
        if self.os_version in [OSVersion.WINDOWS_11_23H2, OSVersion.WINDOWS_11_24H2]:
            self.preview_state.show_gallery = gb(adv, "ShowGallery", 1, True)
        else:
            self.preview_state.show_gallery = False
        self.preview_state.classic_context_menu = SpecialSettings.get_classic_context_menu()
    
    def _filter_os(self, settings):
        return [s for s in settings if is_setting_supported(s, self.os_version)]
    
    def _get_categories(self):
        cats, seen = [], set()
        for s in self.settings:
            if s.category not in seen:
                cats.append(s.category)
                seen.add(s.category)
        if self.os_version != OSVersion.WINDOWS_10 and "Windows 11" not in cats:
            cats.append("Windows 11")
        return cats
    
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0, minsize=180)
        self.grid_columnconfigure(1, weight=1, minsize=400)
        self.grid_columnconfigure(2, weight=0, minsize=480)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_settings()
        self._build_preview()
    
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=UI["sidebar"], width=180, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text=f"🛠 {APP_NAME}", font=ctk.CTkFont(size=16, weight="bold"), text_color=UI["text"]).pack(anchor="w", padx=12, pady=(16, 2))
        ctk.CTkLabel(sidebar, text=f"v{APP_VERSION}", font=ctk.CTkFont(size=9), text_color=UI["text_dim"]).pack(anchor="w", padx=12)

        # Search bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        self.search_entry = ctk.CTkEntry(
            sidebar, placeholder_text="Search settings...",
            textvariable=self.search_var,
            font=ctk.CTkFont(size=10), height=28,
            fg_color=UI["hover"], border_color=UI["border"],
            text_color=UI["text"], placeholder_text_color=UI["text_dim"]
        )
        self.search_entry.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkFrame(sidebar, fg_color=UI["border"], height=1).pack(fill="x", padx=12, pady=6)

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.pack(fill="both", expand=True, padx=6)

        emojis = {"Appearance": "🎨", "Navigation": "🧭", "Privacy": "🔒", "Search": "🔍", "Taskbar": "📌", "Performance": "⚡", "Theme": "🌙", "Windows 11": "🪟", "Tools": "🧰"}

        for cat in self.categories:
            btn = NavButton(nav, cat, emojis.get(cat, "📁"), lambda c=cat: self._on_nav(c), selected=(cat == self.current_cat))
            btn.pack(fill="x", pady=1)
            self.nav_buttons[cat] = btn

        # Tools button (Send To, Recent Wipe, Presets, Photo Viewer)
        ctk.CTkFrame(nav, fg_color=UI["border"], height=1).pack(fill="x", pady=4)
        tools_btn = NavButton(nav, "Tools", "🧰", lambda: self._on_nav("Tools"), selected=(self.current_cat == "Tools"))
        tools_btn.pack(fill="x", pady=1)
        self.nav_buttons["Tools"] = tools_btn

        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(fill="x", side="bottom", padx=8, pady=12)
        shell_row = ctk.CTkFrame(bottom, fg_color="transparent")
        shell_row.pack(fill="x", pady=(0, 6))
        ctk.CTkButton(shell_row, text="Refresh Shell", command=self._refresh_shell, font=ctk.CTkFont(size=10, weight="bold"), fg_color=UI["accent"], hover_color=UI["accent_hover"], height=30, corner_radius=6).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ctk.CTkButton(shell_row, text="Restart", command=self._restart, font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=30, corner_radius=6).pack(side="left", expand=True, fill="x", padx=(3, 0))

        br = ctk.CTkFrame(bottom, fg_color="transparent")
        br.pack(fill="x")
        ctk.CTkButton(br, text="Export", command=self._export, font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ctk.CTkButton(br, text="Import", command=self._import, font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(side="right", expand=True, fill="x", padx=(2, 0))

        br2 = ctk.CTkFrame(bottom, fg_color="transparent")
        br2.pack(fill="x", pady=(4, 0))
        ctk.CTkButton(br2, text="Export .reg", command=self._export_reg, font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ctk.CTkButton(br2, text="Presets", command=self._show_presets, font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(side="right", expand=True, fill="x", padx=(2, 0))

        br3 = ctk.CTkFrame(bottom, fg_color="transparent")
        br3.pack(fill="x", pady=(4, 0))
        ctk.CTkButton(br3, text="Export .ps1", command=self._export_ps1, font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(fill="x")
    
    def _build_settings(self):
        self.settings_panel = ctk.CTkFrame(self, fg_color=UI["bg"], corner_radius=0)
        self.settings_panel.grid(row=0, column=1, sticky="nsew")
        self.settings_panel.grid_columnconfigure(0, weight=1)
        self.settings_panel.grid_rowconfigure(1, weight=1)
        
        self.header = ctk.CTkLabel(self.settings_panel, text="", font=ctk.CTkFont(size=20, weight="bold"), text_color=UI["text"])
        self.header.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))
        
        self.scroll = ctk.CTkScrollableFrame(self.settings_panel, fg_color="transparent", scrollbar_button_color=UI["hover"])
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.scroll.grid_columnconfigure(0, weight=1)
    
    def _build_preview(self):
        self.preview_panel = ctk.CTkFrame(self, fg_color=UI["sidebar"], width=480, corner_radius=0)
        self.preview_panel.grid(row=0, column=2, sticky="nsew")
        self.preview_panel.grid_propagate(False)
        self.preview_panel.grid_columnconfigure(0, weight=1)
        self.preview_panel.grid_rowconfigure(1, weight=1)
        
        self.preview_title = ctk.CTkLabel(self.preview_panel, text="👁 Preview", font=ctk.CTkFont(size=13, weight="bold"), text_color=UI["text"])
        self.preview_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        
        self.preview_container = ctk.CTkFrame(self.preview_panel, fg_color="transparent")
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_rowconfigure(0, weight=1)
    
    def _create_previews(self):
        self.previews = {
            "Appearance": AppearancePreview(self.preview_container, self.preview_state),
            "Navigation": NavigationPreview(self.preview_container, self.preview_state),
            "Privacy": PrivacyPreview(self.preview_container, self.preview_state),
            "Search": SearchPreview(self.preview_container, self.preview_state),
            "Taskbar": TaskbarPreview(self.preview_container, self.preview_state),
            "Performance": PerformancePreview(self.preview_container, self.preview_state),
            "Theme": ThemePreview(self.preview_container, self.preview_state),
            "Windows 11": Windows11Preview(self.preview_container, self.preview_state),
        }
        for p in self.previews.values():
            p.grid(row=0, column=0, sticky="nsew")
            p.grid_remove()
    
    def _show_category(self, cat):
        self.current_cat = cat
        self.header.configure(text=cat)
        self.preview_title.configure(text=f"👁 {cat} Preview")

        for w in self.scroll.winfo_children(): w.destroy()
        row = 0

        # Tools page
        if cat == "Tools":
            self._render_tools_page()
            for name, preview in self.previews.items():
                preview.grid_remove()
            return

        # Search results page
        if cat == "_search":
            self._render_search_results()
            for name, preview in self.previews.items():
                preview.grid_remove()
            return

        if cat == "Windows 11" and self.os_version != OSVersion.WINDOWS_10:
            SpecialCard(self.scroll, "Classic Context Menu", "Full Win10 menu.", SpecialSettings.get_classic_context_menu, SpecialSettings.set_classic_context_menu, self._on_change, "classic_context_menu").grid(row=row, column=0, sticky="ew", pady=(0, 4))
            row += 1

            # Photo Viewer toggle
            SpecialCard(self.scroll, "Classic Photo Viewer", "Register Windows Photo Viewer for images.", is_photo_viewer_registered, set_photo_viewer, self._on_change, None).grid(row=row, column=0, sticky="ew", pady=(0, 4))
            row += 1

        if cat == "Taskbar":
            SearchModeCard(self.scroll, self._on_change).grid(row=row, column=0, sticky="ew", pady=(0, 4))
            row += 1

        cat_settings = [s for s in self.settings if s.category == cat]
        subcats = {}
        for s in cat_settings: subcats.setdefault(s.subcategory, []).append(s)

        for subcat, slist in subcats.items():
            ctk.CTkLabel(self.scroll, text=subcat, font=ctk.CTkFont(size=10, weight="bold"), text_color=UI["text_dim"]).grid(row=row, column=0, sticky="w", pady=(8 if row > 0 else 0, 4))
            row += 1
            for s in slist:
                SettingCard(self.scroll, s, self._on_setting_change).grid(row=row, column=0, sticky="ew", pady=(0, 4))
                row += 1

        for name, preview in self.previews.items():
            if name == cat:
                preview.grid()
                preview.state = self.preview_state
                preview.update()
            else:
                preview.grid_remove()
    
    def _on_nav(self, cat):
        for c, btn in self.nav_buttons.items(): btn.set_selected(c == cat)
        self._show_category(cat)
    
    def _on_setting_change(self, setting, value):
        if setting.preview_key:
            setattr(self.preview_state, setting.preview_key, value)
            if self.current_cat in self.previews:
                self.previews[self.current_cat].state = self.preview_state
                self.previews[self.current_cat].update()
    
    def _on_change(self, key, value):
        if key and hasattr(self.preview_state, key):
            setattr(self.preview_state, key, value)
            if self.current_cat in self.previews:
                self.previews[self.current_cat].state = self.preview_state
                self.previews[self.current_cat].update()
    
    # ================================================================
    # SEARCH
    # ================================================================

    def _on_search(self, *args):
        query = self.search_var.get().strip()
        if not query:
            # Restore to current category
            if self.current_cat and self.current_cat != "_search":
                self._show_category(self.current_cat)
            return
        self._show_category("_search")

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Simple fuzzy matching: all query words must appear in text."""
        query_lower = query.lower()
        text_lower = text.lower()
        # Direct substring
        if query_lower in text_lower:
            return True
        # All words must match
        words = query_lower.split()
        return all(w in text_lower for w in words)

    def _render_search_results(self):
        query = self.search_var.get().strip()
        self.header.configure(text=f'Search: "{query}"')

        row = 0
        matches = []
        for s in self.settings:
            searchable = f"{s.name} {s.description} {s.category} {s.subcategory} {s.id}"
            if s.info:
                searchable += f" {s.info}"
            if self._fuzzy_match(query, searchable):
                matches.append(s)

        if not matches:
            ctk.CTkLabel(self.scroll, text="No matching settings found.", font=ctk.CTkFont(size=12), text_color=UI["text_dim"]).grid(row=0, column=0, pady=20)
            return

        ctk.CTkLabel(self.scroll, text=f"{len(matches)} result(s)", font=ctk.CTkFont(size=10), text_color=UI["text_dim"]).grid(row=row, column=0, sticky="w", pady=(0, 6))
        row += 1

        for s in matches:
            card = SettingCard(self.scroll, s, self._on_setting_change)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 4))
            row += 1

    # ================================================================
    # TOOLS PAGE
    # ================================================================

    def _render_tools_page(self):
        self.header.configure(text="Tools")
        row = 0

        # --- Presets section ---
        ctk.CTkLabel(self.scroll, text="Presets", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).grid(row=row, column=0, sticky="w", pady=(0, 6))
        row += 1

        for name, preset in BUILTIN_PRESETS.items():
            pf = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=8)
            pf.grid(row=row, column=0, sticky="ew", pady=(0, 4))
            pf.grid_columnconfigure(0, weight=1)

            hdr = ctk.CTkFrame(pf, fg_color="transparent")
            hdr.pack(fill="x", padx=12, pady=(10, 2))
            hdr.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(hdr, text=name, font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["text"]).grid(row=0, column=0, sticky="w")
            ctk.CTkButton(hdr, text="Apply", command=lambda n=name: self._apply_preset(n), font=ctk.CTkFont(size=10, weight="bold"), fg_color=UI["accent"], hover_color=UI["accent_hover"], width=60, height=26, corner_radius=4).grid(row=0, column=1, sticky="e")

            ctk.CTkLabel(pf, text=preset["description"], font=ctk.CTkFont(size=10), text_color=UI["text_sec"], wraplength=320, justify="left", anchor="w").pack(anchor="w", padx=12, pady=(0, 10))
            row += 1

        # Save current as preset
        save_f = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=8)
        save_f.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        ctk.CTkButton(save_f, text="Save Current Settings as Preset...", command=self._save_preset_dialog, font=ctk.CTkFont(size=11), fg_color=UI["hover"], hover_color=UI["border"], height=32, corner_radius=4).pack(fill="x", padx=12, pady=10)
        row += 1

        # --- Send To Manager ---
        ctk.CTkLabel(self.scroll, text="Send To Folder", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).grid(row=row, column=0, sticky="w", pady=(12, 6))
        row += 1

        entries = get_sendto_entries()
        if entries:
            for entry in entries:
                ef = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=6)
                ef.grid(row=row, column=0, sticky="ew", pady=(0, 2))
                ef.grid_columnconfigure(0, weight=1)

                inner = ctk.CTkFrame(ef, fg_color="transparent")
                inner.pack(fill="x", padx=10, pady=6)
                inner.grid_columnconfigure(0, weight=1)

                icon = "🔗" if entry["is_link"] else "📄"
                ctk.CTkLabel(inner, text=f"{icon} {entry['name']}", font=ctk.CTkFont(size=10), text_color=UI["text"], anchor="w").grid(row=0, column=0, sticky="w")
                ctk.CTkButton(inner, text="Remove", command=lambda p=entry["path"]: self._remove_sendto(p), font=ctk.CTkFont(size=9), fg_color=UI["off"], hover_color="#d32f2f", width=55, height=22, corner_radius=3).grid(row=0, column=1, sticky="e")
                row += 1
        else:
            ctk.CTkLabel(self.scroll, text="No Send To entries found.", font=ctk.CTkFont(size=10), text_color=UI["text_dim"]).grid(row=row, column=0, sticky="w", pady=4)
            row += 1

        # --- Recent Items Wipe ---
        ctk.CTkLabel(self.scroll, text="Recent Items", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).grid(row=row, column=0, sticky="w", pady=(12, 6))
        row += 1

        wipe_f = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=8)
        wipe_f.grid(row=row, column=0, sticky="ew", pady=(0, 4))

        wipe_inner = ctk.CTkFrame(wipe_f, fg_color="transparent")
        wipe_inner.pack(fill="x", padx=12, pady=10)
        wipe_inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(wipe_inner, text="Clear all recent files, Jump Lists, and destination history.", font=ctk.CTkFont(size=10), text_color=UI["text_sec"], anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(wipe_inner, text="Wipe Now", command=self._wipe_recent, font=ctk.CTkFont(size=10, weight="bold"), fg_color=UI["off"], hover_color="#d32f2f", width=80, height=28, corner_radius=4).grid(row=0, column=1, sticky="e", padx=(8, 0))
        row += 1

        # --- Classic Photo Viewer ---
        ctk.CTkLabel(self.scroll, text="Photo Viewer", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).grid(row=row, column=0, sticky="w", pady=(12, 6))
        row += 1

        SpecialCard(self.scroll, "Classic Photo Viewer", "Register Windows Photo Viewer for .jpg, .png, .bmp, .gif, .tif, .ico images.", is_photo_viewer_registered, set_photo_viewer, self._on_change, None).grid(row=row, column=0, sticky="ew", pady=(0, 4))
        row += 1

        # --- Diff View ---
        ctk.CTkLabel(self.scroll, text="Diff View", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).grid(row=row, column=0, sticky="w", pady=(12, 6))
        row += 1

        diff_f = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=8)
        diff_f.grid(row=row, column=0, sticky="ew", pady=(0, 4))

        diff_inner = ctk.CTkFrame(diff_f, fg_color="transparent")
        diff_inner.pack(fill="x", padx=12, pady=10)
        diff_inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(diff_inner, text="Compare current system state against a saved profile or preset.", font=ctk.CTkFont(size=10), text_color=UI["text_sec"], anchor="w").grid(row=0, column=0, sticky="w")

        diff_btns = ctk.CTkFrame(diff_inner, fg_color="transparent")
        diff_btns.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ctk.CTkButton(diff_btns, text="Diff vs File...", command=self._diff_vs_file, font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=28, corner_radius=4).pack(side="left", padx=(0, 4))
        for pname in BUILTIN_PRESETS:
            ctk.CTkButton(diff_btns, text=f"vs {pname}", command=lambda n=pname: self._diff_vs_preset(n), font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(side="left", padx=2)
        row += 1

        # --- Deployment ---
        ctk.CTkLabel(self.scroll, text="Deployment", font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["accent"]).grid(row=row, column=0, sticky="w", pady=(12, 6))
        row += 1

        deploy_f = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=8)
        deploy_f.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        deploy_f.grid_columnconfigure(0, weight=1)

        deploy_inner = ctk.CTkFrame(deploy_f, fg_color="transparent")
        deploy_inner.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(deploy_inner, text="Export PowerShell deployment scripts, backup bundles, and shell integrations.", font=ctk.CTkFont(size=10), text_color=UI["text_sec"], anchor="w", wraplength=350, justify="left").pack(anchor="w", pady=(0, 8))

        deploy_btns = ctk.CTkFrame(deploy_inner, fg_color="transparent")
        deploy_btns.pack(fill="x")
        ctk.CTkButton(deploy_btns, text="Export .ps1", command=self._export_ps1, font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=28, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ctk.CTkButton(deploy_btns, text="All Users .ps1", command=lambda: self._export_ps1(all_users=True), font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=28, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(3, 0))

        bundle_btns = ctk.CTkFrame(deploy_inner, fg_color="transparent")
        bundle_btns.pack(fill="x", pady=(6, 0))
        ctk.CTkButton(bundle_btns, text="Backup Bundle", command=self._backup_bundle, font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=28, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ctk.CTkButton(bundle_btns, text="Restore Bundle", command=self._restore_bundle, font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=28, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(3, 0))

        state_btns = ctk.CTkFrame(deploy_inner, fg_color="transparent")
        state_btns.pack(fill="x", pady=(6, 0))
        context_text = "Remove Shell Menu" if is_context_menu_installed() else "Install Shell Menu"
        darkmode_text = "Remove Auto Dark" if is_darkmode_auto_switch_installed() else "Install Auto Dark"
        ctk.CTkButton(state_btns, text=context_text, command=self._toggle_context_menu, font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=28, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ctk.CTkButton(state_btns, text=darkmode_text, command=self._toggle_darkmode_auto_switch, font=ctk.CTkFont(size=10), fg_color=UI["hover"], hover_color=UI["border"], height=28, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(3, 0))
        row += 1

    def _diff_vs_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        data = load_preset_from_file(path)
        if not data:
            messagebox.showerror("Error", "Could not load profile.")
            return
        profile_settings = data.get("settings", data)
        self._show_diff(os.path.basename(path), profile_settings)

    def _diff_vs_preset(self, name: str):
        preset = BUILTIN_PRESETS.get(name)
        if preset:
            self._show_diff(name, preset["settings"])

    def _show_diff(self, profile_name: str, profile_settings: dict):
        """Show a diff between current system state and a profile."""
        self.header.configure(text=f"Diff: Current vs {profile_name}")
        self.preview_title.configure(text=f"Diff Results")
        for w in self.scroll.winfo_children():
            w.destroy()
        for name, preview in self.previews.items():
            preview.grid_remove()

        row = 0
        settings_map = {s.id: s for s in self.settings}
        diffs = []
        matches = []

        for sid, target_val in profile_settings.items():
            if sid.startswith("_"):
                continue
            s = settings_map.get(sid)
            if not s:
                continue

            current_reg = get_registry_value(s.reg_path, s.reg_name)
            if current_reg is None:
                current_reg = s.default_value

            current_enabled = (current_reg == s.enable_value)

            if isinstance(target_val, bool):
                if current_enabled != target_val:
                    diffs.append((s, current_enabled, target_val))
                else:
                    matches.append((s, current_enabled))
            elif isinstance(target_val, int):
                if current_reg != target_val:
                    diffs.append((s, current_reg, target_val))
                else:
                    matches.append((s, current_reg))

        # Summary
        total = len(diffs) + len(matches)
        ctk.CTkLabel(self.scroll, text=f"{len(diffs)} difference(s) out of {total} setting(s)", font=ctk.CTkFont(size=11, weight="bold"), text_color=UI["text"]).grid(row=row, column=0, sticky="w", pady=(0, 8))
        row += 1

        if diffs:
            ctk.CTkLabel(self.scroll, text="Differences", font=ctk.CTkFont(size=10, weight="bold"), text_color=UI["off"]).grid(row=row, column=0, sticky="w", pady=(0, 4))
            row += 1

            for s, current, target in diffs:
                df = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=6)
                df.grid(row=row, column=0, sticky="ew", pady=(0, 3))
                df.grid_columnconfigure(0, weight=1)

                inner = ctk.CTkFrame(df, fg_color="transparent")
                inner.pack(fill="x", padx=10, pady=6)
                inner.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(inner, text=s.name, font=ctk.CTkFont(size=11, weight="bold"), text_color=UI["text"]).grid(row=0, column=0, sticky="w")

                vals = ctk.CTkFrame(inner, fg_color="transparent")
                vals.grid(row=0, column=1, sticky="e")

                cur_str = str(current) if not isinstance(current, bool) else ("ON" if current else "OFF")
                tgt_str = str(target) if not isinstance(target, bool) else ("ON" if target else "OFF")
                ctk.CTkLabel(vals, text=cur_str, font=ctk.CTkFont(size=10, weight="bold"), text_color=UI["off"]).pack(side="left", padx=(0, 4))
                ctk.CTkLabel(vals, text="->", font=ctk.CTkFont(size=10), text_color=UI["text_dim"]).pack(side="left", padx=2)
                ctk.CTkLabel(vals, text=tgt_str, font=ctk.CTkFont(size=10, weight="bold"), text_color=UI["on"]).pack(side="left", padx=(4, 0))
                row += 1

        if matches:
            ctk.CTkLabel(self.scroll, text="Matching", font=ctk.CTkFont(size=10, weight="bold"), text_color=UI["on"]).grid(row=row, column=0, sticky="w", pady=(8, 4))
            row += 1

            for s, val in matches:
                mf = ctk.CTkFrame(self.scroll, fg_color=UI["card"], corner_radius=6)
                mf.grid(row=row, column=0, sticky="ew", pady=(0, 2))

                inner = ctk.CTkFrame(mf, fg_color="transparent")
                inner.pack(fill="x", padx=10, pady=4)
                inner.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(inner, text=s.name, font=ctk.CTkFont(size=10), text_color=UI["text_sec"]).grid(row=0, column=0, sticky="w")
                val_str = str(val) if not isinstance(val, bool) else ("ON" if val else "OFF")
                ctk.CTkLabel(inner, text=val_str, font=ctk.CTkFont(size=9), text_color=UI["on"]).grid(row=0, column=1, sticky="e")
                row += 1

    def _apply_preset(self, name: str):
        preset = BUILTIN_PRESETS.get(name)
        if not preset:
            return
        if not messagebox.askyesno("Apply Preset", f'Apply "{name}" preset?\n\n{preset["description"]}'):
            return
        count = apply_preset(preset["settings"], self.all_settings, self.os_version)
        self._load_preview_state()
        for p in self.previews.values():
            p.state = self.preview_state
        messagebox.showinfo(
            "Preset Applied",
            f'Applied {count} settings from "{name}".\n\nTargeted shell refresh was sent. Restart Explorer remains available if Windows does not repaint every view.',
        )
        self._show_category(self.current_cat)

    def _save_preset_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter a name for this preset:", title="Save Preset")
        name = dialog.get_input()
        if not name:
            return
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile=f"{name.replace(' ', '_')}.json"
        )
        if path:
            save_preset_to_file(name, f"User preset: {name}", self.settings, path)
            messagebox.showinfo("Saved", f"Preset saved to:\n{path}")

    def _remove_sendto(self, path: str):
        name = os.path.basename(path)
        if messagebox.askyesno("Remove Send To Entry", f'Remove "{name}" from Send To?'):
            if remove_sendto_entry(path):
                self._show_category("Tools")  # Refresh
            else:
                messagebox.showerror("Error", "Could not remove the entry.")

    def _wipe_recent(self):
        if not messagebox.askyesno("Wipe Recent Items", "This will clear:\n- Recent files\n- Jump Lists\n- AutomaticDestinations\n- CustomDestinations\n\nContinue?"):
            return
        results = wipe_recent_items()
        messagebox.showinfo("Done", f"Deleted {results['deleted']} file(s).\nErrors: {results['errors']}")

    def _show_presets(self):
        self._on_nav("Tools")

    def _export_reg(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".reg",
            filetypes=[("Registry File", "*.reg")],
            initialfile="ExplorerTweaks_settings.reg"
        )
        if path:
            export_reg_file(self.settings, path)
            messagebox.showinfo("Export", f"Registry file saved:\n{path}\n\nDouble-click to import on any PC.")

    def _export_ps1(self, all_users: bool = False):
        from tkinter import filedialog
        initial = "ExplorerTweaks_apply_all_users.ps1" if all_users else "ExplorerTweaks_apply_current_user.ps1"
        path = filedialog.asksaveasfilename(
            defaultextension=".ps1",
            filetypes=[("PowerShell Script", "*.ps1")],
            initialfile=initial,
        )
        if path:
            export_ps1_file(self.settings, path, all_users=all_users)
            mode = "all loaded users by default" if all_users else "current user by default"
            messagebox.showinfo("Export", f"PowerShell deployment script saved:\n{path}\n\nMode: {mode}.")

    def _backup_bundle(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("Backup Bundle", "*.zip")],
            initialfile="ExplorerTweaks_backup.zip",
        )
        if path:
            try:
                metadata = create_backup_bundle(path)
                count = len(metadata.get("registry_exports", []))
                messagebox.showinfo("Backup", f"Backup bundle saved:\n{path}\n\nRegistry exports: {count}")
            except Exception as exc:
                messagebox.showerror("Backup", str(exc))

    def _restore_bundle(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Backup Bundle", "*.zip")])
        if path:
            try:
                results = restore_backup_bundle(path)
                messagebox.showinfo(
                    "Restore",
                    f"Restore complete.\n\nRegistry files: {results['registry_imported']}\nFiles restored: {results['files_restored']}\nErrors: {results['errors']}",
                )
            except Exception as exc:
                messagebox.showerror("Restore", str(exc))

    def _toggle_context_menu(self):
        enable = not is_context_menu_installed()
        if set_context_menu_integration(enable):
            messagebox.showinfo("Shell Menu", "ExplorerTweaks shell menu installed." if enable else "ExplorerTweaks shell menu removed.")
            self._show_category("Tools")
        else:
            messagebox.showerror("Shell Menu", "Could not update ExplorerTweaks shell menu.")

    def _toggle_darkmode_auto_switch(self):
        try:
            if is_darkmode_auto_switch_installed():
                uninstall_darkmode_auto_switch()
                messagebox.showinfo("Auto Dark Mode", "ExplorerTweaks auto dark-mode task removed.")
            else:
                path = install_darkmode_auto_switch()
                messagebox.showinfo("Auto Dark Mode", f"ExplorerTweaks auto dark-mode task installed.\n\nScript:\n{path}")
            self._show_category("Tools")
        except Exception as exc:
            messagebox.showerror("Auto Dark Mode", str(exc))

    def _refresh_shell(self):
        report = refresh_shell_now()
        if report.success:
            detail = "\n".join(report.messages) or "Targeted shell refresh sent."
            messagebox.showinfo("Refresh Shell", f"{detail}\n\nRestart Explorer remains available if Windows does not repaint every view.")
        else:
            messagebox.showwarning(
                "Refresh Shell",
                "\n".join(report.errors) + "\n\nRestart Explorer remains available as an explicit fallback.",
            )

    def _restart(self):
        if messagebox.askyesno("Restart Explorer", "Force restart Explorer as a fallback?"):
            if restart_explorer():
                messagebox.showinfo("Restart Explorer", "Explorer restarted.")
            else:
                messagebox.showerror("Restart Explorer", "Could not restart Explorer. Check the console output for details.")

    def _export(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            data = {s.id: get_registry_value(s.reg_path, s.reg_name) for s in self.settings if get_registry_value(s.reg_path, s.reg_name) is not None}
            data["_classic"], data["_search"] = SpecialSettings.get_classic_context_menu(), SpecialSettings.get_search_mode()
            with open(path, 'w', encoding="utf-8") as f: json.dump(data, f, indent=2)
            messagebox.showinfo("Export", f"Saved:\n{path}")
    
    def _import(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r', encoding="utf-8-sig") as f: data = json.load(f)
            count = apply_profile_values(data.get("settings", data), self.settings, self.os_version)
            self._load_preview_state()
            for p in self.previews.values(): p.state = self.preview_state
            self._show_category(self.current_cat)
            messagebox.showinfo("Import", f"Applied {count} setting(s).")


def cli_apply(profile_path: str, dry_run: bool = False, multi_user: bool = False):
    """Apply a profile JSON from the command line."""
    global DRY_RUN
    DRY_RUN = dry_run

    if not os.path.isfile(profile_path):
        print(f"Error: File not found: {profile_path}")
        sys.exit(1)

    data = load_preset_from_file(profile_path)
    if not data:
        print(f"Error: Could not parse: {profile_path}")
        sys.exit(1)

    settings_dict = data.get("settings", data)
    # If it's a plain export (id -> value), convert to toggle format
    all_s = get_all_settings()
    os_ver = get_windows_version()
    name = data.get("name", os.path.basename(profile_path))

    print(f"{'[DRY-RUN] ' if dry_run else ''}Applying profile: {name}")
    print(f"OS: {os_ver.value}")
    print()

    count = apply_profile_values(settings_dict, all_s, os_ver, multi_user=multi_user)

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Applied {count} setting(s).")
    if not dry_run:
        print("Targeted shell refresh sent where supported. Restart Explorer manually only if a view does not repaint.")


def cli_export(output_path: str, fmt: str = "json", all_users: bool = False):
    """Export current settings from CLI."""
    all_s = get_all_settings()

    if fmt == "reg":
        export_reg_file(all_s, output_path)
        print(f"Exported .reg file: {output_path}")
    elif fmt == "ps1":
        export_ps1_file(all_s, output_path, all_users=all_users)
        print(f"Exported PowerShell script: {output_path}")
    else:
        data = {s.id: get_registry_value(s.reg_path, s.reg_name) for s in all_s if get_registry_value(s.reg_path, s.reg_name) is not None}
        data["_classic"] = SpecialSettings.get_classic_context_menu()
        data["_search"] = SpecialSettings.get_search_mode()
        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Exported JSON: {output_path}")


def cli_export_profile_ps1(profile_path: str, output_path: str, all_users: bool = False):
    export_profile_ps1(profile_path, output_path, all_users=all_users)
    print(f"Exported profile PowerShell script: {output_path}")


def parse_computer_targets(computer_args: List[str], computers_arg: Optional[str]) -> List[str]:
    targets: List[str] = []
    for value in computer_args:
        targets.extend(part.strip() for part in value.split(",") if part.strip())
    if computers_arg:
        targets.extend(part.strip() for part in computers_arg.split(",") if part.strip())
    return list(dict.fromkeys(targets))


def cli_list_presets():
    """List available built-in presets."""
    print("Built-in Presets:")
    print()
    for name, preset in BUILTIN_PRESETS.items():
        print(f"  {name}")
        print(f"    {preset['description']}")
        print(f"    Settings: {len(preset['settings'])}")
        print()


def main():
    if platform.system() != "Windows":
        print("Windows only.")
        return

    parser = argparse.ArgumentParser(
        prog="ExplorerTweaks",
        description="Windows File Explorer Configuration Utility",
    )
    parser.add_argument("--version", action="version", version=f"ExplorerTweaks v{APP_VERSION}")
    parser.add_argument("--apply", metavar="PROFILE", help="Apply a JSON profile (preset or exported settings)")
    parser.add_argument("--preset", metavar="NAME", help="Apply a built-in preset (Minimal, Privacy, Power User)")
    parser.add_argument("--export", metavar="FILE", help="Export current settings to JSON or .reg file")
    parser.add_argument("--format", choices=["json", "reg", "ps1"], default="json", help="Export format (default: json)")
    parser.add_argument("--export-profile-ps1", nargs=2, metavar=("PROFILE", "FILE"), help="Export a profile as a PowerShell deployment script")
    parser.add_argument("--all-users", action="store_true", help="Apply/export PowerShell for all loaded user hives plus .DEFAULT")
    parser.add_argument("--remote-apply", metavar="PROFILE", help="Apply a profile to remote computers with PowerShell Remoting")
    parser.add_argument("--computer", action="append", default=[], help="Remote computer name for --remote-apply; repeat or comma-separate")
    parser.add_argument("--computers", help="Comma-separated remote computer list for --remote-apply")
    parser.add_argument("--backup", metavar="FILE", help="Create an ExplorerTweaks backup bundle")
    parser.add_argument("--restore", metavar="FILE", help="Restore an ExplorerTweaks backup bundle")
    parser.add_argument("--install-context-menu", action="store_true", help="Install ExplorerTweaks right-click shell entries")
    parser.add_argument("--uninstall-context-menu", action="store_true", help="Remove ExplorerTweaks right-click shell entries")
    parser.add_argument("--context-menu-status", action="store_true", help="Print ExplorerTweaks shell integration status")
    parser.add_argument("--install-darkmode-auto-switch", action="store_true", help="Install sunrise/sunset dark-mode scheduled task")
    parser.add_argument("--uninstall-darkmode-auto-switch", action="store_true", help="Remove sunrise/sunset dark-mode scheduled task")
    parser.add_argument("--darkmode-lat", type=float, help="Latitude override for dark-mode auto-switch")
    parser.add_argument("--darkmode-lon", type=float, help="Longitude override for dark-mode auto-switch")
    parser.add_argument("--focus", help="Open the GUI focused on a category or setting id")
    parser.add_argument("--dry-run", action="store_true", help="Print operations without writing to registry")
    parser.add_argument("--list-presets", action="store_true", help="List available built-in presets")
    parser.add_argument("--wipe-recent", action="store_true", help="Clear recent files, Jump Lists, and destinations")

    # Only parse if there are CLI arguments (otherwise launch GUI)
    if len(sys.argv) > 1:
        args = parser.parse_args()
        global DRY_RUN
        DRY_RUN = args.dry_run

        if args.list_presets:
            cli_list_presets()
            return

        if args.context_menu_status:
            print("installed" if is_context_menu_installed() else "not installed")
            return

        if args.install_context_menu or args.uninstall_context_menu:
            enabled = args.install_context_menu
            if set_context_menu_integration(enabled):
                print("ExplorerTweaks context menu installed." if enabled else "ExplorerTweaks context menu removed.")
                return
            print("Error: Could not update ExplorerTweaks context menu.")
            sys.exit(1)

        if args.install_darkmode_auto_switch:
            try:
                path = install_darkmode_auto_switch(args.darkmode_lat, args.darkmode_lon)
                print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Dark-mode auto-switch installed: {path}")
                return
            except Exception as exc:
                print(f"Error: {exc}")
                sys.exit(1)

        if args.uninstall_darkmode_auto_switch:
            if uninstall_darkmode_auto_switch():
                print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Dark-mode auto-switch removed.")
                return
            print("Error: Could not fully remove dark-mode auto-switch.")
            sys.exit(1)

        if args.backup:
            try:
                metadata = create_backup_bundle(args.backup)
                print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Backup bundle: {args.backup}")
                print(f"Registry exports: {len(metadata.get('registry_exports', []))}")
                print(f"Missing registry paths: {len(metadata.get('missing_registry_paths', []))}")
                return
            except Exception as exc:
                print(f"Error: {exc}")
                sys.exit(1)

        if args.restore:
            try:
                results = restore_backup_bundle(args.restore)
                print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Restore complete.")
                print(f"Registry files: {results['registry_imported']}")
                print(f"Files restored: {results['files_restored']}")
                print(f"Errors: {results['errors']}")
                return
            except Exception as exc:
                print(f"Error: {exc}")
                sys.exit(1)

        if args.export_profile_ps1:
            profile_path, output_path = args.export_profile_ps1
            try:
                cli_export_profile_ps1(profile_path, output_path, all_users=args.all_users)
                return
            except Exception as exc:
                print(f"Error: {exc}")
                sys.exit(1)

        if args.remote_apply:
            targets = parse_computer_targets(args.computer, args.computers)
            try:
                remote_apply_profile(args.remote_apply, targets, all_users=args.all_users, dry_run=DRY_RUN)
                print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Remote apply complete.")
                return
            except Exception as exc:
                print(f"Error: {exc}")
                sys.exit(1)

        if args.wipe_recent:
            results = wipe_recent_items()
            print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Deleted {results['deleted']} file(s). Errors: {results['errors']}")
            return

        if args.apply:
            cli_apply(args.apply, args.dry_run, multi_user=args.all_users)
            return

        if args.preset:
            preset = BUILTIN_PRESETS.get(args.preset)
            if not preset:
                print(f"Unknown preset: {args.preset}")
                print(f"Available: {', '.join(BUILTIN_PRESETS.keys())}")
                sys.exit(1)
            all_s = get_all_settings()
            os_ver = get_windows_version()
            print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Applying preset: {args.preset}")
            print(f"  {preset['description']}")
            count = apply_profile_values(preset["settings"], all_s, os_ver, multi_user=args.all_users)
            print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Applied {count} setting(s).")
            if not DRY_RUN:
                print("Targeted shell refresh sent where supported. Restart Explorer manually only if a view does not repaint.")
            return

        if args.export:
            cli_export(args.export, args.format, all_users=args.all_users)
            return

        # If only --dry-run or --focus is passed, launch GUI with that mode.
        if args.dry_run or args.focus:
            App(initial_focus=args.focus).mainloop()
            return

        parser.print_help()
        return

    App().mainloop()

if __name__ == "__main__":
    main()
