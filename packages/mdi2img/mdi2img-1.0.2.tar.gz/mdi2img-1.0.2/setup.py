"""
File containing the required information to successfully build a python package
"""

import setuptools


def clean_requirements(raw_requirements: list) -> list:
    """
    Clean the requirements list
    """
    r_index = 0
    r_length = len(raw_requirements)
    while r_index < r_length:
        if raw_requirements[r_index].startswith("#"):
            print(f"comment removed: {raw_requirements[r_index]}")
            raw_requirements.pop(r_index)
            r_length -= 1
            continue
        if len(raw_requirements[r_index]) == 0:
            print(f"empty string removed: '{raw_requirements[r_index]}'")
            raw_requirements.pop(r_index)
            r_length -= 1
            continue
        if " " in raw_requirements[r_index]:
            print(f"space removed: {raw_requirements[r_index]}")
            raw_requirements[
                r_index
            ] = raw_requirements[r_index].replace(" ", "")
        r_index += 1
    return raw_requirements


with open("README.md", "r", encoding="utf-8", newline="\n") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8", newline="\n") as fh:
    lib_requirements = fh.read().split("\n")

lib_requirements = clean_requirements(lib_requirements)

print(f"requirements = {lib_requirements}")

setuptools.setup(
    name='mdi2img',
    version='1.0.2',
    packages=setuptools.find_packages(),
    install_requires=lib_requirements,
    include_package_data=True,
    package_data={
        "mdi2img": ['bin/*'],
    },
    # data_files=[
    #     ("bin", ['MDI2TIF.EXE', 'MDTFCORE.DLL',
    #      'MDTFINK.DLL', 'MSPTLS.DLL', 'RICHED20.DLL'])
    # ],
    author="Henry Letellier",
    author_email="henrysoftwarehouse@protonmail.com",
    description="A module that allows you to convert mdi files to tiff and other formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hanra-s-work/MDI2IMG",
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
