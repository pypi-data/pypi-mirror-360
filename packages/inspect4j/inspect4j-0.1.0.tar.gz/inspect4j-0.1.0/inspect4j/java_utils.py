"""
Java Utility Functions for inspect4j

This module contains utility functions for Java code analysis, extracted from the main
JavaInspection class to improve code organization and reusability.

Similar to inspect4py's utils.py structure.
"""

import os
import json
import javalang
import re
import git
import requests
from pathlib import Path
from json2html import *
from .structure_tree import DisplayablePath, get_directory_structure
import xml.etree.ElementTree as ET

def clean_empty_fields(data):
    """
    Recursively remove empty fields from a dictionary.
    This method simplifies the resultant JSON.
    
    :param data: dictionary to clean
    :return: cleaned dictionary with no empty fields
    """
    if isinstance(data, dict):
        return {
            key: value
            for key, value in ((k, clean_empty_fields(v)) for k, v in data.items())
            if value not in (None, "", {}, [], set(), ()) and not (isinstance(value, dict) and not value)
        }
    elif isinstance(data, list):
        return [clean_empty_fields(item) for item in data if item not in (None, "", {}, [], set(), ())]
    return data


def create_output_dirs(output_dir):
    """
    Create output directories for storing JSON files.
    
    :param output_dir: Base output directory path
    :return: JSON directory path
    """
    json_dir = os.path.join(output_dir, "json_files")
    if not os.path.exists(json_dir):
        print(f"Creating JSON directory: {json_dir}")
        os.makedirs(json_dir)
    return json_dir


def get_type_name(type_node):
    """
    Extract type name from a Java AST type node.
    
    :param type_node: javalang type node
    :return: String representation of the type
    """
    if type_node is None:
        return None
    if hasattr(type_node, 'name'):
        # Handle array types
        if hasattr(type_node, 'dimensions') and type_node.dimensions:
            return type_node.name + '[]' * len(type_node.dimensions)
        return type_node.name
    elif hasattr(type_node, 'value'):
        return type_node.value
    # For more complex types, convert to string and check for arrays
    type_str = str(type_node)
    if 'ReferenceType' in type_str and 'dimensions=' in type_str:
        # Extract the type name and add [] for each dimension
        if hasattr(type_node, 'name') and hasattr(type_node, 'dimensions'):
            return type_node.name + '[]' * len(type_node.dimensions)
    return str(type_node)


def is_method_or_constructor_call(node):
    """
    Check if a node represents a method call or constructor call.
    
    :param node: javalang AST node
    :return: True if node is a method/constructor call
    """
    if isinstance(node, (javalang.tree.MethodInvocation, javalang.tree.ClassCreator)):
        return True
    # Check for literals with method selectors (e.g., "test".toUpperCase())
    elif isinstance(node, javalang.tree.Literal) and hasattr(node, 'selectors') and node.selectors:
        return any(isinstance(selector, javalang.tree.MethodInvocation) for selector in node.selectors)
    return False


def method_call_to_str(node):
    """
    Convert method call node to string representation.
    Enhanced to support method overloading by including argument types.
    
    :param node: javalang method call node
    :return: String representation of the method call
    """
    if isinstance(node, javalang.tree.MethodInvocation):
        method_name = node.member
        
        # Try to infer argument types for overload resolution
        arg_types = _infer_argument_types_util(node.arguments) if node.arguments else []
        
        if node.qualifier:
            qualifier_str = expression_to_str(node.qualifier)
            if arg_types:
                arg_signature = ",".join(arg_types)
                return f"{qualifier_str}.{method_name}({arg_signature})"
            else:
                return f"{qualifier_str}.{method_name}"
        else:
            if arg_types:
                arg_signature = ",".join(arg_types)
                return f"{method_name}({arg_signature})"
            else:
                return method_name
                
    elif isinstance(node, javalang.tree.ClassCreator):
        class_name = node.type.name
        
        # Try to infer argument types for constructor overload resolution
        arg_types = _infer_argument_types_util(node.arguments) if node.arguments else []
        
        if arg_types:
            arg_signature = ",".join(arg_types)
            return f"new {class_name}({arg_signature})"
        else:
            return f"new {class_name}"
            
    elif isinstance(node, javalang.tree.Literal) and hasattr(node, 'selectors') and node.selectors:
        # Handle cases like "test".toUpperCase()
        # Use "expr" as placeholder to indicate this needs type resolution
        for selector in node.selectors:
            if isinstance(selector, javalang.tree.MethodInvocation):
                # Try to get argument types for the selector method call
                arg_types = _infer_argument_types_util(selector.arguments) if selector.arguments else []
                if arg_types:
                    arg_signature = ",".join(arg_types)
                    return f"expr.{selector.member}({arg_signature})"
                else:
                    return f"expr.{selector.member}"
        return str(node.value) if hasattr(node, 'value') else str(node)
    return str(node)

def _infer_argument_types_util(arguments):
    """
    Utility function to infer argument types for method_call_to_str.
    
    :param arguments: List of argument AST nodes
    :return: List of inferred argument type strings
    """
    if not arguments:
        return []
        
    arg_types = []
    
    for arg in arguments:
        inferred_type = _infer_expression_type_util(arg)
        if inferred_type:
            arg_types.append(inferred_type)
        else:
            # If we can't infer any type, return empty list to fall back to simple naming
            return []
            
    return arg_types

def _infer_expression_type_util(expr):
    """
    Utility function to infer expression types for method_call_to_str.
    
    :param expr: Expression AST node
    :return: Inferred type string or None
    """
    if isinstance(expr, javalang.tree.Literal):
        # Handle literal values - javalang stores all literals as strings
        if expr.value is None:
            return "null"
        elif isinstance(expr.value, str):
            value_str = expr.value
            
            # Character literals: 'c'
            if (len(value_str) == 3 and value_str.startswith("'") and value_str.endswith("'")):
                return "char"
            
            # String literals: "text"
            elif value_str.startswith('"') and value_str.endswith('"'):
                return "String"
            
            # Boolean literals
            elif value_str in ["true", "false"]:
                return "boolean"
            
            # Integer literals
            elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
                # Check for long suffix
                if value_str.lower().endswith('l'):
                    return "long"
                else:
                    return "int"
            
            # Floating point literals
            elif _is_float_literal_util(value_str):
                # Check for float suffix
                if value_str.lower().endswith('f'):
                    return "float"
                else:
                    return "double"
            
            # Default to String for unrecognized patterns
            else:
                return "String"
        else:
            # Fallback for non-string values (shouldn't happen with javalang)
            return "String"
    
    elif isinstance(expr, javalang.tree.ClassCreator):
        # Constructor call - the type is the class being instantiated
        return expr.type.name
        
    # For other expression types, return None (can't infer)
    return None

