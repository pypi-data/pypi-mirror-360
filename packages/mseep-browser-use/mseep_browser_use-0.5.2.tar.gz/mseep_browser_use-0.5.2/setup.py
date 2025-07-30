from setuptools import setup, find_packages

setup(
    name='mseep-browser-use',
    version='0.5.2',
    description='Make websites accessible for AI agents',
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
    install_requires=['aiofiles>=24.1.0', 'anyio>=4.9.0', 'bubus>=1.4.5', 'google-api-core>=2.25.0', 'httpx>=0.28.1', 'markdownify==1.1.0', 'patchright>=1.52.5', 'playwright>=1.52.0', 'portalocker>=2.7.0,<3.0.0', 'posthog>=3.7.0', 'psutil>=7.0.0', 'pydantic>=2.11.5', "pyobjc>=11.0; platform_system == 'darwin'", 'pyperclip>=1.9.0', 'python-dotenv>=1.0.1', 'requests>=2.32.3', "screeninfo>=0.8.1; platform_system != 'darwin'", 'typing-extensions>=4.12.2', 'uuid7>=0.1.0', 'authlib>=1.6.0', 'google-genai>=1.21.1', 'openai>=1.81.0', 'anthropic>=0.54.0', 'groq>=0.28.0', 'ollama>=0.5.1', 'google-api-python-client>=2.174.0', 'google-auth>=2.40.3', 'google-auth-oauthlib>=1.2.2', 'mcp>=1.10.1', 'pypdf>=5.7.0'],
    keywords=['mseep'],
)
