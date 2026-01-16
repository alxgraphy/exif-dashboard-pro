"""
EXIF Analyzer - Extract metadata from photos
"""
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from tqdm import tqdm


class ExifAnalyzer:
    """Extract and analyze EXIF data from photos"""
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    
    def __init__(self):
        self.photos_data = []
    
    def scan_folder(self, folder_path, recursive=True):
        """
        Scan folder for photos and extract EXIF data
        
        Args:
            folder_path: Path to folder containing photos
            recursive: Whether to scan subfolders
            
        Returns:
            List of dictionaries containing EXIF data
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")
        
        # Find all image files
        if recursive:
            image_files = [f for f in folder.rglob('*') if f.suffix.lower() in self.SUPPORTED_FORMATS]
        else:
            image_files = [f for f in folder.glob('*') if f.suffix.lower() in self.SUPPORTED_FORMATS]
        
        print(f"Found {len(image_files)} photos to analyze...")
        
        # Extract EXIF from each file
        self.photos_data = []
        for img_path in tqdm(image_files, desc="Extracting EXIF data"):
            exif_data = self.extract_exif(img_path)
            if exif_data:
                self.photos_data.append(exif_data)
        
        return self.photos_data
    
    def extract_exif(self, image_path):
        """
        Extract EXIF data from a single image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted EXIF data or None
        """
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                return None
            
            # Initialize parsed data
            parsed_data = {
                'filename': image_path.name,
                'filepath': str(image_path),
                'file_size': image_path.stat().st_size / (1024 * 1024),  # MB
            }
            
            # Extract key metadata
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                if tag_name == "Make":
                    parsed_data['camera_make'] = str(value).strip()
                elif tag_name == "Model":
                    parsed_data['camera_model'] = str(value).strip()
                elif tag_name == "LensModel":
                    parsed_data['lens'] = str(value).strip()
                elif tag_name == "FocalLength":
                    parsed_data['focal_length'] = self._parse_rational(value)
                elif tag_name == "FNumber":
                    parsed_data['aperture'] = self._parse_rational(value)
                elif tag_name == "ExposureTime":
                    parsed_data['shutter_speed'] = self._parse_shutter_speed(value)
                elif tag_name == "ISOSpeedRatings":
                    parsed_data['iso'] = int(value)
                elif tag_name in ["DateTime", "DateTimeOriginal"]:
                    parsed_data['datetime'] = self._parse_datetime(value)
                elif tag_name == "Flash":
                    parsed_data['flash_used'] = bool(value & 1)
                elif tag_name == "GPSInfo":
                    gps_data = self._parse_gps(value)
                    if gps_data:
                        parsed_data.update(gps_data)
            
            # Add image dimensions and orientation
            parsed_data['width'], parsed_data['height'] = image.size
            parsed_data['orientation'] = 'portrait' if image.size[1] > image.size[0] else 'landscape'
            
            return parsed_data
            
        except Exception as e:
            print(f"Error processing {image_path.name}: {str(e)}")
            return None
    
    def _parse_rational(self, value):
        """Parse rational number (fraction) from EXIF"""
        try:
            if isinstance(value, tuple):
                return round(value[0] / value[1], 1)
            return float(value)
        except:
            return None
    
    def _parse_shutter_speed(self, value):
        """Parse shutter speed from EXIF"""
        try:
            if isinstance(value, tuple):
                numerator, denominator = value
                if numerator >= denominator:
                    return f"{numerator / denominator:.1f}s"
                else:
                    return f"1/{int(denominator / numerator)}"
            return str(value)
        except:
            return None
    
    def _parse_datetime(self, value):
        """Parse datetime from EXIF"""
        try:
            return datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
        except:
            return None
    
    def _parse_gps(self, gps_info):
        """Parse GPS coordinates from EXIF"""
        try:
            gps_data = {}
            for tag_id, value in gps_info.items():
                tag_name = GPSTAGS.get(tag_id, tag_id)
                gps_data[tag_name] = value
            
            if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                lat = self._convert_to_degrees(gps_data['GPSLatitude'])
                lon = self._convert_to_degrees(gps_data['GPSLongitude'])
                
                # Handle hemisphere
                if gps_data.get('GPSLatitudeRef') == 'S':
                    lat = -lat
                if gps_data.get('GPSLongitudeRef') == 'W':
                    lon = -lon
                
                return {'latitude': lat, 'longitude': lon}
        except:
            pass
        return None
    
    def _convert_to_degrees(self, value):
        """Convert GPS coordinates to degrees"""
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)