def _is_float_literal_util(value_str):
    """
    Utility function to check if a string represents a floating point literal.
    
    :param value_str: String value to check
    :return: True if it's a float literal
    """
    try:
        # Remove possible suffixes
        test_str = value_str.lower().rstrip('fd')
        
        # Check if it contains a decimal point or scientific notation
        if '.' in test_str or 'e' in test_str:
            float(test_str)
            return True
        
        return False
    except ValueError:
        return False


def parse_method_signature(call_name):
    """
    Parse a method call name to extract base method name and parameter signature.
    
    :param call_name: Method call name (e.g., "process(String,int)" or "process")
    :return: Tuple of (base_method_name, parameter_signature)
    """
    if "(" in call_name and call_name.endswith(")"):
        # Method with parameter signature
        open_paren = call_name.index("(")
        base_name = call_name[:open_paren]
        param_sig = call_name[open_paren+1:-1]  # Remove ( and )
        return base_name, param_sig
    else:
        # Simple method name without parameters
        return call_name, None


def expression_to_simple_str(node):
    """
    Convert expressions to simple string representations.
    This is a simplified version for basic call extraction.
    
    :param node: Expression AST node
    :return: Simple string representation
    """
    if isinstance(node, javalang.tree.MemberReference):
        if node.qualifier:
            return f"{node.qualifier}.{node.member}"
        return node.member
    elif isinstance(node, javalang.tree.Literal):
        return str(node.value)
    elif hasattr(node, 'name'):
        return node.name
    elif isinstance(node, str):
        # Handle simple string qualifiers (like "Utility" in Utility.staticMethod())
        return node
    else:
        return "expr"


def is_float_literal(value_str):
    """
    Check if a string represents a floating point literal.
    
    :param value_str: String value to check
    :return: True if it's a float literal
    """
    try:
        # Remove possible suffixes
        test_str = value_str.lower().rstrip('fd')
        
        # Check if it contains a decimal point or scientific notation
        if '.' in test_str or 'e' in test_str:
            float(test_str)
            return True
        
        return False
    except ValueError:
        return False


def infer_expression_type(expr):
    """
    Infer the type of an expression for overload resolution.
    
    :param expr: Expression AST node
    :return: Inferred type string or None
    """
    if isinstance(expr, javalang.tree.Literal):
        # Handle literal values - javalang stores all literals as strings
        if expr.value is None:
            return "null"
        elif isinstance(expr.value, str):
            value_str = expr.value
            
            # Character literals: 'c'
            if (len(value_str) == 3 and value_str.startswith("'") and value_str.endswith("'")):
                return "char"
            
            # String literals: "text"
            elif value_str.startswith('"') and value_str.endswith('"'):
                return "String"
            
            # Boolean literals
            elif value_str in ["true", "false"]:
                return "boolean"
            
            # Integer literals
            elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
                # Check for long suffix
                if value_str.lower().endswith('l'):
                    return "long"
                else:
                    return "int"
            
            # Floating point literals
            elif is_float_literal(value_str):
                # Check for float suffix
                if value_str.lower().endswith('f'):
                    return "float"
                else:
                    return "double"
            
            # Default to String for unrecognized patterns
            else:
                return "String"
        else:
            # Fallback for non-string values (shouldn't happen with javalang)
            return "String"
    
    elif isinstance(expr, javalang.tree.MemberReference):
        # Variable or field reference - would need variable context to resolve
        # For now, return None to indicate we can't infer the type
        return None
        
    elif isinstance(expr, javalang.tree.ClassCreator):
        # Constructor call - the type is the class being instantiated
        return expr.type.name
        
    elif isinstance(expr, javalang.tree.MethodInvocation):
        # Method call - would need to know the return type
        # For now, return None to indicate we can't infer the type
        return None
        
    elif isinstance(expr, javalang.tree.BinaryOperation):
        # Binary operations like +, -, etc.
        # The result type depends on operand types and operation
        # For simplicity, return None for now
        return None
        
    elif isinstance(expr, javalang.tree.Cast):
        # Explicit cast - the type is specified
        return get_type_name(expr.type) if expr.type else None
        
    # For other expression types, return None
    return None


def infer_argument_types(arguments):
    """
    Infer the types of arguments in a method or constructor call.
    This enables proper overload resolution in call lists.
    
    :param arguments: List of argument AST nodes
    :return: List of inferred argument type strings
    """
    if not arguments:
        return []
        
    arg_types = []
    
    for arg in arguments:
        inferred_type = infer_expression_type(arg)
        if inferred_type:
            arg_types.append(inferred_type)
        else:
            # If we can't infer the type, return empty list to fall back to simple naming
            return []
            
    return arg_types


def is_string_method(method_name):
    """
    Check if this is a common String method.
    
    :param method_name: Method name to check
    :return: True if it's a String method
    """
    string_methods = {
        'charAt', 'length', 'substring', 'toLowerCase', 'toUpperCase',
        'trim', 'replace', 'replaceAll', 'split', 'indexOf', 'lastIndexOf',
        'startsWith', 'endsWith', 'contains', 'equals', 'equalsIgnoreCase',
        'concat', 'valueOf', 'isEmpty', 'matches'
    }
    return method_name in string_methods


def resolve_standard_library_method(method_name):
    """
    Resolve common Java standard library method calls.
    
    :param method_name: Method name
    :return: Resolved call or None
    """
    # System.out methods
    if method_name in ['println', 'print', 'printf']:
        return f"System.out.{method_name}"
    
    # System.err methods  
    if method_name in ['println', 'print', 'printf'] and 'err' in str(method_name).lower():
        return f"System.err.{method_name}"
    
    # Math methods
    math_methods = {
        'abs', 'max', 'min', 'sqrt', 'pow', 'sin', 'cos', 'tan',
        'random', 'round', 'ceil', 'floor', 'log', 'exp'
    }
    if method_name in math_methods:
        return f"Math.{method_name}"
    
    # Arrays methods
    arrays_methods = {'sort', 'binarySearch', 'fill', 'copyOf', 'equals', 'toString'}
    if method_name in arrays_methods:
        return f"Arrays.{method_name}"
    
    return None


