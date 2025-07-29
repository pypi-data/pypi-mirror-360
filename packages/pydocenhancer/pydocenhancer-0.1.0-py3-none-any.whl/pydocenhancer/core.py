import ast
import inspect
from typing import Dict, List
import os

class DocEnhancer:
    def __init__(self, provider: str = "mock", api_key: str = None, model: str = "mock-model"):
        """
        Initialize PyDocEnhancer with an AI provider.
        :param provider: AI provider ("mock", "openai", "local").
        :param api_key: API key for cloud providers (optional).
        :param model: Model name for LLM (e.g., "llama3.2" for local).
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.llm = None if provider == "mock" else self._init_llm()

    def _init_llm(self):
        """Initialize the LLM client based on provider."""
        if self.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)
        elif self.provider == "local":
            from llama_cpp import Llama
            return Llama(model_path=self.model)
        return None

    def _mock_llm(self, text: str, task: str) -> str:
        """Mock LLM response for demo purposes."""
        if task == "summarize":
            return f"Summary of {text[:50]}...: This code performs a specific function."
        elif task == "explain":
            return f"Explanation of {text[:50]}...: This function processes input data."
        return ""

    def parse_module(self, module_path: str) -> List[Dict]:
        """Parse a Python module and extract function details."""
        with open(module_path, "r") as file:
            code = file.read()
        tree = ast.parse(code)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                docstring = ast.get_docstring(node) or "No docstring"
                source = inspect.getsource(getattr(inspect.getmodule(node), func_name, None))
                functions.append({
                    "name": func_name,
                    "docstring": docstring,
                    "source": source,
                    "summary": self._mock_llm(docstring, "summarize"),
                    "explanation": self._mock_llm(source, "explain")
                })
        return functions

    def generate_docs(self, module_path: str, output_dir: str) -> None:
        """Generate markdown documentation for a module."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        functions = self.parse_module(module_path)
        output_file = os.path.join(output_dir, f"{os.path.basename(module_path)}.md")
        with open(output_file, "w") as f:
            f.write(f"# Documentation for {os.path.basename(module_path)}\n\n")
            for func in functions:
                f.write(f"## Function: {func['name']}\n")
                f.write(f"**Docstring**: {func['docstring']}\n\n")
                f.write(f"**Summary**: {func['summary']}\n\n")
                f.write(f"**Explanation**: {func['explanation']}\n\n")
                f.write("```python\n" + func['source'] + "\n```\n\n")

    def search_docs(self, query: str, docs_dir: str) -> List[str]:
        """Search documentation using a natural language query (mock implementation)."""
        return [f"Found match for '{query}' in {docs_dir} (mock result)"] 