from setuptools import setup, find_packages

setup(
    name='api_hunter',
    version='0.1.1',
    packages=find_packages(),
    install_requires=["google-genai","python-dotenv","pydantic"],
    entry_points={
        'console_scripts': [
            'hunt=api_hunt.cli:main',  
        ],
    },
    author='Joe Mama',
    description='Scan staged Git files for secrets like API keys.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
