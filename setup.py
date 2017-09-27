from setuptools import setup


setup(
    name='benchmark',
    version='0.1',
    description='benchmark gromacs simulations',
    author='Max Linke',
    install_requires=[
        'numpy>=1.8',
        'mdsynthesis',
        'click',
        'jinja2',
        'seaborn',
        'pandas',
        'matplotlib'
    ],
    tests_require=[
        'pytest',
        'scipy'
    ],
    entry_points={'console_scripts':
                  ['benchmark=benchmark.cli:cli']},
    zip_safe=False)
