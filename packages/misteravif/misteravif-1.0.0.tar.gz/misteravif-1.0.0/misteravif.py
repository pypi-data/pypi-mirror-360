#!/usr/bin/env python3
import os
import shutil
import subprocess
import argparse
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import pillow_avif
from tqdm import tqdm
from dataclasses import dataclass

@dataclass(frozen=True)
class AvifFile:
    path: str
    quality: int

@dataclass(frozen=True)
class AvifImage:
    path: str
    quality: int
    image: Image.Image

# Function to convert image to AVIF at different quality levels
def convert_to_avif(input_path, output_path, quality, speed=3):
    subprocess.run(["avifenc", "-s", str(speed), "-q", str(quality), input_path, output_path])

# Function to create sections and place quality labels on each
def join_sections_for_visual_compare(sectioned_images: List[AvifImage]):
    # Get dimensions from first section
    first_section = sectioned_images[0].image
    section_width, section_height = first_section.size  # w, h
    
    # Calculate canvas size based on section dimensions
    canvas_width = section_width * 5  # 5 columns
    canvas_height = section_height * 4  # 4 rows
    
    # Create canvas once outside the loop
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    font = ImageFont.load_default(size=45)
    
    for precomputed_section in sectioned_images:
        # Calculate row and column based on quality
        quality = precomputed_section.quality
        row = (quality - 5) // 25    # Maps 5-100 to rows 0-3
        col = ((quality - 5) % 25) // 5  # Maps 5-100 to columns 0-4
        
        # Calculate text position relative to section size
        text_x = section_width * 0.03  # 3% from left
        text_y = section_height * 0.9   # 90% from top
        
        # Draw quality label
        draw = ImageDraw.Draw(precomputed_section.image)
        draw.text((text_x, text_y), f"q={quality}", fill="red", font=font)
        
        # Paste section onto canvas
        canvas.paste(precomputed_section.image, 
                    (col * section_width, row * section_height))
    
    return canvas

def convert_images_to_avif(image_path, avif_files, speed=3):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(convert_to_avif, image_path, avif_file.path, avif_file.quality, speed=speed)
            for avif_file in avif_files
        ]
        for future in futures:
            future.result()

def check_missing_avif_files(avif_paths: List[AvifFile]):
    missing_files = [avif_file.path for avif_file in avif_paths if not os.path.exists(avif_file.path)]
    if missing_files:
        print(f"Missing AVIF files: {missing_files}")
        return True
    return False

def load_avif_images(avif_paths: List[AvifFile]) -> List[AvifImage]:
    """
    Load multiple AVIF images into a list
    
    Args:
        avif_paths: List of paths to AVIF image files
        
    Returns:
        List of AvifImage instances
    """
    images = []
    for avif_file in tqdm(avif_paths, desc="Loading AVIF images"):
        try:
            image = AvifImage(
                path=avif_file.path,
                quality=avif_file.quality,
                image=Image.open(avif_file.path)
            )
            images.append(image)
        except Exception as e:
            print(f"Error loading {avif_file.path}: {e}")
            continue
    return images

def extract_section_from_images(images: List[AvifImage], coords):
    """Process image sections using cached images."""
    quality_images = []
    x, y, w, h = coords
    
    for cached_img in images:
        section = cached_img.image.crop((x, y, x + w, y + h))
        avif_image = AvifImage(path=cached_img.path, quality=cached_img.quality, image=section)
        quality_images.append(avif_image)

        
    return quality_images

def get_grid_positions(width, height, min_width):
    # Precompute x and y positions
    x_positions = [int(width * factor) for factor in (0.25, 0.5, 0.75)]
    y_positions = [int(height * factor) for factor in (0.25, 0.5, 0.75)]
    
    # Adjustment for centering
    offset = min_width // 2
    
    # Generate all grid positions
    positions = {
        f"{row}{col}": (x - offset, y - offset, min_width, min_width)
        for y, row in zip(y_positions, 'abc')
        for x, col in zip(x_positions, [1, 2, 3])
    }
    
    return positions

def main():
    parser = argparse.ArgumentParser(description="Recompress image to AVIF and analyze quality.")
    parser.add_argument("image_path", type=str, help="Path to the image file.")
    parser.add_argument("-a", "--analyze-only", action="store_true", help="Only analyze the image sections, skip exporting to AVIF.")
    parser.add_argument("-s", "--speed", type=int, choices=range(0, 11), 
                        default=6, help="AVIF encoding speed (0-10, default: 3). Lower is slower but better quality")
    args = parser.parse_args()

    # 1. Set up paths and create directory structure
    image_path = args.image_path
    filename = os.path.basename(image_path)
    filename_no_ext = os.path.splitext(filename)[0]
    # Create output_dir in the same directory as the source image
    image_dir = os.path.dirname(os.path.abspath(image_path))
    output_dir = os.path.join(image_dir, filename_no_ext)
    os.makedirs(output_dir, exist_ok=True)
    original_image_path = os.path.join(output_dir, f"Original{os.path.splitext(filename)[1]}")
    shutil.copy(image_path, original_image_path)

    # 2. Convert image to AVIF at various quality levels in parallel
    quality_levels = list(range(5, 101, 5))
    # Create instances of the namedtuple
    avif_paths = [AvifFile(os.path.join(output_dir, f"q{q:02d}.avif"), q) for q in quality_levels]

    if not args.analyze_only:
        convert_images_to_avif(image_path, avif_paths, speed=args.speed)
    else:
        # Check if all AVIF images are present
        if check_missing_avif_files(avif_paths):
            return

    # 3. Plot quality vs filesize in percentage
    original_size = os.path.getsize(original_image_path)
    avif_sizes = [os.path.getsize(avif_file.path) for avif_file in avif_paths]
    filesize_ratios = [(size / original_size) * 100 for size in avif_sizes]
    plt.plot(quality_levels, filesize_ratios, marker='o')
    plt.xlabel("Quality")
    plt.ylabel("File Size (% of original)")
    plt.title("File Size vs Quality for AVIF Compression")
    plt.savefig(os.path.join(output_dir, "Filesizes.png"))
    plt.close()

    # 4. Extract sections at three positions
    input_image = Image.open(original_image_path)
    width, height = input_image.size
    sections = get_grid_positions(width, height, max(int(width * 0.1), 200))

    # Load images once
    images = load_avif_images(avif_paths)

    # Load each quality level image and create sectioned images
    sectioned_images = {}
    for key, coords in tqdm(sections.items(), desc="Extracting sections"):
        sections = extract_section_from_images(images, coords)
        
        # Generate a combined sectioned image
        joined_sections = join_sections_for_visual_compare(sectioned_images=sections)
        joined_sections.save(os.path.join(output_dir, f"Section {key}.png"))

if __name__ == "__main__":
    main()
