"""
EXIF Dashboard Pro - Streamlit Web Application
"""
import streamlit as st
import sys
from pathlib import Path
import tempfile
import zipfile
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from exif_analyzer import ExifAnalyzer
from data_processor import DataProcessor


# Page configuration
st.set_page_config(
    page_title="EXIF Dashboard Pro",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<div class="main-header">📸 EXIF Dashboard Pro</div>', unsafe_allow_html=True)
    st.markdown("### Analyze your photo collection's EXIF metadata")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        st.markdown("---")
        st.markdown("### Upload Photos")
        st.info("📦 **ZIP files**: Can contain nested folders - all photos will be scanned recursively!")
        
        upload_type = st.radio("Upload method:", ["ZIP file (supports nested folders)", "Individual photos"])
        
        if upload_type == "ZIP file (supports nested folders)":
            uploaded_file = st.file_uploader(
                "Choose a ZIP file with photos", 
                type=['zip'],
                help="Your ZIP can have folders within folders - we'll scan everything!"
            )
        else:
            uploaded_files = st.file_uploader(
                "Choose photos", 
                type=['jpg', 'jpeg', 'png', 'tiff'], 
                accept_multiple_files=True,
                help="Select multiple photos at once"
            )
        
        st.markdown("---")
        st.markdown("### Analysis Options")
        show_gps = st.checkbox("Show GPS Map", value=True)
        timeline_freq = st.selectbox(
            "Timeline frequency", 
            ['D', 'W', 'M', 'Y'], 
            format_func=lambda x: {'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly', 'Y': 'Yearly'}[x],
            index=2
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("Built with ❤️ by [thealxlabs](https://github.com/thealxlabs)")
    
    # Main content
    if upload_type == "ZIP file (supports nested folders)" and uploaded_file is not None:
        process_zip_upload(uploaded_file, show_gps, timeline_freq)
    elif upload_type == "Individual photos" and uploaded_files:
        process_individual_uploads(uploaded_files, show_gps, timeline_freq)
    else:
        show_welcome_screen()


def show_welcome_screen():
    """Display welcome screen with instructions"""
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🚀 Get Started")
        st.markdown("""
        ### How to use:
        1. **Upload your photos** using the sidebar
           - 📦 **ZIP file**: Perfect for large collections with nested folders
             - Example: `Photos/2024/January/Trip/IMG_001.jpg` ✅
             - We'll scan ALL folders recursively!
           - 📸 **Individual photos**: Select multiple files at once
        
        2. **Analyze** your photography habits
           - See which cameras and lenses you use most
           - Discover your preferred settings (ISO, aperture, focal length)
           - View when and where you take photos
        
        3. **Explore** your statistics
           - Interactive charts and visualizations
           - GPS location mapping
           - Timeline analysis
        
        ### 💡 Tips:
        - ZIP files can have folders within folders - we scan everything!
        - Works best with original photos (not edited or social media versions)
        - Photos must have EXIF metadata (most camera/phone photos do)
        - Large collections (1000+ photos) take 1-2 minutes to process
        """)


def process_zip_upload(uploaded_file, show_gps, timeline_freq):
    """Process uploaded ZIP file with nested folder support"""
    with st.spinner("📦 Extracting ZIP and scanning all folders (including nested ones)..."):
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract ZIP
            zip_path = temp_path / "photos.zip"
            with open(zip_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            st.info("🔍 Scanning all folders recursively for photos...")
            
            # Analyze photos (recursive=True scans all nested folders)
            analyzer = ExifAnalyzer()
            photos_data = analyzer.scan_folder(str(extract_path), recursive=True)
            
            if not photos_data:
                st.error("❌ No valid photos with EXIF data found in the ZIP file (checked all nested folders).")
                st.info("💡 Make sure your photos are JPG, PNG, or TIFF with EXIF metadata intact.")
                return
            
            st.success(f"✅ Found {len(photos_data)} photos across all folders!")
            
            # Process and display results
            display_dashboard(photos_data, show_gps, timeline_freq)


def process_individual_uploads(uploaded_files, show_gps, timeline_freq):
    """Process individually uploaded photos"""
    with st.spinner(f"Analyzing {len(uploaded_files)} photos..."):
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded files
            for uploaded_file in uploaded_files:
                file_path = temp_path / uploaded_file.name
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
            
            # Analyze photos
            analyzer = ExifAnalyzer()
            photos_data = analyzer.scan_folder(str(temp_path), recursive=False)
            
            if not photos_data:
                st.error("No valid photos with EXIF data found.")
                return
            
            # Process and display results
            display_dashboard(photos_data, show_gps, timeline_freq)


def display_dashboard(photos_data, show_gps, timeline_freq):
    """Display comprehensive analysis dashboard"""
    
    # Create data processor
    processor = DataProcessor(photos_data)
    
    # Get summary report
    summary = processor.get_summary_report()
    
    # Display summary statistics
    st.markdown("---")
    st.markdown("## 📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{summary['total_photos']}</div>
            <div class="stat-label">Total Photos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{summary['unique_cameras']}</div>
            <div class="stat-label">Cameras Used</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{summary['unique_lenses']}</div>
            <div class="stat-label">Lenses Used</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{summary['photos_with_gps']}</div>
            <div class="stat-label">Photos with GPS</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Camera and Lens Usage
    st.markdown("---")
    st.markdown("## 📷 Camera & Lens Usage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Camera Distribution")
        camera_df = processor.get_camera_usage()
        if not camera_df.empty:
            fig = px.pie(
                camera_df, 
                values='Photos', 
                names='Camera', 
                title='Camera Usage',
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show table
            st.dataframe(camera_df, use_container_width=True, hide_index=True)
        else:
            st.info("No camera data available")
    
    with col2:
        st.markdown("### Lens Distribution")
        lens_df = processor.get_lens_usage()
        if not lens_df.empty:
            fig = px.pie(
                lens_df, 
                values='Photos', 
                names='Lens',
                title='Lens Usage',
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show table
            st.dataframe(lens_df, use_container_width=True, hide_index=True)
        else:
            st.info("No lens data available")
    
    # Settings Analysis
    st.markdown("---")
    st.markdown("## ⚙️ Camera Settings Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ISO Distribution")
        iso_df = processor.get_iso_distribution()
        if not iso_df.empty:
            fig = px.bar(
                iso_df, 
                x='ISO', 
                y='Count', 
                title='ISO Usage',
                labels={'Count': 'Number of Photos'}
            )
            fig.update_traces(marker_color='#1f77b4')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ISO data available")
    
    with col2:
        st.markdown("### Aperture Distribution")
        aperture_df = processor.get_aperture_distribution()
        if not aperture_df.empty:
            fig = px.bar(
                aperture_df, 
                x='Aperture', 
                y='Count', 
                title='Aperture Usage',
                labels={'Count': 'Number of Photos', 'Aperture': 'f-stop'}
            )
            fig.update_traces(marker_color='#ff7f0e')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No aperture data available")
    
    with col3:
        st.markdown("### Focal Length Distribution")
        fl_df = processor.get_focal_length_distribution()
        if not fl_df.empty:
            fig = px.bar(
                fl_df, 
                x='Focal Length (mm)', 
                y='Count', 
                title='Focal Length Usage',
                labels={'Count': 'Number of Photos'}
            )
            fig.update_traces(marker_color='#2ca02c')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No focal length data available")
    
    # Timeline Analysis
    st.markdown("---")
    st.markdown("## 📅 Shooting Timeline")
    
    timeline_df = processor.get_shooting_timeline(freq=timeline_freq)
    if not timeline_df.empty:
        fig = px.line(
            timeline_df, 
            x='Date', 
            y='Photos', 
            title='Photos Over Time',
            labels={'Photos': 'Number of Photos'}
        )
        fig.update_traces(mode='lines+markers', line_color='#1f77b4')
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date data available for timeline")
    
    # Time of Day Analysis
    st.markdown("---")
    st.markdown("## 🌅 Shooting Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Time of Day Distribution")
        tod_df = processor.get_time_of_day_distribution()
        if not tod_df.empty:
            fig = px.bar(
                tod_df, 
                x='Time of Day', 
                y='Photos',
                title='Photos by Time of Day',
                labels={'Photos': 'Number of Photos'}
            )
            fig.update_traces(marker_color='#ff7f0e')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No time data available")
    
    with col2:
        st.markdown("### Day of Week Distribution")
        dow_df = processor.get_day_of_week_distribution()
        if not dow_df.empty:
            fig = px.bar(
                dow_df, 
                x='Day', 
                y='Photos',
                title='Photos by Day of Week',
                labels={'Photos': 'Number of Photos'}
            )
            fig.update_traces(marker_color='#2ca02c')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No day data available")
    
    # GPS Map
    if show_gps:
        st.markdown("---")
        st.markdown("## 🗺️ Photo Locations")
        
        gps_df = processor.get_gps_photos()
        if not gps_df.empty:
            # Create map centered on average location
            center_lat = gps_df['latitude'].mean()
            center_lon = gps_df['longitude'].mean()
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
            
            # Add markers for each photo
            for idx, row in gps_df.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    popup=row['filename'],
                    color='blue',
                    fill=True,
                    fillColor='blue',
                    fillOpacity=0.6
                ).add_to(m)
            
            # Display map
            folium_static(m, width=1200, height=500)
            st.info(f"Showing {len(gps_df)} photos with GPS coordinates")
        else:
            st.info("No GPS data available in photos")
    
    # Additional Statistics
    st.markdown("---")
    st.markdown("## 📈 Additional Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Photo Orientation")
        orientation_stats = processor.get_orientation_stats()
        if orientation_stats:
            fig = go.Figure(data=[go.Pie(
                labels=['Portrait', 'Landscape'],
                values=[orientation_stats.get('portrait', 0), orientation_stats.get('landscape', 0)],
                hole=0.3
            )])
            fig.update_layout(title='Portrait vs Landscape')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Flash Usage")
        flash_stats = processor.get_flash_usage_stats()
        if flash_stats:
            fig = go.Figure(data=[go.Pie(
                labels=['Flash Used', 'No Flash'],
                values=[flash_stats.get('used', 0), flash_stats.get('not_used', 0)],
                hole=0.3
            )])
            fig.update_layout(title='Flash Usage')
            st.plotly_chart(fig, use_container_width=True)
    
    # Show detailed summary at the end
    if 'date_range' in summary:
        st.markdown("---")
        st.markdown("## 📋 Collection Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Date Range", f"{summary['date_range']['span_days']} days")
            st.caption(f"From {summary['date_range']['earliest'].strftime('%Y-%m-%d')} to {summary['date_range']['latest'].strftime('%Y-%m-%d')}")
        
        with col2:
            if 'iso_stats' in summary:
                st.metric("ISO Range", f"{summary['iso_stats']['min']} - {summary['iso_stats']['max']}")
                st.caption(f"Average: {summary['iso_stats']['mean']}")
        
        with col3:
            if 'aperture_stats' in summary:
                st.metric("Aperture Range", f"f/{summary['aperture_stats']['min']} - f/{summary['aperture_stats']['max']}")
                if summary['aperture_stats']['most_common']:
                    st.caption(f"Most used: f/{summary['aperture_stats']['most_common']}")


if __name__ == "__main__":
    main()

# Made with ❤️ in Toronto, Canada 🇨🇦 by Alexander Wondwossen (@thealxlabs)
