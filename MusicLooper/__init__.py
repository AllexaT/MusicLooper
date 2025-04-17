try:
    from importlib.metadata import version
    __version__ = version(__name__)
except:
    __version__ = "1.2.0"  # 設置一個默認版本號
