"""
Plant/Leaf Image Validator and Quality Auditor for AgriShield AI.

Implements research-grade image validation:
1. Physical Quality Audit:
   - Resolution verification
   - Brightness / exposure limits (prevent dark/blown-out images)
   - RMS Contrast validation (prevent flat, washed-out images)
   - Laplacian focus/blur detection
2. Multi-factor Spectral & Texture Analysis:
   - Vegetation ratio (green-dominance with chlorosis tolerance)
   - Excess Green Index (ExG = 2G - R - B)
   - Organic venation texture
   - Skin-tone detection (human/animal filter)
   - Achromatic/document/screenshot rejection
   - Blue sky/water rejection
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple
import numpy as np


PLANT_CONFIDENCE_THRESHOLD: float = 0.35   # hard rejection gate
AMBIGUOUS_THRESHOLD: float = 0.50          # borderline uncertainty gate
MIN_ACCEPTABLE_RESOLUTION = (128, 128)


@dataclass
class PlantValidationResult:
    is_valid: bool
    plant_confidence: float          # 0.0 to 1.0
    is_ambiguous: bool               # True when score is valid but uncertain
    rejection_reason: Optional[str]  # human-readable message when rejected
    quality_score: float             # composite 0.0 to 1.0
    quality_audit: Dict[str, Any] = field(default_factory=dict)
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


def _audit_image_quality(img_arr: np.ndarray, original_size: Optional[Tuple[int, int]] = None) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluates physical image quality: exposure, contrast, blur, and resolution.
    """
    # Grayscale luminance
    y = 0.299 * img_arr[:, :, 0] + 0.587 * img_arr[:, :, 1] + 0.114 * img_arr[:, :, 2]
    mean_lum = float(np.mean(y))
    contrast_std = float(np.std(y))

    # Laplacian variance for focus/blur detection
    # Discretized 2D Laplacian kernel convolution
    h, w = y.shape
    lap = (
        y[0:h-2, 1:w-1] + y[2:h, 1:w-1] +
        y[1:h-1, 0:w-2] + y[1:h-1, 2:w] -
        4.0 * y[1:h-1, 1:w-1]
    )
    blur_var = float(np.var(lap))

    # Quality indicators
    brightness_ok = 0.12 <= mean_lum <= 0.88
    contrast_ok = contrast_std >= 0.07
    blur_detected = blur_var < 0.0006  # threshold for 0-1 scaled normalized array
    resolution_ok = True
    if original_size:
        resolution_ok = original_size[0] >= 120 and original_size[1] >= 120

    # Composite quality score (0.0 to 1.0)
    score = 1.0
    if not brightness_ok:
        score -= 0.35
    if not contrast_ok:
        score -= 0.25
    if blur_detected:
        score -= 0.30
    if not resolution_ok:
        score -= 0.20
    quality_score = max(0.1, min(1.0, score))

    audit = {
        "valid": bool(brightness_ok and contrast_ok and not blur_detected and resolution_ok),
        "quality_score": round(quality_score, 2),
        "leaf_detected": True,
        "blur_detected": bool(blur_detected),
        "blur_variance": round(blur_var * 1000, 3),
        "brightness_ok": bool(brightness_ok),
        "mean_luminance": round(mean_lum, 3),
        "contrast_ok": bool(contrast_ok),
        "rms_contrast": round(contrast_std, 3),
        "resolution_ok": bool(resolution_ok),
        "original_resolution": list(original_size) if original_size else [128, 128],
    }

    return quality_score, audit


def validate_is_plant_leaf(
    img_arr: np.ndarray,
    original_size: Optional[Tuple[int, int]] = None,
) -> PlantValidationResult:
    """
    Validates whether img_arr contains a bona fide plant or leaf image
    AND evaluates physical quality (blur, exposure, contrast).
    """
    r = img_arr[:, :, 0]
    g = img_arr[:, :, 1]
    b = img_arr[:, :, 2]

    # Run physical quality audit
    quality_score, quality_audit = _audit_image_quality(img_arr, original_size)

    # 1. Vegetation greenness
    green_dom = (
        (g > r * 1.03)   # green exceeds red by 3%
        & (g > b * 0.88) # green is 88% of blue (allows yellow-green)
        & (g > 0.16)     # not pitch black
    )
    vegetation_ratio = float(np.mean(green_dom))

    # 2. Excess Green Index (ExG = 2G - R - B)
    exg = 2.0 * g - r - b
    mean_exg = float(np.mean(exg))
    exg_score = float(np.clip((mean_exg + 0.15) / 0.65, 0.0, 1.0))

    # 3. Organic texture (leaf venation / disease spots)
    green_std = float(np.std(g))
    texture_score = float(np.clip((green_std - 0.02) / 0.18, 0.0, 1.0))

    # 4. Skin-tone detection (human/animal photos)
    hue, sat, val = _compute_hsv(r, g, b)
    skin_mask = (
        ((hue <= 45) | (hue >= 330))
        & (sat > 0.12) & (sat < 0.92)
        & (val > 0.18) & (val < 0.97)
    )
    skin_ratio = float(np.mean(skin_mask))

    # 5. Achromatic pixels (screenshots, concrete, documents)
    achromatic_ratio = float(np.mean(sat < 0.10))

    # 6. Blue dominance (sky, water, blue backgrounds)
    blue_dom = (b > r * 1.18) & (b > g * 1.12) & (b > 0.28)
    blue_ratio = float(np.mean(blue_dom))

    # 7. Bright-uniform (screenshot / document / white wall)
    bright_uniform = (
        float(np.mean(val > 0.87)) > 0.60
        and achromatic_ratio > 0.50
    )

    # Composite score
    positive = (
        0.38 * vegetation_ratio
        + 0.30 * exg_score
        + 0.12 * texture_score
    )
    negative = (
        0.44 * min(skin_ratio * 2.2, 1.0)
        + 0.18 * achromatic_ratio
        + 0.12 * blue_ratio
        + (0.28 if bright_uniform else 0.0)
    )
    plant_confidence = float(np.clip(positive - negative, 0.0, 1.0))

    is_valid = plant_confidence >= PLANT_CONFIDENCE_THRESHOLD
    is_ambiguous = is_valid and (plant_confidence < AMBIGUOUS_THRESHOLD or quality_audit["blur_detected"])
    quality_audit["leaf_detected"] = bool(is_valid)

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
    elif quality_audit["blur_detected"]:
        is_ambiguous = True

    detail = {
        "vegetation_ratio": round(vegetation_ratio, 3),
        "exg_score": round(exg_score, 3),
        "mean_exg": round(mean_exg, 3),
        "texture_score": round(texture_score, 3),
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
        quality_score=quality_score,
        quality_audit=quality_audit,
        detail=detail,
    )
