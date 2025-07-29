from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='imad213tools',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'bs4',
        'pycryptodome>=3.19.0',
        'pyfiglet>=0.8.post1',
        'psutil'
    ],
    entry_points={
        'console_scripts': [
            'imad213tools = imad213tools.main:main',
        ],
    },
    author='IMAD 213',
    author_email='madmadimado59@gmail.com',
    description='The imad213 followers tool is back under a new name: imad213tools — faster, smarter, and ready for action.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Security :: Cryptography',
    ],
    python_requires='>=3.6',
)
