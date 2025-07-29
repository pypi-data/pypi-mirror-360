from setuptools import setup, find_packages

setup(
    name='enrobocode',
    version='0.2.0',  # ⚡ Increment version!
    description='English Robot Code — control robots easily',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'InquirerPy',  # Add this so users get it automatically!
    ],
    python_requires='>=3.6',
)