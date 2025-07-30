from skbuild import setup

setup(
    name="libcasm-clexulator",
    version="2.1.0",
    packages=["libcasm", "libcasm.clexulator"],
    package_dir={"": "python"},
    cmake_install_dir="python/libcasm",
    include_package_data=False,
)
