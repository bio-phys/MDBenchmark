from setuptools import setup

setup(
    name='benchmark',
    version='2.2.0',
    description='benchmark gromacs simulations',
    author='Max Linke, Michael Gecht',
    packages=['benchmark'],
    package_data={'benchmark': ['templates/*']},
    install_requires=[
        'numpy>=1.8', 'mdsynthesis', 'click', 'jinja2', 'pandas', 'matplotlib',
        'python-Levenshtein', 'xdg',
    ],
    entry_points={'console_scripts': ['benchmark=benchmark.cli:cli']},
    zip_safe=False)
