from setuptools import setup, find_packages

setup(
    name='envconfig-checker',
    version='0.1.0',
    author='Royal Kuriyakose M',
    description='A simple CLI tool to check environment variables',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    py_modules=['cli'],
    install_requires=[
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'env-checker = cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
