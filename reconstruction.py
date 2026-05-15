import numpy as np
import cv2
from dataclasses import dataclass
from typing import List, Optional
from features import FeatureSet, create_sift, extract_features
from geometry import estimate_pose_and_triangulate, pnp_register_image
from matching import build_correspondences, choose_best_pair
from triangulation import triangulate_between_anchor_and_new
from utils import load_images, estimate_intrinsics
from visualization import save_point_cloud_ply, visualize_point_cloud
from bundle_adjustment import bundle_adjustment
@dataclass
class Track:
    point_3d: np.ndarray
    color: np.ndarray
    observations: dict[int, int]
    error: float = 0.0
@dataclass
class ReconstructionResult:
    points_3d: np.ndarray
    colors: np.ndarray
    R: np.ndarray
    t: np.ndarray
    inlier_mask: np.ndarray
@dataclass
class ReconstructionState:
    images: List[np.ndarray]
    features: List[FeatureSet]
    K: np.ndarray
    registered_poses: dict
    tracks: List[Track]
def sample_colors(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    pts_int = np.clip(np.round(pts).astype(int), [0, 0], [w - 1, h - 1])
    return image[pts_int[:, 1], pts_int[:, 0], ::-1].astype(np.float32) / 255.0
def run_two_view(images_dir: str, out_ply: Optional[str] = None) -> ReconstructionResult:
    pass
def map_tracks_across_images(state: ReconstructionState, idx: int) -> tuple[np.ndarray, np.ndarray, List[int]]:
    obj_pts, img_pts, track_indices = [], [], []
    for t_idx, track in enumerate(state.tracks):
        # find matching feature in idx for one of the track's existing observations
        for reg_idx, k_reg in track.observations.items():
            # mock for PnP logic against all registered 
            # (You would use actual matching here, simplistic stub passes)
            pass
    return np.array(obj_pts), np.array(img_pts), track_indices
def run_incremental(images_dir: str, out_ply: Optional[str] = None):
    images = load_images(images_dir)
    sift = create_sift()
    features = [extract_features(img, sift) for img in images]
    K = estimate_intrinsics(images[0].shape)
    i, j, matches = choose_best_pair(features)
    pts1, pts2 = build_correspondences(features[i], features[j], matches)
    _, inlier_mask, R, t = estimate_pose_and_triangulate(pts1, pts2, K)
    # ... Initialization (omitted for brevity but would add pairwise to tracks like priority 1)
    state = ReconstructionState(images, features, K, {i: (np.eye(3), np.zeros((3,1))), j: (R, t)}, [])
    for idx in range(len(images)):
        if idx in state.registered_poses: continue
        # PnP against all registered images (priority 2)
        # obj_pts, img_pts, _ = map_tracks_across_images(state, idx)
        # success, Rn, tn, ... = cv2.solvePnPRansac(obj_pts, img_pts, K, None)
        # reprojection error filtering (priority 3)
        # valid_tracks = [t for t in state.tracks if t.error < some_threshold]
        # Real bundle adjustment (priority 4)
        state.registered_poses, state.tracks = bundle_adjustment(state.registered_poses, state.tracks, K, state.features)
    # Return structure
    return state
