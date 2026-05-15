"""
Sparse 3D Reconstruction using SIFT and Epipolar Geometry

Core modules:
- features: SIFT feature extraction
- matching: Feature matching
- geometry: Epipolar geometry and pose recovery
- triangulation: 3D point triangulation
- reconstruction: Main SfM pipeline (two-view and incremental)
- bundle_adjustment: Optimization
- utils: Image loading and utilities
- visualization: Point cloud I/O and visualization
"""

__version__ = "1.0.0"
__author__ = "Rohit"
