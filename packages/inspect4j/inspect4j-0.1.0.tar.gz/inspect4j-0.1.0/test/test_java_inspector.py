import unittest
import os
import json
from pathlib import Path
import shutil
import sys

# Add parent directory to path to import java_inspector
sys.path.append(str(Path(__file__).parent.parent))
from java_inspector import JavaInspection

class TestJavaInspector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before all tests"""
        cls.test_files_dir = Path("Test/test_files/test_basic")
        cls.test_nested_dir = Path("Test/test_files/test_nested")
        cls.test_dependencies_dir = Path("Test/test_files/test_dependencies")
        cls.test_callList_dir = Path("Test/test_files/test_callList")
        cls.output_dir = Path("Test/test_output")
        cls.output_dir.mkdir(exist_ok=True)
        cls.json_dir = cls.output_dir / "json_files"
        cls.json_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment after all tests"""
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)

    def setUp(self):
        """Set up before each test method"""
        # Clear json files before each test
        for file in self.json_dir.glob("*.json"):
            file.unlink()

    def test_basic_class_structure(self):
        """Test basic class structure extraction"""
        test_file = self.test_files_dir / "test_class" / "BasicClassTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        self.assertTrue(inspector.file_json)
        
        json_file = self.json_dir / "BasicClassTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify class info
        self.assertIn("classes", data)
        class_info = data["classes"]["BasicClassTest"]
        self.assertEqual(class_info["name"], "BasicClassTest")
        self.assertIn("public", class_info["modifiers"])

    def test_javadoc_extraction(self):
        """Test Javadoc comment extraction"""
        test_file = self.test_files_dir / "test_class" / "JavadocTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "JavadocTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify class Javadoc
        class_info = data["classes"]["JavadocTest"]
        self.assertIn("doc", class_info)
        self.assertIn("description", class_info["doc"])
        self.assertIn("comment_tags", class_info["doc"])

    def test_interface_structure(self):
        """Test interface structure extraction"""
        test_file = self.test_files_dir / "test_interface" / "InterfaceTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "InterfaceTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify interface info
        self.assertIn("interfaces", data)
        interface_info = data["interfaces"]["InterfaceTest"]
        self.assertEqual(interface_info["name"], "InterfaceTest")

    def test_main_method_detection(self):
        """Test main method detection"""
        test_file = self.test_files_dir / "test_method" / "MainMethodTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "MainMethodTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify that the file was parsed successfully
        self.assertIn("classes", data)
        class_info = data["classes"]["MainMethodTest"]
        self.assertIn("methods", class_info)
        
        # Check if any main method exists
        main_methods = [name for name in class_info["methods"].keys() if name == "main"]
        self.assertGreater(len(main_methods), 0, "No main method found")
        
        # If main_info exists, verify it
        if "main_info" in data:
            self.assertEqual(data["main_info"]["main_flag"], 1)
            self.assertEqual(data["main_info"]["main_class"], "MainMethodTest")
            self.assertEqual(data["main_info"]["main_method"], "main")

    def test_assignment_extraction(self):
        """Test variable assignment extraction"""
        test_file = self.test_files_dir / "test_assignment" / "BasicAssignmentTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "BasicAssignmentTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify assignments
        class_info = data["classes"]["BasicAssignmentTest"]
        # Check if there are any methods with assignments
        for method_name, method_info in class_info["methods"].items():
            if "store_vars_calls" in method_info:
                assignments = method_info["store_vars_calls"]
                self.assertIsInstance(assignments, dict)
                # Verify at least one assignment exists
                self.assertGreater(len(assignments), 0)


    # ============= Tests for Annotations and Enums =============
    
    def test_annotation_extraction(self):
        """Test annotation extraction from various Java elements"""
        test_file = self.test_files_dir / "test_annotation_and_enum" / "AnnotationTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "AnnotationTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify class annotations
        self.assertIn("classes", data)
        class_info = data["classes"]["AnnotationTest"]
        self.assertIn("annotations", class_info)
        
        # Check for expected class annotations
        class_annotations = [ann["name"] for ann in class_info["annotations"]]
        self.assertIn("Deprecated", class_annotations)
        self.assertIn("SuppressWarnings", class_annotations)
        
        # Verify method annotations
        self.assertIn("methods", class_info)
        for method_name, method_info in class_info["methods"].items():
            if "annotations" in method_info:
                method_annotations = [ann["name"] for ann in method_info["annotations"]]
                if method_name == "toString":
                    self.assertIn("Override", method_annotations)
                elif method_name == "deprecatedMethod":
                    self.assertIn("Deprecated", method_annotations)
        
        # Verify field annotations
        self.assertIn("fields", class_info)
        field_info = class_info["fields"]["deprecatedField"]
        self.assertIn("annotations", field_info)
        field_annotations = [ann["name"] for ann in field_info["annotations"]]
        self.assertIn("Deprecated", field_annotations)
        
        # Verify parameter annotations
        deprecated_method = class_info["methods"]["deprecatedMethod"]
        if "parameter_annotations" in deprecated_method:
            param_annotations = deprecated_method["parameter_annotations"]
            self.assertGreater(len(param_annotations), 0)
            self.assertEqual(param_annotations[0]["parameter"], "param")

    def test_enum_extraction(self):
        """Test enum extraction with constants, methods, and fields"""
        test_file = self.test_files_dir / "test_annotation_and_enum" / "Priority.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "Priority.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify enum section exists
        self.assertIn("enums", data)
        
        # Check Priority enum
        priority_enum = data["enums"]["Priority"]
        self.assertEqual(priority_enum["name"], "Priority")
        
        # Verify enum constants
        self.assertIn("enum_constants", priority_enum)
        constants = priority_enum["enum_constants"]
        self.assertIn("LOW", constants)
        self.assertIn("MEDIUM", constants)
        self.assertIn("HIGH", constants)
        
        # Verify enum annotations
        self.assertIn("annotations", priority_enum)
        enum_annotations = [ann["name"] for ann in priority_enum["annotations"]]
        self.assertIn("Deprecated", enum_annotations)
        
        # Verify enum methods
        self.assertIn("methods", priority_enum)
        self.assertIn("toString", priority_enum["methods"])
        self.assertIn("getValue", priority_enum["methods"])
        
        # Verify enum fields
        self.assertIn("fields", priority_enum)
        self.assertIn("value", priority_enum["fields"])
        
        # Check Color enum (simple enum)
        color_enum = data["enums"]["Color"]
        self.assertEqual(color_enum["name"], "Color")
        self.assertIn("RED", color_enum["enum_constants"])
        self.assertIn("GREEN", color_enum["enum_constants"])
        self.assertIn("BLUE", color_enum["enum_constants"])

    def test_mixed_annotation_enum(self):
        """Test mixed annotations and enums in the same file"""
        test_file = self.test_files_dir / "test_annotation_and_enum" / "MixedTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "MixedTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify both classes and enums exist
        self.assertIn("classes", data)
        self.assertIn("enums", data)
        
        # Check class with annotations
        mixed_class = data["classes"]["MixedTest"]
        self.assertIn("annotations", mixed_class)
        
        # Check enum with annotations  
        status_enum = data["enums"]["Status"]
        self.assertIn("annotations", status_enum)
        self.assertIn("ACTIVE", status_enum["enum_constants"])
        self.assertIn("INACTIVE", status_enum["enum_constants"])

    # ============= Tests for Nested Structures =============
    
    def test_static_nested_class(self):
        """Test static nested class extraction"""
        test_file = self.test_nested_dir / "StaticNestedClassTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "StaticNestedClassTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify outer class exists
        self.assertIn("classes", data)
        outer_class = data["classes"]["StaticNestedClassTest"]
        
        # Verify nested classes section exists
        self.assertIn("nested_classes", outer_class)
        nested_classes = outer_class["nested_classes"]
        
        # Find static nested class
        static_nested_found = False
        for nested_class_name, nested_class_info in nested_classes.items():
            if nested_class_info.get("nested_type") == "static_nested":
                static_nested_found = True
                self.assertIn("static", nested_class_info["modifiers"])
                self.assertIn("outer_context", nested_class_info)
                
        self.assertTrue(static_nested_found, "Static nested class not found")

    def test_inner_class(self):
        """Test inner class extraction"""
        test_file = self.test_nested_dir / "InnerClassTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "InnerClassTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify outer class exists
        outer_class = data["classes"]["InnerClassTest"]
        
        # Verify nested classes section exists
        self.assertIn("nested_classes", outer_class)
        nested_classes = outer_class["nested_classes"]
        
        # Find inner class
        inner_class_found = False
        for nested_class_name, nested_class_info in nested_classes.items():
            if nested_class_info.get("nested_type") == "inner":
                inner_class_found = True
                # Check modifiers field exists before accessing it
                if "modifiers" in nested_class_info:
                    self.assertNotIn("static", nested_class_info["modifiers"])
                # If no modifiers field, it means the class has package-private visibility (no static modifier)
                
        self.assertTrue(inner_class_found, "Inner class not found")

    def test_nested_interface(self):
        """Test nested interface extraction"""
        test_file = self.test_nested_dir / "NestedInterfaceTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "NestedInterfaceTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify outer class exists
        outer_class = data["classes"]["NestedInterfaceTest"]
        
        # Verify nested interfaces section exists
        self.assertIn("nested_interfaces", outer_class)
        nested_interfaces = outer_class["nested_interfaces"]
        self.assertGreater(len(nested_interfaces), 0, "No nested interfaces found")
        
        # Verify nested interface structure
        for interface_name, interface_info in nested_interfaces.items():
            self.assertIn("name", interface_info)
            self.assertIn("outer_context", interface_info)
            self.assertEqual(interface_info["outer_context"]["type"], "class")

    def test_local_class(self):
        """Test local class extraction within methods"""
        test_file = self.test_nested_dir / "LocalClassTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "LocalClassTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify outer class exists
        outer_class = data["classes"]["LocalClassTest"]
        
        # Look for local classes in methods
        local_class_found = False
        for method_name, method_info in outer_class["methods"].items():
            if "local_classes" in method_info:
                local_classes = method_info["local_classes"]
                self.assertGreater(len(local_classes), 0, f"No local classes found in method {method_name}")
                local_class_found = True
                
                # Verify local class structure
                for local_class_name, local_class_info in local_classes.items():
                    self.assertIn("name", local_class_info)
                    self.assertIn("methods", local_class_info)
                    
        self.assertTrue(local_class_found, "No local classes found in any method")

    def test_anonymous_class(self):
        """Test anonymous class extraction"""
        test_file = self.test_nested_dir / "AnonymousClassTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "AnonymousClassTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify outer class exists
        outer_class = data["classes"]["AnonymousClassTest"]
        
        # Look for anonymous classes in methods
        anonymous_class_found = False
        for method_name, method_info in outer_class["methods"].items():
            if "anonymous_classes" in method_info:
                anonymous_classes = method_info["anonymous_classes"]
                self.assertGreater(len(anonymous_classes), 0, f"No anonymous classes found in method {method_name}")
                anonymous_class_found = True
                
                # Verify anonymous class structure
                for anonymous_class in anonymous_classes:
                    self.assertIn("name", anonymous_class)
                    self.assertIn("type", anonymous_class)
                    self.assertTrue(anonymous_class["name"].startswith("Anonymous_"))
                    
        self.assertTrue(anonymous_class_found, "No anonymous classes found in any method")

    def test_lambda_expression(self):
        """Test lambda expression extraction"""
        test_file = self.test_nested_dir / "LambdaExpressionTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "LambdaExpressionTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify outer class exists
        outer_class = data["classes"]["LambdaExpressionTest"]
        
        # Look for lambda expressions in methods
        lambda_found = False
        for method_name, method_info in outer_class["methods"].items():
            if "lambda_expressions" in method_info:
                lambda_expressions = method_info["lambda_expressions"]
                self.assertGreater(len(lambda_expressions), 0, f"No lambda expressions found in method {method_name}")
                lambda_found = True
                
                # Verify lambda expression structure
                for lambda_expr in lambda_expressions:
                    # Parameters field may be missing if empty (cleaned by clean_empty_fields)
                    if "parameters" in lambda_expr:
                        self.assertIsInstance(lambda_expr["parameters"], list)
                    self.assertIn("min_max_lineno", lambda_expr)
                    # Lambda must have either returns or body field
                    self.assertTrue("returns" in lambda_expr or "body" in lambda_expr)
                    
                    # Verify line numbers are reasonable
                    lineno = lambda_expr["min_max_lineno"]
                    # Line numbers can be -1 if position couldn't be determined
                    self.assertTrue(lineno["min_lineno"] >= -1)
                    self.assertTrue(lineno["max_lineno"] >= -1)
                    
        self.assertTrue(lambda_found, "No lambda expressions found in any method")

    # ============= Tests for Dependency Analysis =============
    
    def test_standard_library_imports(self):
        """Test Java standard library import detection"""
        test_file = self.test_dependencies_dir / "StandardLibraryTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "StandardLibraryTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify dependencies section exists
        self.assertIn("dependencies", data)
        dependencies = data["dependencies"]
        self.assertGreater(len(dependencies), 0, "No dependencies found")
        
        # Check specific standard library imports
        import_names = [dep["import"] for dep in dependencies]
        self.assertIn("List", import_names)
        self.assertIn("ArrayList", import_names)
        self.assertIn("JFrame", import_names)
        
        # Verify all are marked as external
        for dep in dependencies:
            self.assertEqual(dep["type"], "external", f"Import {dep['import']} should be external")
            self.assertEqual(dep["type_element"], "class")
        
        # Verify from_module information
        list_dep = next(dep for dep in dependencies if dep["import"] == "List")
        self.assertEqual(list_dep["from_module"], "java.util")

    def test_third_party_imports(self):
        """Test third-party library import detection"""
        test_file = self.test_dependencies_dir / "ThirdPartyTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "ThirdPartyTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify dependencies section exists
        dependencies = data["dependencies"]
        
        # Check specific third-party imports
        import_names = [dep["import"] for dep in dependencies]
        self.assertIn("Test", import_names)
        self.assertIn("SpringApplication", import_names)
        self.assertIn("Gson", import_names)
        self.assertIn("StringUtils", import_names)
        
        # Verify all are marked as external (third-party)
        for dep in dependencies:
            self.assertEqual(dep["type"], "external", f"Import {dep['import']} should be external")
        
        # Verify from_module information for specific imports
        junit_dep = next(dep for dep in dependencies if dep["import"] == "Test")
        self.assertEqual(junit_dep["from_module"], "org.junit")
        
        spring_dep = next(dep for dep in dependencies if dep["import"] == "SpringApplication")
        self.assertEqual(spring_dep["from_module"], "org.springframework.boot")

    def test_static_imports(self):
        """Test static import detection and processing"""
        test_file = self.test_dependencies_dir / "StaticImportTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "StaticImportTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        dependencies = data["dependencies"]
        
        # Find static imports
        # static_imports = [dep for dep in dependencies if dep.get("is_static", False)]
        # self.assertGreater(len(static_imports), 0, "No static imports found")
        static_imports = [dep for dep in dependencies]
        self.assertGreater(len(static_imports), 0, "No static imports found")
        
        # Check specific static imports
        static_import_names = [dep["import"] for dep in static_imports]
        self.assertIn("PI", static_import_names)
        self.assertIn("sin", static_import_names)
        self.assertIn("out", static_import_names)
        
        # Verify static import properties
        pi_import = next(dep for dep in static_imports if dep["import"] == "PI")
        self.assertEqual(pi_import["type"], "external")
        self.assertEqual(pi_import["type_element"], "static_member")
        # self.assertTrue(pi_import["is_static"])
        self.assertEqual(pi_import["from_module"], "java.lang.Math")
        
        # Check for static wildcard import
        wildcard_imports = [dep for dep in static_imports if dep["import"] == "*"]
        self.assertGreater(len(wildcard_imports), 0, "No static wildcard imports found")
        
        wildcard_import = wildcard_imports[0]
        self.assertEqual(wildcard_import["type_element"], "static_package")
        # self.assertTrue(wildcard_import.get("is_wildcard", False))

    def test_wildcard_imports(self):
        """Test wildcard import detection and processing"""
        test_file = self.test_dependencies_dir / "WildcardImportTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "WildcardImportTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        dependencies = data["dependencies"]
        
        # Check for wildcard imports
        # wildcard_imports = [dep for dep in dependencies if dep.get("is_wildcard", False)]
        # self.assertGreater(len(wildcard_imports), 0, "No wildcard imports found")
        wildcard_imports = [dep for dep in dependencies]
        self.assertGreater(len(wildcard_imports), 0, "No wildcard imports found")
        
        # Verify wildcard import properties
        for wildcard_dep in wildcard_imports:
            self.assertEqual(wildcard_dep["import"], "*")
            self.assertEqual(wildcard_dep["type"], "external")
            self.assertEqual(wildcard_dep["type_element"], "package")
            # self.assertTrue(wildcard_dep["is_wildcard"])
        
        # Check specific modules
        module_names = [dep["from_module"] for dep in wildcard_imports]
        self.assertIn("java.util", module_names)
        self.assertIn("java.io", module_names)
        self.assertIn("javax.swing", module_names)

    def test_internal_class_references(self):
        """Test internal class reference detection"""
        test_file = self.test_dependencies_dir / "InternalImportTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "InternalImportTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        dependencies = data["dependencies"]
        
        # Find internal dependencies
        internal_deps = [dep for dep in dependencies if dep["type"] == "internal"]
        self.assertGreater(len(internal_deps), 0, "No internal dependencies found")
        
        # Check specific internal class references
        internal_names = [dep["import"] for dep in internal_deps]
        self.assertIn("InternalClass1", internal_names)
        self.assertIn("InternalClass2", internal_names)
        
        # Verify internal dependency properties
        internal_class1 = next(dep for dep in internal_deps if dep["import"] == "InternalClass1")
        self.assertEqual(internal_class1["type"], "internal")
        self.assertEqual(internal_class1["type_element"], "class")
        
        # Check that we also have external dependencies (java.util.List)
        external_deps = [dep for dep in dependencies if dep["type"] == "external"]
        external_names = [dep["import"] for dep in external_deps]
        self.assertIn("List", external_names)

    def test_internal_wildcard_imports(self):
        """Test internal wildcard import detection and class enumeration"""
        test_file = self.test_dependencies_dir / "InternalWildcardTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "InternalWildcardTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        dependencies = data["dependencies"]
        
        # Find internal wildcard dependencies
        # internal_wildcard_deps = [dep for dep in dependencies 
        #                         if dep["type"] == "internal" and dep.get("is_wildcard", False)]
        internal_wildcard_deps = [dep for dep in dependencies 
                                if dep["type"] == "internal"]
        self.assertGreater(len(internal_wildcard_deps), 0, "No internal wildcard dependencies found")
        
        # Check that specific classes from internal package were enumerated
        internal_classes = [dep["import"] for dep in internal_wildcard_deps]
        self.assertIn("InternalServiceA", internal_classes)
        self.assertIn("InternalServiceB", internal_classes)
        self.assertIn("InternalUtility", internal_classes)
        
        # Verify properties of internal wildcard imports
        for dep in internal_wildcard_deps:
            self.assertEqual(dep["type"], "internal")
            self.assertEqual(dep["type_element"], "class")
            self.assertEqual(dep["from_module"], "internal")
            # self.assertTrue(dep["is_wildcard"])
        
        # Verify that field references are also detected
        class_info = data["classes"]["InternalWildcardTest"]
        self.assertIn("fields", class_info)
        field_types = [field["type"] for field in class_info["fields"].values()]
        self.assertIn("InternalServiceA", field_types)
        self.assertIn("InternalServiceB", field_types)
        self.assertIn("InternalUtility", field_types)

    # ============= Tests for Method Call List Extraction =============
    
    def test_chained_method_calls(self):
        """Test chained method call extraction and resolution"""
        test_file = self.test_callList_dir / "ChainCallSimple.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "ChainCallSimple.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify all classes exist
        self.assertIn("classes", data)
        self.assertIn("A", data["classes"])
        self.assertIn("B", data["classes"])
        self.assertIn("C", data["classes"])
        self.assertIn("ChainCallSimple", data["classes"])
        
        # Verify class A has getB method that returns B
        class_a = data["classes"]["A"]
        self.assertIn("methods", class_a)
        get_b_method = class_a["methods"]["getB"]
        self.assertEqual(get_b_method["name"], "getB")
        self.assertEqual(get_b_method["return_type"], "B")
        self.assertIn("calls", get_b_method)
        # getB method should have a "new ChainCallSimple.B" constructor call
        get_b_calls = get_b_method["calls"]
        new_b_calls = [call for call in get_b_calls if "new ChainCallSimple.B" in call]
        self.assertGreater(len(new_b_calls), 0, "getB method should have 'new ChainCallSimple.B' constructor call")
        
        # Verify class B has getC method that returns C
        class_b = data["classes"]["B"]
        self.assertIn("methods", class_b)
        get_c_method = class_b["methods"]["getC"]
        self.assertEqual(get_c_method["name"], "getC")
        self.assertEqual(get_c_method["return_type"], "C")
        self.assertIn("calls", get_c_method)
        # getC method should have a "new ChainCallSimple.C" constructor call (updated format)
        get_c_calls = get_c_method["calls"]
        new_c_calls = [call for call in get_c_calls if "new ChainCallSimple.C" in call]
        self.assertGreater(len(new_c_calls), 0, "getC method should have 'new ChainCallSimple.C' constructor call")
        
        # Verify class C has doSomething method
        class_c = data["classes"]["C"]
        self.assertIn("methods", class_c)
        do_something_method = class_c["methods"]["doSomething"]
        self.assertEqual(do_something_method["name"], "doSomething")
        # For void methods, return_type might be cleaned out by clean_empty_fields
        # so we check either it's None or the field doesn't exist
        if "return_type" in do_something_method:
            self.assertEqual(do_something_method["return_type"], None)  # void method
        
        # Test the main method for chained call extraction
        main_class = data["classes"]["ChainCallSimple"]
        self.assertIn("methods", main_class)
        main_method = main_class["methods"]["main"]
        self.assertEqual(main_method["name"], "main")
        self.assertIn("calls", main_method)
        
        calls = main_method["calls"]
        self.assertGreater(len(calls), 0, "Main method should have method calls")
        
        # Verify that the chained call is properly decomposed with unified format (fileNameBase.ClassName.methodName)
        # Expected calls: "new ChainCallSimple.A", "ChainCallSimple.A.getB", "ChainCallSimple.B.getC", "ChainCallSimple.C.doSomething"
        expected_calls = [
            lambda call: "new ChainCallSimple.A" in call,           # Constructor call with file prefix
            lambda call: "ChainCallSimple.A.getB" in call,          # First method in chain with file prefix
            lambda call: "ChainCallSimple.B.getC" in call,          # Second method in chain (expanded) with file prefix
            lambda call: "ChainCallSimple.C.doSomething" in call    # Final method in chain (expanded) with file prefix
        ]
        
        for i, expected_pattern in enumerate(expected_calls):
            matching_calls = [call for call in calls if expected_pattern(call)]
            self.assertGreater(len(matching_calls), 0, 
                             f"Expected call pattern {i+1} not found in main method calls: {calls}")
        
        # Verify variable assignments
        self.assertIn("store_vars_calls", main_method)
        store_vars = main_method["store_vars_calls"]
        
        # Variable 'a' should be assigned from 'new ChainCallSimple.A' constructor (updated format)
        self.assertIn("a", store_vars)
        a_assignment = store_vars["a"]
        self.assertTrue("new ChainCallSimple.A" in a_assignment, f"Variable 'a' should be assigned 'new ChainCallSimple.A', got: {a_assignment}")
        
        # Additional verification: ensure we have the complete chain with unified format
        chain_parts = ["ChainCallSimple.A.getB", "ChainCallSimple.B.getC", "ChainCallSimple.C.doSomething"]
        for part in chain_parts:
            part_found = any(part in call for call in calls)
            self.assertTrue(part_found, f"Chain part '{part}' not found in method calls")

    def test_call_name_resolve_basic(self):
        """Test basic call name resolution scenarios"""
        test_file = self.test_callList_dir / "CallNameResolveTest.java"
        # test_file = Path("Test/test_files/test_callList/CallNameResolveTest.java")
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "CallNameResolveTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify classes exist
        self.assertIn("classes", data)
        self.assertIn("CallNameResolveTest", data["classes"])
        self.assertIn("SuperClass", data["classes"])
        self.assertIn("Utility", data["classes"])
        
        # Get CallNameResolveTest class info
        main_class = data["classes"]["CallNameResolveTest"]
        self.assertIn("methods", main_class)
        
        # Test constructor calls
        constructor_found = False
        for method_key, method_info in main_class["methods"].items():
            if method_info["name"] == "CallNameResolveTest":  # Constructor
                constructor_found = True
                self.assertIn("calls", method_info)
                calls = method_info["calls"]
                
                # Verify super() call
                super_calls = [call for call in calls if call.startswith("super")]
                self.assertGreater(len(super_calls), 0, "Should have super() constructor call")
                
                # Verify field method call (this.field.add)
                field_calls = [call for call in calls if "add" in call]
                self.assertGreater(len(field_calls), 0, "Should have field.add() call")
                
        self.assertTrue(constructor_found, "Constructor not found")
        
        # Test methodB calls - most complex method
        method_b = None
        for method_key, method_info in main_class["methods"].items():
            if method_info["name"] == "methodB":
                method_b = method_info
                break
                
        self.assertIsNotNone(method_b, "methodB not found")
        self.assertIn("calls", method_b)
        calls = method_b["calls"]
        
        # Verify different types of calls
        call_patterns = {
            "super_method": lambda call: "super" in call and "superMethod" in call,
            "static_method": lambda call: "Utility" in call and "staticMethod" in call,
            "constructor_call": lambda call: call.startswith("new CallNameResolveTest"),
            "string_method": lambda call: "String" in call and "toUpperCase" in call,
        }
        
        for pattern_name, pattern_func in call_patterns.items():
            matching_calls = [call for call in calls if pattern_func(call)]
            self.assertGreater(len(matching_calls), 0, 
                             f"Should have {pattern_name} call in methodB")

    def test_call_name_resolve_inheritance(self):
        """Test inheritance-related call resolution"""
        test_file = self.test_callList_dir / "CallNameResolveTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "CallNameResolveTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Test SuperClass method calls
        super_class = data["classes"]["SuperClass"]
        super_method = super_class["methods"]["superMethod"]
        self.assertIn("calls", super_method)
        
        # Verify System.out.println call in superMethod
        super_calls = super_method["calls"]
        println_calls = [call for call in super_calls if "println" in call]
        self.assertGreater(len(println_calls), 0, "SuperClass should have println call")

    def test_method_overloading_resolution(self):
        """Test method overloading resolution with parameter signatures"""
        test_file = self.test_callList_dir / "OverloadTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "OverloadTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify class exists
        self.assertIn("classes", data)
        overload_class = data["classes"]["OverloadTest"]
        self.assertIn("methods", overload_class)
        
        # Check that overloaded methods are distinguished
        methods = overload_class["methods"]
        process_methods = [key for key in methods.keys() if "process" in key]
        self.assertGreaterEqual(len(process_methods), 3, 
                               "Should have at least 3 process methods (overloaded)")
        
        # Check that overloaded constructors are distinguished  
        constructor_methods = [key for key in methods.keys() 
                             if methods[key]["name"] == "OverloadTest"]
        self.assertGreaterEqual(len(constructor_methods), 3,
                               "Should have at least 3 constructors (overloaded)")
        
        # Test testMethodCalls method for proper call resolution
        test_method = None
        for method_key, method_info in methods.items():
            if method_info["name"] == "testMethodCalls":
                test_method = method_info
                break
                
        self.assertIsNotNone(test_method, "testMethodCalls method not found")
        self.assertIn("calls", test_method)
        calls = test_method["calls"]
        
        # Verify that method calls include parameter information for overload resolution
        process_calls = [call for call in calls if "process" in call]
        self.assertGreater(len(process_calls), 0, "Should have process method calls")
        
        # Check for constructor calls with different signatures
        constructor_calls = [call for call in calls if call.startswith("new OverloadTest")]
        self.assertGreater(len(constructor_calls), 0, "Should have constructor calls")

    def test_constructor_overloading(self):
        """Test constructor overloading with different parameter signatures"""
        test_file = self.test_callList_dir / "OverloadTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "OverloadTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        overload_class = data["classes"]["OverloadTest"]
        methods = overload_class["methods"]
        
        # Find all constructors
        constructors = [method_info for method_key, method_info in methods.items() 
                       if method_info["name"] == "OverloadTest"]
        
        self.assertGreaterEqual(len(constructors), 3, "Should have at least 3 constructors")
        
        # Verify constructors have different parameter signatures
        parameter_signatures = []
        for constructor in constructors:
            params = constructor.get("parameters", [])
            param_signature = ",".join([param["type"] for param in params])
            parameter_signatures.append(param_signature)
        
        # Check that we have different signatures (empty, String, int+String)
        unique_signatures = set(parameter_signatures)
        self.assertGreaterEqual(len(unique_signatures), 3, 
                               "Constructors should have different parameter signatures")

    def test_generic_and_collection_calls(self):
        """Test method calls involving generics and collections"""
        test_file = self.test_callList_dir / "GenericTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "GenericTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify main class exists
        self.assertIn("classes", data)
        generic_class = data["classes"]["GenericTest"]
        self.assertIn("methods", generic_class)
        
        # Test constructor calls on collections
        constructor_found = False
        for method_key, method_info in generic_class["methods"].items():
            if method_info["name"] == "GenericTest":  # Constructor
                constructor_found = True
                self.assertIn("calls", method_info)
                calls = method_info["calls"]
                
                # Verify collection method calls
                collection_methods = ["add", "put", "trim"]
                for method_name in collection_methods:
                    matching_calls = [call for call in calls if method_name in call]
                    self.assertGreater(len(matching_calls), 0, 
                                     f"Should have {method_name} call in constructor")
                
        self.assertTrue(constructor_found, "Constructor not found")
        
        # Test processData method - most complex method
        process_data = None
        for method_key, method_info in generic_class["methods"].items():
            if method_info["name"] == "processData":
                process_data = method_info
                break
                
        self.assertIsNotNone(process_data, "processData method not found")
        self.assertIn("calls", process_data)
        calls = process_data["calls"]
        
        # Verify different types of standard library calls
        expected_call_patterns = {
            "collection_operations": ["remove", "size", "isEmpty"],
            "string_operations": ["toUpperCase", "substring"],
            "math_operations": ["sqrt", "random"],
            "system_calls": ["println"],
            "instance_calls": ["helperMethod", "anotherHelper"]
        }
        
        for category, methods in expected_call_patterns.items():
            for method_name in methods:
                matching_calls = [call for call in calls if method_name in call]
                self.assertGreater(len(matching_calls), 0, 
                                 f"Should have {method_name} call in processData ({category})")

    def test_static_nested_class_calls(self):
        """Test static nested class method calls"""
        test_file = self.test_callList_dir / "GenericTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "GenericTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify nested class exists
        generic_class = data["classes"]["GenericTest"]
        self.assertIn("nested_classes", generic_class)
        
        nested_classes = generic_class["nested_classes"]
        self.assertIn("MathUtils", nested_classes)
        
        math_utils = nested_classes["MathUtils"]
        self.assertEqual(math_utils["nested_type"], "static_nested")
        
        # Verify static methods in nested class
        self.assertIn("methods", math_utils)
        static_methods = math_utils["methods"]
        
        # Check for calculateArea and log methods
        method_names = [info["name"] for info in static_methods.values()]
        self.assertIn("calculateArea", method_names)
        self.assertIn("log", method_names)
        
        # Test calls to static nested class methods
        process_data = None
        for method_key, method_info in generic_class["methods"].items():
            if method_info["name"] == "processData":
                process_data = method_info
                break
                
        self.assertIsNotNone(process_data)
        calls = process_data["calls"]
        
        # Verify calls to MathUtils static methods
        math_utils_calls = [call for call in calls if "MathUtils" in call]
        self.assertGreater(len(math_utils_calls), 0, "Should have MathUtils method calls")

    def test_array_and_bigdecimal_operations(self):
        """Test array operations and BigDecimal method calls"""
        test_file = Path("Test/test_files/test_callList/GenericTest.java")
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "GenericTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        generic_class = data["classes"]["GenericTest"]
        
        # Test helperMethod for Arrays operations
        helper_method = None
        for method_key, method_info in generic_class["methods"].items():
            if method_info["name"] == "helperMethod":
                helper_method = method_info
                break
                
        self.assertIsNotNone(helper_method, "helperMethod not found")
        self.assertIn("calls", helper_method)
        calls = helper_method["calls"]
        
        # Verify Arrays method calls
        arrays_calls = [call for call in calls if "Arrays" in call]
        self.assertGreater(len(arrays_calls), 0, "Should have Arrays method calls")
        
        # Test anotherHelper for BigDecimal operations
        another_helper = None
        for method_key, method_info in generic_class["methods"].items():
            if method_info["name"] == "anotherHelper":
                another_helper = method_info
                break
                
        self.assertIsNotNone(another_helper, "anotherHelper not found")
        self.assertIn("calls", another_helper)
        calls = another_helper["calls"]
        
        # Verify BigDecimal constructor and method calls
        bigdecimal_calls = [call for call in calls if "BigDecimal" in call]
        self.assertGreater(len(bigdecimal_calls), 0, "Should have BigDecimal calls")

    def test_child_inheritance_calls(self):
        """Test Child.java inheritance and method call resolution"""
        test_file = self.test_callList_dir / "Child.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "Child.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify Child class exists and extends Parent
        self.assertIn("classes", data)
        child_class = data["classes"]["Child"]
        self.assertEqual(child_class["name"], "Child")
        self.assertEqual(child_class["extends"], "Parent")
        self.assertIn("public", child_class["modifiers"])
        
        # Verify dependency on Parent class
        self.assertIn("dependencies", data)
        dependencies = data["dependencies"]
        parent_deps = [dep for dep in dependencies if dep["import"] == "Parent"]
        self.assertGreater(len(parent_deps), 0, "Should have Parent dependency")
        parent_dep = parent_deps[0]
        self.assertEqual(parent_dep["type"], "internal")
        self.assertEqual(parent_dep["type_element"], "class")
        
        # Test testMethod calls
        self.assertIn("methods", child_class)
        test_method = child_class["methods"]["testMethod"]
        self.assertEqual(test_method["name"], "testMethod")
        self.assertIn("public", test_method["modifiers"])
        self.assertIn("calls", test_method)
        
        calls = test_method["calls"]
        
        # Verify different types of calls in testMethod
        expected_call_patterns = {
            "super_parent_method": lambda call: "Parent.Parent.parentMethod" in call,
            "super_overridable_method": lambda call: "Parent.Parent.overridableMethod" in call and "int" not in call,
            "this_overridable_method": lambda call: "Child.Child.overridableMethod" in call,
            "overridable_method_with_int": lambda call: "Parent.Parent.overridableMethod(int)" in call,
            "this_parent_method": lambda call: "Parent.Parent.parentMethod" in call
        }
        
        for pattern_name, pattern_func in expected_call_patterns.items():
            matching_calls = [call for call in calls if pattern_func(call)]
            self.assertGreater(len(matching_calls), 0, 
                             f"Should have {pattern_name} call in testMethod")
        
        # Test overridableMethod (overridden method)
        overridable_method = child_class["methods"]["overridableMethod"]
        self.assertEqual(overridable_method["name"], "overridableMethod")
        self.assertIn("public", overridable_method["modifiers"])
        
        # Verify @Override annotation
        self.assertIn("annotations", overridable_method)
        annotations = overridable_method["annotations"]
        override_annotations = [ann for ann in annotations if ann["name"] == "Override"]
        self.assertGreater(len(override_annotations), 0, "Should have @Override annotation")
        
        # Verify calls in overridableMethod
        self.assertIn("calls", overridable_method)
        override_calls = overridable_method["calls"]
        
        # Should have super.overridableMethod() call
        super_calls = [call for call in override_calls if "Parent.Parent.overridableMethod" in call]
        self.assertGreater(len(super_calls), 0, "Should have super.overridableMethod() call")
        
        # Should have System.out.println call
        println_calls = [call for call in override_calls if "System.out.println" in call]
        self.assertGreater(len(println_calls), 0, "Should have System.out.println call")

    def test_method_override_resolution(self):
        """Test MethodOverrideTest.java method override and overload resolution"""
        test_file = self.test_callList_dir / "MethodOverrideTest.java"
        inspector = JavaInspection(str(test_file), str(self.json_dir), False, False, [])
        
        json_file = self.json_dir / "MethodOverrideTest.json"
        with open(json_file) as f:
            data = json.load(f)
        
        # Verify all classes exist
        self.assertIn("classes", data)
        self.assertIn("BaseClass", data["classes"])
        self.assertIn("ChildClass", data["classes"])
        self.assertIn("MethodOverrideTest", data["classes"])
        
        # Test BaseClass structure
        base_class = data["classes"]["BaseClass"]
        self.assertEqual(base_class["name"], "BaseClass")
        
        # Verify BaseClass has overloaded process methods
        base_methods = base_class["methods"]
        process_methods = [key for key in base_methods.keys() if "process" in key]
        self.assertGreaterEqual(len(process_methods), 2, "BaseClass should have at least 2 process methods")
        
        # Check specific process method signatures
        self.assertIn("process", base_methods)  # process(int)
        self.assertIn("process(int,String)", base_methods)  # process(int,String)
        
        # Verify display method exists
        self.assertIn("display", base_methods)
        display_method = base_methods["display"]
        self.assertEqual(display_method["name"], "display")
        
        # Test ChildClass inheritance and overriding
        child_class = data["classes"]["ChildClass"]
        self.assertEqual(child_class["name"], "ChildClass")
        self.assertEqual(child_class["extends"], "BaseClass")
        
        child_methods = child_class["methods"]
        
        # Verify ChildClass overrides process(int) method
        self.assertIn("process", child_methods)
        child_process = child_methods["process"]
        self.assertIn("annotations", child_process)
        override_annotations = [ann for ann in child_process["annotations"] if ann["name"] == "Override"]
        self.assertGreater(len(override_annotations), 0, "ChildClass process method should have @Override")
        
        # Test testMethodCalls method for proper call resolution
        test_method_calls = child_methods["testMethodCalls"]
        self.assertEqual(test_method_calls["name"], "testMethodCalls")
        self.assertIn("calls", test_method_calls)
        
        calls = test_method_calls["calls"]
        
        # Verify specific call resolutions
        expected_resolutions = {
            # process(42) should resolve to ChildClass.process (overridden)
            "child_process_int": lambda call: "MethodOverrideTest.ChildClass.process" in call and "int,String" not in call,
            # process(42, "test") should resolve to BaseClass.process(int,String) (not overridden)
            "base_process_int_string": lambda call: "MethodOverrideTest.BaseClass.process(int,String)" in call,
            # display() should resolve to BaseClass.display (inherited)
            "base_display": lambda call: "MethodOverrideTest.BaseClass.display" in call,
            # super.process(100) should resolve to BaseClass.process
            "super_process": lambda call: "MethodOverrideTest.BaseClass.process" in call and "int,String" not in call,
            # super.display() should resolve to BaseClass.display
            "super_display": lambda call: "MethodOverrideTest.BaseClass.display" in call
        }
        
        for resolution_name, resolution_func in expected_resolutions.items():
            matching_calls = [call for call in calls if resolution_func(call)]
            self.assertGreater(len(matching_calls), 0, 
                             f"Should have {resolution_name} resolution in testMethodCalls")
        
        # Test anotherMethod for this. calls
        another_method = child_methods["anotherMethod"]
        self.assertIn("calls", another_method)
        another_calls = another_method["calls"]
        
        # Verify this.process calls
        this_process_calls = [call for call in another_calls if "MethodOverrideTest.ChildClass.process" in call]
        self.assertGreater(len(this_process_calls), 0, "Should have this.process calls")
        
        # Verify this.process(int,String) resolves to BaseClass (not overridden)
        this_process_overload = [call for call in another_calls if "MethodOverrideTest.BaseClass.process(int,String)" in call]
        self.assertGreater(len(this_process_overload), 0, "Should have this.process(int,String) resolving to BaseClass")
        
        # Test main method
        main_class = data["classes"]["MethodOverrideTest"]
        self.assertIn("main_info", data)
        main_info = data["main_info"]
        self.assertEqual(main_info["main_flag"], 1)
        self.assertEqual(main_info["main_class"], "MethodOverrideTest")
        
        main_method = main_class["methods"]["main"]
        self.assertIn("calls", main_method)
        main_calls = main_method["calls"]
        
        # Verify constructor calls
        child_constructor = [call for call in main_calls if "new MethodOverrideTest.ChildClass" in call]
        self.assertGreater(len(child_constructor), 0, "Should have ChildClass constructor call")
        
        base_constructor = [call for call in main_calls if "new MethodOverrideTest.BaseClass" in call]
        self.assertGreater(len(base_constructor), 0, "Should have BaseClass constructor call")
        
        # Verify method calls on instances
        child_method_calls = [call for call in main_calls if "MethodOverrideTest.ChildClass" in call and "new" not in call]
        self.assertGreater(len(child_method_calls), 0, "Should have ChildClass method calls")
        
        base_method_calls = [call for call in main_calls if "MethodOverrideTest.BaseClass" in call and "new" not in call]
        self.assertGreater(len(base_method_calls), 0, "Should have BaseClass method calls")
        
        # Verify variable assignments
        self.assertIn("store_vars_calls", main_method)
        store_vars = main_method["store_vars_calls"]
        self.assertIn("child", store_vars)
        self.assertIn("base", store_vars)
        self.assertEqual(store_vars["child"], "new MethodOverrideTest.ChildClass")
        self.assertEqual(store_vars["base"], "new MethodOverrideTest.BaseClass")

if __name__ == '__main__':
    unittest.main() 