"""
Automatic Media Optimizer for TDMai Website
Converts all uploaded images to WebP format (ultra-fast, highly compressed, crisp quality).
Converts all uploaded videos to WebM format using ffmpeg (if installed on server),
with graceful fallback if ffmpeg is unavailable.
"""

import os
import shutil
import subprocess
import tempfile
import logging
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


def convert_image_to_webp(field_file, max_width=1920, quality=82):
    """
    Converts an ImageField / FileField file to WebP format.
    - Preserves alpha transparency for PNGs and icons
    - Auto-orients images based on EXIF
    - Downscales massive camera photos to max_width (default 1920px)
    - Returns a new ContentFile with .webp extension, or None if no change.
    """
    if not field_file or not field_file.name:
        return None

    filename = field_file.name
    ext = os.path.splitext(filename)[1].lower()

    # Determine if this is a newly uploaded file
    try:
        is_new_upload = hasattr(field_file, 'file') and isinstance(field_file.file, UploadedFile)
    except (FileNotFoundError, OSError):
        return None

    # If already webp and not a raw new upload needing resize/compression, skip
    if ext == '.webp' and not is_new_upload:
        return None

    try:
        field_file.open()
        img = Image.open(field_file)

        # Auto-rotate based on EXIF (prevents sideways smartphone photos)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # Resize if width exceeds max_width
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * float(ratio))
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Handle color modes
        has_alpha = False
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')
            has_alpha = True
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        output_buf = BytesIO()
        # Save as WebP
        img.save(
            output_buf,
            format='WEBP',
            quality=quality,
            method=5,
            lossless=False
        )
        output_buf.seek(0)

        base_name = os.path.splitext(os.path.basename(filename))[0]
        # Clean slug base_name if needed
        clean_name = f"{base_name}.webp"

        return ContentFile(output_buf.getvalue(), name=clean_name)

    except Exception as e:
        logger.warning(f"Could not convert image {filename} to WebP: {e}")
        return None


def convert_video_to_webm(field_file):
    """
    Converts a video FileField to WebM format using ffmpeg if available.
    If ffmpeg is missing or conversion fails, safely leaves the original video intact.
    """
    if not field_file or not field_file.name:
        return None

    filename = field_file.name
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.webm':
        return None

    # Only process newly uploaded files to avoid re-encoding on simple edits
    is_new_upload = hasattr(field_file, 'file') and isinstance(field_file.file, UploadedFile)
    if not is_new_upload:
        return None

    ffmpeg_bin = shutil.which('ffmpeg')
    if not ffmpeg_bin:
        logger.info("ffmpeg not found on system. Video kept as original format.")
        return None

    in_temp_path = None
    out_temp_path = None
    try:
        suffix = ext if ext else '.mp4'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as in_f:
            field_file.open()
            in_f.write(field_file.read())
            in_temp_path = in_f.name

        out_temp_path = in_temp_path + '.webm'

        # Fast VP9/VP8 encode to produce high quality, small webm
        cmd = [
            ffmpeg_bin, '-y',
            '-i', in_temp_path,
            '-c:v', 'libvpx-vp9',
            '-crf', '32',
            '-b:v', '0',
            '-c:a', 'libopus',
            '-threads', '2',
            out_temp_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)

        if res.returncode == 0 and os.path.exists(out_temp_path) and os.path.getsize(out_temp_path) > 0:
            with open(out_temp_path, 'rb') as out_f:
                content = out_f.read()
            base_name = os.path.splitext(os.path.basename(filename))[0]
            clean_name = f"{base_name}.webm"
            return ContentFile(content, name=clean_name)
        else:
            logger.warning(f"ffmpeg conversion to webm failed: {res.stderr.decode('utf-8', errors='ignore')[:300]}")
    except Exception as e:
        logger.warning(f"Error converting video {filename} to WebM: {e}")
    finally:
        if in_temp_path and os.path.exists(in_temp_path):
            try:
                os.remove(in_temp_path)
            except Exception:
                pass
        if out_temp_path and os.path.exists(out_temp_path):
            try:
                os.remove(out_temp_path)
            except Exception:
                pass

    return None
