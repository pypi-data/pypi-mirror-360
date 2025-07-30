from skbuild import setup

setup(
    name="libcasm-xtal",
    version="2.1.0",
    packages=["libcasm", "libcasm.xtal"],
    package_dir={"": "python"},
    cmake_install_dir="python/libcasm",
    include_package_data=False,
)
