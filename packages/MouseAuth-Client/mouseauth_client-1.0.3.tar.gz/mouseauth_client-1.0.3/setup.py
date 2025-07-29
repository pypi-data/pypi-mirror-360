from setuptools import setup, find_packages
import shutil
import os

dist_path = os.path.join(os.path.dirname(__file__), 'dist')
if os.path.exists(dist_path):
    shutil.rmtree(dist_path)
os.makedirs(dist_path, exist_ok=True)

setup(
    name='MouseAuth-Client',
    version='1.0.3',
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
