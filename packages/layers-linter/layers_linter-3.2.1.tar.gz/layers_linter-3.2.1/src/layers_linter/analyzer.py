from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from layers_linter.config import LayerConfig, LibConfig, load_config
from layers_linter.imports import collect_imports
from layers_linter.search_modules import (
    ModulePathT,
    find_modules_in_directory,
    FilePathT,
    match_pattern,
)


@dataclass
class Problem:
    line_number: int
    module_path: str
    imported_module: str
    code: str

    @property
    def message(self) -> str:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def file_path(self) -> str:
        return self.module_path.replace(".", "/") + ".py"


@dataclass
class LayerProblem(Problem):
    layer_from: str
    layer_to: str

    @property
    def message(self) -> str:
        return (
            f"Invalid layer dependency: '{self.layer_from or 'not-defined'}' "
            f"-> '{self.layer_to or 'not-defined'}'"
        )

    def __str__(self):
        return f"{self.file_path}:{self.line_number}: {self.message}"


@dataclass
class LibProblem(Problem):
    lib_name: str
    layers: List[str]

    @property
    def message(self) -> str:
        layers_str = ", ".join(self.layers)
        return f"Layers [{layers_str or 'not-defined'}] cannot use restricted library '{self.lib_name}'"

    def __str__(self):
        return f"{self.file_path}:{self.line_number}: {self.message}"


@dataclass
class NoLayerProblem(Problem):
    @property
    def message(self) -> str:
        return f"Module '{self.module_path}' does not belong to any layer"

    def __str__(self):
        return f"{self.file_path}: {self.message}"


def analyze_dependencies(
    project_root: Path,
    layers: Dict[str, LayerConfig],
    libs: Dict[str, LibConfig],
    exclude_modules: List[str],
    check_no_layer: bool = False,
) -> List[Problem]:
    modules_list = find_modules_in_directory(
        FilePathT(project_root), patterns=None, exclude_patterns=exclude_modules
    )
    all_project_modules = set(module_path for _, module_path in modules_list)

    module_to_layers: Dict[ModulePathT, List[str]] = defaultdict(list)
    for _, module_path in modules_list:
        for layer_name, layer_info in layers.items():
            # Check if module should be excluded for this layer
            excluded = False
            if layer_info.exclude_modules:
                for pattern in layer_info.exclude_modules:
                    if match_pattern(module_path, pattern):
                        excluded = True
                        break

            if excluded:
                continue

            for pattern in layer_info.contains_modules:
                if match_pattern(module_path, pattern):
                    module_to_layers[module_path].append(layer_name)
                    break

    # Check for modules that belong to multiple layers
    for module_path, module_layers in module_to_layers.items():
        if len(module_layers) > 1:
            layers_str = ", ".join(module_layers)
            raise ValueError(f"Module '{module_path}' belongs to multiple layers: [{layers_str}]")

    module_imports = collect_imports(all_project_modules, modules_list)

    problems = []

    for module_path, imports in module_imports.items():
        layers_a = module_to_layers.get(module_path, [])
        for import_info in imports:
            imported_module = import_info.module
            lineno = import_info.line_number

            if not import_info.is_internal:
                continue

            layers_b = module_to_layers.get(imported_module, [])

            if not layers_a or not layers_b:
                continue

            allowed = False
            for la_name in layers_a:
                for lb_name in layers_b:
                    la = layers[la_name]

                    # Depends_on check: layer A can only depend on those specified in depends_on.
                    depends_on_ok = True
                    if la.depends_on is not None:
                        if lb_name not in la.depends_on:
                            depends_on_ok = False

                    if depends_on_ok:
                        allowed = True
                        break
                if allowed:
                    break

            if not allowed:
                for la_name in layers_a:
                    for lb_name in layers_b:
                        problems.append(
                            LayerProblem(
                                line_number=lineno,
                                module_path=module_path,
                                imported_module=imported_module,
                                layer_from=la_name,
                                layer_to=lb_name,
                                code="LA001",
                            )
                        )

    # Check library dependencies
    for module_path, imports in module_imports.items():
        layers_a = module_to_layers.get(module_path, [])

        for import_info in imports:
            imported_module = import_info.module
            lineno = import_info.line_number

            # Skip if it's not a library import
            if import_info.is_internal:
                continue

            # Find if this is a known library
            matching_libs = []
            for lib_name in libs:
                if imported_module == lib_name or imported_module.startswith(f"{lib_name}."):
                    matching_libs.append(lib_name)

            for lib_name in matching_libs:
                lib_config = libs[lib_name]

                # If library has no restrictions, skip
                if lib_config.allowed_in is None:
                    continue

                # Check if any of the module's layers are allowed to use this library
                allowed = False
                for layer_name in layers_a:
                    if layer_name in lib_config.allowed_in:
                        allowed = True
                        break

                if not allowed:
                    problems.append(
                        LibProblem(
                            line_number=lineno,
                            module_path=module_path,
                            imported_module=imported_module,
                            code="LA020",
                            lib_name=lib_name,
                            layers=layers_a,
                        )
                    )

    if check_no_layer:
        for file_path, module_path in modules_list:
            if module_path not in module_to_layers:
                problems.append(
                    NoLayerProblem(
                        line_number=0,
                        module_path=module_path,
                        imported_module="",
                        code="LA002",
                    )
                )

    return problems


def run_linter(project_root: Path, config_path: Path, check_no_layer: bool = False) -> List[Problem]:
    layers, libs, exclude_modules = load_config(config_path)
    return analyze_dependencies(project_root, layers, libs, exclude_modules, check_no_layer)
