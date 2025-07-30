from typing import TypeVar, NewType, Any, TypeGuard, TypeAlias

import numpy as np

from ._shape import Width, Height
from ..data import DataLabel, is_data_label

T = TypeVar("T", bound=np.generic)

Image: TypeAlias = np.ndarray[tuple[Width, Height], np.dtype[T]]

ImageLabel = NewType("ImageLabel", DataLabel)


def is_image(image: Any) -> TypeGuard[Image]:
    """Check if image has a valid image type."""

    return isinstance(image, np.ndarray) and image.ndim == 2


def is_image_label(label: Any) -> TypeGuard[ImageLabel]:
    """Check if label has a valid image label type."""

    return is_data_label(label)
