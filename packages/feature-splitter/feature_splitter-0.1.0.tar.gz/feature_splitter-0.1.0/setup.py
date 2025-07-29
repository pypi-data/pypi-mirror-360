from setuptools import setup, find_packages

setup(
    name='feature_splitter',
    version='0.1.0',
    description='Split a DataFrame by column variation and save CSV parts',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
    ],
    python_requires='>=3.6',
)