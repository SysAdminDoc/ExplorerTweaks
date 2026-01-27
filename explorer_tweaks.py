#!/usr/bin/env python3
"""
ExplorerTweaks v2.2.0 - Windows File Explorer Configuration Utility
Pixel-accurate Windows 11 File Explorer and Taskbar simulation.

Author: SysAdminDoc
License: MIT
"""

import customtkinter as ctk
from tkinter import messagebox
import winreg
import platform
import subprocess
import json
from typing import Optional, Callable, List, Any
from dataclasses import dataclass
from enum import Enum

APP_NAME = "ExplorerTweaks"
APP_VERSION = "2.2.0"

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

def restart_explorer():
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
    except: pass

def get_registry_value(path: str, name: str, hive: int = winreg.HKEY_CURRENT_USER) -> Optional[Any]:
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except: return None

def set_registry_value(path: str, name: str, value: Any, reg_type: str, hive: int = winreg.HKEY_CURRENT_USER) -> bool:
    try:
        type_map = {"DWORD": winreg.REG_DWORD, "String": winreg.REG_SZ}
        key = winreg.CreateKeyEx(hive, path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, name, 0, type_map.get(reg_type, winreg.REG_DWORD), value)
        winreg.CloseKey(key)
        return True
    except: return False

def registry_key_exists(path: str, hive: int = winreg.HKEY_CURRENT_USER) -> bool:
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except: return False


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
        RegistrySetting("show_extensions", "Show File Extensions", "Display .txt, .exe, .pdf after filenames.", "Appearance", "File Display", ADV, "HideFileExt", "DWORD", 0, 1, 1, inverted=True, preview_key="show_extensions"),
        RegistrySetting("show_hidden", "Show Hidden Files", "Display hidden files and folders.", "Appearance", "File Display", ADV, "Hidden", "DWORD", 1, 2, 2, preview_key="show_hidden"),
        RegistrySetting("show_system", "Show System Files", "Display protected OS files.", "Appearance", "File Display", ADV, "ShowSuperHidden", "DWORD", 1, 0, 0, warning="!", preview_key="show_system"),
        RegistrySetting("colored_encrypted", "Colored Encrypted/Compressed", "Green=encrypted, Blue=compressed.", "Appearance", "File Display", ADV, "ShowEncryptCompressedColor", "DWORD", 1, 0, 0, preview_key="colored_encrypted"),
        RegistrySetting("show_checkboxes", "Selection Checkboxes", "Checkboxes for multi-select.", "Appearance", "File Display", ADV, "AutoCheckSelect", "DWORD", 1, 0, 0, preview_key="show_checkboxes"),
        RegistrySetting("compact_mode", "Compact View", "Reduce spacing between items.", "Appearance", "View Options", ADV, "UseCompactMode", "DWORD", 1, 0, 0, min_os=OSVersion.WINDOWS_11_21H2, preview_key="compact_mode"),
        RegistrySetting("show_thumbnails", "Show Thumbnails", "Image previews instead of icons.", "Appearance", "View Options", ADV, "IconsOnly", "DWORD", 0, 1, 0, inverted=True, preview_key="show_thumbnails"),
        RegistrySetting("type_overlay", "Type Overlay", "Badge on thumbnails (W, X, P).", "Appearance", "View Options", ADV, "ShowTypeOverlay", "DWORD", 1, 0, 1, preview_key="show_type_overlay"),
        RegistrySetting("status_bar", "Status Bar", "Item count at bottom.", "Appearance", "View Options", ADV, "ShowStatusBar", "DWORD", 1, 0, 1, preview_key="show_status_bar"),
        RegistrySetting("full_row_select", "Full Row Selection", "Highlight entire row.", "Appearance", "View Options", ADV, "FullRowSelect", "DWORD", 1, 0, 1, preview_key="full_row_select"),
        RegistrySetting("tooltips", "Tooltips", "Show details on hover.", "Appearance", "View Options", ADV, "ShowInfoTip", "DWORD", 1, 0, 1, preview_key="show_tooltips"),
        RegistrySetting("full_path_title", "Full Path in Title", "C:\\Users\\... in title bar.", "Appearance", "Title Bar", CAB, "FullPath", "DWORD", 1, 0, 0, preview_key="full_path_title"),
        RegistrySetting("full_path_address", "Full Path in Address", "Text path vs breadcrumbs.", "Appearance", "Title Bar", CAB, "FullPathAddress", "DWORD", 1, 0, 0, preview_key="full_path_address"),
        RegistrySetting("launch_to_thispc", "Open to This PC", "Start at drives view.", "Navigation", "Startup", ADV, "LaunchTo", "DWORD", 1, 2, 2, preview_key="launch_to_thispc"),
        RegistrySetting("expand_to_folder", "Expand to Folder", "Auto-expand nav tree.", "Navigation", "Nav Pane", ADV, "NavPaneExpandToCurrentFolder", "DWORD", 1, 0, 0, preview_key="expand_to_folder"),
        RegistrySetting("show_all_folders", "Show All Folders", "Recycle Bin, Control Panel.", "Navigation", "Nav Pane", ADV, "NavPaneShowAllFolders", "DWORD", 1, 0, 0, preview_key="show_all_folders"),
        RegistrySetting("separate_process", "Separate Process", "Independent windows.", "Navigation", "Windows", ADV, "SeparateProcess", "DWORD", 1, 0, 0, preview_key="separate_process"),
        RegistrySetting("restore_folders", "Restore at Logon", "Reopen after restart.", "Navigation", "Windows", ADV, "PersistBrowsers", "DWORD", 1, 0, 0, preview_key="restore_folders"),
        RegistrySetting("sharing_wizard", "Sharing Wizard", "Simple vs advanced.", "Navigation", "Windows", ADV, "SharingWizardOn", "DWORD", 1, 0, 1, preview_key="use_sharing_wizard"),
        RegistrySetting("show_recent", "Recent Files", "Recently opened files.", "Privacy", "Quick Access", EXP, "ShowRecent", "DWORD", 1, 0, 1, preview_key="show_recent"),
        RegistrySetting("show_frequent", "Frequent Folders", "Often used folders.", "Privacy", "Quick Access", EXP, "ShowFrequent", "DWORD", 1, 0, 1, preview_key="show_frequent"),
        RegistrySetting("track_docs", "Track Documents", "Remember opened docs.", "Privacy", "Tracking", ADV, "Start_TrackDocs", "DWORD", 1, 0, 1, preview_key="track_docs"),
        RegistrySetting("track_apps", "Track Apps", "Remember launched apps.", "Privacy", "Tracking", ADV, "Start_TrackProgs", "DWORD", 1, 0, 1, preview_key="track_apps"),
        RegistrySetting("sync_notifications", "OneDrive Notifications", "Sync provider promos.", "Privacy", "Ads", ADV, "ShowSyncProviderNotifications", "DWORD", 1, 0, 1, preview_key="sync_notifications"),
        RegistrySetting("silent_installs", "Silent App Installs", "Auto-install apps.", "Privacy", "Ads", CDM, "SilentInstalledAppsEnabled", "DWORD", 1, 0, 1, preview_key="silent_installs"),
        RegistrySetting("bing_search", "Bing Web Search", "Web results in search.", "Search", "Web", SEARCH, "BingSearchEnabled", "DWORD", 1, 0, 1, preview_key="bing_search"),
        RegistrySetting("cortana", "Cortana", "Voice assistant.", "Search", "Cortana", SEARCH, "CortanaConsent", "DWORD", 1, 0, 1, preview_key="cortana"),
        RegistrySetting("search_history", "Search History", "Remember searches.", "Search", "Cortana", SEARCH, "HistoryViewEnabled", "DWORD", 1, 0, 1, preview_key="search_history"),
        RegistrySetting("taskview_button", "Task View", "Virtual desktops button.", "Taskbar", "Buttons", ADV, "ShowTaskViewButton", "DWORD", 1, 0, 1, preview_key="taskview_button"),
        RegistrySetting("widgets_button", "Widgets", "News/weather button.", "Taskbar", "Buttons", ADV, "TaskbarDa", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_21H2, preview_key="widgets_button"),
        RegistrySetting("center_taskbar", "Center Icons", "Center vs left align.", "Taskbar", "Layout", ADV, "TaskbarAl", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_21H2, preview_key="center_taskbar"),
        RegistrySetting("end_task", "End Task Menu", "Add End Task option.", "Taskbar", "Menu", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings", "TaskbarEndTask", "DWORD", 1, 0, 0, min_os=OSVersion.WINDOWS_11_22H2, preview_key="end_task"),
        RegistrySetting("taskbar_animations", "Animations", "Animate taskbar.", "Performance", "Animations", ADV, "TaskbarAnimations", "DWORD", 1, 0, 1, preview_key="taskbar_animations"),
        RegistrySetting("aero_peek", "Aero Peek", "Desktop preview.", "Performance", "Effects", DWM, "EnableAeroPeek", "DWORD", 1, 0, 1, preview_key="aero_peek"),
        RegistrySetting("disable_thumb_cache", "Disable Thumb Cache", "No thumbnail storage.", "Performance", "Thumbnails", ADV, "DisableThumbnailCache", "DWORD", 1, 0, 0, preview_key="disable_thumb_cache"),
        RegistrySetting("disable_network_thumbs", "No Network Thumbs", "No thumbs.db on network.", "Performance", "Thumbnails", ADV, "DisableThumbsDBOnNetworkFolders", "DWORD", 1, 0, 0),
        RegistrySetting("snap_assist", "Snap Assist", "Window suggestions.", "Performance", "Snapping", ADV, "SnapAssist", "DWORD", 1, 0, 1, preview_key="snap_assist"),
        RegistrySetting("snap_layouts", "Snap Layouts", "Layout grid.", "Performance", "Snapping", ADV, "EnableSnapBar", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_21H2, preview_key="snap_layouts"),
        RegistrySetting("dark_system", "Dark System", "Dark taskbar/Start.", "Theme", "Mode", THEME, "SystemUsesLightTheme", "DWORD", 0, 1, 1, inverted=True, preview_key="dark_mode"),
        RegistrySetting("dark_apps", "Dark Apps", "Dark app windows.", "Theme", "Mode", THEME, "AppsUseLightTheme", "DWORD", 0, 1, 1, inverted=True, preview_key="dark_mode"),
        RegistrySetting("show_gallery", "Gallery", "Photo gallery in nav.", "Windows 11", "Nav Pane", ADV, "ShowGallery", "DWORD", 1, 0, 1, min_os=OSVersion.WINDOWS_11_23H2, preview_key="show_gallery"),
    ]


