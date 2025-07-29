#!/usr/bin/env python3
"""
inspect4j - Java code inspection tool
Command-line interface for Java code analysis
"""

import argparse
import sys
import os
from pathlib import Path

# Import the main inspector functionality
from .java_inspector import main as java_inspector_main
from . import __version__


def main():
    """Main CLI entry point for inspect4j"""
    parser = argparse.ArgumentParser(
        description='inspect4j - Java code inspection and analysis tool',
        prog='inspect4j'
    )
    
    parser.add_argument('--version', action='version', version=f'inspect4j {__version__}')
    
    parser.add_argument('-i', '--input', required=True, 
                       help='Input Java file or directory to inspect')
    
    parser.add_argument('-o', '--output', default='output_dir',
                       help='Output directory for results (default: output_dir)')
    
    parser.add_argument('-cl', '--call-list', action='store_true',
                       help='Generate call list in HTML and JSON format')
    
    parser.add_argument('-html', '--html-output', action='store_true',
                       help='Generate HTML output for visualization')
    
    parser.add_argument('-dt', '--directory-tree', action='store_true',
                       help='Extract directory tree structure')
    
    parser.add_argument('-ld', '--license-detection', action='store_true',
                       help='Detect license information')
    
    parser.add_argument('-rm', '--readme', action='store_true',
                       help='Extract README files')
    
    parser.add_argument('-md', '--metadata', action='store_true',
                       help='Extract GitHub metadata')
    
    parser.add_argument('-r', '--requirements', action='store_true',
                       help='Extract Java dependencies (Maven/Gradle)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert to the format expected by java_inspector_main
    sys.argv = ['inspect4j']
    
    # Add arguments in the order expected by java_inspector_main
    sys.argv.extend(['-i', args.input])
    sys.argv.extend(['-o', args.output])
    
    if args.call_list:
        sys.argv.append('-cl')
    
    if args.html_output:
        sys.argv.append('-html')
    
    if args.directory_tree:
        sys.argv.append('-dt')
    
    if args.license_detection:
        sys.argv.append('-ld')
    
    if args.readme:
        sys.argv.append('-rm')
    
    if args.metadata:
        sys.argv.append('-md')
    
    if args.requirements:
        sys.argv.append('-r')
    
    # Call the main java inspector function
    try:
        java_inspector_main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main() 