def find_collection_field_for_method(method_name, fields_info):
    """
    Find if there's a collection field that could support this method.
    
    :param method_name: Method name (e.g., 'add', 'remove', 'size')
    :param fields_info: Dictionary of field information
    :return: Collection type name or None
    """
    # Common collection methods
    collection_methods = {
        'add', 'remove', 'contains', 'size', 'isEmpty', 'clear', 
        'iterator', 'toArray', 'addAll', 'removeAll', 'retainAll'
    }
    
    if method_name not in collection_methods:
        return None
        
    for field_name, field_info in fields_info.items():
        field_type = field_info.get("type", "")
        if field_type in ["List", "ArrayList", "LinkedList", "Vector",
                        "Set", "HashSet", "TreeSet", "LinkedHashSet",
                        "Collection", "Queue", "Deque", "ArrayDeque"]:
            return field_type
    
    # If we have collection fields but didn't match specific type, use generic
    for field_name, field_info in fields_info.items():
        field_type = field_info.get("type", "")
        if any(coll in field_type.lower() for coll in ['list', 'set', 'collection', 'queue']):
            return "Collection"
            
    return None


def has_string_field(fields_info):
    """
    Check if there are any String fields.
    
    :param fields_info: Dictionary of field information
    :return: True if there are String fields
    """
    return any(field_info.get("type") == "String" for field_info in fields_info.values())


def resolve_typed_call(variable_type, method_name, import_mapping=None):
    """
    Resolve method calls based on known variable types.
    Enhanced to support cross-file type resolution.
    
    :param variable_type: The type of the variable
    :param method_name: The method being called
    :param import_mapping: Optional import mapping for cross-file resolution
    :return: Resolved call name
    """
    # Enhanced: Check if type is imported from another file
    if import_mapping and variable_type in import_mapping:
        from_module = import_mapping[variable_type]
        return f"{from_module}.{variable_type}.{method_name}"
    
    # Handle primitive wrapper types and common library classes
    if variable_type in ["String"]:
        return f"String.{method_name}"
    elif variable_type in ["List", "ArrayList", "LinkedList"]:
        return f"List.{method_name}"
    elif variable_type in ["Set", "HashSet", "TreeSet"]:
        return f"Set.{method_name}"
    elif variable_type in ["Map", "HashMap", "TreeMap"]:
        return f"Map.{method_name}"
    elif variable_type in ["Collection"]:
        return f"Collection.{method_name}"
    elif variable_type.endswith("[]"):  # Array types
        return f"Array.{method_name}"
    else:
        # For custom types or unknown types, use the type name
        return f"{variable_type}.{method_name}"


def infer_type_from_initializer(initializer, classes_info, import_info):
    """
    Try to infer the type of a variable from its initializer expression.
    
    :param initializer: The initializer expression
    :param classes_info: Dictionary of class information
    :param import_info: List of import information
    :return: Inferred type or None
    """
    if isinstance(initializer, javalang.tree.ClassCreator):
        # new ClassName() -> ClassName
        class_name = initializer.type.name
        # Check if it's an internal class
        if class_name in classes_info:
            return class_name
        # Check imports for fully qualified name
        for dep in import_info:
            if dep["import"] == class_name:
                return class_name
        return class_name
        
    elif isinstance(initializer, javalang.tree.Literal):
        # Literal values
        if isinstance(initializer.value, str):
            return "String"
        elif isinstance(initializer.value, int):
            return "int"
        elif isinstance(initializer.value, float):
            return "double"
        elif isinstance(initializer.value, bool):
            return "boolean"
    
    elif isinstance(initializer, javalang.tree.MethodInvocation):
        # Method call - could try to infer from method return type
        # For now, keep it simple
        pass
        
    return None


def expression_to_str(node):
    """
    Stringify of common javalang expression nodes.
    
    :param node: javalang expression node
    :return: String representation of the expression
    """
    if node is None:
        return ""

    if isinstance(node, javalang.tree.Literal):
        return str(node.value)                

    if isinstance(node, javalang.tree.MemberReference):
        qualifier = f"{node.qualifier}." if node.qualifier else ""
        return f"{qualifier}{node.member}"

    if isinstance(node, javalang.tree.MethodInvocation):
        qualifier = f"{node.qualifier}." if node.qualifier else ""
        args = ", ".join(expression_to_str(a) for a in node.arguments or [])
        return f"{qualifier}{node.member}({args})"

    if isinstance(node, javalang.tree.BinaryOperation):
        left = expression_to_str(node.operandl)
        right = expression_to_str(node.operandr)
        return f"{left} {node.operator} {right}"

    if isinstance(node, javalang.tree.Cast):
        typ = expression_to_str(node.type)
        inner = expression_to_str(node.expression)
        return f"({typ}) {inner}"
        
    if isinstance(node, javalang.tree.LambdaExpression):
        # Handle nested lambda expressions
        params = []
        if node.parameters:
            for param in node.parameters:
                if hasattr(param, 'name'):
                    params.append(param.name)
                elif hasattr(param, 'member'):
                    params.append(param.member)
                else:
                    params.append(str(param))
        
        param_str = f"({', '.join(params)})" if len(params) > 1 else (params[0] if params else "()")
        
        if isinstance(node.body, javalang.tree.BlockStatement) or isinstance(node.body, list):
            return f"{param_str} -> {{ ... }}"
        else:
            body_str = expression_to_str(node.body)
            return f"{param_str} -> {body_str}"
            
    if isinstance(node, javalang.tree.ClassCreator):
        return f"new {node.type.name}(...)"

    if hasattr(node, "name"):
        return node.name

    return "expr"


def statement_to_str(stmt):
    """
    Convert a statement to string representation.
    
    :param stmt: javalang statement node
    :return: String representation of the statement
    """
    if isinstance(stmt, javalang.tree.LocalVariableDeclaration):
        # e.g., "String result = "computed""
        parts = []
        for declarator in stmt.declarators:
            init_str = ""
            if declarator.initializer:
                init_str = f" = {expression_to_str(declarator.initializer)}"
            parts.append(f"{declarator.name}{init_str}")
        type_str = get_type_name(stmt.type)
        return f"{type_str} {', '.join(parts)};"
        
    elif isinstance(stmt, javalang.tree.StatementExpression):
        return f"{expression_to_str(stmt.expression)};"
        
    elif isinstance(stmt, javalang.tree.ReturnStatement):
        if stmt.expression:
            return f"return {expression_to_str(stmt.expression)};"
        else:
            return "return;"
            
    elif isinstance(stmt, javalang.tree.IfStatement):
        condition = expression_to_str(stmt.condition)
        return f"if ({condition}) {{ ... }}"
        
    elif isinstance(stmt, javalang.tree.ForStatement):
        return "for (...) { ... }"
        
    elif isinstance(stmt, javalang.tree.WhileStatement):
        condition = expression_to_str(stmt.condition)
        return f"while ({condition}) {{ ... }}"
        
    else:
        # For unknown statement types, return a generic representation
        return f"{type(stmt).__name__}"


