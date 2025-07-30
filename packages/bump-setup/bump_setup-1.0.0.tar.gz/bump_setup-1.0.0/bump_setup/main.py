import sys
import os
import re
from tree_sitter import Language, Parser
# Load Tree-sitter's Python language
PY_LANGUAGE = Language('tree-sitter-python.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)
def bump_version(file_path, version_type):
"""
Bumps the version in a `setup.py` file using Tree-sitter to find and modify the version keyword argument.
:param file_path: Path to the setup.py file
:param version_type: Type of version bump ('major', 'minor', or 'patch')
"""
# Read the content of the setup.py
with open(file_path, 'r') as f:
code = f.read()
# Parse the code to get the syntax tree
tree = parser.parse(bytes(code, 'utf8'))
# Function to check if setup is imported from setuptools
def check_setup_import(tree):
root_node = tree.root_node
for node in root_node.children:
if node.type == 'import_statement':
# Look for imports of setup from setuptools
# Check for 'from <module> import <name>'
for child in node.children:
if child.type == 'from':  # 'from' part of the import
module_node = child.child_by_field_name('module')
if module_node and code[module_node.start_byte:module_node.end_byte].decode('utf-8') == 'setuptools':
# Check if 'setup' is imported
import_node = child.child_by_field_name('import')
if import_node and code[import_node.start_byte:import_node.end_byte].decode('utf-8') == 'setup':
return True
return False
# Check if setup is imported from setuptools
if not check_setup_import(tree):
print(f"Error: 'setup' is not imported from 'setuptools' in {file_path}")
sys.exit(1)
# Function to find the setup() call and extract the version argument
def find_version_in_setup(tree):
root_node = tree.root_node
setup_node = None
# Iterate through the children of the root node
for node in root_node.children:
if node.type == 'call' and 'setup' in code[node.start_byte:node.end_byte].decode('utf-8'):
setup_node = node
break
if setup_node:
# Now find the version argument in the setup call
for child in setup_node.children:
if child.type == 'argument' and 'version' in code[child.start_byte:child.end_byte].decode('utf-8'):
return child
return None
# Find the version argument in setup()
version_node = find_version_in_setup(tree)
if version_node is None:
print(f"Version argument not found in setup() in {file_path}")
sys.exit(1)
# Extract the version string using regex
version_regex = r'(\d+)\.(\d+)\.(\d+)'
match = re.search(version_regex, code[version_node.start_byte:version_node.end_byte].decode('utf-8'))
if not match:
print(f"Could not extract version from {file_path}")
sys.exit(1)
major, minor, patch = map(int, match.groups())
# Bump the version based on the user's choice
if version_type == "major":
major += 1
minor = 0
patch = 0
elif version_type == "minor":
minor += 1
patch = 0
elif version_type == "patch":
patch += 1
else:
print(f"Invalid version type: {version_type}")
sys.exit(1)
new_version = f'{major}.{minor}.{patch}'
# Replace the version in the code with the new version
new_code = re.sub(version_regex, new_version, code)
# Write the modified code back to the file
with open(file_path, 'w') as f:
f.write(new_code)
print(f"Version bumped to {new_version}")
def main():
if len(sys.argv) < 2:
print("Usage: bump-setup <major|minor|patch>")
sys.exit(1)
# Set the file path to 'setup.py' in the current directory by default
file_path = sys.argv[1] if len(sys.argv) > 1 else 'setup.py'
# Check if the file exists
if not os.path.exists(file_path):
print(f"Error: {file_path} not found.")
sys.exit(1)
version_type = sys.argv[2] if len(sys.argv) > 2 else 'patch'
bump_version(file_path, version_type)
if __name__ == "__main__":
main()
