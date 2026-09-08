#!/usr/bin/env python3
"""Render sample product states without using the interactive desktop."""
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import time
import uuid

SESSION = None
SOURCE_PATHS = ('explorer_tweaks.py', 'tools/capture_marketing.py', 'requirements.txt', 'ExplorerTweaks.spec', 'assets/runtime_hook_mp.py', 'branding/icon.ico', 'branding/icon-128.png')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(argv):
    """Move this capture-only process to its own desktop before Tk is imported."""
    global SESSION
    if '--marketing-capture' not in argv:
        return
    if len(argv) != 3 or argv[1] != '--marketing-capture':
        raise ValueError('Use --marketing-capture OUTPUT alone.')
    output = Path(argv[2]).resolve()
    if output == Path(output.anchor) or output == Path.home():
        raise ValueError('Use a dedicated capture output folder.')
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.CreateDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID]
    user.CreateDesktopW.restype = wintypes.HANDLE
    user.SetThreadDesktop.argtypes = [wintypes.HANDLE]
    user.SetThreadDesktop.restype = wintypes.BOOL
    user.CloseDesktop.argtypes = [wintypes.HANDLE]
    name = 'ExplorerTweaksCapture-' + uuid.uuid4().hex
    desktop = user.CreateDesktopW(name, None, None, 0, 0x000F01FF, None)
    if not desktop:
        raise ctypes.WinError(ctypes.get_last_error())
    if not user.SetThreadDesktop(desktop):
        error = ctypes.get_last_error()
        user.CloseDesktop(desktop)
        raise ctypes.WinError(error)
    user.SetProcessDPIAware()
    runtime = tempfile.TemporaryDirectory(prefix='explorertweaks-capture-')
    os.environ['APPDATA'] = runtime.name
    os.environ['LOCALAPPDATA'] = runtime.name
    sys.dont_write_bytecode = True
    # Libraries may otherwise run a shell command while identifying Windows.
    # The sample fixture represents Windows 11 25H2, not the current machine.
    platform.system = lambda: 'Windows'
    platform.release = lambda: '11'
    platform.version = lambda: '10.0.26200'
    SESSION = dict(output=output, runtime=runtime, desktop=desktop, user=user, name=name)
    sys.addaudithook(reject_system_mutation)


def reject_system_mutation(event, args):
    if event.startswith(('winreg.Set', 'winreg.Create', 'winreg.Delete')) or event in ('subprocess.Popen', 'os.system', 'os.startfile', 'os.startfile/2'):
        raise RuntimeError('System commands are disabled in sample capture mode: ' + event)


def source_record(root):
    root = Path(root)
    if getattr(sys, 'frozen', False):
        return json.loads((root / 'build-provenance.json').read_text(encoding='utf-8-sig'))['sourceFiles']
    return [dict(path=name, bytes=(root / name).stat().st_size, sha256=digest(root / name)) for name in SOURCE_PATHS]