def compute_interval(node):
    """
    Extract the lines (min and max) for a given class, method, or other AST node.
    Uses a simple traversal approach similar to inspect4py.
    
    :param node: javalang AST node
    :return: dict with min_lineno and max_lineno
    """
    # Special handling for Lambda expressions which don't have position
    if isinstance(node, javalang.tree.LambdaExpression):
        return compute_lambda_interval(node)
    
    if not hasattr(node, 'position') or not node.position:
        return {
            "min_lineno": None,
            "max_lineno": None
        }
    
    min_lineno = node.position[0]
    max_lineno = node.position[0]
    
    # Traverse all child nodes to find actual min and max line numbers
    for child in traverse_all_nodes(node):
        if hasattr(child, 'position') and child.position:
            child_line = child.position[0]
            min_lineno = min(min_lineno, child_line)
            max_lineno = max(max_lineno, child_line)
    
    return {
        "min_lineno": min_lineno,
        "max_lineno": max_lineno + 1  # Add 1 to include the closing line
    }


def compute_lambda_interval(lambda_node):
    """
    Compute line interval for lambda expressions by examining their body and parameters.
    
    :param lambda_node: LambdaExpression node
    :return: dict with min_lineno and max_lineno
    """
    positions = []
    
    # Collect positions from parameters
    if lambda_node.parameters:
        for param in lambda_node.parameters:
            if hasattr(param, 'position') and param.position:
                positions.append(param.position[0])
    
    # Collect positions from body and all child nodes
    if lambda_node.body:
        for child in traverse_all_nodes(lambda_node.body):
            if hasattr(child, 'position') and child.position:
                positions.append(child.position[0])
    
    if positions:
        min_lineno = min(positions)
        max_lineno = max(positions)
        return {
            "min_lineno": min_lineno,
            "max_lineno": max_lineno + 1
        }
    else:
        # If we can't find positions, return a placeholder indicating unknown position
        # rather than None which gets filtered out
        return {
            "min_lineno": -1,
            "max_lineno": -1
        }


def traverse_all_nodes(node):
    """
    Generator that recursively traverses all child nodes in the AST.
    Similar to ast.walk() in Python's ast module.
    
    :param node: Starting AST node
    :yield: All child nodes in the subtree
    """
    yield node
    
    # Get all attributes that might contain child nodes
    # Handle nodes that might not have __dict__ attribute
    try:
        attrs = vars(node).items()
    except TypeError:
        # Node doesn't have __dict__, try to get attributes directly
        attrs = []
        if hasattr(node, '__slots__'):
            for attr_name in node.__slots__:
                if hasattr(node, attr_name):
                    attrs.append((attr_name, getattr(node, attr_name)))
    
    for attr_name, attr_value in attrs:
        if attr_value is None:
            continue
            
        # Handle single node attributes
        if hasattr(attr_value, '__class__') and hasattr(attr_value, 'position'):
            yield from traverse_all_nodes(attr_value)
        
        # Handle list attributes that might contain nodes
        elif isinstance(attr_value, list):
            for item in attr_value:
                if hasattr(item, '__class__') and hasattr(item, 'position'):
                    yield from traverse_all_nodes(item)
                elif hasattr(item, '__class__') and hasattr(item, '__dict__'):
                    # Some nodes might not have position but still contain child nodes
                    yield from traverse_all_nodes(item)


def extract_annotations(node):
    """
    Extract annotations from a Java AST node.
    
    :param node: javalang AST node
    :return: List of annotation information
    """
    annotations = []
    if hasattr(node, 'annotations') and node.annotations:
        for annotation in node.annotations:
            annotation_info = {
                "name": annotation.name if hasattr(annotation, 'name') else str(annotation),
                "type": "annotation"
            }
            
            # Extract annotation arguments if present
            if hasattr(annotation, 'element') and annotation.element:
                annotation_info["value"] = expression_to_str(annotation.element)
            elif hasattr(annotation, 'member') and annotation.member:
                annotation_info["member"] = annotation.member
            
            annotations.append(annotation_info)
    
    return annotations


def get_unique_method_key(method_name, parameters, existing_methods):
    """
    Generate a unique key for methods to handle overloading.
    
    :param method_name: Base method name
    :param parameters: List of parameter dictionaries
    :param existing_methods: Dictionary of existing methods
    :return: Unique method key
    """
    base_key = method_name
    
    # If no conflict, use the base name
    if base_key not in existing_methods:
        return base_key
    
    # Create signature-based key for overloaded methods
    param_types = [param["type"] for param in parameters]
    signature = f"{method_name}({','.join(param_types)})"
    
    # If this signature key is also taken, add a counter
    counter = 1
    unique_key = signature
    while unique_key in existing_methods:
        unique_key = f"{signature}_{counter}"
        counter += 1
        
    return unique_key


def is_main_method(method_key, method_info):
    """
    Check if a method is the main method (entry point for Java applications).
    
    :param method_key: Method key (may include signature for overloaded methods)
    :param method_info: Dictionary containing method information
    :return: True if this is a main method
    """
    # Extract the actual method name from the key (handle overloaded methods)
    method_name = method_info["name"]
    
    # Check if method is named "main"
    if method_name != "main":
        return False
    # Check if it has the right modifiers (public static)
    if "public" not in method_info["modifiers"] or "static" not in method_info["modifiers"]:
        return False
    # Check if return type is void (represented as None)
    if method_info["return_type"] is not None:
        return False
    # Check if it has the right parameter (String[] args)
    params = method_info["parameters"]
    if len(params) != 1:
        return False
    param_type = params[0]["type"]
    # Java accepts both String[] and String... for main method
    if param_type not in ["String[]", "String..."]:
        return False
    return True


def is_standard_library(import_path):
    """
    Check if the import is from Java standard library.
    
    :param import_path: Full import path
    :return: True if it's a standard library import
    """
    standard_prefixes = [
        'java.',        # Core Java packages
        'javax.',       # Java extensions
        'javafx.',      # JavaFX
        'jdk.',         # JDK-specific packages
        'com.sun.',     # Sun/Oracle internal packages
        'sun.',         # Sun internal packages (deprecated but still used)
        'org.w3c.',     # W3C standards
        'org.xml.',     # XML processing
        'org.ietf.',    # IETF standards
    ]
    
    return any(import_path.startswith(prefix) for prefix in standard_prefixes)


# def ast_to_json(ast_node):
#     """
#     Convert Java AST node to JSON format representation.
#     Simplified version for better performance and readability.
    
#     :param ast_node: javalang AST node
#     :return: Dictionary representation of the AST
#     """
#     result = {
#         "type": type(ast_node).__name__,
#         "name": getattr(ast_node, 'name', None),
#         "position": getattr(ast_node, 'position', None)
#     }
    
