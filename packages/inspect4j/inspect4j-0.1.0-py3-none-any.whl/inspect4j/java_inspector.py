import javalang
from pathlib import Path
from collections import defaultdict
import json
import os
import click
import time
import sys
import re

# Import utility functions from java_utils
from .java_utils import *


def extract_call_functions(funcs_info, body=0):
    """
    Extract call list from functions information.
    Adapted from inspect4py's version for Java.
    
    :param funcs_info: Functions information dictionary
    :param body: Whether processing body calls (1) or regular functions (0)
    :return: Call list dictionary
    """
    call_list = {}
    if body:
        if "calls" in funcs_info and funcs_info["calls"]:
            call_list["local"] = funcs_info["calls"]
    else:
        for funct in funcs_info:
            if "calls" in funcs_info[funct] and funcs_info[funct]["calls"]:
                call_list[funct] = {}
                call_list[funct]["local"] = funcs_info[funct]["calls"]
                # Handle nested functions if present
                if "functions" in funcs_info[funct] and funcs_info[funct]["functions"]:
                    call_list[funct]["nested"] = extract_call_functions(funcs_info[funct]["functions"])
    return call_list


def extract_call_methods(classes_info):
    """
    Extract call list from classes/methods information.
    Adapted from inspect4py's version for Java.
    
    :param classes_info: Classes information dictionary
    :return: Call list dictionary for methods
    """
    call_list = {}
    for method in classes_info:
        if "calls" in classes_info[method] and classes_info[method]["calls"]:
            call_list[method] = {}
            call_list[method]["local"] = classes_info[method]["calls"]
            # Handle nested functions in methods if present
            if "functions" in classes_info[method] and classes_info[method]["functions"]:
                call_list[method]["nested"] = extract_call_methods(classes_info[method]["functions"])
    return call_list


def call_list_file(inspector):
    """
    Generate call list for a single file.
    Adapted from inspect4py's version for Java.
    
    :param inspector: JavaInspection instance
    :return: Call list dictionary for the file
    """
    call_list = {}
    
    # Extract function calls - Java doesn't have standalone functions like Python
    # We'll use static methods instead
    call_list["functions"] = {}
    
    # Extract body calls - Java version doesn't have body in the same way as Python
    # but we can extract main method calls or static method calls
    call_list["body"] = {}
    if hasattr(inspector, 'main_info') and inspector.main_info and "calls" in inspector.main_info:
        call_list["body"] = extract_call_functions(inspector.main_info, body=1)
    
    # Extract class method calls
    call_list["classes"] = {}
    if hasattr(inspector, 'classes_info') and inspector.classes_info:
        for class_name in inspector.classes_info:
            class_data = inspector.classes_info[class_name]
            if "methods" in class_data and class_data["methods"]:
                call_list["classes"][class_name] = extract_call_methods(class_data["methods"])
    
    return call_list


def call_list_dir(dir_info):
    """
    Generate call list for directory containing multiple files.
    Adapted from inspect4py's version for Java.
    
    :param dir_info: Directory information dictionary
    :return: Call list dictionary for the directory
    """
    call_list = {}
    
    for dir_path in dir_info:
        call_list[dir_path] = {}
        
        for file_info in dir_info[dir_path]:
            file_path = file_info["file"]["path"]
            call_list[dir_path][file_path] = {}
            
            # Extract function calls - Java doesn't have standalone functions
            call_list[dir_path][file_path]["functions"] = {}
            
            # Extract body calls (main method or static calls)
            if "main_info" in file_info and file_info["main_info"] and "calls" in file_info["main_info"]:
                call_list[dir_path][file_path]["body"] = extract_call_functions(file_info["main_info"], body=1)
            else:
                call_list[dir_path][file_path]["body"] = {}
            
            # Extract class method calls
            call_list[dir_path][file_path]["classes"] = {}
            if "classes" in file_info:
                for class_name in file_info["classes"]:
                    class_data = file_info["classes"][class_name]
                    if "methods" in class_data and class_data["methods"]:
                        call_list[dir_path][file_path]["classes"][class_name] = extract_call_methods(class_data["methods"])
    
    return call_list