class SpecialSettings:
    @staticmethod
    def get_classic_context_menu() -> bool:
        return registry_key_exists(r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32")
    
    @staticmethod
    def set_classic_context_menu(enable: bool) -> bool:
        path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
        parent = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
        if enable:
            try:
                key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
                winreg.CloseKey(key)
                return True
            except: return False
        else:
            try:
                try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
                except: pass
                try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, parent)
                except: pass
                return True
            except: return False
    
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
        self.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
        header.grid_columnconfigure(0, weight=1)
        
        nf = ctk.CTkFrame(header, fg_color="transparent")
        nf.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(nf, text=setting.name, font=ctk.CTkFont(size=12, weight="bold"), text_color=UI["text"]).pack(side="left")
        if setting.warning:
            ctk.CTkLabel(nf, text=" ⚠", font=ctk.CTkFont(size=10), text_color=UI["off"]).pack(side="left")
        
        self.switch_var = ctk.BooleanVar()
        self.switch = ctk.CTkSwitch(header, text="", variable=self.switch_var, command=self._toggle, width=40, height=20, switch_width=36, switch_height=18, progress_color=UI["accent"], button_color="#fff", fg_color=UI["hover"])
        self.switch.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(self, text=setting.description, font=ctk.CTkFont(size=10), text_color=UI["text_sec"], wraplength=320, justify="left", anchor="w").grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))
        self._load_state()
    
    def _load_state(self):
        val = get_registry_value(self.setting.reg_path, self.setting.reg_name)
        if val is None: val = self.setting.default_value
        enabled = (val == self.setting.enable_value)
        if self.setting.inverted: enabled = not enabled
        self.switch_var.set(enabled)
    
    def _toggle(self):
        enabled = self.switch_var.get()
        actual = not enabled if self.setting.inverted else enabled
        val = self.setting.enable_value if actual else self.setting.disable_value
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
    def __init__(self):
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
        self.current_cat = self.categories[0] if self.categories else None
        self.nav_buttons = {}
        self.previews = {}
        
        self._build_ui()
        self._create_previews()
        if self.current_cat: self._show_category(self.current_cat)
    
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
        order = [OSVersion.WINDOWS_10, OSVersion.WINDOWS_11_21H2, OSVersion.WINDOWS_11_22H2, OSVersion.WINDOWS_11_23H2, OSVersion.WINDOWS_11_24H2]
        idx = order.index(self.os_version) if self.os_version in order else -1
        return [s for s in settings if (not s.min_os or idx >= order.index(s.min_os)) and (not s.max_os or idx <= order.index(s.max_os))]
    
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
        
        ctk.CTkFrame(sidebar, fg_color=UI["border"], height=1).pack(fill="x", padx=12, pady=10)
        
        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.pack(fill="both", expand=True, padx=6)
        
        emojis = {"Appearance": "🎨", "Navigation": "🧭", "Privacy": "🔒", "Search": "🔍", "Taskbar": "📌", "Performance": "⚡", "Theme": "🌙", "Windows 11": "🪟"}
        for cat in self.categories:
            btn = NavButton(nav, cat, emojis.get(cat, "📁"), lambda c=cat: self._on_nav(c), selected=(cat == self.current_cat))
            btn.pack(fill="x", pady=1)
            self.nav_buttons[cat] = btn
        
        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(fill="x", side="bottom", padx=8, pady=12)
        ctk.CTkButton(bottom, text="🔄 Restart Explorer", command=self._restart, font=ctk.CTkFont(size=11, weight="bold"), fg_color=UI["accent"], hover_color=UI["accent_hover"], height=34, corner_radius=6).pack(fill="x", pady=(0, 6))
        
        br = ctk.CTkFrame(bottom, fg_color="transparent")
        br.pack(fill="x")
        ctk.CTkButton(br, text="Export", command=self._export, font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ctk.CTkButton(br, text="Import", command=self._import, font=ctk.CTkFont(size=9), fg_color=UI["hover"], hover_color=UI["border"], height=26, corner_radius=4).pack(side="right", expand=True, fill="x", padx=(2, 0))
    
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
        
        if cat == "Windows 11" and self.os_version != OSVersion.WINDOWS_10:
            SpecialCard(self.scroll, "Classic Context Menu", "Full Win10 menu.", SpecialSettings.get_classic_context_menu, SpecialSettings.set_classic_context_menu, self._on_change, "classic_context_menu").grid(row=row, column=0, sticky="ew", pady=(0, 4))
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
    
    def _restart(self):
        if messagebox.askyesno("Restart", "Restart Explorer?"): restart_explorer()
    
    def _export(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            data = {s.id: get_registry_value(s.reg_path, s.reg_name) for s in self.settings if get_registry_value(s.reg_path, s.reg_name) is not None}
            data["_classic"], data["_search"] = SpecialSettings.get_classic_context_menu(), SpecialSettings.get_search_mode()
            with open(path, 'w') as f: json.dump(data, f, indent=2)
            messagebox.showinfo("Export", f"Saved:\n{path}")
    
    def _import(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f: data = json.load(f)
            for s in self.settings:
                if s.id in data: set_registry_value(s.reg_path, s.reg_name, data[s.id], s.reg_type)
            if "_classic" in data: SpecialSettings.set_classic_context_menu(data["_classic"])
            if "_search" in data: SpecialSettings.set_search_mode(data["_search"])
            self._load_preview_state()
            for p in self.previews.values(): p.state = self.preview_state
            self._show_category(self.current_cat)
            messagebox.showinfo("Import", "Done!")


def main():
    if platform.system() != "Windows":
        print("Windows only.")
        return
    App().mainloop()

if __name__ == "__main__":
    main()
