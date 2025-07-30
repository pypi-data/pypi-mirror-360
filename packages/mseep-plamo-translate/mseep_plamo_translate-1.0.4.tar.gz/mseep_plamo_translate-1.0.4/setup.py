from setuptools import setup, find_packages

setup(
    name='mseep-plamo-translate',
    version='1.0.4',
    description='A command-line interface for translation using the plamo-2-translate model with local execution.',
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
    install_requires=['mcp[cli]>=1.9.2', 'numba>=0.60.0', "mlx-lm>=0.25.2 ; sys_platform == 'darwin'"],
    keywords=['mseep', 'machine translation', 'transformer', 'nlp', 'natural language processing', 'deep learning', 'mlx', 'mlx-lm', 'sentencepiece', 'plamo', 'plamo-translate', 'plamo-translate-cli'],
)
