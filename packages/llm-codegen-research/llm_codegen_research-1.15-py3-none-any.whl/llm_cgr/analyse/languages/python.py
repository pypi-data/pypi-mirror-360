"""Utility functions for Python code analysis."""

import ast
import sys
from collections import defaultdict
from typing import Any

from llm_cgr.analyse.languages.code_data import CodeData


PYTHON_STDLIB = getattr(
    sys, "stdlib_module_names", []
)  # use this below to categorise packages


class PythonAnalyser(ast.NodeVisitor):
    def __init__(self):
        self.std_libs: set[str] = set()
        self.ext_libs: set[str] = set()
        self.imports: dict[str, str] = {}
        self.lib_usage: defaultdict[str, list[dict]] = defaultdict(list)

    def visit_Import(self, node: ast.Import):
        # save `import module` imports
        for alias in node.names:
            # save all imports
            name = alias.name
            asname = alias.asname or alias.name
            self.imports[asname] = name

            # save packages
            top_level = name.split(".")[0]
            if top_level in PYTHON_STDLIB:
                self.std_libs.add(top_level)
            else:
                self.ext_libs.add(top_level)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # save `from module import thing` imports
        module = node.module or ""

        # save packages
        # node.level is 0 for absolute imports, 1+ for relative imports
        if module and node.level == 0:
            package = module.split(".")[0]
            if package in PYTHON_STDLIB:
                self.std_libs.add(package)
            else:
                self.ext_libs.add(package)

        # save all imports
        for alias in node.names:
            full_name = f"{module}.{alias.name}" if module else alias.name
            asname = alias.asname or alias.name
            self.imports[asname] = full_name

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # handle attribute calls: e.g., np.func() or np.sub.func()
        full_name = self._resolve_attribute(node=node.func)

        if full_name:
            # extract arguments if we have a full function name
            library, _, function = full_name.partition(".")
            arg_strs = [ast.unparse(arg) for arg in node.args]
            kw_strs = {kw.arg: ast.unparse(kw.value) for kw in node.keywords}

            self.lib_usage[library].append(
                {
                    "type": "call",
                    "member": function,
                    "args": arg_strs,
                    "kwargs": kw_strs,
                }
            )

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # handle any attribute access on imported modules/submodules
        full_name = self._resolve_attribute(node)
        if full_name:
            library, _, member = full_name.partition(".")
            self.lib_usage[library].append(
                {
                    "type": "access",
                    "member": member,
                }
            )
        self.generic_visit(node)

    def _resolve_attribute(self, node: Any) -> str | None:
        # resolve the full module path for an attribute call
        attr_names = []
        current: Any = node
        # unwind attribute chains to build full module path
        while isinstance(current, ast.Attribute):
            attr_names.append(current.attr)
            current = current.value
        # save if the base module is in imports
        if isinstance(current, ast.Name) and current.id in self.imports:
            base = self.imports[current.id]
            path = ".".join([base] + list(reversed(attr_names)))
            return path
        # not a valid import
        return None


def analyse_python_code(code: str) -> CodeData:
    """
    Analyse Python code to extract functions and imports.
    """
    tree = ast.parse(code)
    analyser = PythonAnalyser()
    analyser.visit(tree)

    lib_usage: dict[str, list[dict]] = {}
    for library, usage in analyser.lib_usage.items():
        lib_usage[library] = []
        all_members = [u["member"] for u in usage]
        call_members = [u["member"] for u in usage if u["type"] == "call"]
        for record in usage:
            # skip access records if the member is already used in a call
            if record["type"] == "access":
                if record["member"] in call_members or any(
                    m.startswith(f"{record['member']}.") for m in all_members
                ):
                    continue

            lib_usage[library].append(record)

    return CodeData(
        valid=True,
        std_libs=analyser.std_libs,
        ext_libs=analyser.ext_libs,
        lib_usage=lib_usage,
    )
