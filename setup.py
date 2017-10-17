from setuptools import setup

setup(
    name='benchmark',
    version='1.0',
    description='benchmark gromacs simulations',
    author='Max Linke',
    packages=['benchmark'],
    install_requires=[
        'numpy>=1.8', 'mdsynthesis', 'click', 'jinja2', 'pandas', 'matplotlib'
    ],
    entry_points={'console_scripts': ['benchmark=benchmark.cli:cli']},
    zip_safe=False)
