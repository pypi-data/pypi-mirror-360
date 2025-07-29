from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='jsrify',
    version='0.1.1',
    description='A plug-and-play tool to detect and rate hallucinations in ASR outputs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Anshit Mukherjee',
    author_email='anshitmukherjee1@gmail.com',
    url='https://github.com/yourusername/jsrify',
    license='MIT',
    install_requires=[
        'openai-whisper',
        'soundfile',
        'numpy',
        'scipy',
        'jiwer',
        'librosa',
        'torch',
        'torchaudio',
        'matplotlib',
        'seaborn',
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'jsrify=main:cli_entry',
        ],
    },
) 