"""
Data Processor - Process and analyze EXIF data
"""
import pandas as pd
from typing import List, Dict


class DataProcessor:
    """Process EXIF data for analysis and visualization"""
    
    def __init__(self, photos_data: List[Dict]):
        """
        Initialize with extracted EXIF data
        
        Args:
            photos_data: List of dictionaries containing EXIF data
        """
        self.df = pd.DataFrame(photos_data)
        self.process_data()
    
    def process_data(self):
        """Clean and prepare data for analysis"""
        if self.df.empty:
            return
        
        # Process datetime data
        if 'datetime' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['datetime'])
            self.df['year'] = self.df['date'].dt.year
            self.df['month'] = self.df['date'].dt.month
            self.df['day_of_week'] = self.df['date'].dt.day_name()
            self.df['hour'] = self.df['date'].dt.hour
            self.df['time_of_day'] = self.df['hour'].apply(self._categorize_time_of_day)
    
    def _categorize_time_of_day(self, hour):
        """Categorize hour into time of day periods"""
        if pd.isna(hour):
            return 'Unknown'
        if 5 <= hour < 8:
            return 'Early Morning'
        elif 8 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 20:
            return 'Golden Hour'
        elif 20 <= hour < 23:
            return 'Evening'
        else:
            return 'Night'
    
    def get_camera_usage(self) -> pd.DataFrame:
        """Get camera usage statistics"""
        if 'camera_model' not in self.df.columns:
            return pd.DataFrame()
        
        camera_counts = self.df['camera_model'].value_counts()
        return pd.DataFrame({
            'Camera': camera_counts.index,
            'Photos': camera_counts.values,
            'Percentage': (camera_counts.values / len(self.df) * 100).round(1)
        })
    
    def get_lens_usage(self) -> pd.DataFrame:
        """Get lens usage statistics"""
        if 'lens' not in self.df.columns:
            return pd.DataFrame()
        
        lens_counts = self.df['lens'].value_counts()
        return pd.DataFrame({
            'Lens': lens_counts.index,
            'Photos': lens_counts.values,
            'Percentage': (lens_counts.values / len(self.df) * 100).round(1)
        })
    
    def get_iso_distribution(self) -> pd.DataFrame:
        """Get ISO distribution"""
        if 'iso' not in self.df.columns:
            return pd.DataFrame()
        
        iso_counts = self.df['iso'].value_counts().sort_index()
        return pd.DataFrame({
            'ISO': iso_counts.index,
            'Count': iso_counts.values
        })
    
    def get_aperture_distribution(self) -> pd.DataFrame:
        """Get aperture distribution"""
        if 'aperture' not in self.df.columns:
            return pd.DataFrame()
        
        aperture_counts = self.df['aperture'].value_counts().sort_index()
        return pd.DataFrame({
            'Aperture': aperture_counts.index,
            'Count': aperture_counts.values
        })
    
    def get_focal_length_distribution(self) -> pd.DataFrame:
        """Get focal length distribution"""
        if 'focal_length' not in self.df.columns:
            return pd.DataFrame()
        
        fl_counts = self.df['focal_length'].value_counts().sort_index()
        return pd.DataFrame({
            'Focal Length (mm)': fl_counts.index,
            'Count': fl_counts.values
        })
    
    def get_shooting_timeline(self, freq='M') -> pd.DataFrame:
        """
        Get photo count over time
        
        Args:
            freq: Frequency ('D'=day, 'W'=week, 'M'=month, 'Y'=year)
        """
        if 'date' not in self.df.columns:
            return pd.DataFrame()
        
        timeline = self.df.groupby(pd.Grouper(key='date', freq=freq)).size()
        return pd.DataFrame({
            'Date': timeline.index,
            'Photos': timeline.values
        })
    
    def get_time_of_day_distribution(self) -> pd.DataFrame:
        """Get distribution of photos by time of day"""
        if 'time_of_day' not in self.df.columns:
            return pd.DataFrame()
        
        time_order = ['Early Morning', 'Morning', 'Afternoon', 'Golden Hour', 'Evening', 'Night']
        tod_counts = self.df['time_of_day'].value_counts()
        tod_counts = tod_counts.reindex(time_order, fill_value=0)
        
        return pd.DataFrame({
            'Time of Day': tod_counts.index,
            'Photos': tod_counts.values
        })
    
    def get_day_of_week_distribution(self) -> pd.DataFrame:
        """Get distribution of photos by day of week"""
        if 'day_of_week' not in self.df.columns:
            return pd.DataFrame()
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = self.df['day_of_week'].value_counts()
        dow_counts = dow_counts.reindex(day_order, fill_value=0)
        
        return pd.DataFrame({
            'Day': dow_counts.index,
            'Photos': dow_counts.values
        })
    
    def get_orientation_stats(self) -> Dict:
        """Get portrait vs landscape statistics"""
        if 'orientation' not in self.df.columns:
            return {}
        
        orientation_counts = self.df['orientation'].value_counts()
        return {
            'portrait': orientation_counts.get('portrait', 0),
            'landscape': orientation_counts.get('landscape', 0)
        }
    
    def get_flash_usage_stats(self) -> Dict:
        """Get flash usage statistics"""
        if 'flash_used' not in self.df.columns:
            return {}
        
        flash_counts = self.df['flash_used'].value_counts()
        return {
            'used': flash_counts.get(True, 0),
            'not_used': flash_counts.get(False, 0)
        }
    
    def get_gps_photos(self) -> pd.DataFrame:
        """Get all photos with GPS data"""
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            return pd.DataFrame()
        
        gps_df = self.df[['filename', 'latitude', 'longitude', 'date']].dropna()
        return gps_df
    
    def get_summary_report(self) -> Dict:
        """Generate comprehensive summary report"""
        report = {
            'total_photos': len(self.df),
            'unique_cameras': self.df['camera_model'].nunique() if 'camera_model' in self.df.columns else 0,
            'unique_lenses': self.df['lens'].nunique() if 'lens' in self.df.columns else 0,
            'photos_with_gps': self.df['latitude'].notna().sum() if 'latitude' in self.df.columns else 0,
        }
        
        # Date range
        if 'date' in self.df.columns:
            report['date_range'] = {
                'earliest': self.df['date'].min(),
                'latest': self.df['date'].max(),
                'span_days': (self.df['date'].max() - self.df['date'].min()).days
            }
        
        # ISO stats
        if 'iso' in self.df.columns:
            report['iso_stats'] = {
                'min': int(self.df['iso'].min()),
                'max': int(self.df['iso'].max()),
                'mean': int(self.df['iso'].mean()),
                'median': int(self.df['iso'].median())
            }
        
        # Aperture stats
        if 'aperture' in self.df.columns:
            report['aperture_stats'] = {
                'min': float(self.df['aperture'].min()),
                'max': float(self.df['aperture'].max()),
                'most_common': float(self.df['aperture'].mode()[0]) if len(self.df['aperture'].mode()) > 0 else None
            }
        
        # Focal length stats
        if 'focal_length' in self.df.columns:
            report['focal_length_stats'] = {
                'min': float(self.df['focal_length'].min()),
                'max': float(self.df['focal_length'].max()),
                'most_common': float(self.df['focal_length'].mode()[0]) if len(self.df['focal_length'].mode()) > 0 else None
            }
        
        return report