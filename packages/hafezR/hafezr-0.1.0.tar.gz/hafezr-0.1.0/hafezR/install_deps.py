# hafezR/install_deps.py

import subprocess
from pathlib import Path

def check_and_install_gcc():
    try:
        output = subprocess.check_output(["gcc", "--version"], text=True)
        print("gcc is already installed:\n", output)
    except FileNotFoundError:
        print("gcc not found. Installing with brew...")
        subprocess.run(["brew", "install", "gcc"], check=True)

def configure_makevars():
    home = Path.home()
    r_dir = home / ".R"
    makevars_path = r_dir / "Makevars"

    r_dir.mkdir(parents=True, exist_ok=True)
    if not makevars_path.exists():
        makevars_path.touch()

    lines = [
        "FC = /opt/homebrew/Cellar/gcc/11.3.0_2/bin/gfortran",
        "F77 = /opt/homebrew/Cellar/gcc/11.3.0_2/bin/gfortran",
        "FLIBS = -L/opt/homebrew/Cellar/gcc/11.3.0_2/lib/gcc/11"
    ]

    with open(makevars_path, "a") as f:
        for line in lines:
            f.write(f"{line}\n")

def install_dependencies():
    check_and_install_gcc()
    configure_makevars()
    print("✅ GCC check complete and Makevars configured.")

