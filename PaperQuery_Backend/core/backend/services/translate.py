
"""Offline English-to-Chinese translation for selected PDF passages."""

from functools import lru_cache
import os
import re
import tempfile
from pathlib import Path


def configure_argos_environment():
    # SentencePiece cannot load model files from this project's Unicode path on
    # some Windows installations. Keep the downloaded package at an ASCII path.
    root = Path(os.getenv('ARGOS_DATA_ROOT', Path(tempfile.gettempdir()) / 'researchspace-argos'))
    os.environ.setdefault('XDG_DATA_HOME', str(root / 'data'))
    os.environ.setdefault('XDG_CONFIG_HOME', str(root / 'config'))
    os.environ.setdefault('XDG_CACHE_HOME', str(root / 'cache'))
    os.environ.setdefault('ARGOS_CHUNK_TYPE', 'MINISBD')


configure_argos_environment()


@lru_cache(maxsize=1)
def _english_to_chinese():
    try:
        import argostranslate.translate
    except ImportError as exc:
        raise RuntimeError('离线翻译组件未安装，请先安装 requirement.txt 中的依赖') from exc

    languages = {lang.code: lang for lang in argostranslate.translate.get_installed_languages()}
    if "en" not in languages or "zh" not in languages:
        raise RuntimeError("离线英中翻译模型未安装，请运行 scripts/install_offline_translation.py")
    translation = languages["en"].get_translation(languages["zh"])
    if translation is None:
        raise RuntimeError("离线英中翻译模型未安装，请运行 scripts/install_offline_translation.py")
    return translation


class Translator:
    def __init__(self, from_lang="en", to_lang="zh", llm=None):
        if from_lang not in ('en', 'zh') or to_lang not in ('en', 'zh'):
            raise ValueError('目前支持英文和简体中文互译')
        self.from_lang, self.to_lang, self.llm = from_lang, to_lang, llm

    def translate(self, text: str) -> str:
        source = re.sub(r"-\s*\r?\n\s*", "", text.replace("\u00ad", ""))
        source = " ".join(source.split())
        if not source:
            return ""
        if self.from_lang == self.to_lang:
            return source
        if os.getenv('TRANSLATION_PROVIDER', 'deepseek').lower() != 'offline':
            if self.llm is None:
                self.llm = _translation_llm()
            from langchain_core.messages import SystemMessage, HumanMessage
            target = '简体中文' if self.to_lang == 'zh' else 'English'
            answer = self.llm.invoke([
                SystemMessage(content=f'将用户文本翻译为{target}。只输出译文，保留论文术语、公式和引用编号，不添加解释。'),
                HumanMessage(content=source),
            ])
            return answer.content
        if (self.from_lang, self.to_lang) != ('en', 'zh'):
            raise RuntimeError('离线模式仅支持英译中；中英互译请使用 TRANSLATION_PROVIDER=deepseek')
        translation = _english_to_chinese()
        chunks: list[str] = []
        current = ""
        for sentence in re.split(r"(?<=[.!?;])\s+", source):
            if len(current) + len(sentence) + 1 <= 1200:
                current = f"{current} {sentence}".strip()
                continue
            if current:
                chunks.append(current)
                current = ""
            if len(sentence) <= 1200:
                current = sentence
                continue
            words = sentence.split()
            for word in words:
                if len(current) + len(word) + 1 > 1200 and current:
                    chunks.append(current)
                    current = ""
                current = f"{current} {word}".strip()
        if current:
            chunks.append(current)
        return "\n\n".join(translation.translate(chunk) for chunk in chunks)


@lru_cache(maxsize=1)
def _translation_llm():
    from core.llm.LLM import LLM
    if not os.getenv('DEEPSEEK_API_KEY', '').strip():
        raise RuntimeError('请配置 DEEPSEEK_API_KEY 以启用翻译')
    return LLM().get_llm('deepseek')