#     # Add method/constructor specific information
#     if isinstance(ast_node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
#         result.update({
#             "modifiers": list(getattr(ast_node, 'modifiers', [])),
#             "return_type": get_type_name(getattr(ast_node, 'return_type', None)) if hasattr(ast_node, 'return_type') else None,
#             "parameters": [{
#                 "name": param.name,
#                 "type": get_type_name(param.type),
#                 "annotations": [ann.name for ann in getattr(param, 'annotations', [])]
#             } for param in getattr(ast_node, 'parameters', [])],
#             "annotations": [ann.name for ann in getattr(ast_node, 'annotations', [])],
#             "body_summary": get_body_summary(ast_node)
#         })
    
#     return result
def ast_to_json(ast_node):
    """
    Convert Java AST node to JSON format representation similar to inspect4py.
        
    :param ast_node: javalang AST node
    :return: List representation of the AST similar to inspect4py format
    """
    node_id = 0
        
    def node_to_dict(node, current_id):
        nonlocal node_id
            
        if node is None:
            return None
            
        # Create base node structure
        result = {
            "id": current_id,
            "type": type(node).__name__
        }
            
        # Add value for nodes that have meaningful string representation
        if hasattr(node, 'name') and node.name:
            result["value"] = node.name
        elif hasattr(node, 'member') and node.member:
            result["value"] = node.member
        elif hasattr(node, 'value') and isinstance(node.value, (str, int, float, bool)):
            result["value"] = str(node.value)
        elif isinstance(node, javalang.tree.Literal) and node.value is not None:
            result["value"] = str(node.value)
            
        # Collect children
        children_ids = []
        child_nodes = []
            
        # Get all child nodes from the node's attributes
        try:
            attrs = vars(node).items()
        except TypeError:
            attrs = []
            if hasattr(node, '__slots__'):
                for attr_name in node.__slots__:
                    if hasattr(node, attr_name):
                        attrs.append((attr_name, getattr(node, attr_name)))
            
        for attr_name, attr_value in attrs:
            if attr_name.startswith('_') or attr_name in ['position']:
                continue
                    
            if attr_value is None:
                continue
            elif isinstance(attr_value, list):
                for item in attr_value:
                    if hasattr(item, '__class__') and hasattr(item.__class__, '__name__'):
                        child_nodes.append(item)
            elif hasattr(attr_value, '__class__') and hasattr(attr_value.__class__, '__name__'):
                # Check if it's a javalang AST node
                if hasattr(attr_value, '__module__') and 'javalang' in str(attr_value.__module__):
                    child_nodes.append(attr_value)
            
        # Process children and collect their IDs
        child_results = []
        for child in child_nodes:
            node_id += 1
            child_id = node_id
            children_ids.append(child_id)
            child_result = node_to_dict(child, child_id)
            if child_result:
                child_results.append(child_result)
            
        # Add children field if there are children
        if children_ids:
            result["children"] = children_ids
            
        return [result] + [item for sublist in child_results for item in (sublist if isinstance(sublist, list) else [sublist])]
        
    # Start processing from root node
    ast_list = node_to_dict(ast_node, 0)
    return ast_list if isinstance(ast_list, list) else [ast_list] if ast_list else []


def get_body_summary(method_node):
    """
    Get summary information about method body.
    
    :param method_node: Method or constructor AST node
    :return: Dictionary with body summary information
    """
    if not hasattr(method_node, 'body') or not method_node.body:
        return {"statements_count": 0, "is_abstract": True}
    
    body = method_node.body
    statement_types = [type(stmt).__name__ for stmt in body[:5]]  # First 5 statements
    
    return {
        "statements_count": len(body),
        "statement_types": statement_types,
        "is_abstract": False
    }


