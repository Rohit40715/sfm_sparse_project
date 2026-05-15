# Sparse 3D Reconstruction Project (SfM)

A **Structure-from-Motion (SfM)** system that reconstructs 3D scenes from multiple overlapping photographs using classical computer vision techniques. This project implements a complete sparse 3D reconstruction pipeline with two operational modes: fast two-view reconstruction and comprehensive multi-view incremental reconstruction.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [How It Works](#how-it-works)
- [Pipeline Architecture](#pipeline-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Parameters & Tuning](#parameters--tuning)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)

---

## 📸 Project Overview

**What is Structure-from-Motion?**

Structure-from-Motion (SfM) is a computer vision technique that reconstructs 3D geometry of a scene from a collection of 2D images taken from different viewpoints. Given overlapping photographs, the algorithm:

1. Detects distinctive features in each image
2. Matches corresponding features across image pairs
3. Estimates the relative camera poses (positions and orientations)
4. Triangulates matched features to create 3D points
5. Optimizes the solution for geometric consistency

**Project Capabilities:**

✅ Automatic camera intrinsics estimation  
✅ Robust feature extraction using SIFT  
✅ Multi-view feature matching and validation  
✅ Essential matrix and pose recovery  
✅ Incremental camera registration  
✅ Track-based 3D point management  
✅ Bundle adjustment optimization  
✅ PLY format output for visualization  

---

## 🎯 How It Works

### Two-View Reconstruction (Fast Mode)

The two-view mode performs quick 3D reconstruction using the best matched image pair:

```
Input Images
    ↓
SIFT Feature Detection (10,000 features per image)
    ↓
Feature Matching (All image pairs, Lowe's ratio test)
    ↓
Select Best Pair (Maximum number of matches)
    ↓
Essential Matrix Estimation (RANSAC, σ=2.0 pixels)
    ↓
Camera Pose Recovery (Rotation R + Translation t)
    ↓
Triangulation (3D reconstruction from correspondences)
    ↓
Color Sampling (RGB values from first image)
    ↓
PLY Output (3D Point Cloud)
```

**Use Case:** Quick preview, testing, or when only 2 high-quality images available.

### Incremental Multi-View Reconstruction (Full Mode)

The incremental mode processes all images sequentially, building a comprehensive 3D model:

```
Input Images
    ↓
SIFT Feature Detection & Extraction
    ↓
Find Best Image Pair → Triangulate (Seed pair)
    ↓
Create Initial Tracks (3D point observations)
    ↓
For Each Remaining Image:
  ├─ Collect 3D-2D Correspondences
  ├─ PnP-RANSAC Registration (Estimate pose)
  ├─ Multi-view Triangulation (New 3D points)
  ├─ Track Management (Extend/Create tracks)
  └─ Update Camera Poses
    ↓
Bundle Adjustment (Global optimization)
    ↓
Reprojection Error Filtering (Keep best points)
    ↓
PLY Output (Dense Point Cloud)
```

**Use Case:** Production-quality 3D reconstructions, complete scene modeling.

---

## 🔧 Pipeline Architecture

### 1. **Feature Detection** (`features.py`)

**Algorithm:** SIFT (Scale-Invariant Feature Transform)

- Detects 10,000 keypoints per image
- Computes 128-dimensional descriptors
- Scale and rotation invariant
- Highly distinctive and repeatable

### 2. **Feature Matching** (`matching.py`)

**Algorithm:** Brute-Force Matching + Lowe's Ratio Test

- L2 (Euclidean) distance between descriptors
- Ratio test: `distance_best / distance_2nd_best < 0.85`
- Rejects ambiguous matches
- Automatic best pair selection

### 3. **Geometry Estimation** (`geometry.py`)

**Essential Matrix:**
- Captures geometric relationship between two views
- Epipolar constraint: `x₂ᵀ E x₁ = 0`
- Estimated using RANSAC (σ=2.0 pixels, confidence=99%)

**Pose Recovery:**
- Decomposes essential matrix into R (rotation) and t (translation)
- Selects physically valid solution (points in front of both cameras)
- Returns 4 possible poses, picks best via triangulation test

### 4. **3D Triangulation** (`triangulation.py`)

**Direct Linear Transform (DLT):**

- Input: 2D correspondences from both views + projection matrices
- Solves overdetermined linear system: `AX = 0`
- Output: 3D homogeneous coordinates `X = [X, Y, Z, W]`
- Normalized: `P_3d = [X/W, Y/W, Z/W]`

**Validation:**
- Keeps only points with Z > 0 (in front of camera)
- Removes infinite/NaN values
- Samples RGB color from source image

### 5. **Incremental Registration** (`reconstruction.py`)

**For each new image:**

1. **PnP-RANSAC:** Solves for camera pose using known 3D points
   - 3D world points from existing tracks
   - 2D observations in new image
   - RANSAC: σ=8.0 pixels, confidence=95%, iterations=300

2. **Track Management:**
   - **Extend existing tracks:** 3D point seen in another image
   - **Create new tracks:** Novel 3D points from new views
   - Avoids duplicate observations

3. **Multi-View Triangulation:**
   - Match new image with all registered images
   - Validate using Fundamental matrix (σ=2.5 pixels)
   - Triangulate new 3D points
   - Update and extend tracks

### 6. **Bundle Adjustment** (`bundle_adjustment.py`)

**Global Optimization:**

- Minimizes sum of squared reprojection errors
- Variables: Camera poses (6 DOF each) + 3D points (3 coords each)
- Algorithm: Trust Region Reflected method (scipy.optimize.least_squares)
- Refines geometry for global consistency

**Cost Function:**
```
E = Σ ||projection(P_i) - observation_2d||²
```

### 7. **Filtering & Output** (`visualization.py`)

- Compute mean reprojection error for each 3D point
- Keep points with error < 4.0 pixels
- Remove outliers
- Save to PLY format (ASCII)

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

**Or install individually:**

```bash
# Core dependencies
pip install opencv-contrib-python numpy open3d

# Optional: For bundle adjustment optimization
pip install scipy
```

### Verify Installation

```bash
python -c "import cv2, numpy, open3d, scipy; print('All dependencies installed!')"
```

---

## 🚀 Usage

### Basic Commands

**Two-View Mode (Fast):**
```bash
python main.py --images_dir ./images --mode two_view
```

**Incremental Mode (Complete):**
```bash
python main.py --images_dir ./images --mode incremental
```

**Custom Output Location:**
```bash
python main.py --images_dir ./images --out_ply ./results/my_scene.ply --mode incremental
```

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--images_dir` | str | **Required** | Path to folder containing images (JPG, PNG, BMP, TIF) |
| `--mode` | str | `two_view` | Reconstruction mode: `two_view` or `incremental` |
| `--out_ply` | str | `results/sparse_cloud.ply` | Output path for PLY file |

### Input Image Requirements

- **Format:** JPG, PNG, BMP, TIF, TIFF
- **Count:** Minimum 2 images
- **Overlap:** 50-80% recommended
- **Content:** Clear, well-textured scenes (features to match)
- **Ordering:** Not required (automatic pair selection)

**Good examples:**
- Building facades photographed from multiple angles
- Object photographed around 360°
- Landscape with overlapping photos

**Bad examples:**
- Featureless scenes (blank walls, sky)
- Extremely blurry images
- Images with zero overlap

---

## 📷 Examples

### Example 1: Two-View Reconstruction

**Input:**
> [Add 2 example input images side-by-side here]

**Command:**
```bash
python main.py --images_dir ./images/example1 --mode two_view --out_ply ./results/example1_two_view.ply
```

**Output Statistics:**
```
Initialized seed pair: Image 1 & Image 3
Matched features: 245
Inliers (Essential Matrix RANSAC): 198
3D points reconstructed: 198
Cameras registered: 2
Output saved: results/example1_two_view.ply
```

**Visualization:**
> [Add screenshot of point cloud output here]

---

### Example 2: Incremental Reconstruction

**Input:**
> [Add 3-4 example input images here]

**Command:**
```bash
python main.py --images_dir ./images/example2 --mode incremental --out_ply ./results/example2_incremental.ply
```

**Output Statistics:**
```
Seed pair: Image 2 & Image 5
Initial 3D points: 456

Registering Image 1: +145 new, +67 extended
Registering Image 4: +189 new, +92 extended
Registering Image 6: +234 new, +156 extended

Bundle Adjustment:
  Optimizing 4 cameras + 1024 points...
  Convergence achieved after 12 iterations
  Final reprojection error: 0.87 pixels

Filtering (error < 4.0 px):
  Points kept: 987 / 1024

Final Output:
  3D points: 987
  Cameras registered: 6
  Output saved: results/example2_incremental.ply
```

**Visualization:**
> [Add screenshot of dense point cloud here]

---

### Example 3: Comparison: Two-View vs Incremental

**Same Input Images:**
> [Add input image set here]

**Two-View Results:**
- Points reconstructed: ~250
- Cameras: 2
- Reconstruction time: ~5 seconds
- Density: Low (only best pair)

**Incremental Results:**
- Points reconstructed: ~1200
- Cameras: All N images
- Reconstruction time: ~30 seconds
- Density: High (all views combined)

**Visual Comparison:**
> [Add side-by-side point cloud visualizations]

---

## ⚙️ Parameters & Tuning

### Feature Extraction
| Parameter | Location | Default | Effect |
|-----------|----------|---------|--------|
| `nfeatures` | `src/features.py` | 10,000 | Increase for more features, slower |

### Matching
| Parameter | Location | Default | Effect |
|-----------|----------|---------|--------|
| `ratio` (two-view) | `src/matching.py` | 0.85 | Lower = stricter, fewer matches |
| `ratio` (incremental) | `src/reconstruction.py` | 0.75 | Lower = stricter (more selective) |

### Geometry
| Parameter | Location | Default | Effect |
|-----------|----------|---------|--------|
| `threshold` (E-matrix) | `src/geometry.py` | 2.0 px | RANSAC inlier threshold |
| `prob` (E-matrix) | `src/geometry.py` | 0.99 | RANSAC confidence level |
| `threshold` (F-matrix) | `src/reconstruction.py` | 2.5 px | Epipolar geometry validation |

### Registration (Incremental Only)
| Parameter | Location | Default | Effect |
|-----------|----------|---------|--------|
| `reprojectionError` | `src/reconstruction.py` | 8.0 px | PnP-RANSAC inlier threshold |
| `iterationsCount` | `src/reconstruction.py` | 300 | RANSAC iterations |
| `confidence` | `src/reconstruction.py` | 0.95 | RANSAC confidence |

### Filtering
| Parameter | Location | Default | Effect |
|-----------|----------|---------|--------|
| `error threshold` | `src/reconstruction.py` | 4.0 px | Keep points with error < this |

### Bundle Adjustment
| Parameter | Location | Default | Effect |
|-----------|----------|---------|--------|
| `ftol` | `src/bundle_adjustment.py` | 1e-4 | Optimization convergence tolerance |

---

## 📁 Project Structure

```
sfm_sparse_project/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── features.py              # SIFT feature extraction
│   ├── matching.py              # Feature matching (Lowe's ratio test)
│   ├── geometry.py              # Essential matrix & pose recovery
│   ├── triangulation.py         # 3D point triangulation
│   ├── reconstruction.py        # Main SfM pipeline
│   ├── bundle_adjustment.py     # Global optimization
│   ├── utils.py                 # Image I/O & camera intrinsics
│   └── visualization.py         # PLY file I/O
│
├── main.py                       # Entry point / CLI
├── setup.py                      # Package setup
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .gitignore                    # Git exclusions
│
├── data/                         # Input image datasets
│   └── .gitkeep
│
├── results/                      # Output point clouds
│   └── .gitkeep
│
├── images/                       # Working image directory
└── .git/                         # Version control
```

---

## 🔬 Technical Details

### Camera Model

**Pinhole Camera Model:**
```
Intrinsics K (3×3 matrix):
┌              ┐
│ f_x   0  c_x │
│  0   f_y  c_y│
│  0    0    1 │
└              ┘

Auto-estimated:
  f_x = f_y = 0.9 × max(width, height)  [focal length]
  c_x = width / 2                        [principal point X]
  c_y = height / 2                       [principal point Y]

No lens distortion assumed.
```

**Projection Formula:**
```
x_homogeneous = K × [R | t] × P_world
x_image = x_homogeneous[:2] / x_homogeneous[2]
```

### Coordinate Systems

**World Frame:** Arbitrary (first camera at origin)  
**Camera Frame:** Z-axis points forward (into scene)  
**Image Frame:** Origin at top-left, X right, Y down

**Important:** Only 3D points with Z > 0 are valid (in front of camera).

### Track Structure (Incremental Mode)

```python
@dataclass
class Track:
    point_3d: np.ndarray        # 3D coordinate [X, Y, Z]
    color: np.ndarray           # RGB color [R, G, B] (0-1 normalized)
    observations: dict          # {image_id: keypoint_index}
    error: float                # Mean reprojection error
```

**Track Lifecycle:**
1. **Created** from initial seed pair triangulation
2. **Extended** when existing observation found in new image
3. **New tracks** created when novel 3D points triangulated
4. **Refined** during bundle adjustment
5. **Filtered** based on reprojection error

### SIFT Descriptors

- **Size:** 128-dimensional vectors
- **Invariance:** Scale and rotation
- **Matching:** L2 (Euclidean) distance
- **Validation:** Lowe's ratio test

### RANSAC Parameters Explained

**σ (threshold):** Distance in pixels below which a match is considered an inlier

**confidence:** Probability that at least one random sample is outlier-free

**iterationsCount:** Number of random samples to test

**Formula:**
```
N = log(1 - confidence) / log(1 - (1 - outlier_ratio)^num_samples)
```

---

## 📊 Expected Output

### PLY File Format

```
ply
format ascii 1.0
comment Generated by SfM Sparse Reconstruction
element vertex 1024
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
-1.234 5.678 2.345 255 128 64
0.456 -2.789 3.456 200 150 100
...
```

### Console Output

```
Loading images from: ./images/
Found 6 images
Estimated camera intrinsics:
  Focal length: 3000.0 px
  Principal point: (2000.0, 1500.0)

[Two-View Mode]
Best image pair: (1, 4)
Matched features: 567
RANSAC inliers: 432
3D points: 432

[Incremental Mode]
Seed: Image 1 & 4 → 432 initial points

Registering Image 2:
  PnP inliers: 287
  New 3D points: 156
  Extended tracks: 89

[Bundle Adjustment]
Optimizing 6 cameras + 1245 points...
Iteration 1: error = 2.34 px
Iteration 2: error = 1.87 px
Iteration 3: error = 1.76 px
Converged!

[Filtering]
Points before: 1245
Points after (error < 4.0): 1189
Kept: 95.5%

Results saved to: results/sparse_cloud.ply
```

---

## 🎓 Educational Use

This project is designed to be interview-friendly and educational. It demonstrates:

- **Classical Computer Vision:** SIFT, epipolar geometry, triangulation
- **Optimization:** Bundle adjustment using least-squares
- **RANSAC:** Robust estimation in presence of outliers
- **Multi-view Geometry:** Essential matrix, camera poses, 3D reconstruction
- **Software Architecture:** Modular design, clear pipeline

**Key Learning Points:**
- How structure-from-motion works end-to-end
- Implementation of computer vision algorithms
- Handling real-world challenges (matching ambiguity, outliers)
- Optimization and refinement techniques

---

## 🔗 Related Concepts

- **SfM (Structure-from-Motion):** 3D scene reconstruction from images
- **SLAM (Simultaneous Localization and Mapping):** Real-time SfM variant
- **MVS (Multi-View Stereo):** Dense reconstruction (dense point clouds)
- **SfM vs MVS:** This project produces sparse clouds; MVS produces denser models
- **Photogrammetry:** Professional 3D reconstruction (commercial: Agisoft Metashape, RealityCapture)

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 👨‍💻 Author

**Rohit** - Created as part of computer vision learning

---

## 📧 Questions & Support

For issues or questions:
1. Check console output for error messages
2. Verify input images have sufficient overlap
3. Try two-view mode first to debug
4. Check image quality and features


