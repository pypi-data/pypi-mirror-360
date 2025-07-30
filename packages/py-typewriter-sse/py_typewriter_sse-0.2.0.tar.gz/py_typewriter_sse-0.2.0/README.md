# Py-Typewriter

[![PyPI version](https://badge.fury.io/py/py-typewriter.svg)](https://badge.fury.io/py/py-typewriter)

一个简单、灵活的 Python 库，用于在终端模拟自然的打字机输出效果。

## 特点

- **简单易用**: 只需一行代码即可实现打字机效果。
- **自然模拟**: 通过随机延迟和标点停顿，效果更逼真。
- **高度灵活**: 提供底层生成器，允许你完全自定义输出行为。

## 安装

```bash
pip install py-typewriter
```

## 使用方法

### 快速上手

最简单的方式是使用 `typewrite()` 函数：

```python
import typewriter

story = "很久很久以前，在一个遥远的国度里...\n一切都显得那么宁静。"
typewriter.typewrite(story)
```

### 高级用法 (使用生成器)

如果是更灵活的调用，可以使用 `generate_typewriter_flow()` 生成器：

```python
import time
import typewriter

text = "这是一个更高级的用法。"

flow = typewriter.generate_typewriter_flow(text, base_delay=0.1)

for char, delay in flow:
    print(char, end='', flush=True)
    time.sleep(delay)
print()
```
### 支持 char(Default)、word模式，word模式支持对中文进行分词，更贴近实际效果
```python
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
``` 

## 贡献

欢迎提交 Issues 和 Pull Requests！

## 许可证

本项目使用 [MIT License](LICENSE)。


#### 4. 许可证 (`LICENSE`)



```text
# LICENSE

MIT License

Copyright (c) 2025 orxvan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```