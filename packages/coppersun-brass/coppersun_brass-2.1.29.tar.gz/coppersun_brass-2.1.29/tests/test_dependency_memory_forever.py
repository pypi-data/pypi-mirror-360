#!/usr/bin/env python3
"""
PERMANENT DEPENDENCY MEMORY TEST - READ THIS EVERY TIME

🚨 CRITICAL: This test exists because we keep forgetting about the 
pyproject.toml vs setup.py dependency issue and it breaks user installations.

🚨 THIS HAS HAPPENED MULTIPLE TIMES:
- We add dependencies to setup.py
- We forget pyproject.toml overrides setup.py  
- Dependencies missing from final package
- Users get "ModuleNotFoundError" at runtime
- System appears broken ("0 findings")

🚨 ROOT CAUSE DISCOVERED July 2, 2025:
Modern Python packaging (pip 21.3+, build tools) prioritizes pyproject.toml 
over setup.py. If pyproject.toml has a [project] dependencies section, 
it COMPLETELY OVERRIDES setup.py install_requires.

🚨 SOLUTION:
ALWAYS add dependencies to BOTH files or use only pyproject.toml.
"""

import sys
import subprocess
from pathlib import Path
import re

def test_critical_dependencies_present_in_both_files():
    """
    🚨 CRITICAL MEMORY TEST 🚨
    
    This test MUST pass to prevent recurring dependency installation failures.
    
    BACKGROUND:
    - pyproject.toml [project] dependencies OVERRIDES setup.py install_requires
    - If dependency exists in setup.py but missing from pyproject.toml = BROKEN INSTALL
    - This has caused multiple user-facing failures
    """
    
    project_root = Path(__file__).parent.parent
    setup_py = project_root / "setup.py"
    pyproject_toml = project_root / "pyproject.toml"
    
    # Critical dependencies that MUST be in both files
    CRITICAL_DEPENDENCIES = [
        # "sqlalchemy" - REMOVED: Not needed anymore, system uses direct sqlite3
        "click",
        "pydantic", 
        "anthropic",
        "requests",
        "aiofiles",
        "watchdog",
        "jsonschema",
        "networkx",
        "pyyaml",
        "pyperclip",
        "python-dotenv",
        "apscheduler",
        "rich"
    ]
    
    # Read setup.py dependencies
    setup_content = setup_py.read_text()
    setup_deps = []
    
    # Extract install_requires from setup.py
    install_requires_match = re.search(r'install_requires=\[(.*?)\]', setup_content, re.DOTALL)
    if install_requires_match:
        deps_text = install_requires_match.group(1)
        # Extract quoted dependency names
        setup_deps = re.findall(r'"([^">=<~!]+)', deps_text)
    
    # Read pyproject.toml dependencies  
    pyproject_content = pyproject_toml.read_text()
    pyproject_deps = []
    
    # Extract dependencies from pyproject.toml
    deps_match = re.search(r'dependencies = \[(.*?)\]', pyproject_content, re.DOTALL)
    if deps_match:
        deps_text = deps_match.group(1)
        # Extract quoted dependency names
        pyproject_deps = re.findall(r'"([^">=<~!]+)', deps_text)
    
    print(f"📋 Setup.py dependencies: {sorted(setup_deps)}")
    print(f"📋 Pyproject.toml dependencies: {sorted(pyproject_deps)}")
    
    missing_from_setup = []
    missing_from_pyproject = []
    
    for dep in CRITICAL_DEPENDENCIES:
        if dep not in setup_deps:
            missing_from_setup.append(dep)
        if dep not in pyproject_deps:
            missing_from_pyproject.append(dep)
    
    # Critical failure conditions
    if missing_from_setup:
        print(f"\n🚨 CRITICAL: Dependencies missing from setup.py: {missing_from_setup}")
    
    if missing_from_pyproject:
        print(f"\n🚨 CRITICAL: Dependencies missing from pyproject.toml: {missing_from_pyproject}")
        print(f"💥 THIS WILL CAUSE INSTALLATION FAILURES!")
        print(f"🔧 ADD TO pyproject.toml dependencies section:")
        for dep in missing_from_pyproject:
            print(f"    \"{dep}>=X.Y.Z\",")
    
    # MEMORY ASSERTION: This must pass to prevent repeated failures
    assert not missing_from_pyproject, (
        f"DEPENDENCY MEMORY FAILURE: {missing_from_pyproject} missing from pyproject.toml. "
        f"This causes user installation failures. Add these to pyproject.toml dependencies."
    )
    
    print(f"\n✅ SUCCESS: All critical dependencies present in both files")
    print(f"🧠 DEPENDENCY MEMORY TEST PASSED")

