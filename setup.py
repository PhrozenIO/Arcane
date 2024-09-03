from pathlib import Path

from setuptools import find_packages, setup  # type: ignore[import]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='arcane_viewer',
    version='1.0.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyQt6',
        'setuptools',
    ],
    entry_points={
        'console_scripts': [
            'arcane-viewer = arcane_viewer.main:main',
        ],
    },
    author="Jean-Pierre LESUEUR",
    author_email="jplesueur@phrozen.io",
    description="A secure remote desktop application for Windows with the particularity of having a server entirely "
                "written in PowerShell and a cross-platform client (Python/QT6)",
    license="Apache License 2.0",
    keywords="remote desktop, remote control, remote access, remote administration, remote assistance, powershell",
    url="https://github.com/PhrozenIO/Arcane",
    python_requires='>=3.8',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
