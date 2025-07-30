from setuptools import setup, find_packages

setup(
    name='mseep-masquerade',
    version='0.2.0',
    description='A privacy firewall for PDF files that automatically detects and redacts sensitive data',
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
    install_requires=['fastmcp==0.4.1', 'mcp==1.3.0', 'PyMuPDF==1.23.8', 'tinfoil'],
    keywords=['mseep'],
)
