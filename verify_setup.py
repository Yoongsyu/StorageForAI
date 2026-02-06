import sys
import importlib.util

def check_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    if spec is None:
        print(f"[MISSING] {package_name} (import: {import_name}) not found.")
        return False
    else:
        try:
            module = __import__(import_name)
            # Try to get version from the module, or submodules if needed
            version = getattr(module, "__version__", "unknown")
            print(f"[OK] {package_name} found (version: {version})")
            return True
        except ImportError as e:
            print(f"[ERROR] {package_name} found but could not be imported: {e}")
            return False

# List of (Package Name, Import Name)
# If Import Name is same as Package Name, can use None
required_packages = [
    ("streamlit", "streamlit"),
    ("google-generativeai", "google.generativeai"),
    ("requests", "requests"),
    ("feedparser", "feedparser"),
    ("PyGithub", "github")
]

print(f"Python Executable: {sys.executable}")
print("-" * 30)

all_good = True
for pkg_name, imp_name in required_packages:
    if not check_package(pkg_name, imp_name):
        all_good = False

print("-" * 30)
if all_good:
    print("SUCCESS: All required packages are installed correctly in this environment!")
else:
    print("WARNING: Some packages are missing or broken.")
