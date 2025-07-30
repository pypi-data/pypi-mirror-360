import os
import sys
import subprocess

def main():
    """Wrapper entry point to invoke dsniff C binaries."""
    bin_name = os.path.basename(sys.argv[0])
    pkg_dir = os.path.dirname(__file__)
    exe_path = os.path.join(pkg_dir, 'bin', bin_name)
    if not os.path.isfile(exe_path):
        sys.stderr.write(f"Executable {bin_name} not found at {exe_path}\n")
        return 1
    args = [exe_path] + sys.argv[1:]
    return subprocess.call(args)

if __name__ == "__main__":
    sys.exit(main())