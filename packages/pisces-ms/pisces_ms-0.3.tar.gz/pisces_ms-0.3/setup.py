from setuptools import setup

setup(
    name='pisces-ms',
    version=0.3,
    description='Managing assignment of spliced peptides.',
    author='John Cormican, Juliane Liepe',
    author_email='juliane.liepe@mpinat.mpg.de',
 	license_files = ('LICENSE.txt',),
    packages=[
        'pisces',
        'pisces.report',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    py_modules=[
        'pisces',
        'pisces.report',
    ],
    entry_points={
        'console_scripts': [
            'pisces=pisces.run:run_pisces'
        ]
    },
    python_requires='>=3.11',
    install_requires=[
        'inspirems==3.0rc3',
        'regex==2024.11.6',
        'suffix-tree==0.1.2',
    ],
    project_urls={
        'Homepage': 'https://github.com/QuantSysBio/inSPIRE',
        'Tracker': 'https://github.com/QuantSysBio/inSPIRE/issues',
    },
)