class JavaInspection:
    def __init__(self, input_path, json_dir, abstract_syntax_tree, source_code, parser):
        self.path = input_path
        self.json_dir = json_dir
        self.abstract_syntax_tree = abstract_syntax_tree
        self.source_code = source_code
        self.parser = parser
        self.source_lines = self.read_source_file()
        self.tree = self.parse_file()
        # Initialize anonymous class counter
        self._anonymous_class_counter = 0
        if self.tree:
            self.package_info = self.inspect_package()
            self.import_info = self.inspect_imports() 
            # Build import mapping for cross-file resolution
            self._build_import_mapping()
            class_and_interface_result = self.inspect_classes()
            if len(class_and_interface_result) == 3:
                self.classes_info, self.interfaces_info, self.enums_info = class_and_interface_result
            else:
                self.classes_info, self.interfaces_info = class_and_interface_result
                self.enums_info = {}
            # Enrich method calls after all information is collected
            self._enrich_all_method_calls()
            self.main_info = self._inspect_main()
            self.file_json = self.create_file_json()
        else:
            self.file_json = {}

    def read_source_file(self):
        """Read source file and return lines for JavaDoc extraction"""
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                return file.readlines()
        except Exception as e:
            print(f"Failed to read {self.path}: {str(e)}")
            return []

    def parse_file(self):
        """Parse Java file into AST using javalang"""
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                content = file.read()
            return javalang.parse.parse(content)
        except Exception as e:
            print(f"Failed to parse {self.path}: {str(e)}")
            return None
        

    def extract_javadoc(self, node):
        """Extract JavaDoc for a node based on its position"""
        if not hasattr(node, 'position') or not node.position:
            return {}
        
        start_line = node.position[0] #accounting for 1-indexing
        
        # Look for JavaDoc comment before the node's line
        javadoc_lines = []
        i = start_line - 2  # Start from line before node (source_line accounting for 0-indexing)
        
        # Go backwards until we find the start of a JavaDoc comment
        while i >= 0:
            line = self.source_lines[i].strip()
            if line.endswith('*/'):
                # Found end of JavaDoc comment, collect all lines
                javadoc_lines.insert(0, line)
                i -= 1
                while i >= 0:
                    line = self.source_lines[i].strip()
                    javadoc_lines.insert(0, line)
                    if line.startswith('/**'):
                        # Found start of JavaDoc
                        return self.parse_javadoc('\n'.join(javadoc_lines))
                    i -= 1
            elif line == '' or line.startswith('//'):
                # Skip empty lines and single-line comments
                i -= 1
            else:
                # Not a comment, stop looking
                break
        
        return {}
    

    def parse_javadoc(self, javadoc_text):
        """Parse JavaDoc text into description and tags"""
        if not javadoc_text:
            return {}
            
        # Remove comment markers and clean up
        # javadoc_text = re.sub(r'/\*\*|\*/|^\s*\*\s?', '', javadoc_text, flags=re.MULTILINE)
        # javadoc_text = javadoc_text.strip()
        javadoc_text = javadoc_text.replace('/**', '').replace('*/', '')

        lines = javadoc_text.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = re.sub(r'^\s*\*\s?', '', line).rstrip('*').rstrip()
            cleaned_lines.append(cleaned_line)
        
        javadoc_text = '\n'.join(cleaned_lines).strip()
        
        # Split into description and tags
        parts = re.split(r'\n(?=@\w+)', javadoc_text)
        
        description = parts[0].strip() if parts else ""
        tags = [tag.strip() for tag in parts[1:]] if len(parts) > 1 else []
        
        # Format tags for readability
        # formatted_tags = []
        # for tag in tags:
        #     if tag.startswith('@'):
        #         tag_parts = tag.split(None, 1)
        #         tag_name = tag_parts[0]
        #         tag_content = tag_parts[1] if len(tag_parts) > 1 else ""
        #         formatted_tags.append(f"{tag_name}: {tag_content}")


        tag_dict = defaultdict(list)

        for tag in tags:
            if tag.startswith('@'):
                tag_parts = tag.split(None, 1)
                tag_name = tag_parts[0][1:]  # get rid of "@"
                tag_content = tag_parts[1].strip() if len(tag_parts) > 1 else ""
                tag_dict[tag_name].append(tag_content)

        # If a tag has only one value, it is expanded to a string.
        for key in tag_dict:
            if len(tag_dict[key]) == 1:
                tag_dict[key] = tag_dict[key][0]

        
        # return {
        #     "description": description,
        #     "comment_tags": formatted_tags
        # }
        return {
            "description": description,
            "comment_tags": dict(tag_dict)
        }
    

    def inspect_package(self):
        package_info = {}
        if self.tree.package:
            package_info["name"] = self.tree.package.name
            package_info["doc"] = self.extract_javadoc(self.tree.package)
        return package_info

    def inspect_imports(self):
        dependencies = []
        for imp in self.tree.imports:
            # Handle standard imports
            if not imp.static:
                import_path = imp.path
                
                # Check if this is a wildcard import using javalang's wildcard attribute
                if hasattr(imp, 'wildcard') and imp.wildcard:
                    # Process wildcard import: import package.*;
                    wildcard_imports = self._process_wildcard_import(import_path)
                    dependencies.extend(wildcard_imports)
                else:
                    # Process specific import
                    import_name = import_path.split('.')[-1]
                    import_type = self._determine_import_type(import_path)
                    
                    dep_info = {
                        "import": import_name,
                        "type": import_type,
                        "type_element": "class"  # Most Java imports are classes
                    }
                    
                    if len(import_path.split('.')) > 1:
                        dep_info["from_module"] = '.'.join(import_path.split('.')[:-1])
                    
                    dependencies.append(dep_info)
            
            # Handle static imports
            else:
                import_path = imp.path
                # Static imports can also be wildcards
                if hasattr(imp, 'wildcard') and imp.wildcard:
                    # Static wildcard import: import static package.*;
                    dep_info = {
                        "import": "*",
                        "type": self._determine_import_type(import_path),
                        "type_element": "static_package",
                        "from_module": import_path
                        # "is_static": True,
                        # "is_wildcard": True
                    }
                    dependencies.append(dep_info)
                else:
                    import_name = import_path.split('.')[-1]
                    import_type = self._determine_import_type(import_path)
                    
                    dep_info = {
                        "import": import_name,
                        "type": import_type,
                        "type_element": "static_member"
                        # "is_static": True
                    }
                    
                    if len(import_path.split('.')) > 1:
                        dep_info["from_module"] = '.'.join(import_path.split('.')[:-1])
                    
                    dependencies.append(dep_info)
                
        # Also check for internal class references that are not imported
        # (same package or implicit references)
        internal_refs = self._find_internal_class_references()
        dependencies.extend(internal_refs)
        
        return dependencies

    def _find_internal_class_references(self):
        """
        Find references to internal classes that are not explicitly imported.
        This includes same-package classes and classes referenced through field types.
        
        :return: List of internal class references
        """
        internal_refs = []
        project_root = Path(self.path).parent
        
        # Get current package from file or assume default package
        current_package = ""
        if hasattr(self, 'package_info') and self.package_info and 'name' in self.package_info:
            current_package = self.package_info['name']
        
        # Look for class references in field types, method parameters, etc.
        if self.tree.types:
            for type_decl in self.tree.types:
                if hasattr(type_decl, 'fields'):
                    for field in type_decl.fields:
                        field_type = get_type_name(field.type)
                        # Check if this type refers to an internal class
                        if self._is_likely_internal_class_reference(field_type, current_package, project_root):
                            internal_ref = {
                                "import": field_type,
                                "type": "internal",
                                "type_element": "class",
                                "from_module": current_package,
                            }
                            # Avoid duplicates
                            if not any(ref["import"] == field_type for ref in internal_refs):
                                internal_refs.append(internal_ref)
        
        return internal_refs

    def _is_likely_internal_class_reference(self, type_name, current_package, project_root):
        """
        Check if a type name likely refers to an internal class.
        
        :param type_name: The type name to check
        :param current_package: Current package name
        :param project_root: Project root directory
        :return: True if likely an internal class
        """
        # Skip primitive types and common Java types
        if type_name in ['int', 'long', 'short', 'byte', 'float', 'double', 'boolean', 'char', 'void',
                        'String', 'Object', 'Class', 'Integer', 'Long', 'Short', 'Byte', 'Float', 
                        'Double', 'Boolean', 'Character', 'Void']:
            return False
        
        # Skip array types and generic types
        if '[' in type_name or '<' in type_name or '>' in type_name:
            return False
        
        # Skip if it starts with java. or javax. (standard library)
        if type_name.startswith('java.') or type_name.startswith('javax.'):
            return False
        
        # Check if file exists in current directory (same package)
        current_dir = Path(self.path).parent
        potential_file = current_dir / f"{type_name}.java"
        if potential_file.exists():
            return True
        
        # Check in common source directories
        source_dirs = ['src/main/java/', 'src/', 'source/', 'java/', '']
        
        # If we have a package, construct the full path
        if current_package:
            package_path = current_package.replace('.', '/')
            for source_dir in source_dirs:
                potential_file = project_root / source_dir / package_path / f"{type_name}.java"
                if potential_file.exists():
                    return True
        
        return False

    def _determine_import_type(self, import_path):
        """
        Determine if an import is internal (project) or external (library/JDK).
        
        :param import_path: Full import path (e.g., 'java.util.List')
        :return: 'internal' or 'external'
        """
        # Check for standard Java libraries
        if is_standard_library(import_path):
            return "external"
        
        # Check if it's an internal import (exists in project)
        if self._is_internal_import(import_path):
            return "internal"
        
        # Default to external (third-party dependencies)
        return "external"



    def _is_internal_import(self, import_path):
        """
        Check if the import refers to a class within the current project.
        
        :param import_path: Full import path (e.g., 'com.example.MyClass')
        :return: True if it's an internal import
        """
        # Convert package path to file system path
        relative_path = import_path.replace('.', '/') + '.java'
        
        # Get project root directory
        project_root = Path(self.path).parent
        
        # Common Java source directory patterns
        source_dirs = [
            'src/main/java/',    # Maven/Gradle standard
            'src/',              # Simple structure
            'source/',           # Alternative naming
            'java/',             # Alternative naming
            '',                  # Root level
        ]
        
        # Check if the file exists in any of the source directories
        for source_dir in source_dirs:
            potential_file = project_root / source_dir / relative_path
            if potential_file.exists():
                return True
        
        # Also check based on package declaration in current file
        if hasattr(self, 'package_info') and self.package_info and 'name' in self.package_info:
            current_package = self.package_info['name']
            # If import starts with same package prefix, likely internal
            if import_path.startswith(current_package.split('.')[0]):
                return True
        
        return False

    def _process_wildcard_import(self, package_path):
        """
        Process wildcard imports (import package.*;) by finding all classes in the package.
        
        :param package_path: Package path without the wildcard (e.g., 'java.util')
        :return: List of dependency info for each class found
        """
        dependencies = []
        
        # For standard library packages, we can't easily enumerate all classes
        # So we'll just record the wildcard import itself
        if is_standard_library(package_path + '.'):
            dep_info = {
                "import": "*",
                "type": "external",
                "type_element": "package",
                "from_module": package_path
                # "is_wildcard": True
            }
            dependencies.append(dep_info)
            return dependencies
        
        # For internal packages, try to find actual classes
        relative_package_path = package_path.replace('.', '/')
        project_root = Path(self.path).parent
        
        source_dirs = [
            'src/main/java/',
            'src/',
            'source/',
            'java/',
            '',
        ]
        
        classes_found = []
        for source_dir in source_dirs:
            package_dir = project_root / source_dir / relative_package_path
            if package_dir.exists() and package_dir.is_dir():
                # Find all .java files in the package directory (non-recursive)
                for java_file in package_dir.glob('*.java'):
                    class_name = java_file.stem  # Filename without .java extension
                    if class_name not in classes_found:
                        classes_found.append(class_name)
                        
                        dep_info = {
                            "import": class_name,
                            "type": "internal",
                            "type_element": "class",
                            "from_module": package_path
                            # "is_wildcard": True
                        }
                        dependencies.append(dep_info)
                break  # Found the package, no need to check other source dirs
        
        # If no classes found, record the wildcard import as-is
        if not classes_found:
            dep_info = {
                "import": "*",
                "type": "external" if not self._is_internal_import(package_path + '.DummyClass') else "internal",
                "type_element": "package",
                "from_module": package_path
                # "is_wildcard": True
            }
            dependencies.append(dep_info)
        
        return dependencies

    def _build_import_mapping(self):
        """
        Build a quick lookup mapping for imported classes and their modules.
        This enables efficient cross-file call resolution.
        """
        self.import_mapping = {}
        for dep in self.import_info:
            import_name = dep["import"]
            from_module = dep.get("from_module")
            if from_module:
                self.import_mapping[import_name] = from_module
            else:
                # For imports without from_module (like java.lang), use the import name
                self.import_mapping[import_name] = import_name

    def inspect_classes(self):
        classes_info = {}
        interfaces_info = {}
        
        # Only process top-level classes and interfaces from tree.types
        # This prevents nested classes from being processed twice
        if self.tree.types:
            for type_decl in self.tree.types:
                if isinstance(type_decl, javalang.tree.ClassDeclaration):
                    # Extract class-level assignments
                    class_assignments = {}
                    for field in type_decl.fields:
                        for declarator in field.declarators:
                            if is_method_or_constructor_call(declarator.initializer):
                                class_assignments[declarator.name] = method_call_to_str(declarator.initializer)
                    
                    # Extract class-level method calls from field initializations
                    class_calls = []
                    for field in type_decl.fields:
                        for declarator in field.declarators:
                            if declarator.initializer:
                                self._extract_calls_from_single_node(declarator.initializer, class_calls)
                    
                    class_info = {
                        "name": type_decl.name,
                        "modifiers": list(type_decl.modifiers),
                        "extends": type_decl.extends.name if type_decl.extends else None,
                        "implements": [i.name for i in type_decl.implements] if type_decl.implements else [],
                        "min_max_lineno": compute_interval(type_decl),
                        "doc": self.extract_javadoc(type_decl),
                        "methods": self.inspect_methods(type_decl),
                        "fields": self.inspect_fields(type_decl),
                        "calls": class_calls,
                        "store_vars_calls": class_assignments
                    }
                    
                    # Add annotations if present
                    annotations = extract_annotations(type_decl)
                    if annotations:
                        class_info["annotations"] = annotations
                    
                    # Add nested structure inspection
                    nested_structures = self.inspect_nested_structures(type_decl)
                    if nested_structures:
                        class_info.update(nested_structures)
                    
                    classes_info[type_decl.name] = class_info
                
                elif isinstance(type_decl, javalang.tree.InterfaceDeclaration):
                    interface_info = {
                        "name": type_decl.name,
                        "modifiers": list(type_decl.modifiers),
                        "extends": [e.name for e in type_decl.extends] if type_decl.extends else [],
                        "min_max_lineno": compute_interval(type_decl),
                        "doc": self.extract_javadoc(type_decl),
                        "methods": self.inspect_interface_methods(type_decl),
                        "fields": self.inspect_fields(type_decl)
                    }
                    
                    # Add annotations if present
                    annotations = extract_annotations(type_decl)
                    if annotations:
                        interface_info["annotations"] = annotations
                    
                    # Add nested structure inspection for interfaces
                    nested_structures = self.inspect_nested_structures(type_decl)
                    if nested_structures:
                        interface_info.update(nested_structures)
                        
                    interfaces_info[type_decl.name] = interface_info
                
                elif isinstance(type_decl, javalang.tree.EnumDeclaration):
                    # Extract enums as basic elements
                    enum_info = {
                        "name": type_decl.name,
                        "modifiers": list(type_decl.modifiers),
                        "implements": [i.name for i in type_decl.implements] if type_decl.implements else [],
                        "min_max_lineno": compute_interval(type_decl),
                        "doc": self.extract_javadoc(type_decl),
                        "enum_constants": [const.name for const in type_decl.body.constants] if type_decl.body and type_decl.body.constants else []
                    }
                    
                    # Add annotations if present
                    annotations = extract_annotations(type_decl)
                    if annotations:
                        enum_info["annotations"] = annotations
                    
                    # Extract enum methods and fields
                    if type_decl.body and hasattr(type_decl.body, 'declarations') and type_decl.body.declarations:
                        methods = {}
                        fields = {}
                        for decl in type_decl.body.declarations:
                            if isinstance(decl, javalang.tree.MethodDeclaration):
                                method_info = {
                                    "name": decl.name,
                                    "modifiers": list(decl.modifiers),
                                                                    "return_type": get_type_name(decl.return_type) if decl.return_type else None,
                                "parameters": [{
                                    "name": param.name,
                                    "type": get_type_name(param.type)
                                } for param in decl.parameters],
                                    "min_max_lineno": compute_interval(decl),
                                    "doc": self.extract_javadoc(decl)
                                }
                                # Add method annotations
                                method_annotations = extract_annotations(decl)
                                if method_annotations:
                                    method_info["annotations"] = method_annotations
                                # Add AST and source code extraction for enum methods
                                if self.abstract_syntax_tree:
                                    method_info["ast"] = ast_to_json(decl)
                                if self.source_code:
                                    method_info["source_code"] = ast_to_source_code(decl, self.source_lines)
                                methods[decl.name] = method_info
                            elif isinstance(decl, javalang.tree.FieldDeclaration):
                                for declarator in decl.declarators:
                                    field_info = {
                                        "name": declarator.name,
                                        "type": get_type_name(decl.type),
                                        "modifiers": list(decl.modifiers),
                                        "doc": self.extract_javadoc(decl)
                                    }
                                    # Add field annotations
                                    field_annotations = extract_annotations(decl)
                                    if field_annotations:
                                        field_info["annotations"] = field_annotations
                                    fields[declarator.name] = field_info
                            elif isinstance(decl, javalang.tree.ConstructorDeclaration):
                                # Handle enum constructors
                                method_info = {
                                    "name": decl.name,
                                    "modifiers": list(decl.modifiers),
                                    "return_type": None,
                                    "parameters": [{
                                        "name": param.name,
                                                                            "type": get_type_name(param.type)
                                } for param in decl.parameters],
                                    "min_max_lineno": compute_interval(decl),
                                    "doc": self.extract_javadoc(decl)
                                }
                                # Add constructor annotations
                                constructor_annotations = extract_annotations(decl)
                                if constructor_annotations:
                                    method_info["annotations"] = constructor_annotations
                                # Add AST and source code extraction for enum constructors
                                if self.abstract_syntax_tree:
                                    method_info["ast"] = ast_to_json(decl)
                                if self.source_code:
                                    method_info["source_code"] = ast_to_source_code(decl, self.source_lines)
                                methods[decl.name] = method_info
                        
                        if methods:
                            enum_info["methods"] = methods
                        if fields:
                            enum_info["fields"] = fields
                    
                    # Store enums in a separate section
                    if "enums_info" not in locals():
                        enums_info = {}
                    enums_info[type_decl.name] = enum_info
                
        # Add enums to the return if any were found
        if 'enums_info' in locals():
            return classes_info, interfaces_info, enums_info
        else:
            return classes_info, interfaces_info

    def inspect_methods(self, class_node):
        methods_info = {}
        
        for constructor in class_node.constructors:
            method_info = {
                "name": constructor.name,
                "modifiers": list(constructor.modifiers),
                "return_type": None,  # no return type for constructor
                "parameters": [{
                    "name": param.name,
                    "type": get_type_name(param.type)
                } for param in constructor.parameters],
                "min_max_lineno": compute_interval(constructor),
                "doc": self.extract_javadoc(constructor),
                "calls": self._extract_method_calls(constructor.body if constructor.body else []),
                "store_vars_calls": self._extract_assignments(constructor.body if constructor.body else [])
            }
            
            # Add constructor annotations
            annotations = extract_annotations(constructor)
            if annotations:
                method_info["annotations"] = annotations
            
            # Add parameter annotations
            param_annotations = []
            for param in constructor.parameters:
                param_ann = extract_annotations(param)
                if param_ann:
                    param_annotations.append({
                        "parameter": param.name,
                        "annotations": param_ann
                    })
            if param_annotations:
                method_info["parameter_annotations"] = param_annotations
            
            # Extract local and anonymous classes within constructor
            local_structures = self._extract_method_level_structures(constructor.body if constructor.body else [])
            if local_structures:
                method_info.update(local_structures)
            
            # Add AST and source code extraction for constructors
            if self.abstract_syntax_tree:
                method_info["ast"] = ast_to_json(constructor)
            if self.source_code:
                method_info["source_code"] = ast_to_source_code(constructor, self.source_lines)
            
            # Handle constructor overloading
            method_key = get_unique_method_key(constructor.name, method_info["parameters"], methods_info)
            methods_info[method_key] = method_info
        
        for method in class_node.methods:
            returns = []
            if method.body:
                returns = self._extract_returns(method.body)
            
            method_info = {
                "name": method.name,
                "modifiers": list(method.modifiers),
                "return_type": get_type_name(method.return_type) if method.return_type else None,
                "parameters": [{
                    "name": param.name,
                    "type": get_type_name(param.type)
                } for param in method.parameters],
                "min_max_lineno": compute_interval(method),
                "doc": self.extract_javadoc(method),
                "returns": returns,
                "calls": self._extract_method_calls(method.body if method.body else []),
                "store_vars_calls": self._extract_assignments(method.body if method.body else [])
            }
            
            # Add method annotations
            annotations = extract_annotations(method)
            if annotations:
                method_info["annotations"] = annotations
            
            # Add parameter annotations
            param_annotations = []
            for param in method.parameters:
                param_ann = extract_annotations(param)
                if param_ann:
                    param_annotations.append({
                        "parameter": param.name,
                        "annotations": param_ann
                    })
            if param_annotations:
                method_info["parameter_annotations"] = param_annotations
            
            # Extract local and anonymous classes within method
            local_structures = self._extract_method_level_structures(method.body if method.body else [])
            if local_structures:
                method_info.update(local_structures)
            
            # Add AST and source code extraction for methods
            if self.abstract_syntax_tree:
                method_info["ast"] = ast_to_json(method)
            if self.source_code:
                method_info["source_code"] = ast_to_source_code(method, self.source_lines)
            
            # Handle method overloading
            method_key = get_unique_method_key(method.name, method_info["parameters"], methods_info)
            methods_info[method_key] = method_info
            
        return methods_info

    def _extract_method_level_structures(self, method_body):
        """
        Extract local classes, anonymous classes, and lambda expressions from method body.
        
        :param method_body: List of statements in the method body
        :return: Dictionary containing method-level nested structures
        """
        method_structures = {}
        
        # Extract local classes
        local_classes = self._extract_local_classes(method_body)
        if local_classes:
            method_structures["local_classes"] = local_classes
            
        # Extract anonymous classes
        anonymous_classes = self._extract_anonymous_classes(method_body)
        if anonymous_classes:
            method_structures["anonymous_classes"] = anonymous_classes
            
        # Extract lambda expressions
        lambda_expressions = self._extract_lambda_expressions(method_body)
        if lambda_expressions:
            method_structures["lambda_expressions"] = lambda_expressions
            
        return method_structures

    def _extract_local_classes(self, statements):
        """Extract local classes from method body statements"""
        local_classes = {}
        
        def extract_from_statements(stmts):
            for stmt in stmts:
                # Local class declaration
                if isinstance(stmt, javalang.tree.ClassDeclaration):
                    class_info = {
                        "name": stmt.name,
                        "modifiers": list(stmt.modifiers),
                        "extends": stmt.extends.name if stmt.extends else None,
                        "implements": [i.name for i in stmt.implements] if stmt.implements else [],
                        "min_max_lineno": compute_interval(stmt),
                        "doc": self.extract_javadoc(stmt),
                        "methods": self.inspect_methods(stmt),
                        "fields": self.inspect_fields(stmt)
                    }
                    local_classes[stmt.name] = class_info
                    
                # Recursively check block statements (if, for, while, etc.)
                elif hasattr(stmt, 'body') and stmt.body:
                    extract_from_statements(stmt.body)
                elif hasattr(stmt, 'statements') and stmt.statements:
                    extract_from_statements(stmt.statements)
                # Handle try-catch-finally blocks
                elif isinstance(stmt, javalang.tree.TryStatement):
                    if stmt.block:
                        extract_from_statements(stmt.block)
                    if stmt.catches:
                        for catch in stmt.catches:
                            if catch.block:
                                extract_from_statements(catch.block)
                # Handle switch statements
                elif isinstance(stmt, javalang.tree.SwitchStatement):
                    if stmt.cases:
                        for case in stmt.cases:
                            if case.statements:
                                extract_from_statements(case.statements)
        
        extract_from_statements(statements)
        return local_classes

    def _extract_anonymous_classes(self, statements):
        """Extract anonymous classes from method body statements"""
        anonymous_classes = []
        self._anonymous_class_counter = getattr(self, '_anonymous_class_counter', 0)
        
        def extract_from_statements(stmts):
            for stmt in stmts:
                # Look for ClassCreator expressions (new ClassName() { ... })
                if isinstance(stmt, javalang.tree.StatementExpression):
                    anonymous_in_expr = self._find_anonymous_in_expression(stmt.expression)
                    anonymous_classes.extend(anonymous_in_expr)
                elif isinstance(stmt, javalang.tree.LocalVariableDeclaration):
                    for declarator in stmt.declarators:
                        if declarator.initializer:
                            anonymous_in_expr = self._find_anonymous_in_expression(declarator.initializer)
                            anonymous_classes.extend(anonymous_in_expr)
                # Recursively check block statements
                elif hasattr(stmt, 'body') and stmt.body:
                    extract_from_statements(stmt.body)
                elif hasattr(stmt, 'statements') and stmt.statements:
                    extract_from_statements(stmt.statements)
                elif isinstance(stmt, javalang.tree.TryStatement):
                    if stmt.block:
                        extract_from_statements(stmt.block)
                    if stmt.catches:
                        for catch in stmt.catches:
                            if catch.block:
                                extract_from_statements(catch.block)
                elif isinstance(stmt, javalang.tree.SwitchStatement):
                    if stmt.cases:
                        for case in stmt.cases:
                            if case.statements:
                                extract_from_statements(case.statements)
        
        extract_from_statements(statements)
        return anonymous_classes

    def _find_anonymous_in_expression(self, expr):
        """Find anonymous classes within an expression"""
        anonymous_classes = []
        
        if isinstance(expr, javalang.tree.ClassCreator):
            if expr.body:  # Anonymous class has a body
                self._anonymous_class_counter += 1
                
                anonymous_info = {
                    "name": f"Anonymous_{self._anonymous_class_counter}",
                    "type": expr.type.name if expr.type else "Unknown",
                    "min_max_lineno": compute_interval(expr),
                    "methods": {},
                    "fields": {}
                }
                
                # Extract methods and fields from anonymous class body
                if expr.body:
                    for member in expr.body:
                        if isinstance(member, javalang.tree.MethodDeclaration):
                            method_info = {
                                "name": member.name,
                                "modifiers": list(member.modifiers),
                                "return_type": get_type_name(member.return_type) if member.return_type else None,
                                "parameters": [{
                                    "name": param.name,
                                    "type": get_type_name(param.type)
                                } for param in member.parameters],
                                "min_max_lineno": compute_interval(member),
                                "doc": self.extract_javadoc(member)
                            }
                            anonymous_info["methods"][member.name] = method_info
                        elif isinstance(member, javalang.tree.FieldDeclaration):
                            for declarator in member.declarators:
                                field_info = {
                                    "name": declarator.name,
                                    "type": get_type_name(member.type),
                                    "modifiers": list(member.modifiers),
                                    "doc": self.extract_javadoc(member)
                                }
                                anonymous_info["fields"][declarator.name] = field_info
                
                anonymous_classes.append(anonymous_info)
        
        # Recursively check method invocations and other expressions
        elif isinstance(expr, javalang.tree.MethodInvocation):
            if expr.arguments:
                for arg in expr.arguments:
                    anonymous_classes.extend(self._find_anonymous_in_expression(arg))
        
        return anonymous_classes

    def _extract_lambda_expressions(self, statements):
        """Extract lambda expressions from method body statements"""
        lambda_expressions = []

        def extract_from_statements(stmts):
            for stmt in stmts:
                # Handle local variable declarations
                if isinstance(stmt, javalang.tree.LocalVariableDeclaration):
                    for declarator in stmt.declarators:
                        if declarator.initializer:
                            lambda_expressions.extend(
                                self._find_lambdas_in_expression(declarator.initializer)
                            )

                # Handle expressions
                elif isinstance(stmt, javalang.tree.StatementExpression):
                    lambda_expressions.extend(
                        self._find_lambdas_in_expression(stmt.expression)
                    )

                # Recursively process known statement containers
                for attr in ['body', 'statements', 'block', 'finally_block']:
                    inner = getattr(stmt, attr, None)
                    if isinstance(inner, list):
                        extract_from_statements(inner)
                    elif inner:
                        extract_from_statements([inner])

                # Handle catches in try statements
                if isinstance(stmt, javalang.tree.TryStatement) and stmt.catches:
                    for catch in stmt.catches:
                        if catch.block:
                            extract_from_statements(catch.block)

                # Handle cases in switch statements
                if isinstance(stmt, javalang.tree.SwitchStatement) and stmt.cases:
                    for case in stmt.cases:
                        if case.statements:
                            extract_from_statements(case.statements)

        extract_from_statements(statements)
        return lambda_expressions

    def _find_lambdas_in_expression(self, expr):
        """Find lambda expressions within an expression"""
        lambda_expressions = []
        
        if isinstance(expr, javalang.tree.LambdaExpression):
            parameters = []
            if expr.parameters:
                for param in expr.parameters:
                    if hasattr(param, 'name'):
                        parameters.append(param.name)
                    elif hasattr(param, 'member'):
                        parameters.append(param.member)
                    else:
                        parameters.append(str(param))
            
            returns = []
            body_statements = []
            
            if expr.body:
                if isinstance(expr.body, javalang.tree.BlockStatement):
                    # Block lambda - expr.body is a BlockStatement, check for statements attribute
                    statements = getattr(expr.body, 'statements', [])
                    returns = self._extract_returns(statements)
                    
                    if not returns:
                        # No return statements, include body
                        body_statements = [statement_to_str(s) for s in statements]
                elif isinstance(expr.body, list):
                    # Block lambda - expr.body is a list of statements directly
                    returns = self._extract_returns(expr.body)
                    
                    if not returns:
                        # No return statements, include body
                        body_statements = [statement_to_str(s) for s in expr.body]
                else:
                    # Expression lambda - the body itself is the return value
                    returns = [expression_to_str(expr.body)]
            
            lambda_info = {
                "parameters": parameters,
                "min_max_lineno": compute_interval(expr),
                "returns": returns,
            }
            
            # Only add body field if there are no returns and we have statements
            if not returns and body_statements:
                lambda_info["body"] = body_statements
            
            lambda_expressions.append(lambda_info)
        
        elif isinstance(expr, javalang.tree.MethodInvocation):
            if expr.arguments:
                for arg in expr.arguments:
                    lambda_expressions.extend(self._find_lambdas_in_expression(arg))
        
        return lambda_expressions



    def _extract_returns(self, nodes):
        """Return a list of readable strings for every ReturnStatement expression."""
        returns = []

        for node in nodes:
            if isinstance(node, javalang.tree.ReturnStatement):
                if node.expression:
                    returns.append(expression_to_str(node.expression))
                else:
                    returns.append("void")        # bare 'return;'
                continue

            for attr in ("body", "then_statement", "else_statement", "finally_block", "block"):
                sub = getattr(node, attr, None)
                if isinstance(sub, list):
                    returns.extend(self._extract_returns(sub))
                elif sub:
                    returns.extend(self._extract_returns([sub]))

            if hasattr(node, "statements") and node.statements:
                returns.extend(self._extract_returns(node.statements))

            if isinstance(node, javalang.tree.TryStatement) and node.catches:
                for c in node.catches:
                    if c.block:
                        returns.extend(self._extract_returns(c.block))

            if isinstance(node, javalang.tree.SwitchStatement) and node.cases:
                for case in node.cases:
                    if case.statements:
                        returns.extend(self._extract_returns(case.statements))

        return returns

    def _extract_method_calls(self, nodes):
        """
        Extract method calls from a list of statements or expressions.
        This is the core function for building the method call list.
        In this phase, we extract basic calls. Chain expansion happens in _enrich_method_calls.
        
        :param nodes: List of AST nodes (statements, expressions, etc.)
        :return: List of method call strings
        """
        calls = []
        
        def extract_calls_from_node(node):
            """Recursively extract calls from a single node"""
            if node is None:
                return
                
            # Handle method invocations (e.g., myObject.doWork()) - Enhanced for chain calls
            if isinstance(node, javalang.tree.MethodInvocation):
                call_str = self._method_invocation_to_str(node)
                if call_str and call_str not in calls:
                    calls.append(call_str)
                
                # CRITICAL FIX: Handle selectors for chain calls (like a.getB().getC().doSomething())
                # javalang parses chain calls with the first call as the main MethodInvocation
                # and subsequent calls as selectors
                if hasattr(node, 'selectors') and node.selectors:
                    for selector in node.selectors:
                        if isinstance(selector, javalang.tree.MethodInvocation):
                            # Use "expr" prefix for selector calls to enable precise type resolution
                            selector_call_str = f"expr.{selector.member}"
                            if selector_call_str not in calls:
                                calls.append(selector_call_str)
                            
                            # Process selector arguments recursively
                            if selector.arguments:
                                for arg in selector.arguments:
                                    extract_calls_from_node(arg)
                
                # Recursively process qualifier and arguments
                if node.qualifier:
                    extract_calls_from_node(node.qualifier)
                if node.arguments:
                    for arg in node.arguments:
                        extract_calls_from_node(arg)
                        
            # Handle super method invocations (e.g., super.doWork())
            elif isinstance(node, javalang.tree.SuperMethodInvocation):
                # Enhanced to include argument types for overload resolution
                method_name = node.member
                arg_types = infer_argument_types(node.arguments) if node.arguments else []
                
                if arg_types:
                    # Include argument types in the method signature
                    arg_signature = ",".join(arg_types)
                    call_str = f"super.{method_name}({arg_signature})"
                else:
                    # Fallback to simple method name if we can't infer types
                    call_str = f"super.{method_name}"
                    
                if call_str and call_str not in calls:
                    calls.append(call_str)
                # Process arguments
                if node.arguments:
                    for arg in node.arguments:
                        extract_calls_from_node(arg)
                        
            # Handle super constructor calls (e.g., super())
            elif isinstance(node, javalang.tree.SuperConstructorInvocation):
                call_str = "super"
                if call_str and call_str not in calls:
                    calls.append(call_str)
                # Process arguments
                if node.arguments:
                    for arg in node.arguments:
                        extract_calls_from_node(arg)
                        
            # Handle constructor calls (new expressions) (e.g., new MyClass())
            elif isinstance(node, javalang.tree.ClassCreator):
                call_str = self._class_creator_to_str(node)
                if call_str and call_str not in calls:
                    calls.append(call_str)
                # Recursively process arguments
                if node.arguments:
                    for arg in node.arguments:
                        extract_calls_from_node(arg)
                        
            # Handle This expressions with selectors (e.g., this.field.add())
            elif isinstance(node, javalang.tree.This):
                if hasattr(node, 'selectors') and node.selectors:
                    # Process selectors to find method calls
                    self._extract_this_selector_calls(node, calls)
                        
            # Handle various statement types that might contain calls (e.g., String value = someObject.getValue())
            elif isinstance(node, javalang.tree.LocalVariableDeclaration):
                for declarator in node.declarators:
                    if declarator.initializer:
                        extract_calls_from_node(declarator.initializer)
                        
            elif isinstance(node, javalang.tree.StatementExpression):
                extract_calls_from_node(node.expression)
                
            elif isinstance(node, javalang.tree.ReturnStatement):
                if node.expression:
                    extract_calls_from_node(node.expression)
            
            # (e.g., instance = myFactory.createInstance())
            elif isinstance(node, javalang.tree.Assignment):
                extract_calls_from_node(node.value)
                extract_calls_from_node(node.expressionl)
                
            # Handle control flow statements
            elif isinstance(node, javalang.tree.IfStatement):
                extract_calls_from_node(node.condition)
                if node.then_statement:
                    extract_calls_from_node(node.then_statement)
                if node.else_statement:
                    extract_calls_from_node(node.else_statement)
                    
            elif isinstance(node, javalang.tree.ForStatement):
                if node.control:
                    extract_calls_from_node(node.control)
                if node.body:
                    extract_calls_from_node(node.body)
                    
            elif isinstance(node, javalang.tree.WhileStatement):
                extract_calls_from_node(node.condition)
                if node.body:
                    extract_calls_from_node(node.body)
                    
            # Handle block statements (collections of statements)
            elif isinstance(node, javalang.tree.BlockStatement):
                if node.statements:
                    for stmt in node.statements:
                        extract_calls_from_node(stmt)
                        
            # Handle binary operations that might contain method calls
            elif isinstance(node, javalang.tree.BinaryOperation):
                extract_calls_from_node(node.operandl)
                extract_calls_from_node(node.operandr)
                
            # Handle other expression types that might contain calls
            elif hasattr(node, '__dict__'):
                # Generic traversal for other node types
                for attr_name, attr_value in vars(node).items():
                    if attr_name.startswith('_'):
                        continue
                    if isinstance(attr_value, list):
                        for item in attr_value:
                            if hasattr(item, '__class__') and 'javalang' in str(item.__class__):
                                extract_calls_from_node(item)
                    elif hasattr(attr_value, '__class__') and 'javalang' in str(attr_value.__class__):
                        extract_calls_from_node(attr_value)
        
        # Process all nodes in the input list
        for node in nodes:
            extract_calls_from_node(node)
            
        return calls



    def _method_invocation_to_str(self, node):
        """
        Convert a MethodInvocation node to string representation.
        Enhanced to support method overloading and proper chain call extraction.
        
        :param node: MethodInvocation AST node
        :return: String representation of the method call
        """
        if node.qualifier:
            # Enhanced: Check if qualifier is a method invocation (chain call)
            if isinstance(node.qualifier, javalang.tree.MethodInvocation):
                # For chain calls like a.getB().getC(), use "expr" as placeholder
                # This enables proper sequential resolution in enrichment phase
                qualifier_str = "expr"
            else:
                # For simple qualifiers, use the simple string representation
                qualifier_str = expression_to_simple_str(node.qualifier)
            
            method_name = node.member
            
            # Try to infer argument types for overload resolution
            arg_types = infer_argument_types(node.arguments) if node.arguments else []
            
            if arg_types:
                # Include argument types in the method signature
                arg_signature = ",".join(arg_types)
                return f"{qualifier_str}.{method_name}({arg_signature})"
            else:
                # Fallback to simple method name if we can't infer types
                return f"{qualifier_str}.{method_name}"
        else:
            method_name = node.member
            # Try to infer argument types for overload resolution
            arg_types = infer_argument_types(node.arguments) if node.arguments else []
            
            if arg_types:
                # Include argument types in the method signature
                arg_signature = ",".join(arg_types)
                return f"{method_name}({arg_signature})"
            else:
                # Fallback to simple method name if we can't infer types
                return method_name

    def _class_creator_to_str(self, node):
        """
        Convert a ClassCreator node to string representation.
        Enhanced to support constructor overloading by including argument types.
        
        :param node: ClassCreator AST node
        :return: String representation of the constructor call
        """
        class_name = node.type.name
        
        # Try to infer argument types for constructor overload resolution
        arg_types = infer_argument_types(node.arguments) if node.arguments else []
        
        if arg_types:
            # Include argument types in the constructor signature
            arg_signature = ",".join(arg_types)
            return f"new {class_name}({arg_signature})"
        else:
            # Fallback to simple constructor name if we can't infer types
            return f"new {class_name}"



    def _extract_assignments(self, nodes):
        """Extract variable assignments from method/class body"""
        store_vars_calls = {}
        for node in nodes:
            if isinstance(node, javalang.tree.LocalVariableDeclaration):
                for declarator in node.declarators:
                    if declarator.initializer and is_method_or_constructor_call(declarator.initializer):
                        store_vars_calls[declarator.name] = method_call_to_str(declarator.initializer)
            elif isinstance(node, javalang.tree.FieldDeclaration):
                for declarator in node.declarators:
                    if declarator.initializer and is_method_or_constructor_call(declarator.initializer):
                        store_vars_calls[declarator.name] = method_call_to_str(declarator.initializer)
            elif isinstance(node, javalang.tree.StatementExpression):
                if isinstance(node.expression, javalang.tree.Assignment):
                    if is_method_or_constructor_call(node.expression.value):
                        target_name = expression_to_str(node.expression.expressionl)
                        store_vars_calls[target_name] = method_call_to_str(node.expression.value)
            elif hasattr(node, 'body') and node.body:
                # Recursively check blocks
                nested_assignments = self._extract_assignments(node.body)
                store_vars_calls.update(nested_assignments)
        return store_vars_calls

    def inspect_interface_methods(self, interface_node):
        methods_info = {}
        
        for method in interface_node.methods:
            method_info = {
                "name": method.name,
                "modifiers": list(method.modifiers),
                "return_type": get_type_name(method.return_type) if method.return_type else None,
                "parameters": [{
                    "name": param.name,
                    "type": get_type_name(param.type)
                } for param in method.parameters],
                "min_max_lineno": compute_interval(method),
                "doc": self.extract_javadoc(method),
                "calls": self._extract_method_calls(method.body if method.body else [])
            }
            
            # Add AST and source code extraction for interface methods
            if self.abstract_syntax_tree:
                method_info["ast"] = ast_to_json(method)
            if self.source_code:
                method_info["source_code"] = ast_to_source_code(method, self.source_lines)
            
            methods_info[method.name] = method_info
            
        return methods_info


    def inspect_fields(self, class_node):
        fields_info = {}
        
        for field in class_node.fields:
            for declarator in field.declarators:
                field_info = {
                    "name": declarator.name,
                    "type": get_type_name(field.type),
                    "modifiers": list(field.modifiers),
                    "doc": self.extract_javadoc(field)
                }
                
                # Add field annotations
                annotations = extract_annotations(field)
                if annotations:
                    field_info["annotations"] = annotations
                    
                fields_info[declarator.name] = field_info
                
        return fields_info

    
    def _inspect_main(self):
        """
        Method for checking if the Java file contains a main method,
        which is the entry point for Java applications.
        
        :return main_info: dictionary with information about the main method
        """
        main_info = {
            "main_flag": 0,
            "main_class": "",
            "main_method": "",
            "type": "unknown"  # Initialize type 
        }

        for class_name, class_info in self.classes_info.items():
            for method_key, method_info in class_info['methods'].items():
                if is_main_method(method_key, method_info):
                    main_info["main_flag"] = 1
                    main_info["main_class"] = class_name
                    main_info["main_method"] = method_info["name"]  # Use actual name, not key
                    main_info["type"] = "application"
                    # If package is defined, prepend it to the class name
                    if self.package_info and "name" in self.package_info:
                        main_info["fully_qualified_name"] = f"{self.package_info['name']}.{class_name}"
                    else:
                        main_info["fully_qualified_name"] = class_name
                    break  # Found main method, no need to continue
            
            # If main method found, break out of class loop too
            if main_info["main_flag"] == 1:
                break
        
        return main_info



    def create_file_json(self):
        """
        Create and write the JSON output for the file analysis.
        Only include non-empty fields in the output.
        """
        file_name = Path(self.path).name
        
        # Build the base file info
        file_info = {
            "file": {
                "path": str(Path(self.path).absolute()),
                "fileNameBase": file_name.split('.')[0],
                "extension": file_name.split('.')[-1]
            }
        }
        
        # Only add fields that have content
        if self.package_info:
            file_info["package"] = self.package_info
            
        if self.import_info:
            file_info["dependencies"] = self.import_info
            
        if self.classes_info:
            file_info["classes"] = self.classes_info
            
        if self.interfaces_info:
            file_info["interfaces"] = self.interfaces_info
            
        if hasattr(self, 'enums_info') and self.enums_info:
            file_info["enums"] = self.enums_info
            
        # Only add main_info if a main method was found
        if self.main_info and self.main_info.get("main_flag") == 1:
            file_info["main_info"] = self.main_info
            
        # Clean any remaining empty fields recursively
        file_info = clean_empty_fields(file_info)
        
        # Write to JSON file
        json_file = os.path.join(self.json_dir, f"{file_info['file']['fileNameBase']}.json")
        with open(json_file, 'w', encoding='utf-8') as outfile:
            json.dump(file_info, outfile, indent=2)
            
        return [file_info, json_file]

    def inspect_nested_structures(self, parent_node):
        """
        Inspect and extract nested classes and interfaces within a class or interface.
        
        :param parent_node: The parent class or interface node
        :return: Dictionary containing nested structures found
        """
        nested_info = {}
        
        # Extract nested classes (both static and inner)
        nested_classes = self._extract_nested_classes(parent_node)
        if nested_classes:
            nested_info["nested_classes"] = nested_classes
            
        # Extract nested interfaces
        nested_interfaces = self._extract_nested_interfaces(parent_node)
        if nested_interfaces:
            nested_info["nested_interfaces"] = nested_interfaces
            
        return nested_info

    def _extract_nested_classes(self, parent_node):
        """Extract nested classes from a parent class or interface"""
        nested_classes = {}
        
        # Get all class declarations within the parent
        for child in parent_node.body:
            if isinstance(child, javalang.tree.ClassDeclaration):
                # Determine if static or inner class based on modifiers
                is_static = "static" in child.modifiers
                nesting_type = "static_nested" if is_static else "inner"
                
                class_info = {
                    "name": child.name,
                    "modifiers": list(child.modifiers),
                    "extends": child.extends.name if child.extends else None,
                    "implements": [i.name for i in child.implements] if child.implements else [],
                    "min_max_lineno": compute_interval(child),
                    "doc": self.extract_javadoc(child),
                    "methods": self.inspect_methods(child),
                    "fields": self.inspect_fields(child),
                    "nested_type": nesting_type,
                    "outer_context": {
                        "type": "class" if isinstance(parent_node, javalang.tree.ClassDeclaration) else "interface",
                        "name": parent_node.name
                    }
                }
                
                # Recursively extract nested structures within this nested class
                nested_structures = self.inspect_nested_structures(child)
                if nested_structures:
                    class_info.update(nested_structures)
                
                nested_classes[child.name] = class_info
                
        return nested_classes

    def _extract_nested_interfaces(self, parent_node):
        """Extract nested interfaces from a parent class or interface"""
        nested_interfaces = {}
        
        for child in parent_node.body:
            if isinstance(child, javalang.tree.InterfaceDeclaration):
                interface_info = {
                    "name": child.name,
                    "modifiers": list(child.modifiers),
                    "extends": [e.name for e in child.extends] if child.extends else [],
                    "min_max_lineno": compute_interval(child),
                    "doc": self.extract_javadoc(child),
                    "methods": self.inspect_interface_methods(child),
                    "fields": self.inspect_fields(child),
                    "outer_context": {
                        "type": "class" if isinstance(parent_node, javalang.tree.ClassDeclaration) else "interface",
                        "name": parent_node.name
                    }
                }
                
                # Recursively extract nested structures within this nested interface
                nested_structures = self.inspect_nested_structures(child)
                if nested_structures:
                    interface_info.update(nested_structures)
                
                nested_interfaces[child.name] = interface_info
                
        return nested_interfaces

    def _extract_calls_from_single_node(self, node, calls_list):
        """
        Helper method to extract calls from a single node and add them to a list.
        This is used for field initializers and other single expression contexts.
        
        :param node: AST node to extract calls from
        :param calls_list: List to append found calls to
        """
        if node is None:
            return
            
        # Handle method invocations
        if isinstance(node, javalang.tree.MethodInvocation):
            call_str = self._method_invocation_to_str(node)
            if call_str and call_str not in calls_list:
                calls_list.append(call_str)
            # Recursively process qualifier and arguments
            if node.qualifier:
                self._extract_calls_from_single_node(node.qualifier, calls_list)
            if node.arguments:
                for arg in node.arguments:
                    self._extract_calls_from_single_node(arg, calls_list)
                    
        # Handle super method invocations
        elif isinstance(node, javalang.tree.SuperMethodInvocation):
            # Enhanced to include argument types for overload resolution
            method_name = node.member
            arg_types = infer_argument_types(node.arguments) if node.arguments else []
            
            if arg_types:
                # Include argument types in the method signature
                arg_signature = ",".join(arg_types)
                call_str = f"super.{method_name}({arg_signature})"
            else:
                # Fallback to simple method name if we can't infer types
                call_str = f"super.{method_name}"
                
            if call_str and call_str not in calls_list:
                calls_list.append(call_str)
            # Process arguments
            if node.arguments:
                for arg in node.arguments:
                    self._extract_calls_from_single_node(arg, calls_list)
                    
        # Handle super constructor calls
        elif isinstance(node, javalang.tree.SuperConstructorInvocation):
            call_str = "super"
            if call_str and call_str not in calls_list:
                calls_list.append(call_str)
            # Process arguments
            if node.arguments:
                for arg in node.arguments:
                    self._extract_calls_from_single_node(arg, calls_list)
                    
        # Handle constructor calls (new expressions)
        elif isinstance(node, javalang.tree.ClassCreator):
            call_str = self._class_creator_to_str(node)
            if call_str and call_str not in calls_list:
                calls_list.append(call_str)
            # Recursively process arguments
            if node.arguments:
                for arg in node.arguments:
                    self._extract_calls_from_single_node(arg, calls_list)
                    
        # Handle This expressions with selectors (e.g., this.field.add())
        elif isinstance(node, javalang.tree.This):
            if hasattr(node, 'selectors') and node.selectors:
                # Process selectors to find method calls
                                    self._extract_this_selector_calls(node, calls)
                        
            # Handle other expressions that might contain calls
            elif hasattr(node, '__dict__'):
                # Generic traversal for other node types
                for attr_name, attr_value in vars(node).items():
                    if attr_name.startswith('_'):
                        continue
                    if isinstance(attr_value, list):
                        for item in attr_value:
                            if hasattr(item, '__class__') and 'javalang' in str(item.__class__):
                                self._extract_calls_from_single_node(item, calls_list)
                    elif hasattr(attr_value, '__class__') and 'javalang' in str(attr_value.__class__):
                        self._extract_calls_from_single_node(attr_value, calls_list)

    def _enrich_all_method_calls(self):
        """
        Enrich method calls for all classes, interfaces, and enums after 
        all information has been collected. This is a post-processing step.
        """
        # Enrich calls in classes
        for class_name, class_info in self.classes_info.items():
            # Enrich method calls
            if "methods" in class_info:
                for method_key, method_info in class_info["methods"].items():
                    if "calls" in method_info:
                        # Get the actual method AST node for context
                        method_node = self._find_method_node_by_name(class_name, method_info.get("name"))
                        method_info["calls"] = self._enrich_method_calls(
                            method_info["calls"], class_name, method_node
                        )
                    
                    # Also enrich store_vars_calls
                    if "store_vars_calls" in method_info:
                        method_info["store_vars_calls"] = self._enrich_store_vars_calls(
                            method_info["store_vars_calls"], class_name, method_info.get("name")
                        )
            
            # Enrich class-level calls (field initializations)
            if "calls" in class_info:
                class_info["calls"] = self._enrich_method_calls(
                    class_info["calls"], class_name
                )
        
        # Enrich calls in interfaces
        for interface_name, interface_info in self.interfaces_info.items():
            if "methods" in interface_info:
                for method_key, method_info in interface_info["methods"].items():
                    if "calls" in method_info:
                        method_info["calls"] = self._enrich_method_calls(
                            method_info["calls"], interface_name
                        )
        
        # Enrich calls in enums if any
        if hasattr(self, 'enums_info'):
            for enum_name, enum_info in self.enums_info.items():
                if "methods" in enum_info:
                    for method_key, method_info in enum_info["methods"].items():
                        if "calls" in method_info:
                            method_info["calls"] = self._enrich_method_calls(
                                method_info["calls"], enum_name
                            )

    def _enrich_method_calls(self, raw_calls, current_class_name="", method_context=None):
        """
        Enrich method calls by resolving names to their full qualified names.
        Enhanced with precise sequential type tracking for chained calls.
        This replaces the previous heuristic-based chain expansion.
        
        :param raw_calls: List of raw method call strings from _extract_method_calls
        :param current_class_name: Name of the current class (for resolving 'this' references)
        :param method_context: Additional context about the method for variable resolution
        :return: List of enriched method call strings
        """
        enriched_calls = []
        
        # Build variable context for this method if method_context is provided
        variable_context = None
        if method_context and hasattr(method_context, 'body'):
            variable_context = self._build_variable_context(method_context.body, current_class_name)
        
        # Enhanced: Track expression types throughout the call sequence
        # This maintains a mapping of expr -> actual_type for precise chain resolution
        expression_type_tracker = {}
        
        for call in raw_calls:
            # First resolve the call normally
            enriched_call = self._unified_resolve_call_name(call, current_class_name, method_context, variable_context)
            
            # Update expression type tracker with resolved information
            self._update_expression_tracker(call, enriched_call, expression_type_tracker, variable_context)
            
            # Enhanced: Use tracker to resolve expr.method calls precisely
            if call.startswith("expr."):
                # Try to find the precise type for this expr call
                precise_call = self._resolve_expr_with_tracker(call, expression_type_tracker, current_class_name)
                if precise_call:
                    enriched_call = precise_call
            
            # Filter out None values - if resolution fails, keep original call
            if enriched_call is not None:
                enriched_calls.append(enriched_call)
            else:
                # If resolution fails, keep the original call as fallback
                enriched_calls.append(call)
        
        return enriched_calls

    def _update_expression_tracker(self, original_call, resolved_call, tracker, variable_context):
        """
        Update the expression type tracker with information from resolved calls.
        This maintains precise type information for subsequent expr.method resolution.
        
        :param original_call: The original call string
        :param resolved_call: The resolved call string 
        :param tracker: The expression type tracker dictionary
        :param variable_context: Variable type mappings
        """
        if not resolved_call or not original_call:
            return
            
        # Extract return type information from resolved calls
        # Pattern: modulename.ClassName.methodName -> need to find return type
        if "." in resolved_call and not resolved_call.startswith("new "):
            parts = resolved_call.split(".")
            if len(parts) >= 3:  # modulename.ClassName.methodName
                class_name = parts[-2]  # ClassName
                method_name = parts[-1]  # methodName
                
                # Look up the return type in our class information
                return_type = self._get_method_return_type(class_name, method_name)
                if return_type:
                    # Store this type information for subsequent expr resolution
                    # Key: position-based identifier for this expression result
                    expr_key = f"expr_{len(tracker)}"
                    tracker[expr_key] = {
                        "type": return_type,
                        "source_call": original_call,
                        "resolved_call": resolved_call
                    }
        
        # Handle constructor calls - they return the constructed type
        elif resolved_call.startswith("new "):
            constructor_info = resolved_call[4:]  # Remove "new "
            if "." in constructor_info:
                # Extract class name from "modulename.ClassName" or "modulename.ClassName(args)"
                if "(" in constructor_info:
                    full_class_path = constructor_info[:constructor_info.index("(")]
                else:
                    full_class_path = constructor_info
                    
                class_name = full_class_path.split(".")[-1]  # Get just the class name
                
                # Store constructor result type
                expr_key = f"expr_{len(tracker)}"
                tracker[expr_key] = {
                    "type": class_name,
                    "source_call": original_call,
                    "resolved_call": resolved_call
                }

    def _resolve_expr_with_tracker(self, expr_call, tracker, current_class_name):
        """
        Resolve expr.method calls using precise type information from the tracker.
        Enhanced to handle sequential chain resolution by matching call patterns.
        
        :param expr_call: The expr.method call to resolve
        :param tracker: Expression type tracker with precise type information
        :param current_class_name: Current class context
        :return: Precisely resolved call or None
        """
        if not expr_call.startswith("expr."):
            return None
            
        method_part = expr_call[5:]  # Remove "expr."
        
        # Enhanced strategy: Find the most recent expression that has the required method
        # The key insight is that in a chain a.getB().getC().doSomething(),
        # the extraction phase generates calls in this order:
        # 1. a.getB (generates tracker entry with type B)
        # 2. expr.getC (should use type B)
        # 3. expr.doSomething (should use type C from getC's return)
        
        # Sort tracker entries by creation order (most recent first for matching)
        sorted_entries = sorted(tracker.items(), key=lambda x: int(x[0].split('_')[1]), reverse=True)
        
        for expr_key, type_info in sorted_entries:
            expr_type = type_info["type"]
            
            # Check if this type has the method we're looking for
            if self._type_has_method(expr_type, method_part, current_class_name):
                file_base = self._get_file_base()
                
                # Create the resolved call
                if "(" in method_part and method_part.endswith(")"):
                    resolved_call = f"{file_base}.{expr_type}.{method_part}"
                else:
                    resolved_call = f"{file_base}.{expr_type}.{method_part}"
                
                # CRITICAL: Update tracker with the return type of this resolved call
                # This enables the next expr.method call to use the correct type
                method_name = method_part.split("(")[0] if "(" in method_part else method_part
                return_type = self._get_method_return_type(expr_type, method_name)
                
                if return_type:
                    # Add new tracker entry for this resolved call's return type
                    new_expr_key = f"expr_{len(tracker)}"
                    tracker[new_expr_key] = {
                        "type": return_type,
                        "source_call": expr_call,
                        "resolved_call": resolved_call
                    }
                
                return resolved_call
        
        # Fallback to original expr resolution if no precise type found
        return self._resolve_expr_call_unified(method_part, current_class_name, None, None)

    def _get_method_return_type(self, class_name, method_name):
        """
        Get the return type of a method from our class information.
        Enhanced to handle method signatures with parameter types.
        
        :param class_name: Name of the class containing the method
        :param method_name: Name of the method (may include parameter signature)
        :return: Return type or None if not found
        """
        # Parse method name from potential parameter signature
        base_method_name, _ = parse_method_signature(method_name)
        
        # Check in current file's classes
        if class_name in self.classes_info:
            methods = self.classes_info[class_name].get("methods", {})
            
            # Try exact match first
            if method_name in methods:
                return methods[method_name].get("return_type")
            
            # Try base method name match
            for method_key, method_info in methods.items():
                if method_info.get("name") == base_method_name:
                    return method_info.get("return_type")
        
        # Check in interfaces
        if hasattr(self, 'interfaces_info') and class_name in self.interfaces_info:
            methods = self.interfaces_info[class_name].get("methods", {})
            
            # Try exact match first
            if method_name in methods:
                return methods[method_name].get("return_type")
            
            # Try base method name match
            for method_key, method_info in methods.items():
                if method_info.get("name") == base_method_name:
                    return method_info.get("return_type")
        
        return None

    def _type_has_method(self, type_name, method_name, current_class_name):
        """
        Check if a given type has a specific method.
        Enhanced to handle method signatures and inheritance.
        
        :param type_name: Name of the type to check
        :param method_name: Name of the method to look for (may include signature)
        :param current_class_name: Current class context
        :return: True if type has the method
        """
        # Parse method name from potential parameter signature
        base_method_name, _ = parse_method_signature(method_name)
        
        # Check in classes
        if type_name in self.classes_info:
            methods = self.classes_info[type_name].get("methods", {})
            
            # Check exact match
            if method_name in methods:
                return True
                
            # Check base method name
            for method_key, method_info in methods.items():
                if method_info.get("name") == base_method_name:
                    return True
            
            # Check inheritance hierarchy
            resolved = resolve_inheritance_method_call(method_name, type_name, self.classes_info, self.interfaces_info)
            if resolved:
                return True
        
        # Check in interfaces
        if hasattr(self, 'interfaces_info') and type_name in self.interfaces_info:
            methods = self.interfaces_info[type_name].get("methods", {})
            
            # Check exact match
            if method_name in methods:
                return True
                
            # Check base method name
            for method_key, method_info in methods.items():
                if method_info.get("name") == base_method_name:
                    return True
        
        return False

    def _resolve_expr_call_unified(self, method_name, current_class_name, method_context=None, variable_context=None):
        """
        Unified resolution for 'expr.method' calls with enhanced context awareness.
        
        :param method_name: The method being called
        :param current_class_name: Current class context
        :param method_context: Additional method context for variable resolution
        :param variable_context: Variable type mappings
        :return: Best guess for the resolved call
        """
        
        # 1. Check if this is a String method on a literal or String variable
        if is_string_method(method_name):
            # Try to determine if we're calling on a String
            if variable_context:
                # Look for String variables in context
                for var_name, var_type in variable_context.items():
                    if var_type == "String":
                        return f"String.{method_name}"
        
            # Default to String for common String methods
            fields_info = self.classes_info.get(current_class_name, {}).get("fields", {}) if current_class_name in self.classes_info else {}
            if has_string_field(fields_info) or method_name in {
                'charAt', 'length', 'substring', 'toLowerCase', 'toUpperCase',
                'trim', 'replace', 'replaceAll', 'split', 'indexOf', 'lastIndexOf',
                'startsWith', 'endsWith', 'contains', 'equals', 'equalsIgnoreCase'
            }:
                return f"String.{method_name}"
    
        # 2. Check if this is a static method call in any class within the file
        static_method_class = self._find_static_method_in_file(method_name)
        if static_method_class:
            return f"{self._get_file_base()}.{static_method_class}.{method_name}"
    
        # 3. Check if this is an instance method in the current class
        if self._is_instance_method_in_class(method_name, current_class_name):
            file_base = self._get_file_base()
            return f"{file_base}.{current_class_name}.{method_name}"
        
        # 4. Check if this is a method on a field of collection type
        if current_class_name and current_class_name in self.classes_info:
            fields_info = self.classes_info[current_class_name].get("fields", {})
            collection_type = find_collection_field_for_method(method_name, fields_info)
        else:
            collection_type = None
        if collection_type:
            return f"{collection_type}.{method_name}"
    
        # 5. Check standard Java library patterns
        stdlib_resolution = resolve_standard_library_method(method_name)
        if stdlib_resolution:
            return stdlib_resolution
    
        # 6. If we can't resolve it, keep as expr.method
        return f"expr.{method_name}"

    def _find_static_method_in_file(self, method_name):
        """
        Find if the method name exists as a static method in any class in the current file.
        
        :param method_name: Method name to search for
        :return: Class name containing the static method, or None
        """
        for class_name, class_info in self.classes_info.items():
            methods = class_info.get("methods", {})
            for method_key, method_info in methods.items():
                if (method_info.get("name") == method_name and 
                    "static" in method_info.get("modifiers", [])):
                    return class_name
        return None
    
    def _is_instance_method_in_class(self, method_name, class_name):
        """
        Check if the method exists as an instance method in the given class.
        
        :param method_name: Method name to check
        :param class_name: Class name to check in
        :return: True if method exists as instance method
        """
        if not class_name or class_name not in self.classes_info:
            return False
            
        methods = self.classes_info[class_name].get("methods", {})
        for method_key, method_info in methods.items():
            if (method_info.get("name") == method_name and 
                "static" not in method_info.get("modifiers", [])):
                return True
        return False

    def _resolve_this_field_call(self, method_path, current_class_name):
        """
        Resolve this.field.method calls by analyzing field types.
        
        :param method_path: The method path (e.g., "field.add")
        :param current_class_name: Current class name
        :return: Resolved call name
        """
        parts = method_path.split(".", 1)
        field_name = parts[0]
        method_name = parts[1] if len(parts) > 1 else ""
        
        if current_class_name in self.classes_info:
            fields = self.classes_info[current_class_name].get("fields", {})
            
            if field_name in fields:
                field_type = fields[field_name].get("type", "")
                
                # Handle collection types
                if field_type in ["List", "ArrayList", "Set", "Collection"]:
                    return f"{field_type}.{method_name}"
                    
                # Handle other known types
                elif field_type == "String":
                    return f"String.{method_name}"
                    
                # For unknown types, use the type name
                else:
                    return f"{field_type}.{method_name}"
            else:
                # Field not found, use generic resolution
                return f"field.{method_name}"
        
        # Fallback
        return f"this.{method_path}"

    def _resolve_super_call_clean(self, method_name, current_class_name):
        """
        Enhanced super call resolution with cross-file import support.
        Now checks if parent class is imported from another file.
        
        :param method_name: Method being called on super
        :param current_class_name: Current class name
        :return: Resolved super call
        """
        file_base = self._get_file_base()
        
        # Use the new inheritance resolution function to find the actual method location
        resolved = resolve_super_method_call(method_name, current_class_name, self.classes_info)
        
        if resolved:
            # Return with file base prefix for consistency
            return f"{file_base}.{resolved}"
        
        # Enhanced: Check if parent class is imported from another file
        if current_class_name in self.classes_info:
            extends = self.classes_info[current_class_name].get("extends")
            if extends:
                # Check if parent class is imported
                if hasattr(self, 'import_mapping') and extends in self.import_mapping:
                    from_module = self.import_mapping[extends]
                    return f"{from_module}.{extends}.{method_name}"
                else:
                    # Return parent class method with file base prefix
                    return f"{file_base}.{extends}.{method_name}"
        
        # Last fallback - return with generic super prefix if no extends found
        return f"super.{method_name}"

    def _resolve_static_call_clean(self, class_name, method_name):
        """
        Enhanced static call resolution with import mapping support.
        
        :param class_name: Class name
        :param method_name: Static method name
        :return: Resolved static call
        """
        file_base = self._get_file_base()
        
        # Check if it's a class in the current file - use consistent format with file base prefix
        if class_name in self.classes_info:
            return f"{file_base}.{class_name}.{method_name}"
        
        # Enhanced: Use import mapping for faster lookup
        if hasattr(self, 'import_mapping') and class_name in self.import_mapping:
            from_module = self.import_mapping[class_name]
            return f"{from_module}.{class_name}.{method_name}"
        
        # Fallback: Check import_info directly
        for dep in self.import_info:
            if dep["import"] == class_name:
                if dep.get("from_module"):
                    return f"{dep['from_module']}.{class_name}.{method_name}"
                else:
                    return f"{class_name}.{method_name}"
        
        # If not found, assume it's external - just use class name
        return f"{class_name}.{method_name}"

    def _resolve_interface_method_with_imports(self, method_name, current_class_name):
        """
        Check if method comes from imported interface.
        Enhanced to support cross-file interface resolution.
        
        :param method_name: Method name to resolve
        :param current_class_name: Current class name
        :return: Resolved interface method call or None
        """
        if current_class_name not in self.classes_info:
            return None
            
        implements = self.classes_info[current_class_name].get("implements", [])
        
        for interface_name in implements:
            # Check if interface is imported from another file
            if hasattr(self, 'import_mapping') and interface_name in self.import_mapping:
                from_module = self.import_mapping[interface_name]
                return f"{from_module}.{interface_name}.{method_name}"
            
            # Check if interface is in current file
            elif interface_name in self.interfaces_info:
                file_base = self._get_file_base()
                return f"{file_base}.{interface_name}.{method_name}"
        
        return None

    def _resolve_parent_method_with_imports(self, method_name, current_class_name):
        """
        Check if method comes from imported parent class (cross-file inheritance).
        
        :param method_name: Method name to resolve
        :param current_class_name: Current class name
        :return: Resolved parent method call or None
        """
        if current_class_name not in self.classes_info:
            return None
            
        extends = self.classes_info[current_class_name].get("extends")
        if not extends:
            return None
        
        # Check if parent class is imported from another file
        if hasattr(self, 'import_mapping') and extends in self.import_mapping:
            from_module = self.import_mapping[extends]
            return f"{from_module}.{extends}.{method_name}"
        
        return None

    def _method_exists_in_class(self, method_name, class_name):
        """
        Check if a method exists in the specified class.
        
        :param method_name: Method name to check
        :param class_name: Class name to check in
        :return: True if method exists in class
        """
        if class_name not in self.classes_info:
            return False
            
        methods = self.classes_info[class_name].get("methods", {})
        
        # Check if method name exists in any of the method keys or names
        for method_key, method_info in methods.items():
            if method_info.get("name") == method_name:
                return True
        
        return False

    def _get_file_base(self):
        """Get the file base name for internal reference resolution."""
        return Path(self.path).stem

    def _extract_this_selector_calls(self, this_node, calls_list):
        """
        Extract method calls from This expression selectors.
        
        For expressions like this.field.add("init"), the This node has selectors:
        - MemberReference(member=field)  
        - MethodInvocation(member=add)
        
        :param this_node: This AST node
        :param calls_list: List to append found calls to
        """
        if not hasattr(this_node, 'selectors') or not this_node.selectors:
            return
            
        # Build the selector chain to construct the full call
        selector_chain = []
        
        for selector in this_node.selectors:
            if isinstance(selector, javalang.tree.MemberReference):
                selector_chain.append(selector.member)
            elif isinstance(selector, javalang.tree.MethodInvocation):
                # This is the actual method call
                method_name = selector.member
                
                # Try to infer argument types for overload resolution
                arg_types = infer_argument_types(selector.arguments) if selector.arguments else []
                
                if selector_chain:
                    # We have a chain like this.field.add
                    if arg_types:
                        arg_signature = ",".join(arg_types)
                        full_call = f"this.{'.'.join(selector_chain)}.{method_name}({arg_signature})"
                    else:
                        full_call = f"this.{'.'.join(selector_chain)}.{method_name}"
                else:
                    # Direct method call like this.method()
                    if arg_types:
                        arg_signature = ",".join(arg_types)
                        full_call = f"this.{method_name}({arg_signature})"
                    else:
                        full_call = f"this.{method_name}"
                
                if full_call not in calls_list:
                    calls_list.append(full_call)
                
                # Process method arguments recursively
                if selector.arguments:
                    for arg in selector.arguments:
                        self._extract_calls_from_single_node(arg, calls_list)
                        
                # Reset chain after method call
                selector_chain = []

    def _find_method_node_by_name(self, class_name, method_name):
        """
        Find the AST node for a method by its name within a class.
        
        :param class_name: Name of the class
        :param method_name: Name of the method to find
        :return: Method AST node or None if not found
        """
        if not self.tree or not self.tree.types:
            return None
            
        for type_decl in self.tree.types:
            if isinstance(type_decl, javalang.tree.ClassDeclaration) and type_decl.name == class_name:
                # Check constructors
                for constructor in type_decl.constructors:
                    if constructor.name == method_name:
                        return constructor
                        
                # Check methods
                for method in type_decl.methods:
                    if method.name == method_name:
                        return method
                        
        return None

    def _enrich_store_vars_calls(self, store_vars_calls, current_class_name, method_name):
        """
        Enrich store_vars_calls dictionary by resolving variable assignment call names.
        
        :param store_vars_calls: Dictionary of variable assignments
        :param current_class_name: Current class context
        :param method_name: Current method name for context
        :return: Enriched store_vars_calls dictionary
        """
        enriched_store_vars = {}
        
        # Get method node for context
        method_node = self._find_method_node_by_name(current_class_name, method_name)
        variable_context = None
        if method_node and hasattr(method_node, 'body'):
            variable_context = self._build_variable_context(method_node.body, current_class_name)
        
        for var_name, call_value in store_vars_calls.items():
            # Use unified resolution for consistency
            enriched_call = self._unified_resolve_call_name(
                call_value, current_class_name, method_node, variable_context
            )
            enriched_store_vars[var_name] = enriched_call
            
        return enriched_store_vars

    def _resolve_constructor_call(self, class_name):
        """
        Resolve constructor calls (new ClassName).
        Enhanced to support constructor overloading with parameter signatures.
        
        :param class_name: The class being instantiated (might include parameter signature)
        :return: Resolved constructor call
        """
        # Parse class name and parameter signature
        if "(" in class_name and class_name.endswith(")"):
            open_paren = class_name.index("(")
            base_class_name = class_name[:open_paren]
            param_signature = class_name[open_paren:]  # Keep the (parameters) part
        else:
            base_class_name = class_name
            param_signature = ""
        
        file_base = self._get_file_base()
        
        # Check if it's a known internal class - add file base prefix for consistency
        if base_class_name in self.classes_info:
            return f"new {file_base}.{base_class_name}{param_signature}"
        
        # Check if it's an imported class
        for dep in self.import_info:
            if dep["import"] == base_class_name:
                if dep.get("from_module"):
                    return f"new {dep['from_module']}.{base_class_name}{param_signature}"
                else:
                    return f"new {base_class_name}{param_signature}"
        
        # If not found, return as-is (might be from default package or java.lang)
        return f"new {base_class_name}{param_signature}"

    def _unified_resolve_call_name(self, call_name, current_class_name="", method_context=None, variable_context=None):
        """
        Unified method to resolve call names with proper variable context tracking.
        Enhanced to support chained method calls with better type resolution.
        This method handles both direct calls and store_vars_calls consistently.
        
        :param call_name: Raw call name to resolve
        :param current_class_name: Current class context
        :param method_context: Method-specific context
        :param variable_context: Dictionary of variable name -> type mappings from current scope
        :return: Resolved call name
        """
        # Handle constructor calls (new ClassName)
        if call_name.startswith("new "):
            class_name = call_name[4:]  # Remove "new " prefix
            return self._resolve_constructor_call(class_name)
        
        # Handle qualified calls (object.method)
        if "." in call_name:
            return self._resolve_qualified_call_unified(call_name, current_class_name, method_context, variable_context)
        
        # Handle unqualified calls (methodName)
        else:
            return self._resolve_unqualified_call_unified(call_name, current_class_name)

    def _resolve_qualified_call_unified(self, call_name, current_class_name, method_context=None, variable_context=None):
        """
        Unified resolution for qualified method calls with improved context handling.
        Enhanced to support chained method calls with proper type resolution.
        
        :param call_name: Qualified call name (e.g., "expr.println", "this.method", "a.getB")
        :param current_class_name: Current class context
        :param method_context: Additional method context for variable resolution
        :param variable_context: Variable type mappings
        :return: Resolved call name
        """
        parts = call_name.split(".", 1)
        qualifier = parts[0]
        method_name = parts[1]
        
        # Handle 'expr' placeholder - try to resolve based on context
        if qualifier == "expr":
            return self._resolve_expr_call_unified(method_name, current_class_name, method_context, variable_context)
        
        # Handle 'this' references - use inheritance resolution like unqualified calls
        elif qualifier == "this" and current_class_name:
            file_base = self._get_file_base()
            # Check if this is a complex this.field.method call
            if "." in method_name:
                # this.field.add -> need to resolve field type
                return self._resolve_this_field_call(method_name, current_class_name)
            else:
                # Simple this.method call - use inheritance resolution to find the correct class
                resolved = resolve_inheritance_method_call(method_name, current_class_name, self.classes_info, self.interfaces_info)
                if resolved:
                    return f"{file_base}.{resolved}"
                
                # Enhanced: Check if method comes from imported interface
                interface_result = self._resolve_interface_method_with_imports(method_name, current_class_name)
                if interface_result:
                    return interface_result
                
                # Enhanced: Check if method comes from imported parent class (cross-file inheritance)
                parent_result = self._resolve_parent_method_with_imports(method_name, current_class_name)
                if parent_result:
                    return parent_result
                
                # Check if method exists in current class before fallback
                if self._method_exists_in_class(method_name, current_class_name):
                    return f"{file_base}.{current_class_name}.{method_name}"
                
                # Last fallback - if method doesn't exist in current class, it might be inherited
                return f"this.{method_name}"
        
        # Handle 'super' references - MOVED BEFORE store_vars_calls to avoid conflicts
        elif qualifier == "super" and current_class_name:
            return self._resolve_super_call_clean(method_name, current_class_name)
        
        # Handle variable references using variable context - ENHANCED with cross-file support
        elif variable_context and qualifier in variable_context:
            variable_type = variable_context[qualifier]
            
            # Check if variable type is imported from another file
            if hasattr(self, 'import_mapping') and variable_type in self.import_mapping:
                from_module = self.import_mapping[variable_type]
                return f"{from_module}.{variable_type}.{method_name}"
            
            # For internal classes, add file base prefix for consistency
            file_base = self._get_file_base()
            if variable_type in self.classes_info:
                return f"{file_base}.{variable_type}.{method_name}"
            else:
                # For external types, use the original resolve_typed_call logic
                import_mapping = getattr(self, 'import_mapping', None)
                return resolve_typed_call(variable_type, method_name, import_mapping)
        
        # Handle store_vars_calls context - ENHANCED
        elif method_context and hasattr(method_context, 'body'):
            # Try to find the variable in method assignments
            store_vars = self._extract_assignments(method_context.body)
            
            if qualifier in store_vars:
                # Get the assigned value and try to resolve its type
                assigned_value = store_vars[qualifier]
                
                # First, enrich the assigned_value if it's a constructor call
                if assigned_value.startswith("new "):
                    enriched_assigned_value = self._unified_resolve_call_name(assigned_value, current_class_name, method_context, variable_context)
                    assigned_value = enriched_assigned_value or assigned_value
                
                if assigned_value.startswith("new "):
                    # Variable assigned from constructor
                    assigned_class = assigned_value[4:]  # Remove "new "
                    if "(" in assigned_class:
                        assigned_class = assigned_class[:assigned_class.index("(")]
                    
                    # Enhanced: Check if assigned class is imported from another file
                    if hasattr(self, 'import_mapping') and assigned_class in self.import_mapping:
                        from_module = self.import_mapping[assigned_class]
                        return f"{from_module}.{assigned_class}.{method_name}"
                    
                    # Handle file base prefix for internal classes
                    file_base = self._get_file_base()
                    if f"{file_base}." in assigned_class:
                        # assigned_class already has file base prefix (e.g., "MethodOverrideTest.ChildClass")
                        return f"{assigned_class}.{method_name}"
                    elif assigned_class in self.classes_info:
                        # assigned_class is just the class name (e.g., "ChildClass")
                        return f"{file_base}.{assigned_class}.{method_name}"
                    else:
                        return f"{assigned_class}.{method_name}"
                else:
                    # Variable assigned from method call - try to resolve the return type
                    return f"expr.{method_name}"  # Fallback
        
        # Handle class static method calls (ClassName.method) - check if it's a known class
        else:
            return self._resolve_static_call_clean(qualifier, method_name)

    def _resolve_unqualified_call_unified(self, call_name, current_class_name):
        """
        Unified resolution for unqualified method calls with improved duplicate handling.
        Enhanced to support method overloading with parameter signatures and inheritance.
        
        :param call_name: Unqualified method name (might include parameter signature)
        :param current_class_name: Current class context
        :return: Resolved call name
        """
        # Extract base method name and parameter signature
        base_method_name, param_signature = parse_method_signature(call_name)
        file_base = self._get_file_base()
        
        # Try inheritance-based resolution first - pass the full call_name for signature matching
        if current_class_name:
            resolved = resolve_inheritance_method_call(call_name, current_class_name, self.classes_info, self.interfaces_info)
            if resolved:
                return f"{file_base}.{resolved}"
            
            # Enhanced: Check if method comes from imported interface
            interface_result = self._resolve_interface_method_with_imports(base_method_name, current_class_name)
            if interface_result:
                return interface_result
        
        # Check if it's a method in the current class (original logic as fallback)
        if current_class_name and current_class_name in self.classes_info:
            class_methods = self.classes_info[current_class_name].get("methods", {})
            
            # First try to find exact match with signature
            if param_signature and call_name in class_methods:
                method_info = class_methods[call_name]
                method_actual_name = method_info.get("name", call_name)
                if method_actual_name == current_class_name:
                    # This is a constructor call - return as-is to avoid duplication
                    return call_name
                else:
                    # This is a regular method call in the same class - add file base prefix
                    return f"{file_base}.{current_class_name}.{call_name}"
            
            # Then try to match base method name
            for method_key, method_info in class_methods.items():
                method_actual_name = method_info.get("name", method_key)
                if method_actual_name == base_method_name:
                    # Check if this is a constructor call
                    if method_actual_name == current_class_name:
                        # This is a constructor call - return as-is to avoid duplication
                        return call_name if param_signature else method_actual_name
                    else:
                        # This is a regular method call in the same class - add file base prefix
                        return f"{file_base}.{current_class_name}.{call_name}"
    
        # Check if it's a static method in any class in this file
        for class_name, class_info in self.classes_info.items():
            methods = class_info.get("methods", {})
            for method_key, method_info in methods.items():
                method_actual_name = method_info.get("name", method_key)
                if (method_actual_name == base_method_name and 
                    "static" in method_info.get("modifiers", [])):
                    return f"{file_base}.{class_name}.{call_name}"
    
        # If not found, keep as-is (might be inherited or external)
        return call_name

    def _build_variable_context(self, method_body, current_class_name=""):
        """
        Build a context map of variable names to their types within a method.
        This helps resolve expr.method calls more accurately.
        
        :param method_body: List of statements in the method body
        :param current_class_name: Current class context for field lookup
        :return: Dictionary mapping variable names to their types
        """
        variable_context = {}
        
        # Add class fields to context
        if current_class_name and current_class_name in self.classes_info:
            fields = self.classes_info[current_class_name].get("fields", {})
            for field_name, field_info in fields.items():
                variable_context[field_name] = field_info.get("type", "Object")
        
        # Process method body to find local variable declarations and assignments
        def extract_variables_from_statements(statements):
            for stmt in statements:
                if isinstance(stmt, javalang.tree.LocalVariableDeclaration):
                    var_type = get_type_name(stmt.type)
                    for declarator in stmt.declarators:
                        variable_context[declarator.name] = var_type
                        
                        # If there's an initializer, try to infer more specific type
                        if declarator.initializer:
                            inferred_type = infer_type_from_initializer(declarator.initializer, self.classes_info, self.import_info)
                            if inferred_type:
                                variable_context[declarator.name] = inferred_type
                
                # Handle assignments that might tell us about variable types
                elif isinstance(stmt, javalang.tree.StatementExpression):
                    if isinstance(stmt.expression, javalang.tree.Assignment):
                        left_expr = stmt.expression.expressionl
                        right_expr = stmt.expression.value
                        
                        # Try to get the variable name from the left side
                        if hasattr(left_expr, 'member'):
                            var_name = left_expr.member
                        elif hasattr(left_expr, 'name'):
                            var_name = left_expr.name
                        else:
                            var_name = None
                            
                        if var_name:
                            inferred_type = infer_type_from_initializer(right_expr, self.classes_info, self.import_info)
                            if inferred_type:
                                variable_context[var_name] = inferred_type
                
                # Recursively process nested statements
                elif hasattr(stmt, 'body') and stmt.body:
                    extract_variables_from_statements(stmt.body)
                elif hasattr(stmt, 'statements') and stmt.statements:
                    extract_variables_from_statements(stmt.statements)
                elif isinstance(stmt, javalang.tree.TryStatement):
                    if stmt.block:
                        extract_variables_from_statements(stmt.block)
                    if stmt.catches:
                        for catch in stmt.catches:
                            if catch.block:
                                extract_variables_from_statements(catch.block)
                elif isinstance(stmt, javalang.tree.SwitchStatement):
                    if stmt.cases:
                        for case in stmt.cases:
                            if case.statements:
                                extract_variables_from_statements(case.statements)
        
        if method_body:
            extract_variables_from_statements(method_body)
        
        return variable_context

