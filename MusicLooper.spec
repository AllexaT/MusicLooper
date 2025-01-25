# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['MusicLooper/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('MusicLooper/assets/*', 'assets/'),  # 包含資源檔案
        ('MusicLooper/*.py', 'MusicLooper'),  # 包含所有 Python 檔案
    ],
    hiddenimports=[
        'sounddevice',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'numpy',
        'librosa',
        'librosa.util',
        'librosa.feature',
        'librosa.beat',
        'librosa.onset',
        'librosa.sequence',
        'scipy',
        'scipy.signal',
        'scipy.fft',
        'MusicLooper',
        'MusicLooper.cli',
        'MusicLooper.gui',
        'MusicLooper.core',
        'MusicLooper.audio',
        'MusicLooper.analysis',
        'MusicLooper.handler',
        'MusicLooper.playback',
        'MusicLooper.utils',
        'MusicLooper.console',
        'MusicLooper.exceptions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MusicLooper',
    debug=True,  # 啟用除錯
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 暫時開啟控制台以查看錯誤
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt'
) 