def ast_to_source_code(ast_node, source_lines):
    """
    Convert Java AST node to source code string representation.
    Similar to Python's ast.unparse() but for Java.
    
    :param ast_node: javalang AST node
    :param source_lines: List of source file lines
    :return: String representation of the source code
    """
    try:
        # For method and constructor nodes, extract from original source
        if isinstance(ast_node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
            return extract_source_from_lines(ast_node, source_lines)
        else:
            # For other nodes, provide a simplified representation
            node_type = type(ast_node).__name__
            if hasattr(ast_node, 'name'):
                return f"{node_type}: {ast_node.name}"
            elif hasattr(ast_node, 'value'):
                return f"{node_type}: {ast_node.value}"
            else:
                return f"{node_type}"
    except Exception as e:
        return f"// Error extracting source code: {str(e)}"


def extract_source_from_lines(node, source_lines):

    """
    Extract source code from original file lines based on node position.
    This is more accurate than reconstructing from AST.
    
    :param node: AST node with position information
    :param source_lines: List of source file lines
    :return: Original source code string
    """
    if not hasattr(node, 'position') or not node.position:
        return "// No position information available"
    
    try:
        start_line = node.position[0] - 1  # Convert to 0-based indexing
        
        # Find the end line by looking for method/constructor end
        end_line = start_line
        brace_count = 0
        found_opening_brace = False
        
        for i in range(start_line, len(source_lines)):
            line = source_lines[i]
            
            # Count braces to find method end
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening_brace = True
                elif char == '}':
                    brace_count -= 1
                    
                # If we've found the opening brace and closed all braces, we're done
                if found_opening_brace and brace_count == 0:
                    end_line = i
                    break
            
            if found_opening_brace and brace_count == 0:
                break
        
        # Extract the source code lines
        if start_line < len(source_lines):
            source_lines_subset = source_lines[start_line:end_line + 1]
            return ''.join(source_lines_subset).strip()
        else:
            return "// Source line not found"
            
    except Exception as e:
        return f"// Error extracting source: {str(e)}" 
    
def generate_output_html(pruned_json, output_file_html):
    """
    Method to generate a simple HTML view of the obtained JSON.
    :pruned_json JSON to print out
    :output_file_html path where to write the HTML
    """
    html = json2html.convert(json=pruned_json)

    with open(output_file_html, "w") as ht:
        ht.write(html)

def resolve_inheritance_method_call(method_call, current_class_name, classes_info, interfaces_info):
    """
    Resolve method calls in Java inheritance hierarchy using DFS algorithm.
    Enhanced to support method signature-based resolution for proper override/overload handling.
    
    :param method_call: Method call string (e.g., "process" or "process(int,String)")
    :param current_class_name: Current class context
    :param classes_info: Dictionary of class information
    :param interfaces_info: Dictionary of interface information
    :return: Resolved method call string or None if not found
    """
    if current_class_name not in classes_info:
        return None
    
    # Parse method name and signature from the call
    base_method_name, param_signature = parse_method_signature(method_call)
    
    # Try to find exact signature match first, then fallback to name-only match
    resolved = _resolve_method_with_signature(
        base_method_name, param_signature, current_class_name, classes_info, interfaces_info
    )
    
    return resolved


def _resolve_method_with_signature(method_name, param_signature, current_class_name, classes_info, interfaces_info):
    """
    Resolve method calls with signature-aware inheritance handling.
    This handles the case where a child class overrides some but not all overloaded methods.
    
    :param method_name: Base method name (e.g., "process")
    :param param_signature: Parameter signature (e.g., "int,String" or None)
    :param current_class_name: Current class context
    :param classes_info: Dictionary of class information
    :param interfaces_info: Dictionary of interface information
    :return: Resolved method call string or None if not found
    """
    if current_class_name not in classes_info:
        return None
    
    current_class = classes_info[current_class_name]
    
    # 1. First check current class for exact signature match
    if "methods" in current_class:
        exact_match = _find_method_by_signature(current_class["methods"], method_name, param_signature)
        if exact_match:
            return f"{current_class_name}.{exact_match}"
    
    # 2. If no exact match in current class, check parent class recursively
    extends = current_class.get("extends")
    if extends and extends in classes_info:
        parent_result = _resolve_method_with_signature(
            method_name, param_signature, extends, classes_info, interfaces_info
        )
        if parent_result:
            return parent_result
    
    # 3. Check implemented interfaces
    implements = current_class.get("implements", [])
    for interface_name in implements:
        if interface_name in interfaces_info:
            interface_info = interfaces_info[interface_name]
            if "methods" in interface_info:
                exact_match = _find_method_by_signature(interface_info["methods"], method_name, param_signature)
                if exact_match:
                    return f"{interface_name}.{exact_match}"
            
            # Check interface inheritance
            interface_extends = interface_info.get("extends", [])
            for parent_interface in interface_extends:
                if parent_interface in interfaces_info:
                    parent_result = _resolve_interface_method_with_signature(
                        method_name, param_signature, parent_interface, interfaces_info
                    )
                    if parent_result:
                        return parent_result
    
    return None


def _find_method_by_signature(methods_dict, method_name, param_signature):
    """
    Find a method in the methods dictionary by signature.
    Tries exact signature match first, then falls back to name-only match.
    
    :param methods_dict: Dictionary of methods
    :param method_name: Base method name
    :param param_signature: Parameter signature string or None
    :return: Method key if found, None otherwise
    """
    # If we have a parameter signature, try exact match first
    if param_signature:
        full_signature = f"{method_name}({param_signature})"
        if full_signature in methods_dict:
            return full_signature
    
    # Try to find by method name and check parameter compatibility
    for method_key, method_info in methods_dict.items():
        method_info_name = method_info.get("name", method_key)
        
        # Check if method names match
        if method_info_name == method_name:
            # If we have a specific signature we're looking for
            if param_signature:
                # Get the parameters from method_info
                method_parameters = method_info.get("parameters", [])
                
                # Build expected signature from method_info
                if method_parameters:
                    expected_param_types = [param.get("type", "Object") for param in method_parameters]
                    expected_signature = ",".join(expected_param_types)
                else:
                    expected_signature = ""
                
                # Check if signatures match
                if expected_signature == param_signature:
                    return method_key
                    
                # Special case: if method_key doesn't have signature but method_info has parameters
                # and method_key == method_name, this might be the single-parameter version
                if method_key == method_name and expected_signature == param_signature:
                    return method_key
            else:
                # No specific signature required, return first match
                return method_key
    
    return None


def _resolve_interface_method_with_signature(method_name, param_signature, interface_name, interfaces_info):
    """
    Resolve method calls in interface inheritance hierarchy with signature support.
    
    :param method_name: Method name to resolve
    :param param_signature: Parameter signature
    :param interface_name: Interface name to search in
    :param interfaces_info: Dictionary of interface information
    :return: Resolved method call string or None if not found
    """
    if interface_name not in interfaces_info:
        return None
    
    interface_info = interfaces_info[interface_name]
    
    # Check current interface methods
    if "methods" in interface_info:
        exact_match = _find_method_by_signature(interface_info["methods"], method_name, param_signature)
        if exact_match:
            return f"{interface_name}.{exact_match}"
    
    # Check parent interfaces
    extends = interface_info.get("extends", [])
    for parent_interface in extends:
        if parent_interface in interfaces_info:
            parent_result = _resolve_interface_method_with_signature(
                method_name, param_signature, parent_interface, interfaces_info
            )
            if parent_result:
                return parent_result
    
    return None


def resolve_super_method_call(method_call, current_class_name, classes_info):
    """
    Resolve super method calls in Java using inheritance hierarchy.
    Enhanced to support method signature-based resolution.
    
    :param method_call: Method call string (e.g., "process" or "process(int,String)")
    :param current_class_name: Current class context
    :param classes_info: Dictionary of class information
    :return: Resolved super method call string or None if not found
    """
    if current_class_name not in classes_info:
        return None
    
    # Parse method name and signature from the call
    base_method_name, param_signature = parse_method_signature(method_call)
    
    current_class = classes_info[current_class_name]
    extends = current_class.get("extends")
    
    if extends and extends in classes_info:
        # Use the signature-aware resolution for parent class
        parent_result = _resolve_method_with_signature(
            base_method_name, param_signature, extends, classes_info, {}
        )
        if parent_result:
            return parent_result
    
    return None


def resolve_method_call_with_inheritance(call_name, current_class_name, classes_info, interfaces_info, file_base):
    """
    Unified method call resolution with inheritance support for Java.
    Enhanced to support method signature-based resolution for override/overload handling.
    
    :param call_name: Raw method call name (may include signature)
    :param current_class_name: Current class context
    :param classes_info: Dictionary of class information
    :param interfaces_info: Dictionary of interface information
    :param file_base: File base name for internal references
    :return: Resolved method call string
    """
    # Handle super method calls
    if call_name.startswith("super."):
        method_call = call_name[6:]  # Remove "super." prefix
        resolved = resolve_super_method_call(method_call, current_class_name, classes_info)
        if resolved:
            return f"super.{resolved}"
        else:
            return call_name  # Keep original if not resolved
    
    # Handle qualified calls (ClassName.method)
    if "." in call_name:
        parts = call_name.split(".", 1)
        qualifier = parts[0]
        method_call = parts[1]
        
        # If qualifier is a known class, try inheritance resolution
        if qualifier in classes_info:
            resolved = resolve_inheritance_method_call(method_call, qualifier, classes_info, interfaces_info)
            if resolved:
                return f"{file_base}.{resolved}"
        
        # If qualifier is an interface
        elif qualifier in interfaces_info:
            base_method_name, param_signature = parse_method_signature(method_call)
            resolved = _resolve_interface_method_with_signature(
                base_method_name, param_signature, qualifier, interfaces_info
            )
            if resolved:
                return f"{file_base}.{resolved}"
    
    # Handle unqualified calls (just method name)
    else:
        method_call = call_name
        
        # Try to resolve in current class hierarchy
        if current_class_name:
            resolved = resolve_inheritance_method_call(method_call, current_class_name, classes_info, interfaces_info)
            if resolved:
                return f"{file_base}.{resolved}"
    
    # If not resolved through inheritance, return original call
    return call_name


def resolve_interface_method_call(method_call, interface_name, interfaces_info):
    """
    Resolve method calls in interface inheritance hierarchy.
    Enhanced to support method signature-based resolution.
    
    :param method_call: Method call string (e.g., "process" or "process(int,String)")
    :param interface_name: Interface name to search in
    :param interfaces_info: Dictionary of interface information
    :return: Resolved method call string or None if not found
    """
    base_method_name, param_signature = parse_method_signature(method_call)
    return _resolve_interface_method_with_signature(
        base_method_name, param_signature, interface_name, interfaces_info
    )


# ============================================================================
# Language-independent utility functions (adapted from inspect4py)
# ============================================================================

def extract_directory_tree(input_path, ignore_dirs, ignore_files, visual=0):
    """
    Method to obtain the directory tree of a repository.
    The ignored directories and files that were inputted are also ignored.
    Adapted from inspect4py for Java projects.
    
    :param input_path: Path of the repo to analyze
    :param ignore_dirs: List of directory patterns to ignore
    :param ignore_files: List of file patterns to ignore  
    :param visual: Whether to print visual representation (1) or not (0)
    :return: Directory structure dictionary
    """
    ignore_set = ['.git', '__pycache__', '.idea', '.pytest_cache', 'target', 'build', 'bin', '.gradle']
    ignore_set = tuple(list(ignore_dirs) + list(ignore_files) + ignore_set)
    
    if visual:
        paths = DisplayablePath.make_tree(Path(input_path), criteria=lambda
            path: True if path.name not in ignore_set and not os.path.join("../", path.name).endswith(
            ".class") else False)  # Changed from .pyc to .class
        for path in paths:
            print(path.displayable())
    
    return get_directory_structure(input_path, ignore_set)


def dice_coefficient(a, b):
    """
    Dice coefficient 2nt/(na + nb).
    Copied from inspect4py for license detection.
    """
    if not len(a) or not len(b):
        return 0.0
    if len(a) == 1:
        a = a + u"."
    if len(b) == 1:
        b = b + u"."

    a_bigrams = {a[i: i + 2] for i in range(len(a) - 1)}
    b_bigrams = {b[i: i + 2] for i in range(len(b) - 1)}

    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0 / (len(a_bigrams) + len(b_bigrams))
    return dice_coeff


def extract_license(input_path):
    """
    Extracts the license of the repository.
    Adapted from inspect4py - language independent.
    
    :param input_path: Path of the repository to be analyzed
    :return: The license text
    :raises Exception: If a license file is not found
    """
    license_filenames = [
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENSE.rst",
        "COPYING",
        "COPYING.txt",
        "COPYING.md",
        "COPYING.rst",
    ]

    license_file = None
    for filename in os.listdir(input_path):
        if filename in license_filenames:
            license_file = os.path.join(input_path, filename)
            break

    if license_file is None:
        raise Exception("License file not found.")

    with open(license_file, "r", encoding='utf-8') as f:
        license_text = f.read()

    return license_text


def detect_license(license_text, licenses_path, threshold=0.9):
    """
    Function to detect the license type from extracted text.
    Adapted from inspect4py - language independent.

    :param license_text: The extracted license text
    :param licenses_path: Path of the folder containing license templates
    :param threshold: Threshold to consider a license as detected (0-1)
    :return: Ranked list of license types and their percentage match
    """
    # Regex pattern for preprocessing license templates and extract spdx id
    pattern = re.compile(
        "(---\n.*(spdx-id: )(?P<id>.+?)\n.*---\n)(?P<template>.*)", re.DOTALL
    )

    rank_list = []
    for licen in os.listdir(licenses_path):
        try:
            with open(os.path.join(licenses_path, licen), "r", encoding='UTF-8') as f:
                parser = pattern.search(f.read())
                if parser is None:
                    continue
                spdx_id = parser.group("id")
                license_template = parser.group("template")

            dice_coeff = dice_coefficient(license_text.strip(), license_template.strip())
            if dice_coeff > threshold:
                rank_list.append((spdx_id, dice_coeff))
        except Exception as e:
            print(f"Error processing license file {licen}: {e}")
            continue

    return sorted(rank_list, key=lambda t: t[1], reverse=True)


def extract_readme(input_path: str, output_dir: str) -> dict:
    """
    Function to extract content of all readme file under the input directory.
    Adapted from inspect4py - language independent.
    
    :param input_path: Path of the repository to be analyzed
    :param output_dir: The output directory. Used to generate the correct path of the README file
    :return: Dictionary mapping file paths to readme content
    """
    readme_files = {}
    for file in Path(input_path).rglob("README.*"):
        relative_path = os.path.join(output_dir, Path(file).relative_to(Path(input_path).parent))
        try:
            with open(file, 'r', encoding='utf-8') as f:
                readme_files[str(relative_path)] = f.read()
        except Exception as e:
            print(f"Error when opening {file}: {e}")

    return readme_files


def get_github_metadata(input_path: str) -> dict:
    """
    Function to extract metadata from the remote repository using Github api.
    It requires connectivity to the Github API and the local target repository 
    to have .git folder and a remote repository on Github.
    Adapted from inspect4py - language independent.

    :param input_path: Path of the repository to be analyzed
    :return: Dictionary containing GitHub metadata
    """
    github_metadata = {}
    try:
        repo = git.Repo(input_path)
        remote_url = repo.remotes.origin.url

        # Extract owner and repo name from remote url
        api_param = re.search(r".+github.com[:/](?P<param>.+).git", remote_url).group("param")

        # Call Github API to get the metadata
        api_url = f"https://api.github.com/repos/{api_param}"
        response = requests.get(api_url)
        github_metadata = response.json()
    except git.InvalidGitRepositoryError as e:
        print(f"{input_path}.git not found or not valid: {e}")
    except git.NoSuchPathError as e:
        print(f"{input_path} does not exist: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error when accessing GitHub API: {e}")
    except Exception as e:
        print(f"Error extracting GitHub metadata: {e}")

    return github_metadata

def extract_java_requirements(input_path):
    """
    Extract Java project dependencies from Maven pom.xml or Gradle build files.
    This is equivalent to Python's requirements.txt extraction.
    
    :param input_path: Path to the Java project root directory
    :return: Dictionary with dependency information
    """
    print(f"Extracting Java dependencies from {input_path}")
    
    requirements = {}
    
    # Try to find and parse Maven pom.xml
    pom_path = os.path.join(input_path, "pom.xml")
    if os.path.exists(pom_path):
        maven_deps = extract_maven_dependencies(pom_path)
        requirements.update(maven_deps)
        print(f"Found Maven dependencies: {len(maven_deps)} packages")
    
    # Try to find and parse Gradle build files
    gradle_paths = [
        os.path.join(input_path, "build.gradle"),
        os.path.join(input_path, "build.gradle.kts")
    ]
    
    for gradle_path in gradle_paths:
        if os.path.exists(gradle_path):
            gradle_deps = extract_gradle_dependencies(gradle_path)
            requirements.update(gradle_deps)
            print(f"Found Gradle dependencies: {len(gradle_deps)} packages")
            break
    
    # Check for multi-module projects
    for item in os.listdir(input_path):
        item_path = os.path.join(input_path, item)
        if os.path.isdir(item_path):
            # Check for nested pom.xml in submodules
            nested_pom = os.path.join(item_path, "pom.xml")
            if os.path.exists(nested_pom):
                nested_deps = extract_maven_dependencies(nested_pom)
                requirements.update(nested_deps)
            
            # Check for nested build.gradle in submodules
            nested_gradle = os.path.join(item_path, "build.gradle")
            if os.path.exists(nested_gradle):
                nested_deps = extract_gradle_dependencies(nested_gradle)
                requirements.update(nested_deps)
    
    if not requirements:
        print("No Java dependency files found (pom.xml, build.gradle)")
    
    return requirements


def extract_maven_dependencies(pom_path):
    """
    Extract dependencies from Maven pom.xml file
    
    :param pom_path: Path to pom.xml file
    :return: Dictionary with Maven dependencies
    """
    dependencies = {}
    
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        
        # Handle XML namespace
        namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
        if root.tag.startswith('{'):
            # Extract namespace from root tag
            namespace_uri = root.tag.split('}')[0][1:]
            namespace = {'maven': namespace_uri}
        
        # Find all dependency elements
        deps = root.findall('.//maven:dependency', namespace)
        
        # If no namespace found, try without namespace
        if not deps:
            deps = root.findall('.//dependency')
        
        for dep in deps:
            group_id = dep.find('groupId') or dep.find('maven:groupId', namespace)
            artifact_id = dep.find('artifactId') or dep.find('maven:artifactId', namespace)
            version = dep.find('version') or dep.find('maven:version', namespace)
            scope = dep.find('scope') or dep.find('maven:scope', namespace)
            
            if group_id is not None and artifact_id is not None:
                group_text = group_id.text.strip() if group_id.text else ""
                artifact_text = artifact_id.text.strip() if artifact_id.text else ""
                version_text = version.text.strip() if version is not None and version.text else "unknown"
                scope_text = scope.text.strip() if scope is not None and scope.text else "compile"
                
                # Create Maven coordinate key: groupId:artifactId
                maven_key = f"{group_text}:{artifact_text}"
                
                # Store with version and scope information
                dependencies[maven_key] = {
                    "version": version_text,
                    "scope": scope_text,
                    "build_tool": "maven"
                }
        
        print(f"Extracted {len(dependencies)} dependencies from {pom_path}")
        
    except ET.ParseError as e:
        print(f"Error parsing Maven pom.xml: {e}")
    except Exception as e:
        print(f"Error extracting Maven dependencies: {e}")
    
    return dependencies


def extract_gradle_dependencies(gradle_path):
    """
    Extract dependencies from Gradle build.gradle file
    
    :param gradle_path: Path to build.gradle file
    :return: Dictionary with Gradle dependencies
    """
    dependencies = {}
    
    try:
        with open(gradle_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Pattern to match Gradle dependency declarations
        # Supports both single quotes and double quotes
        # Examples: 
        # implementation 'org.springframework:spring-core:5.3.21'
        # testImplementation "junit:junit:4.13.2"
        # compile group: 'org.apache.commons', name: 'commons-lang3', version: '3.12.0'
        
        # Pattern 1: Short notation - scope 'group:artifact:version'
        pattern1 = r'(\w+)\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]'
        matches1 = re.findall(pattern1, content)
        
        for match in matches1:
            scope, group_id, artifact_id, version = match
            maven_key = f"{group_id}:{artifact_id}"
            dependencies[maven_key] = {
                "version": version.strip(),
                "scope": scope.strip(),
                "build_tool": "gradle"
            }
        
        # Pattern 2: Map notation - scope group: 'group', name: 'artifact', version: 'version'
        pattern2 = r'(\w+)\s+group:\s*[\'"]([^\'">]+)[\'"],\s*name:\s*[\'"]([^\'">]+)[\'"],\s*version:\s*[\'"]([^\'">]+)[\'"]'
        matches2 = re.findall(pattern2, content)
        
        for match in matches2:
            scope, group_id, artifact_id, version = match
            maven_key = f"{group_id}:{artifact_id}"
            dependencies[maven_key] = {
                "version": version.strip(),
                "scope": scope.strip(),
                "build_tool": "gradle"
            }
        
        # Pattern 3: Kotlin DSL style
        pattern3 = r'(\w+)\s*\(\s*[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]\s*\)'
        matches3 = re.findall(pattern3, content)
        
        for match in matches3:
            scope, group_id, artifact_id, version = match
            maven_key = f"{group_id}:{artifact_id}"
            dependencies[maven_key] = {
                "version": version.strip(),
                "scope": scope.strip(),
                "build_tool": "gradle"
            }
        
        print(f"Extracted {len(dependencies)} dependencies from {gradle_path}")
        
    except Exception as e:
        print(f"Error extracting Gradle dependencies: {e}")
    
    return dependencies


# def format_java_requirements_for_display(requirements):
#     """
#     Format Java requirements for consistent display similar to Python requirements
    
#     :param requirements: Dictionary with Java dependencies
#     :return: Simplified dictionary for compatibility with existing display logic
#     """
#     formatted = {}
    
#     for maven_key, info in requirements.items():
#         if isinstance(info, dict):
#             version = info.get("version", "unknown")
#             scope = info.get("scope", "compile")
#             build_tool = info.get("build_tool", "unknown")
            
#             # For display compatibility, create a simple string format
#             if scope != "compile":
#                 formatted[maven_key] = f"{version} ({scope})"
#             else:
#                 formatted[maven_key] = version
#         else:
#             # Fallback for simple string values
#             formatted[maven_key] = str(info)
    
#     return formatted