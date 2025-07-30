from setuptools import setup, find_packages
import os

# Safe README read
long_description = ''
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name='blackoryx',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'moviepy==1.0.3',
        'imageio==2.31.1',
        'imageio-ffmpeg==0.4.8',
        'numpy',
        'pillow',
        'tqdm',
        'decorator==4.4.2',
        'proglog',
    ],
    entry_points={
        'console_scripts': [
            'blackoryx=blackoryx.main:main',
        ],
    },
    author='Atharv Puri',
    description='BlackORYX - Custom Video Command Language by Atharv Puri',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Topic :: Multimedia :: Video',
    ],
    python_requires='>=3.11',
)
