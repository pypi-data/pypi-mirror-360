import os
from functools import reduce
from pathlib import Path


class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


def get_directory_structure(rootdir, ignore_set):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        ignore = 0
        folders = path[start:].split(os.sep)
        for i in ignore_set:
            if i in folders:
                ignore = 1

        if not ignore:
            subdir = dict.fromkeys(files)
            subdir = dict_clean(subdir)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir

    return dir


def dict_clean(dictionary):
    """
    Clean dictionary and add file type information.
    Enhanced to support Java-specific file types.
    """
    result = {}
    for key, value in dictionary.items():
        if value is None and 'class' not in key:  # Changed from 'pyc' to 'class' for Java
            key_extension = key.split(".")[-1]

            # Java-specific file types
            if 'java' in key_extension:
                value = 'java source file'
            elif 'class' in key_extension:
                value = 'java class file'
            elif 'jar' in key_extension:
                value = 'java archive file'
            elif 'war' in key_extension:
                value = 'web archive file'
            elif 'ear' in key_extension:
                value = 'enterprise archive file'
            elif 'jsp' in key_extension:
                value = 'java server page'
            elif 'jspx' in key_extension:
                value = 'java server page xml'
            
            # Python files (in case of mixed projects)
            elif 'py' in key_extension and 'ipynb' not in key_extension and 'setup' not in key:
                value = 'python script'

            # Build and configuration files
            elif 'pom.xml' == key:
                value = 'maven project file'
            elif 'build.gradle' == key or 'build.gradle.kts' == key:
                value = 'gradle build file'
            elif 'settings.gradle' == key or 'settings.gradle.kts' == key:
                value = 'gradle settings file'
            elif 'ant.xml' == key or 'build.xml' == key:
                value = 'ant build file'
            elif 'requirements' in key:
                value = 'requirements file'

            # Text and documentation files
            elif 'txt' in key_extension or 'md' in key_extension:
                value = "text file"
            elif 'rst' in key_extension:
                value = "restructured text file"

            # Image and plot files
            elif 'png' in key_extension.lower() or 'svg' in key_extension.lower() or 'dot' in key_extension.lower():
                value = 'plot file'
            elif 'jpg' in key_extension.lower() or 'jpeg' in key_extension.lower():
                value = 'image file'

            # Container and deployment files
            elif 'Dockerfile' in key:
                value = 'docker file'
            elif 'docker-compose' in key:
                value = 'docker compose file'

            # Data files
            elif 'json' in key_extension:
                value = 'json file'
            elif 'xml' in key_extension or 'XML' in key_extension:
                value = 'xml file'
            elif 'properties' in key_extension:
                value = 'properties file'
            elif 'yaml' in key_extension or 'yml' in key_extension:
                value = 'yaml file'

            # Notebook files
            elif 'ipynb' in key_extension:
                value = 'notebook file'

            # Configuration files
            elif 'cfg' in key_extension or 'setup.py' in key:
                value = 'setup file'
            elif 'ini' in key_extension:
                value = 'configuration file'

            # Version control
            elif 'git' in key_extension:
                value = 'git file'
            
            # Other files
            else:
                value = key_extension.lower() + ' file'

        result[key] = value
    return result 