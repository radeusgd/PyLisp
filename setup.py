from setuptools import setup, find_packages

setup(
    name='pylisp',
    version='1.0.0',
    author='Radosław Waśko',
    author_email='wasko.radek@gmail.com',
    description='My LISP interpreter',
    url='https://github.com/radeusgd/pylisp',
    license='Apache',

    packages=find_packages(),

    install_requires=[
        'parsy',
    ],

    tests_require=[
        'pytest',
    ],

    entry_points={
        'console_scripts': [
            'pylisp = pylisp.shell:main',
        ],
    }
)
