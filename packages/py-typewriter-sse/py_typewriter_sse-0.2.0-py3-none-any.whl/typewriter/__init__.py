# src/typewriter/__init__.py

import random
import string
import sys
import time
from collections.abc import Generator
from typing import Tuple

try:
    import jieba
except ImportError:
    jieba = None

__all__ = ["typewrite", "generate_typewriter_flow"]
__version__ = "0.2.0"


PUNCTUATION_EXTENDED = set(string.punctuation) | {
    " ",
    "　",  # 空格和全角空格
    "，",
    "。",
    "！",
    "？",
    "…",
    "；",
    "：",
    "“",
    "”",
    "‘",
    "’",
    "（",
    "）",
    "《",
    "》",
    "【",
    "】",
    "、",
}


def generate_typewriter_flow(
    text: str, base_delay: float = 0.05, mode: str = "char"
) -> Generator[Tuple[str, float], None, None]:
    """
    生成一个模拟打字机效果的字符或词语流。

    它会 yield 一个元组，包含 (下一个文本片段, 延迟时间)。

    :param text: 要处理的文本。
    :param base_delay: 基础延迟时间（秒）。一个字符的平均延迟时间。
    :param mode: 切分模式。
                 'char' (默认): 按单个字符切分，适用于所有语言。
                 'word': 使用 jieba 按词语切分，对中文效果更佳。

    :return:  (文本片段, 延迟时间) 的生成器。

    用法:
        # 模式一：字符模式 (默认)
        flow_char = generate_typewriter_flow("Hello, world! 你好，世界！")
        for char, delay in flow_char:
            print(char, end='', flush=True)
            time.sleep(delay)
        print('\\n---')

        # 模式二：中文分词模式
        flow_word = generate_typewriter_flow("Jieba是一个强大的中文分词库。", mode='word')
        for word, delay in flow_word:
            print(word, end='', flush=True)
            time.sleep(delay)
    """
    if mode == "word":
        if jieba is None:
            raise ImportError("Jieba library is not installed. Please run 'pip install jieba' to use 'word' mode.")
        token_generator = jieba.cut(text)
    else:
        token_generator = iter(text)

    for token in token_generator:
        # 如果整个 token 是一个标点符号，则停顿时间更长
        if token in PUNCTUATION_EXTENDED:
            # 对于标点，尤其是句末标点，给予较长的停顿
            if token in [".", "。", "!", "！", "?", "？", "…"]:
                delay = base_delay * 8
            else:
                delay = base_delay * 2
        else:
            # 对于单词或字符，延迟时间与长度成正比，并加入随机性
            # 这样，长词的“打字”时间会比短词更长，效果更逼真
            delay = base_delay * len(token) + random.uniform(-0.02, 0.02)

        # 确保延迟不会是负数或过小
        delay = max(0.01, delay)

        yield token, delay


def typewrite(text: str, delay: float = 0.05, end: str = "\n") -> None:
    """
    以打字机效果直接在终端打印文本。

    这是一个高级、易于使用的函数，封装了生成和打印的整个过程。

    :param text: 要打印的文本。
    :param delay: 每个字符之间的平均延迟时间（秒）。
    :param end: 文本打印完毕后追加的字符，默认为换行符。

    用法:
        >>> typewrite("你好，世界！")
    """
    flow_generator = generate_typewriter_flow(text, base_delay=delay)

    for char, sleep_time in flow_generator:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(sleep_time)

    sys.stdout.write(end)
    sys.stdout.flush()


if __name__ == "__main__":
    text_sample_cn = "你好，世界！这是一个基于Jieba分词的打字机效果模拟。它能让中文输出更自然、流畅。"
    text_sample_en = "Hello, world! This is a typewriter effect simulation."

    print("--- 模式: 'char' (默认字符模式) ---")
    flow_char = generate_typewriter_flow(text_sample_cn, base_delay=0.03)
    for char, delay in flow_char:
        print(char, end="", flush=True)  # flush=True 确保立即输出
        time.sleep(delay)
    print("\n")  # 换行

    print("--- 模式: 'word' (Jieba分词模式) ---")
    try:
        flow_word = generate_typewriter_flow(text_sample_cn, base_delay=0.03, mode="word")
        for word, delay in flow_word:
            print(word, end="", flush=True)
            time.sleep(delay)
        print("\n")
    except ImportError as e:
        print(f"\n错误: {e}")

    print("--- 英文文本在 'word' 模式下的效果 ---")
    # Jieba 也能很好地处理英文和数字
    try:
        flow_en_word = generate_typewriter_flow(text_sample_en, base_delay=0.03, mode="word")
        for word, delay in flow_en_word:
            print(word, end="", flush=True)
            time.sleep(delay)
        print("\n")
    except ImportError as e:
        print(f"\n错误: {e}")