@click.command()
@click.option('-i', '--input_path', type=str, required=True, help="input path of the file or directory to inspect.")
@click.option('-o', '--output_dir', type=str, default="output_dir",
              help="output directory path to store results. If the directory does not exist, the tool will create it.")
@click.option('-ignore_dir', '--ignore_dir_pattern', multiple=True, default=[".git", "target", "build", "bin"],
              help="ignore directories starting with a certain pattern. This parameter can be provided multiple times "
                   "to ignore multiple directory patterns.")
@click.option('-ignore_file', '--ignore_file_pattern', multiple=True, default=[".", "_"],
              help="ignore files starting with a certain pattern. This parameter can be provided multiple times "
                   "to ignore multiple file patterns.")
@click.option('-r', '--requirements', type=bool, is_flag=True, help="find the requirements of the repository.")
@click.option('-html', '--html_output', type=bool, is_flag=True,
              help="generates an html file of the DirJson in the output directory.")
@click.option('-cl', '--call_list', type=bool, is_flag=True,
              help="generates the call list in a separate html file.")
@click.option('-dt', '--directory_tree', type=bool, is_flag=True,
              help="captures the file directory tree from the root path of the target repository.")
@click.option('-ast', '--abstract_syntax_tree', type=bool, is_flag=True,
              help="generates abstract syntax tree in json format.")