def capture(product):
    if SESSION is None:
        raise RuntimeError('Private capture must be prepared before importing the product.')
    from PIL import ImageGrab

    output = SESSION['output']
    output.mkdir(parents=True, exist_ok=True)
    app = None
    try:
        product.DRY_RUN = True
        defaults = {(setting.reg_path, setting.reg_name): setting.default_value for setting in product.get_all_settings()}
        for name in ('AppsUseLightTheme', 'SystemUsesLightTheme'):
            defaults[(r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize', name)] = 0
        product.get_registry_value = lambda path, name, *args, **kwargs: defaults.get((path, name))
        product.is_setting_policy_locked = lambda setting: False
        product.get_windows_version = lambda: product.OSVersion.WINDOWS_11_25H2
        product.is_photo_viewer_registered = lambda: False
        product.is_context_menu_installed = lambda: False
        product.is_darkmode_auto_switch_installed = lambda: False
        product.SpecialSettings.get_classic_context_menu = staticmethod(lambda: False)
        product.SpecialSettings.get_search_mode = staticmethod(lambda: 1)
        product.folder_view_defaults_preview = lambda: [dict(configured=False) for _ in range(7)]
        app = product.App()
        app.overrideredirect(True)
        app.geometry('1280x800+0+0')
        callback_errors = []
        app.report_callback_exception = lambda kind, value, trace: callback_errors.append(str(value))
        captures = []
        layouts = []
        user = SESSION['user']
        user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        user.GetAncestor.restype = wintypes.HWND
        for index, category in enumerate(('Appearance', 'Navigation', 'Taskbar', 'Theme', 'Tools'), 1):
            app._on_nav(category)
            product.clear_operation_log()
            app._set_status('Sample state. No system changes.')
            for event in product.OPERATION_LOG:
                event['timestamp_utc'] = '2026-09-08T12:00:00Z'
            app._refresh_operation_log()
            deadline = time.monotonic() + 0.7
            while time.monotonic() < deadline:
                app.update()
                time.sleep(0.015)
            if callback_errors:
                raise RuntimeError('; '.join(callback_errors))
            if category == 'Taskbar':
                taskbar = app.previews['Taskbar'].taskbar
                layouts.append(dict(component='Taskbar', width=taskbar.winfo_width(), tray=taskbar.tray.winfo_reqwidth(), icons=taskbar.icons_container.winfo_reqwidth()))
            hwnd = user.GetAncestor(app.winfo_id(), 2)
            if not hwnd:
                raise RuntimeError('The private product window is missing.')
            picture = ImageGrab.grab(window=hwnd)
            if picture.size != (1600, 1000) or all(low == high for low, high in picture.getextrema()):
                raise RuntimeError(f'Invalid capture size or blank window: {picture.size}')
            name = f'{index:02d}-{category.lower()}.png'
            picture.save(output / name, optimize=True)
            captures.append(dict(file=name, category=category, width=1600, height=1000, bytes=(output / name).stat().st_size, sha256=digest(output / name)))
        # Exercise search and return navigation through the real widgets.
        app.search_var.set('extensions')
        if app.current_cat != '_search':
            raise RuntimeError('Search did not open its results.')
        app.search_var.set('')
        if app.current_cat != 'Tools':
            raise RuntimeError('Clearing search did not restore the previous category.')
        app._on_nav('Appearance')
        card = next(widget for widget in app.scroll.winfo_children()
                    if isinstance(widget, product.SettingCard) and widget.setting.id == 'show_extensions')
        card._show_info()
        if not card._info_visible or card.info_label is None:
            raise RuntimeError('The setting explanation did not open.')
        card._show_info()
        product.clear_operation_log()
        before = app.preview_state.show_extensions
        card.switch.toggle()
        if app.preview_state.show_extensions == before or not product.OPERATION_LOG:
            raise RuntimeError('The switch did not update its preview and dry-run plan.')
        card.switch.toggle()
        if app.preview_state.show_extensions != before:
            raise RuntimeError('The switch did not restore its illustrated state.')
        if callback_errors:
            raise RuntimeError('; '.join(callback_errors))
        # The source and frozen entry points carry the same evidence structure.
        report = dict(schemaVersion=1, product=product.APP_NAME, version=product.APP_VERSION,
                      sampleData=True, privateDesktop=True, systemCommands=False,
                      sourceFiles=source_record(app._asset_root), captures=captures,
                      layouts=layouts,
                      exercised=['category navigation', 'search', 'search restoration',
                                 'file-extension switch', 'setting explanation', 'dry-run registry plan'])
        if getattr(sys, 'frozen', False):
            report['executableSha256'] = digest(sys.executable)
        (output / 'capture-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    finally:
        if app is not None:
            app.destroy()
        SESSION['runtime'].cleanup()
        SESSION['user'].CloseDesktop(SESSION['desktop'])
