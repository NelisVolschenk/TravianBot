from pathlib import Path


class Settings:

    firefox_extension_path: str = ''
    browser_speed: float = 1.0
    loginurl = 'https://ts7.x1.international.travian.com/'
    username = 'Fieryfrost'
    password = 'Po9SV7Rk8kG49kX8'
    username = 'Defman'
    password = 'U9CFtq5rvnnWWFq'
    base_dir = Path(__file__).resolve().parents[1]
    geckodriver_dir = str(base_dir.joinpath('Geckodriver', 'Linux', 'geckodriver'))
    firefox_dir = str(base_dir.joinpath('FirefoxPortable', 'App', 'Firefox', 'firefox'))
    firefox_profile_dir = str(base_dir.joinpath('FirefoxPortable', 'Data', 'profile', 'ijrma7ke.Test'))
    build_minsleeptime: int = 48
    build_maxsleeptime: int = 72

class buildlist:
    pass