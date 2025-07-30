from setuptools import setup, find_packages

setup(
    name='dsaedge',
    version='0.3.0',
    author='Thiyagarajan', # Replace with your name
    author_email='trj08012002@gmail.com', # Replace with your email
    description='A comprehensive Python package for various data structures and algorithms implementations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/thiyagarajan2002/dsaedge',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
         'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
    ],
    python_requires='>=3.9',
    keywords='data structures algorithms python linked list tree graph sort search dynamic programming backtracking',
    install_requires=[
        # Add any runtime dependencies here
    ],
    extras_require={
        'dev': [
            'pytest',
            'ruff',
            'black',
            'mypy',
        ],
    },
)
