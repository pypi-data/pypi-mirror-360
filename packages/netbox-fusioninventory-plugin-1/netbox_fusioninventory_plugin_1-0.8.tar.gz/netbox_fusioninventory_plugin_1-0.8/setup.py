from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name='netbox_fusioninventory_plugin_1',
    version='0.8',
    description='A Plugin for import devices from fusion inventory agent',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/Milka64/netbox-fusioninventory-plugin',
    author='Michael Ricart',
    license='BSD License',
    install_requires=[
        'beautifulsoup4',
        'lxml',
        'unicode-slugify',
        ],
    packages=find_packages(),
    include_package_data=True,
)

