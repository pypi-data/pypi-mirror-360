# PyDocEnhancer

AI-powered Python plugin to enhance documentation with summaries, code explanations, examples, and semantic search.

## Features
- **Auto-Generated Summaries**: Summarize modules, classes, and functions.
- **Code Explanations**: Plain-English explanations of code logic.
- **Semantic Search**: Query documentation with natural language (e.g., "find data processing functions").
- **Auto-Generated Examples**: Create working code examples from docstrings.
- **Local LLM Support**: Privacy-first processing with local models (e.g., LLaMA 3.2).
- **Integrations**: Works with Sphinx, MkDocs, and Jupyter Notebooks.

## Installation
```bash
pip install pydocenhancer
```

## Quick Start
```python
from pydocenhancer import DocEnhancer

# Initialize with a local LLM
enhancer = DocEnhancer(provider="local", model="llama3.2")
enhancer.generate_docs(module_path="my_project/utils.py", output_dir="docs")

# Search documentation
results = enhancer.search_docs("file handling functions", "docs")
print(results)
```

## CLI Usage
```bash
# Generate documentation
pydocenhancer enhance --module my_project/utils.py --output docs/ --provider local --model llama3.2

# Search documentation
pydocenhancer search --query "data processing functions" --docs-dir docs/
```

## Requirements
- Python 3.8+
- Local LLM (e.g., LLaMA 3.2 via `llama-cpp-python`) or API key for OpenAI/Anthropic
- Optional: Sphinx or MkDocs for integration

## Documentation
Full documentation is available at [ReadTheDocs](https://pydocenhancer.readthedocs.io).

## License
MIT © Your Name 