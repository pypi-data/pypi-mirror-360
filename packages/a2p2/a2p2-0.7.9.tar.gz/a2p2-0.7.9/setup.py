from setuptools import setup, find_packages

with open('README.rst') as README:
    long_description = README.read()
    description = long_description[
        :long_description.index('Description')].split("*")[1].strip()

versions = {}
with open("a2p2/version.py") as fp:
    exec(fp.read(), versions)

setup(
    version=versions['__version__'],
    description=description
# not yet moved to pyproject.toml
#    packages=find_packages(),
#    include_package_data=True,
#    keywords='observation preparation tool optical-interferometry p2 samp'
)
