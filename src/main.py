"""Entry point for Reversi."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

import logging
import log_config
import sw_metadata as meta

log_config.setup()
log = logging.getLogger(__name__)


def main() -> None:
    import config_ui as UI
    import ai_engine as AE

    log.info("=" * 60)
    log.info("%s  v. %s  --  starting", meta.getSWName(), meta.getVersion())
    log.info("Python %s  |  platform: %s", sys.version.split()[0], sys.platform)
    log.info("AI: %s  |  Skin: %s", AE.get_name(), UI.get_name())
    log.info("=" * 60)

    from ui_main import App
    app = App()
    app.mainloop()

    log.info("=" * 60)
    log.info("%s  --  exited normally", meta.getSWName())
    log.info("=" * 60)


if __name__ == "__main__":
    main()
