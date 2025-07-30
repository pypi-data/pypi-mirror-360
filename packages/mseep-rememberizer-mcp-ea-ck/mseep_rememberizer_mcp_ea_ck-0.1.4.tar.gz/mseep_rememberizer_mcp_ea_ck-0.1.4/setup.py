from setuptools import setup, find_packages

setup(
    name='mseep-rememberizer-mcp-ea-ck',
    version='0.1.4',
    description='This is the public ck for testing purpose',
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author='mseep',
    author_email='support@skydeck.ai',
    maintainer='mseep',
    maintainer_email='support@skydeck.ai',
    url='https://github.com/mseep',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['httpx>=0.27.2', 'mcp>=1.0.0', 'python-dotenv>=1.0.1'],
    keywords=['mseep'],
)
