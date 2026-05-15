from setuptools import setup, find_packages

setup(
    name="sfm-sparse-project",
    version="1.0.0",
    description="Sparse 3D Reconstruction using SIFT and Epipolar Geometry",
    author="Rohit",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "opencv-contrib-python",
        "numpy",
        "open3d",
        "scipy",
    ],
    entry_points={
        "console_scripts": [
            "sfm=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
