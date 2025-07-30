# core/browser_factory.py
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from seleniumfw.config import Config
import os
import builtins

_thread_data = threading.local()


class BrowserFactory:
    @staticmethod
    def create_driver():
        cfg = Config()
        browser = cfg.get("browser", "chrome").lower()
        extra_args = cfg.get_list("args")
        print(f"Creating {browser} driver with args: {extra_args}")

        if browser == "chrome":
            options = ChromeOptions()
            for arg in extra_args:
                options.add_argument(arg)
            driver = webdriver.Chrome(options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            for arg in extra_args:
                # Firefox uses preferences for most things, but
                # headless is a flag, private is a preference:
                if arg == "--headless":
                    options.add_argument(arg)
                elif arg == "--incognito":
                    options.set_preference("browser.privatebrowsing.autostart", True)
                else:
                    options.add_argument(arg)
            driver = webdriver.Firefox(options=options)

        else:
            raise Exception(f"Unsupported browser: {browser}")

        # ensure this thread has its own list
        if not hasattr(_thread_data, "screenshots"):
            _thread_data.screenshots = []

        original_save = driver.save_screenshot

        def save_to_report(path, *a, **kw):
            # Determine the proper folder to write into
            if not os.path.isabs(path):
                try:
                    from seleniumfw.thread_context import _thread_locals, _thread_data
                    rpt = getattr(_thread_locals, "report")
                    rpt_dir = rpt.screenshots_dir
                except (NameError, AttributeError):
                    rpt_dir = os.path.join(os.getcwd(), "screenshots")
                os.makedirs(rpt_dir, exist_ok=True)

                filename = path
                base, ext = os.path.splitext(filename)
                path = os.path.join(rpt_dir, filename)
                i = 1
                while os.path.exists(path):
                    path = os.path.join(rpt_dir, f"{base}_{i}{ext}")
                    i += 1

            # Ensure this thread has its own screenshots list
            if not hasattr(_thread_data, "screenshots"):
                _thread_data.screenshots = []

            # Record the absolute path
            abs_path = os.path.abspath(path)
            _thread_data.screenshots.append(abs_path)

            # Finally, take the actual screenshot
            return original_save(path, *a, **kw)



        driver.save_screenshot = save_to_report
        return driver
