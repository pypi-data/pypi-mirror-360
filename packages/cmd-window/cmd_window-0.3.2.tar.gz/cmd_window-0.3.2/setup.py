from setuptools import setup, find_packages
import pathlib

# A README.md helyes elérési útja (a setup.py-hoz képest)
here = pathlib.Path(__file__).parent.resolve()

# README betöltése, ha van
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="cmd_window",
    version="0.3.2",
    description="This python module makes it easy to create text-based, graphical interfaces.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/peterczegledy/Python-modules/tree/main/cmd_window",
    author="Czeglédy Péter",
    author_email="czegledyp2@gmail.com",
    license="MIT",
    packages=find_packages(),  # Keresse meg automatikusan a csomagokat
    install_requires=[
        "pynput",
        "windows-curses"
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    zip_safe=False,
)
