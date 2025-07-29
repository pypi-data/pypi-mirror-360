# AshAI

**AshAI** is a Python library that helps you group sentences or propositions into intelligent topic-based chunks using an LLM.

## Install

pip install .



## Quick Start
```python
from ashai.chunker import AgenticChunker

chunker = AgenticChunker()
chunker.add_propositions(["Ashay loves pizza.", "Pizza is Italian."])
chunker.pretty_print_chunks()

