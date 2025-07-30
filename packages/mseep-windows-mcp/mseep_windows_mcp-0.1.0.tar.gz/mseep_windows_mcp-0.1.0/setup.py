from setuptools import setup, find_packages

setup(
    name='mseep-windows-mcp',
    version='0.1.0',
    description='Lightweight MCP Server for interacting with Windows Operating System.',
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
    install_requires=['fastmcp>=2.8.1', 'fuzzywuzzy>=0.18.0', 'humancursor>=1.1.5', 'live-inspect>=0.1.1', 'markdownify>=1.1.0', 'pillow>=11.2.1', 'pyautogui>=0.9.54', 'python-levenshtein>=0.27.1', 'requests>=2.32.3', 'uiautomation>=2.0.24'],
    keywords=['mseep', 'windows', 'mcp', 'ai', 'desktop', 'ai agent'],
)
