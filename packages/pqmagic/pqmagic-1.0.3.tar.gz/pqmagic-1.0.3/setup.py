import os
import sys
import subprocess
import shutil
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as build_ext_orig
from Cython.Build import cythonize

with open("README.md", "r", encoding="utf-8") as fh:
    ld = fh.read()

compile_args = {
    'linux': ['-O3'],
    'darwin': ['-O3', '-mmacosx-version-min=10.9'],
    'win32': ['/O2', '/EHsc']
}
link_args = {
    'linux': [],
    'darwin': ['-mmacosx-version-min=10.9'],
    'win32': []
}

platform = sys.platform

class build_ext(build_ext_orig):
    def run(self):
        self.compile_pqmagic()
        super().run()

    def _has_command(self,cmd):
        cmd = os.fspath(cmd)
        for path in os.environ.get("PATH", "").split(os.pathsep):
            full_path = os.path.join(path, cmd)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                return True
        return False

    # Function to compile and install the PQMagic C library
    def compile_pqmagic(self):
        platform = sys.platform         
        build_dir = os.path.join("pqmagic", "PQMagic", "build")
        install_dir = os.path.abspath(os.path.join(build_dir, "install"))  # Custom install directory
        os.makedirs(build_dir, exist_ok=True)

        if platform.startswith("linux") or platform == "darwin":
            # Check for CMake
            if not self._has_command("cmake"):
                sys.stderr.write("Error: CMake is required to build PQMagic. Please install it first.\n")
                sys.exit(1)
            cmake_cmd = ["cmake", "..", f"-DCMAKE_INSTALL_PREFIX={install_dir}"]
            make_cmd = ["make"]
            install_cmd = ["make", "install"]

        elif platform == "win32":
            if self._has_command("ninja"):
                cmake_cmd = ["cmake", "..", "-G", "Ninja", f"-DCMAKE_INSTALL_PREFIX={install_dir}"]
                make_cmd = ["ninja"]
                install_cmd = ["ninja", "install"]
            elif self._has_command("mingw32-make"):
                cmake_cmd = ["cmake", "..", "-G", "MinGW Makefiles", f"-DCMAKE_INSTALL_PREFIX={install_dir}"]
                make_cmd = ["mingw32-make"]
                install_cmd = ["mingw32-make", "install"]
            elif self._has_command("nmake"):
                cmake_cmd = ["cmake", "..", "-G", "NMake Makefiles", f"-DCMAKE_INSTALL_PREFIX={install_dir}"]
                make_cmd = ["nmake"]
                install_cmd = ["nmake", "install"]
            elif self._has_command("cmake"):
                # Try to find a Visual Studio generator if none of the above are found
                # This is a fallback, may need extra logic for arch selection
                cmake_cmd = ["cmake", "..", "-G", "Visual Studio 17 2022", f"-DCMAKE_INSTALL_PREFIX={install_dir}"]
                make_cmd = ["cmake", "--build", ".", "--config", "Release"]
                install_cmd = ["cmake", "--install", ".", "--config", "Release"]
            else:
                print("Error: No suitable build tool found. Please install Ninja, MinGW, or Visual Studio Build Tools.")
                sys.exit(1)
        else:
            print(f"Unsupported platform: {platform}")
            sys.exit(1)

        try:
            subprocess.check_call(cmake_cmd, cwd=build_dir)
            subprocess.check_call(make_cmd, cwd=build_dir)
            subprocess.check_call(install_cmd, cwd=build_dir)

        except FileNotFoundError as e:
            print(f"Build tool not found: {e}\n")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error during PQMagic compilation: {e}\n")
            sys.exit(1)

        try:
            # Copy the compiled library to the package directory
            if platform.startswith('linux'):
                lib_name1, lib_name2 = "libpqmagic.so", "libpqmagic_std.so"
            elif platform == 'darwin':
                lib_name1, lib_name2 = "libpqmagic.dylib", "libpqmagic_std.dylib"
            elif platform == 'win32':
                lib_name1, lib_name2 = "libpqmagic.dll", "libpqmagic_std.dll"
            build_lib_pqmagic = os.path.join(self.build_lib, "pqmagic")
            os.makedirs(build_lib_pqmagic, exist_ok=True)

            src1 = os.path.join(install_dir, "lib", lib_name1)
            dst1 = os.path.join(build_lib_pqmagic, lib_name1)
            src2 = os.path.join(install_dir, "lib", lib_name2)
            dst2 = os.path.join(build_lib_pqmagic, lib_name2)
            shutil.copy2(src1, dst1)
            shutil.copy2(src2, dst2)          
            
        except FileNotFoundError as e:
            print(f"Error copying library: {e}\n")
            sys.exit(1)

#--- Set rpath for extension ---
# The rpath must point to where the .so or .dylib will be at runtime, relative to the extension.
extra_link_args = link_args.get(platform, [])
if platform.startswith('linux'):
    extra_link_args.append("-Wl,-rpath,$ORIGIN")
elif platform == 'darwin':
    extra_link_args.append("-Wl,-rpath,@loader_path")

extensions = [
    Extension(
        name="pqmagic.pqmagic",
        sources=["pqmagic/pqmagic.pyx"],
        libraries=["pqmagic"],  # Link the compiled PQMagic-C library
        library_dirs=["pqmagic/PQMagic/build/install/lib"],
        include_dirs=["pqmagic/PQMagic/build/install/include"],
        extra_compile_args=compile_args.get(platform, []),
        extra_link_args=extra_link_args
    )
]

setup(
    name='pqmagic',
    version='1.0.3',
    install_requires=['Cython', 'wheel', 'setuptools'],
    homepage='https://pqcrypto.cn',
    description='The python bindings for PQMagic https://github.com/pqcrypto-cn/PQMagic',
    long_description=ld,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    ext_modules=cythonize(extensions),
    #options={"bdist_wheel": {"universal": True}},
    package_data={
        "pqmagic": [
            "*.pyx", 
            "*.pxd",
            "*.so",
            "*.dylib",
            "*.dll",
        ]
    },
    include_package_data=True,
    cmdclass={'build_ext': build_ext},
)