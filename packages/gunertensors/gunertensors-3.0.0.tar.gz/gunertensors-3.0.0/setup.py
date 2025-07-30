from setuptools import setup, find_packages

setup(
    name='gunertensors',
    version='3.0.0',
    author='Berat GUNER',
    author_email='gunerberat311@gmail.com',
    description='Advanced AI Optimization Toolkit',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'torch>=2.1.0',
        'transformers>=4.35.0',
        'psutil>=5.9.0',
        'fasttext-wheel>=0.9.2',
        'pynvml>=11.5.0',
        'language-tool-python>=2.7.0',
        'numpy>=1.21.0',
        'tensorboard>=2.15.0'
    ],
    extras_require={
        'cuda': ['cuda-python>=12.0.0'],
    },
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.9',
    keywords='ai nlp deep learning gpu optimization',
  ) 