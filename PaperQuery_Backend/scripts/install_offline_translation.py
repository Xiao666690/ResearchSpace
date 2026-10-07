"""Install the English-to-Chinese Argos package for this local environment."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from core.backend.services.translate import configure_argos_environment

configure_argos_environment()

import argostranslate.package as package
import argostranslate.translate as translate


if __name__ == '__main__':
    installed = {language.code for language in translate.get_installed_languages()}
    if {'en', 'zh'} <= installed:
        print('英文到中文离线翻译包已安装')
    else:
        package.update_package_index()
        candidate = next((item for item in package.get_available_packages()
                          if item.from_code == 'en' and item.to_code == 'zh'), None)
        if candidate is None:
            raise RuntimeError('未找到英文到中文的 Argos 翻译包')
        package.install_from_path(candidate.download())
        print('英文到中文离线翻译包安装完成')
