# setup.py

from setuptools import setup, find_packages

setup(
    name='faceauthX',
    version='1.0.1',
    description='Next-gen real-time face authentication with anti-spoof and face pattern matching',
    author='Sukhraj Singh',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'face_recognition',
        'opencv-python',
        'torch',
        'torchvision',
        'numpy',
        'Pillow'
    ],
    python_requires='>=3.7',
)
