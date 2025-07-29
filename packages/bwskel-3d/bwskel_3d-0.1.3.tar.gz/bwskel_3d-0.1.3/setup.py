from setuptools import setup, find_packages

setup(
    name='bwskel_3d',
    version='0.1.3',
    description='3D binary skeletonization and pruning, Python replication of MATLAB bwskel',
    author='Yunze Du',
    url='https://github.com/dujay971226/bwskel',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'scikit-image'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