@click.option('-sc', '--source_code', type=bool, is_flag=True,
              help="generates the source code of each ast node.")
@click.option('-ld', '--license_detection', type=bool, is_flag=True,
              help="detects the license of the target repository.")
@click.option('-rm', '--readme', type=bool, is_flag=True,
              help="extract all readme files in the target repository.")
@click.option('-md', '--metadata', type=bool, is_flag=True, 
              help="extract metadata of the target repository using Github API. (requires repository to have the .git folder)")
def main(input_path, output_dir, ignore_dir_pattern, ignore_file_pattern, requirements, html_output, call_list,
        directory_tree, abstract_syntax_tree, source_code, license_detection, readme, metadata):
    parser = []
    if (not os.path.isfile(input_path)) and (not os.path.isdir(input_path)):
        print('The file or directory specified does not exist')
        return
        
    # Handle single file
    if os.path.isfile(input_path):
        start_time = time.perf_counter()
        json_dir = create_output_dirs(output_dir)
        inspector = JavaInspection(input_path, json_dir, abstract_syntax_tree, source_code, parser)

        call_list_data = call_list_file(inspector)
        if call_list:
            call_file_html = json_dir + "/CallGraph.html"
            pruned_call_list_data = clean_empty_fields(call_list_data)
            generate_output_html(pruned_call_list_data, call_file_html)
            call_json_file = json_dir + "/CallGraph.json"
            with open(call_json_file, 'w') as outfile:
                json.dump(pruned_call_list_data, outfile)

        if html_output:
            output_file_html = json_dir + "/FileInfo.html"
            f = open(inspector.file_json[1])
            data = json.load(f)
            generate_output_html(data, output_file_html)

        if inspector.file_json:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            size = os.path.getsize(inspector.file_json[1])
            print(f"Analysis complete. Results written to: {inspector.file_json[1]}, size: {size} bytes")
            print(f"Analysis took {execution_time:.3f} seconds")
    
    # Handle directory
    else:
        dir_info = {}
        start_time = time.perf_counter()
        
        # Walk through directory
        for subdir, dirs, files in os.walk(input_path):
            # Apply ignore patterns
            for ignore_d in ignore_dir_pattern:
                dirs[:] = [d for d in dirs if not d.startswith(ignore_d)]
            for ignore_f in ignore_file_pattern:
                files[:] = [f for f in files if not f.startswith(ignore_f)]
                
            # Process java files
            for f in files:
                if f.endswith(".java"):
                    try:
                        path = os.path.join(subdir, f)
                        relative_path = Path(subdir).relative_to(Path(input_path).parent)
                        out_dir = str(Path(output_dir) / relative_path)
                        json_dir = create_output_dirs(out_dir)
                        
                        inspector = JavaInspection(path, json_dir, abstract_syntax_tree, source_code, parser)
                        
                        if inspector.file_json:
                            if out_dir not in dir_info:
                                dir_info[out_dir] = [inspector.file_json[0]]
                            else:
                                dir_info[out_dir].append(inspector.file_json[0])
                            
                            # print(f"Processed: {path}")
                    except Exception as e:
                        print(f"Error processing {f}: {str(e)}")
                        continue
        
        # Generate call list for directory
        call_list_data = call_list_dir(dir_info)
        pruned_call_list_data = clean_empty_fields(call_list_data)
        if call_list:
            call_file_html = output_dir + "/call_graph.html"
            generate_output_html(pruned_call_list_data, call_file_html)
            call_json_file = output_dir + "/call_graph.json"
            with open(call_json_file, 'w') as outfile:
                json.dump(pruned_call_list_data, outfile)

        # Add directory-level features
        directory_summary = {}
        
        # Directory tree extraction
        if directory_tree:
            directory_tree_info = extract_directory_tree(input_path, ignore_dir_pattern, ignore_file_pattern, 1)
            directory_summary["directory_tree"] = directory_tree_info
            
        # License detection
        if license_detection:
            try:
                # Use inspect4j's licenses directory
                licenses_path = str(Path(__file__).parent / "licenses")
                if not os.path.exists(licenses_path):
                    print("Warning: License templates not found. Skipping license detection.")
                    print(f"Expected path: {licenses_path}")
                else:
                    license_text = extract_license(input_path)
                    rank_list = detect_license(license_text, licenses_path)
                    directory_summary["license"] = {}
                    directory_summary["license"]["detected_type"] = [{k: f"{v:.1%}"} for k, v in rank_list]
                    directory_summary["license"]["extracted_text"] = license_text
            except Exception as e:
                print(f"Error when detecting license: {str(e)}")
                
        # README files extraction
        if readme:
            directory_summary["readme_files"] = extract_readme(input_path, output_dir)
            
        # GitHub metadata extraction
        if metadata:
            directory_summary["metadata"] = get_github_metadata(input_path)
        
        # Java requirements extraction
        if requirements:
            print("\n=== Extracting Java Requirements ===")
            java_requirements = extract_java_requirements(input_path)
            if java_requirements:
                # Format requirements for display compatibility with inspect4py
                # formatted_requirements = format_java_requirements_for_display(java_requirements)
                # directory_summary["requirements"] = formatted_requirements
                directory_summary["requirements"] = java_requirements  # Keep detailed info
                print(f"Found {len(java_requirements)} dependencies")
                
                # Print summary of found dependencies
                for dep_key, dep_info in java_requirements.items():
                    if isinstance(dep_info, dict):
                        version = dep_info.get("version", "unknown")
                        scope = dep_info.get("scope", "compile")
                        build_tool = dep_info.get("build_tool", "unknown")
                        if scope != "compile":
                            print(f"  {dep_key}: {version} ({scope}) [{build_tool}]")
                        else:
                            print(f"  {dep_key}: {version} [{build_tool}]")
            else:
                print("No Java dependency files found in the project")

        # Merge directory summary with dir_info
        if directory_summary:
            dir_info.update(directory_summary)

        # Create repository summary
        summary_file = os.path.join(output_dir, "directory_info.json")
        with open(summary_file, 'w', encoding='utf-8') as outfile:
            json.dump(dir_info, outfile, indent=2)
            
        if html_output:
            output_file_html = output_dir + "/directory_info.html"
            generate_output_html(dir_info, output_file_html)

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Repository analysis complete. Summary written to: {summary_file}")
        print(f"Total analysis took {execution_time:.3f} seconds")


if __name__ == "__main__":
    main()