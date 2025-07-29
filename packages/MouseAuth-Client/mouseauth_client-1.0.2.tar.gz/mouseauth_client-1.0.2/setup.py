from setuptools import setup, find_packages

setup(
    name='MouseAuth-Client',
    version='1.0.2',
    author='LacyCat',
    packages=find_packages(),
    description='MouseAuth Client for Python',
    install_requires=[
        'requests>=2.28.0',
        'numpy>=1.21.0',
        'typing-extensions>=4.0.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.10',
)
