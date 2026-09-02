"""
utils.py
--------
Botanical Image Gatekeeping & Segmentation Utility.
Uses OpenCV GrabCut for foreground isolation and strict chlorophyll/color
metrics to reject non-leaf images (animals, human faces, random objects).
"""

import cv2
import numpy as np


def extract_leaf_with_grabcut(image_bytes):
  """Extracts the foreground leaf object and returns the segmented image and binary mask."""
  np_arr = np.frombuffer(image_bytes, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
  if img is None:
    return None, None

  height, width = img.shape[:2]
  rect = (2, 2, width - 4, height - 4)
  mask = np.zeros((height, width), np.uint8)
  bgdModel = np.zeros((1, 65), np.float64)
  fgdModel = np.zeros((1, 65), np.float64)

  try:
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 3, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    # If GrabCut strips out too much foreground, preserve the original frame
    kept_ratio = np.sum(mask2) / (height * width)
    if kept_ratio < 0.08:
      return img, np.ones((height, width), dtype=np.uint8)

    segmented_img = img * mask2[:, :, np.newaxis]
    return segmented_img, mask2
  except Exception:
    return img, np.ones((height, width), dtype=np.uint8)


def is_valid_leaf(
    image_bgr,
    foreground_mask,
    min_foreground_ratio=0.08,
    min_leaf_color_ratio=0.35,
):
  """Strict botanical verification.

  Checks for foreground density, botanical HSV range, and green channel
  dominance.
  """
  total_pixels = foreground_mask.size
  foreground_pixels = int(foreground_mask.sum())
  foreground_ratio = foreground_pixels / total_pixels

  # Check 1: Minimum foreground coverage
  if foreground_ratio < min_foreground_ratio:
    return (
        False,
        "No clear leaf detected in frame. Please capture a closer shot.",
    )

  hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

  # Check 2: Botanical leaf spectrum (chlorophyll green, chlorosis, and dry leaf brown)
  lower_botanical = np.array([25, 35, 25])
  upper_botanical = np.array([88, 255, 255])
  botanical_mask = cv2.inRange(hsv, lower_botanical, upper_botanical)

  combined_mask = cv2.bitwise_and(
      botanical_mask, botanical_mask, mask=foreground_mask
  )
  botanical_pixels = int(np.count_nonzero(combined_mask))
  leaf_ratio = botanical_pixels / (foreground_pixels + 1e-6)

  # Check 3: Green channel dominance (leaves typically have G > R*0.9 and G > B*0.9)
  b, g, r = cv2.split(image_bgr)
  green_dominant = (g > r * 0.90) & (g > b * 0.90) & (foreground_mask > 0)
  green_dom_ratio = int(np.count_nonzero(green_dominant)) / (
      foreground_pixels + 1e-6
  )

  if leaf_ratio < min_leaf_color_ratio and green_dom_ratio < 0.30:
    return (
        False,
        (
            "The uploaded image does not appear to be a plant leaf. Please"
            " upload a clear leaf photo."
        ),
    )

  return True, "OK"