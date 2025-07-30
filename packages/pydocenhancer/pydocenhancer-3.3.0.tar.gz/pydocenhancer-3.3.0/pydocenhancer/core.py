import ast
import inspect
from typing import Dict, List, Optional
import os
import sys
import io
import contextlib
import requests
import glob
import re

class DocEnhancer:
    def __init__(self, provider: str, api_key: str = None, model: str = None, language: str = "en"):
        """
        Initialize PyDocEnhancer with an AI provider.
        :param provider: AI provider ("openai", "local").
        :param api_key: API key for cloud providers (optional).
        :param model: Model name for LLM (e.g., "llama3.2" for local).
        :param language: Output language for documentation (default: "en").
        """
        if provider is None or provider == "mock":
            raise ValueError("A real LLM provider is required. Please specify --provider local or --provider openai and a valid model.")
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.language = language
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize the LLM client based on provider."""
        if self.provider == "openai":
            import openai
            openai.api_key = self.api_key
            return openai
        elif self.provider == "local" and self.model and "ollama" in self.model.lower():
            # No client needed, will use requests to localhost
            return "ollama"
        elif self.provider == "local":
            try:
                from ctransformers import AutoModelForCausalLM
                llm = AutoModelForCausalLM.from_pretrained(self.model)
                return llm
            except ImportError:
                raise ImportError("ctransformers is required for local LLMs. Install with 'pip install pydocenhancer[local]'.")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported providers are 'openai' and 'local'.")

    def _llm_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": self.model.split("/", 1)[-1], "prompt": prompt, "stream": False},
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama LLM request failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error from Ollama LLM: {e}")

    def _llm_openai(self, prompt: str) -> str:
        try:
            completion = self.llm.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI LLM request failed: {e}")

    def _llm_local(self, prompt: str) -> str:
        if not self.llm:
            raise RuntimeError("Local LLM is not initialized.")
        return self.llm(prompt)

    def _llm(self, text: str, task: str, language: str = None) -> str:
        lang = language or self.language
        prompt = ""
        if task == "summarize":
            prompt = f"Summarize the following Python code in {lang}:\n{text}"
        elif task == "explain":
            prompt = f"Explain what the following Python code does in {lang}:\n{text}"
        elif task == "translate":
            prompt = f"Translate the following documentation to {lang}:\n{text}"
        elif task == "example":
            prompt = f"Generate a usage example for the following Python function in {lang}:\n{text}"
        else:
            prompt = text

        if self.provider == "openai":
            return self._llm_openai(prompt)
        elif self.provider == "local" and self.model and "ollama" in self.model.lower():
            return self._llm_ollama(prompt)
        elif self.provider == "local":
            return self._llm_local(prompt)
        else:
            raise ValueError("A real LLM provider is required. The 'mock' provider is not supported.")

    def parse_module(self, module_path: str) -> List[Dict]:
        """Parse a Python module and extract function, class, and module details."""
        try:
            with open(module_path, "r") as file:
                code = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Module file not found: {module_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied when reading: {module_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading file {module_path}: {e}")
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {module_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error parsing AST for {module_path}: {e}")
        items = []
        # Module-level docstring
        module_docstring = ast.get_docstring(tree) or "No module docstring"
        try:
            module_summary = self._llm(module_docstring, "summarize", self.language)
        except Exception as e:
            module_summary = f"Error from LLM: {e}"
        items.append({
            "type": "module",
            "name": os.path.basename(module_path),
            "docstring": module_docstring,
            "summary": module_summary,
        })
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                docstring = ast.get_docstring(node) or "No docstring"
                # Safely extract source code from the AST node
                try:
                    source = ast.unparse(node)
                except AttributeError:
                    source_lines = code.splitlines()
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                    source = '\n'.join(source_lines[start_line:end_line])
                except Exception as e:
                    source = f"Error extracting source: {e}"
                example = self.extract_example_from_docstring(docstring)
                try:
                    docstring_translated = self._llm(docstring, "translate", self.language)
                except Exception as e:
                    docstring_translated = f"Error from LLM: {e}"
                try:
                    summary = self._llm(docstring, "summarize", self.language)
                except Exception as e:
                    summary = f"Error from LLM: {e}"
                try:
                    explanation = self._llm(source, "explain", self.language)
                except Exception as e:
                    explanation = f"Error from LLM: {e}"
                try:
                    example_out = self._llm(source, "example", self.language)
                except Exception as e:
                    example_out = f"Error from LLM: {e}"
                items.append({
                    "type": "function",
                    "name": func_name,
                    "docstring": docstring_translated,
                    "source": source,
                    "summary": summary,
                    "explanation": explanation,
                    "example": example_out,
                    "example_test_result": self.test_example_code(example) if example else None
                })
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                class_docstring = ast.get_docstring(node) or "No docstring"
                try:
                    class_source = ast.unparse(node)
                except AttributeError:
                    source_lines = code.splitlines()
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                    class_source = '\n'.join(source_lines[start_line:end_line])
                except Exception as e:
                    class_source = f"Error extracting source: {e}"
                try:
                    class_docstring_translated = self._llm(class_docstring, "translate", self.language)
                except Exception as e:
                    class_docstring_translated = f"Error from LLM: {e}"
                try:
                    class_summary = self._llm(class_docstring, "summarize", self.language)
                except Exception as e:
                    class_summary = f"Error from LLM: {e}"
                try:
                    class_explanation = self._llm(class_source, "explain", self.language)
                except Exception as e:
                    class_explanation = f"Error from LLM: {e}"
                try:
                    class_example = self._llm(class_source, "example", self.language)
                except Exception as e:
                    class_example = f"Error from LLM: {e}"
                items.append({
                    "type": "class",
                    "name": class_name,
                    "docstring": class_docstring_translated,
                    "source": class_source,
                    "summary": class_summary,
                    "explanation": class_explanation,
                    "example": class_example,
                })
        return items

    def extract_example_from_docstring(self, docstring: str) -> Optional[str]:
        """Extract example code from a docstring if present."""
        # Simple heuristic: look for lines starting with 'Example:' or code blocks
        lines = docstring.splitlines()
        example_lines = []
        in_example = False
        for line in lines:
            if 'Example' in line:
                in_example = True
                continue
            if in_example:
                if line.strip() == '' or line.strip().startswith('>>>'):
                    continue
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    break
                example_lines.append(line)
        return '\n'.join(example_lines).strip() if example_lines else None

    def test_example_code(self, code: str) -> str:
        """Run the example code and return the output or error."""
        if not code:
            return "No example to test."
        try:
            # Redirect stdout to capture print output
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exec(code, {})
            return f"Success. Output:\n{stdout.getvalue()}"
        except Exception as e:
            return f"Error: {e}"

    def generate_docs(self, module_path: str, output_dir: str, language: Optional[str] = None) -> None:
        """Generate markdown documentation for a module, optionally in a different language."""
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                raise RuntimeError(f"Could not create output directory {output_dir}: {e}")
        lang = language or self.language
        try:
            items = self.parse_module(module_path)
        except Exception as e:
            raise RuntimeError(f"Failed to parse module: {e}")
        output_file = os.path.join(output_dir, f"{os.path.basename(module_path)}.{lang}.md")
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Documentation for {os.path.basename(module_path)} [{lang}]\n\n")
                for item in items:
                    if item['type'] == 'module':
                        f.write(f"## Module: {item['name']}\n")
                        f.write(f"**Docstring**: {item['docstring']}\n\n")
                        f.write(f"**Summary**: {item['summary']}\n\n")
                    elif item['type'] == 'function':
                        f.write(f"## Function: {item['name']}\n")
                        f.write(f"**Docstring**: {item['docstring']}\n\n")
                        f.write(f"**Summary**: {item['summary']}\n\n")
                        f.write(f"**Explanation**: {item['explanation']}\n\n")
                        if item['example']:
                            f.write(f"**Example**:\n```python\n{item['example']}\n```\n\n")
                            f.write(f"**Example Test Result**: {item['example_test_result']}\n\n")
                        f.write("```python\n" + item['source'] + "\n```\n\n")
                    elif item['type'] == 'class':
                        f.write(f"## Class: {item['name']}\n")
                        f.write(f"**Docstring**: {item['docstring']}\n\n")
                        f.write("```python\n" + item['source'] + "\n```\n\n")
        except Exception as e:
            raise RuntimeError(f"Failed to write documentation file: {e}")

    def search_docs(self, query: str, docs_dir: str) -> List[str]:
        """Semantic search documentation using a natural language query. Returns the most relevant sections from markdown files in docs_dir."""
        import glob
        import re
        results = []
        sections = []
        section_files = []
        section_headers = []
        # Try to import sentence-transformers for semantic search
        try:
            from sentence_transformers import SentenceTransformer, util
            model = SentenceTransformer('all-MiniLM-L6-v2')
            use_semantic = True
        except ImportError:
            use_semantic = False
        # Extract all sections from all markdown files
        for md_file in glob.glob(os.path.join(docs_dir, "*.md")):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Split by headers (## or #)
                for match in re.finditer(r'^(#+ .+)$', content, re.MULTILINE):
                    start = match.start()
                    header = match.group(1)
                    next_match = re.search(r'^(#+ .+)$', content[start+1:], re.MULTILINE)
                    end = start + 1 + next_match.start() if next_match else len(content)
                    section = content[start:end].strip()
                    sections.append(section)
                    section_files.append(os.path.basename(md_file))
                    section_headers.append(header)
        if not sections:
            return [f"No documentation sections found in {docs_dir}."]
        if use_semantic:
            # Embed all sections and the query
            section_embeddings = model.encode(sections, convert_to_tensor=True)
            query_embedding = model.encode(query, convert_to_tensor=True)
            # Compute cosine similarities
            import torch
            similarities = util.pytorch_cos_sim(query_embedding, section_embeddings)[0]
            top_indices = similarities.argsort(descending=True)[:5]
            for idx in top_indices:
                score = similarities[idx].item()
                if score < 0.3:
                    continue  # Only show relevant matches
                results.append(f"In {section_files[idx]} (score={score:.2f}):\n{sections[idx]}\n")
        else:
            # Fallback: keyword/fuzzy match
            for i, section in enumerate(sections):
                if re.search(re.escape(query), section, re.IGNORECASE):
                    results.append(f"In {section_files[i]}:\n{section}\n")
        if not results:
            return [f"No results found for '{query}' in {docs_dir}."]
        return results

    def generate_readme(self, module_path: str, output_path: str = "README.md", language: Optional[str] = None) -> None:
        """Generate a project-level README.md summarizing the module, its classes, and functions."""
        lang = language or self.language
        items = self.parse_module(module_path)
        # Compose a summary prompt for the whole module
        module_item = next((item for item in items if item['type'] == 'module'), None)
        class_items = [item for item in items if item['type'] == 'class']
        function_items = [item for item in items if item['type'] == 'function']
        try:
            module_summary = self._llm(module_item['docstring'], 'summarize', lang) if module_item else ""
        except Exception as e:
            module_summary = f"Error from LLM: {e}"
        readme = f"# {os.path.basename(module_path)}\n\n"
        readme += f"## Module Summary\n{module_summary}\n\n"
        if class_items:
            readme += "## Classes\n"
            for cls in class_items:
                readme += f"### {cls['name']}\n{cls['docstring']}\n\n"
        if function_items:
            readme += "## Functions\n"
            for func in function_items:
                readme += f"### {func['name']}\n{func['docstring']}\n\n"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(readme) 