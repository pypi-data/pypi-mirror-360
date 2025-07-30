from setuptools import setup, find_packages

setup(
    name='mseep-pydantic-rpc',
    version='0.6.1',
    description='A Python library for building gRPC/ConnectRPC services with Pydantic models.',
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
    install_requires=['pydantic>=2.1.1', 'grpcio-tools>=1.56.2', 'grpcio-reflection>=1.56.2', 'grpcio-health-checking>=1.56.2', 'sonora>=0.2.3', 'connecpy>=1.4.1', 'mcp>=1.9.4', 'starlette>=0.27.0'],
    keywords=['mseep'],
)
