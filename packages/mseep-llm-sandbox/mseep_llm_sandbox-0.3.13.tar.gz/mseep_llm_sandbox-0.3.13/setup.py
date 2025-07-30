from setuptools import setup, find_packages

setup(
    name='mseep-llm-sandbox',
    version='0.3.13',
    description='LLM Sandbox is a lightweight and portable sandbox environment designed to run large language model (LLM) generated code in a safe and isolated mode.',
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
    install_requires=['pydantic>=2.11.5'],
    keywords=['mseep', 'python'],
)
