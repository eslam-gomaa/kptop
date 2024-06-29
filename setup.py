from setuptools import setup, find_packages
import os

requirements = 'kubePtop/requirements.txt'
if os.path.isfile(requirements):
    with open(requirements) as f:
        install_requires = f.read().splitlines()

setup(
    name = 'kptop',
    version = '0.0.10',
    author = 'Eslam Gomaa',
    # license = '<the license you chose>',
    description = 'A CLI tool that provides Monitoring for Kubernetes resources on the terminal through Prometheus metircs',
    long_description_content_type = "text/markdown",
    url = 'https://github.com/eslam-gomaa/kptop',
    py_modules = ['kubePtop', 'kptop_tool'],
    packages = find_packages(),
    install_requires = [install_requires],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    # entry_points = '''
    #     [console_scripts]
    #     opmcli=opmcli_tool:cli
    # '''
    entry_points={
        'console_scripts':['kptop = kptop_tool:run']
   }
)