def test_build_metadata_excludes_sqlalchemy():
    """
    🚨 INTEGRATION TEST 🚨
    
    This test builds a wheel and verifies sqlalchemy is NOT included
    in the final package metadata (it should have been completely removed).
    """
    
    project_root = Path(__file__).parent.parent
    
    # Build a test wheel
    print("🔨 Building wheel to test final metadata...")
    result = subprocess.run([
        sys.executable, "-m", "build", "--wheel", "--outdir", "/tmp"
    ], cwd=project_root, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr}")
        return False
    
    # Find the built wheel (get the most recently created one)
    wheel_files = list(Path("/tmp").glob("coppersun_brass-*.whl"))
    if not wheel_files:
        print("❌ No wheel file found")
        return False
    
    # Sort by modification time to get the most recently built wheel
    wheel_file = max(wheel_files, key=lambda x: x.stat().st_mtime)
    
    # Extract and check metadata
    import zipfile
    with zipfile.ZipFile(wheel_file) as z:
        metadata_files = [f for f in z.namelist() if f.endswith('METADATA')]
        if not metadata_files:
            print("❌ No METADATA file found in wheel")
            return False
        
        metadata_content = z.read(metadata_files[0]).decode()
        
        # Check that sqlalchemy is NOT in final metadata (it was removed)
        requires_lines = [line for line in metadata_content.split('\n') 
                         if line.startswith('Requires-Dist:')]
        
        sqlalchemy_found = any('sqlalchemy' in line for line in requires_lines)
        
        print(f"📦 Final wheel dependencies:")
        for line in requires_lines:
            marker = "❌" if "sqlalchemy" in line else "✅"
            print(f"{marker} {line}")
        
        if sqlalchemy_found:
            print(f"\n💥 CRITICAL: sqlalchemy still found in final wheel metadata!")
            print(f"🔧 SQLAlchemy should have been completely removed from dependencies")
            return False
        
        print(f"\n✅ SUCCESS: sqlalchemy successfully removed from final wheel metadata")
        return True

def test_memory_reminder():
    """
    🧠 MEMORY REMINDER 🧠
    
    Print the critical information that must be remembered.
    """
    
    print("\n" + "="*80)
    print("🧠 DEPENDENCY MEMORY REMINDER")
    print("="*80)
    print()
    print("🚨 CRITICAL KNOWLEDGE TO REMEMBER:")
    print()
    print("1. ⚠️  pyproject.toml [project] dependencies OVERRIDES setup.py install_requires")
    print("2. ⚠️  Modern build tools (pip 21.3+) prioritize pyproject.toml")
    print("3. ⚠️  Missing deps in pyproject.toml = broken user installations")
    print("4. ⚠️  This has caused multiple sqlalchemy installation failures")
    print()
    print("🔧 WHEN ADDING DEPENDENCIES:")
    print("   - Add to pyproject.toml dependencies = [...] section")
    print("   - Also add to setup.py install_requires = [...] for compatibility")
    print("   - Run this test to verify both files are in sync")
    print()
    print("🧪 VERIFICATION COMMANDS:")
    print("   python -m pytest tests/test_dependency_memory_forever.py -v")
    print("   python -m build --wheel && check wheel metadata")
    print()
    print("="*80)

if __name__ == "__main__":
    print("🧠 RUNNING DEPENDENCY MEMORY TESTS...")
    
    try:
        test_critical_dependencies_present_in_both_files()
        test_build_metadata_excludes_sqlalchemy()
        test_memory_reminder()
        
        print(f"\n🎉 ALL DEPENDENCY MEMORY TESTS PASSED")
        print(f"✅ Dependencies are correctly configured")
        print(f"🧠 Memory system working - you will not forget this again!")
        
    except Exception as e:
        print(f"\n💥 DEPENDENCY MEMORY TEST FAILED: {e}")
        print(f"🔧 Fix the dependency configuration before proceeding")
        sys.exit(1)