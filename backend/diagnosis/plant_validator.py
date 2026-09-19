"""
Plant/Leaf Image Validator for AgriShield AI Plant Diagnosis.

Uses multi-factor spectral and texture analysis to determine whether an uploaded
image actually contains a plant leaf BEFORE running the disease classifier.

Algorithm
---------
Positive signals (push score up):
  - vegetation_ratio  : fraction of pixels where green dominates (tolerates diseased yellowing)
  - exg_score         : Excess Green Index (2G - R - B) normalised to [0, 1]
  - texture_score     : spatial std of green channel (organic leaf texture)

Negative signals (push score down):
  - skin_ratio        : fraction of skin-tone pixels (human/animal photos)
  - achromatic_ratio  : fraction of gray/white/black pixels (documents/screenshots)
  - blue_ratio        : fraction of sky/water-blue dominant pixels

Thresholds
----------
PLANT_CONFIDENCE_THRESHOLD = 0.35
    Below this  -> reject entirely  (Invalid Image - no disease model run)
AMBIGUOUS_THRESHOLD = 0.50
    Below this but >= 0.35 -> accept but surface warning to user
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

import numpy as np

# ---------------------------------------------------------------------------
# Configurable thresholds (tuned against real leaf vs non-leaf test images)
# ---------------------------------------------------------------------------
PLANT_CONFIDENCE_THRESHOLD: float = 0.35   # hard rejection gate
AMBIGUOUS_THRESHOLD: float = 0.50          # borderline warning gate


@dataclass
class PlantValidationResult:
    is_valid: bool
    plant_confidence: float          # 0.0 to 1.0
    is_ambiguous: bool               # True when score is valid but uncertain
    rejection_reason: Optional[str]  # human-readable message when rejected
    detail: Dict[str, Any] = field(default_factory=dict)   # numeric breakdown


def _compute_hsv(r: np.ndarray, g: np.ndarray, b: np.ndarray):
    """Vectorised RGB-to-HSV conversion. Inputs in [0, 1] range."""
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    delta = max_c - min_c + 1e-9

    hue = np.zeros_like(r, dtype=np.float32)
    mask_r = (max_c == r) & (delta > 1e-8)
    mask_g = (max_c == g) & (delta > 1e-8)
    mask_b = (max_c == b) & (delta > 1e-8)

    hue[mask_r] = (60.0 * ((g[mask_r] - b[mask_r]) / delta[mask_r])) % 360
    hue[mask_g] = (60.0 * ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 120) % 360
    hue[mask_b] = (60.0 * ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 240) % 360

    sat = np.where(max_c > 1e-8, delta / max_c, 0.0).astype(np.float32)
    val = max_c.astype(np.float32)
    return hue, sat, val


def validate_is_plant_leaf(img_arr: np.ndarray) -> PlantValidationResult:
    """
    Validates whether img_arr (H x W x 3, float32, values in [0, 1])
    contains a plant or leaf image.

    This function MUST be called BEFORE predict_disease_from_image().
    When is_valid == False, the disease classifier must NOT be invoked
    and NO diagnosis record must be saved to the database.

    Parameters
    ----------
    img_arr : np.ndarray
        Preprocessed image array output from preprocess_image().
        Shape (H, W, 3), values in [0.0, 1.0].

    Returns
    -------
    PlantValidationResult
    """
    r = img_arr[:, :, 0]
    g = img_arr[:, :, 1]
    b = img_arr[:, :, 2]

    # ------------------------------------------------------------------
    # Signal 1: Vegetation greenness
    # Pixels where green dominates both red and blue and is not too dark.
    # Loosened red threshold tolerates yellow-cast diseased leaves.
    # ------------------------------------------------------------------
    green_dom = (
        (g > r * 1.03)   # green exceeds red by 3%
        & (g > b * 0.88) # green is 88% of blue (allows yellow-green)
        & (g > 0.16)     # not pitch black
    )
    vegetation_ratio = float(np.mean(green_dom))

    # ------------------------------------------------------------------
    # Signal 2: Excess Green Index (ExG = 2G - R - B)
    # Vegetation typically has ExG > 0.05
    # ------------------------------------------------------------------
    exg = 2.0 * g - r - b            # range approx -2 to +2
    mean_exg = float(np.mean(exg))
    # Normalise: ExG=0.50 -> 1.0, ExG<=-0.15 -> 0.0
    exg_score = float(np.clip((mean_exg + 0.15) / 0.65, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Signal 3: Organic texture (leaf venation / disease spots)
    # Healthy leaf green_std ~0.07-0.20; diseased ~0.05-0.25; doc ~0.01
    # ------------------------------------------------------------------
    green_std = float(np.std(g))
    texture_score = float(np.clip((green_std - 0.02) / 0.18, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Signal 4: Skin-tone detection (human/animal photos)
    # HSV: H in [0,45] or [330,360], S in [0.12,0.92], V in [0.18,0.97]
    # ------------------------------------------------------------------
    hue, sat, val = _compute_hsv(r, g, b)
    skin_mask = (
        ((hue <= 45) | (hue >= 330))
        & (sat > 0.12) & (sat < 0.92)
        & (val > 0.18) & (val < 0.97)
    )
    skin_ratio = float(np.mean(skin_mask))

    # ------------------------------------------------------------------
    # Signal 5: Achromatic pixels (screenshots, concrete, documents)
    # ------------------------------------------------------------------
    achromatic_ratio = float(np.mean(sat < 0.10))

    # ------------------------------------------------------------------
    # Signal 6: Blue dominance (sky, water, blue backgrounds)
    # ------------------------------------------------------------------
    blue_dom = (b > r * 1.18) & (b > g * 1.12) & (b > 0.28)
    blue_ratio = float(np.mean(blue_dom))

    # ------------------------------------------------------------------
    # Signal 7: Bright-uniform (screenshot / document / white wall)
    # ------------------------------------------------------------------
    bright_uniform = (
        float(np.mean(val > 0.87)) > 0.60
        and achromatic_ratio > 0.50
    )

    # ------------------------------------------------------------------
    # Composite score
    # ------------------------------------------------------------------
    positive = (
        0.38 * vegetation_ratio
        + 0.30 * exg_score
        + 0.12 * texture_score
    )
    negative = (
        0.44 * min(skin_ratio * 2.2, 1.0)   # skin penalty (amplified)
        + 0.18 * achromatic_ratio
        + 0.12 * blue_ratio
        + (0.28 if bright_uniform else 0.0)
    )
    plant_confidence = float(np.clip(positive - negative, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Decision
    # ------------------------------------------------------------------
    is_valid = plant_confidence >= PLANT_CONFIDENCE_THRESHOLD
    is_ambiguous = is_valid and (plant_confidence < AMBIGUOUS_THRESHOLD)

    rejection_reason: Optional[str] = None
    if not is_valid:
        if skin_ratio > 0.18:
            rejection_reason = (
                "This image appears to contain a person or animal rather than a plant leaf. "
                "Please upload a close-up photograph of a plant leaf."
            )
        elif achromatic_ratio > 0.62 or bright_uniform:
            rejection_reason = (
                "This image appears to be a document, screenshot, or non-organic surface. "
                "Please upload a close-up photograph of a plant leaf."
            )
        elif blue_ratio > 0.38:
            rejection_reason = (
                "This image appears to show sky, water, or a solid-colour background "
                "without a plant. Please upload a close-up photograph of a plant leaf."
            )
        else:
            rejection_reason = (
                "No supported plant leaf was detected in this image. "
                "Please upload a clear, close-up photograph of a plant leaf."
            )

    detail = {
        "vegetation_ratio": round(vegetation_ratio, 3),
        "exg_score": round(exg_score, 3),
        "mean_exg": round(mean_exg, 3),
        "texture_score": round(texture_score, 3),
        "green_std": round(green_std, 3),
        "skin_ratio": round(skin_ratio, 3),
        "achromatic_ratio": round(achromatic_ratio, 3),
        "blue_ratio": round(blue_ratio, 3),
        "bright_uniform": bright_uniform,
        "positive_score": round(positive, 3),
        "negative_score": round(negative, 3),
    }

    return PlantValidationResult(
        is_valid=is_valid,
        plant_confidence=round(plant_confidence, 3),
        is_ambiguous=is_ambiguous,
        rejection_reason=rejection_reason,
        detail=detail,
    )
