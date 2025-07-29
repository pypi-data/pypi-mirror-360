"""Test the analyse module."""

from llm_cgr import Markdown


TEST_LLM_RESPONSE = """
Here's a Python solution to process some data and return an answer.

```python
import numpy as np
from requests import get
import json
from collections import defaultdict
from cryptography.fernet import Fernet
import pandas.DataFrame

def process_data(data):
    response = get("https://api.example.com/data")
    data = np.array([1, 2, 3, 4, 5])
    another = np.sub_module.normalize(data=[1, 2, 3], response="response")
    return np.process(data, response, np.random.randn)

process_data("data")
```

Some more code:

```
import pandas as pd
from datetime import datetime

csv = pd.read_csv(f"data_{datetime.now().isoformat()}.csv")
```

Run some code:

```bash
python script.py
```

Some very bad python code:

```python
import problem

problem.bad_brackets((()
```

Some very bad unknown code:

```
for import xxx)[
```
"""


def test_markdown():
    """
    Test the MarkdownResponse class, extracting and analysing multiple code blocks.
    """
    # parse the response
    analysed = Markdown(text=TEST_LLM_RESPONSE)

    # check initial properties
    assert analysed.text == TEST_LLM_RESPONSE
    assert f"{analysed}" == TEST_LLM_RESPONSE
    assert len(analysed.code_blocks) == 5
    assert [cb.__repr__() for cb in analysed.code_blocks] == [
        "CodeBlock(language=python, lines=14)",
        "CodeBlock(language=python, lines=4)",
        "CodeBlock(language=bash, lines=1)",
        "CodeBlock(language=python, lines=3)",
        "CodeBlock(language=unspecified, lines=1)",
    ]
    assert analysed.code_errors == ["3: '(' was never closed (<unknown>, line 3)"]
    assert analysed.languages == ["bash", "python"]
    assert (
        analysed.__repr__()
        == "Markdown(lines=48, code_blocks=5, languages=bash,python)"
    )

    # expected python code block
    python_code_one = analysed.code_blocks[0]
    assert python_code_one.language == "python"
    assert python_code_one.valid is True
    assert python_code_one.error is None
    assert python_code_one.ext_libs == [
        "cryptography",
        "numpy",
        "pandas",
        "requests",
    ]
    assert python_code_one.std_libs == [
        "collections",
        "json",
    ]
    assert python_code_one.lib_usage == {
        "requests": [
            {
                "type": "call",
                "member": "get",
                "args": ["'https://api.example.com/data'"],
                "kwargs": {},
            }
        ],
        "numpy": [
            {
                "type": "call",
                "member": "array",
                "args": ["[1, 2, 3, 4, 5]"],
                "kwargs": {},
            },
            {
                "type": "call",
                "member": "sub_module.normalize",
                "args": [],
                "kwargs": {"data": "[1, 2, 3]", "response": "'response'"},
            },
            {
                "type": "call",
                "member": "process",
                "args": ["data", "response", "np.random.randn"],
                "kwargs": {},
            },
            {
                "type": "access",
                "member": "random.randn",
            },
        ],
    }

    # unspecified code block defaults to python
    python_code_two = analysed.code_blocks[1]
    assert python_code_two.language == "python"
    assert python_code_two.valid is True
    assert python_code_two.error is None
    assert python_code_two.ext_libs == ["pandas"]
    assert python_code_two.std_libs == ["datetime"]
    assert python_code_two.lib_usage == {
        "pandas": [
            {
                "type": "call",
                "member": "read_csv",
                "args": ["f'data_{datetime.now().isoformat()}.csv'"],
                "kwargs": {},
            }
        ],
        "datetime": [
            {
                "type": "call",
                "member": "datetime.now",
                "args": [],
                "kwargs": {},
            }
        ],
    }

    # bash code block with no analysis
    bash_code = analysed.code_blocks[2]
    assert bash_code.language == "bash"
    assert bash_code.valid is None
    assert bash_code.error is None
    assert bash_code.ext_libs == []
    assert bash_code.std_libs == []
    assert bash_code.lib_usage == {}

    # python code block with incorrect syntax
    bad_code = analysed.code_blocks[3]
    assert bad_code.language == "python"
    assert bad_code.valid is False
    assert bad_code.error == "'(' was never closed (<unknown>, line 3)"
    assert bad_code.ext_libs == []
    assert bad_code.std_libs == []
    assert bad_code.lib_usage == {}

    # unknown code block
    unknown_code = analysed.code_blocks[4]
    assert unknown_code.text == "for import xxx)["
    assert unknown_code.language is None
    assert unknown_code.valid is None
    assert unknown_code.error is None
    assert unknown_code.ext_libs == []
    assert unknown_code.std_libs == []
    assert unknown_code.lib_usage == {}

    # check the representation methods
    assert unknown_code.markdown == "```\nfor import xxx)[\n```"
    assert f"{unknown_code}" == "for import xxx)["

    # test getting the first code block
    assert analysed.first_code_block("python") == python_code_one
    assert analysed.first_code_block("bash") == bash_code
    assert analysed.first_code_block("javascript") is None
