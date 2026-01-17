# EXIF Dashboard Pro 📸

A powerful web-based photo analysis tool that extracts EXIF metadata from your photo collection and displays beautiful interactive dashboards with statistics, charts, and maps.

Perfect for photographers who want deep insights into their shooting habits, gear usage, and creative patterns.

## Features

* Upload photos via ZIP file or individually
* Supports JPG, PNG, TIFF, and RAW formats (CR2, NEF, ARW)
* **Camera & Lens Statistics** - See which gear you use most
* **Settings Analysis** - ISO, aperture, focal length distributions
* **Timeline Visualization** - When you shoot most often
* **Time of Day Patterns** - Morning, golden hour, night shooting habits
* **GPS Location Mapping** - See everywhere you've photographed
* **Interactive Charts** - Beautiful Plotly visualizations
* **Export Reports** - Save your analysis
## 📸 Screenshots

### Main Dashboard
<img width="1439" alt="EXIF Dashboard Overview" src="https://github.com/user-attachments/assets/43201d85-4203-4fef-8da8-ac29702112b5" />


### Camera & Lens Analysis
<img width="1439" height="789" alt="Image" src="https://github.com/user-attachments/assets/349521b2-e397-41fd-9a3b-2a83b5c97796" />

## Requirements

* Python 3.8+
* Dependencies:
  ```
  Pillow
  pandas
  plotly
  streamlit
  streamlit-folium
  folium
  tqdm
  ```

## Installation & Usage (If you want to run it at home)

**1. Clone the repository:**

```bash
git clone https://github.com/alxgraphy/exif-dashboard-pro.git
cd exif-dashboard-pro
```

**2. Create and activate a virtual environment (recommended):**

```bash
python3 -m venv venv
source venv/bin/activate  # macOS / Linux
```

OR on Windows: `venv\Scripts\activate`

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Run the web app:**

```bash
streamlit run web/app.py
```

**5. Open your browser** to `http://localhost:8501` and upload your photos!

## What Gets Analyzed

* **Camera info** - Make, model, which cameras you use most
* **Lens info** - Lens model, focal lengths, most-used lenses
* **Exposure settings** - ISO range, aperture preferences, shutter speeds
* **Shooting patterns** - Timeline, time of day, day of week
* **GPS data** - Location mapping (if your camera records GPS)
* **Image metadata** - Dimensions, portrait vs landscape ratios
* **Flash usage** - How often you use flash

## Project Structure

```
exif-dashboard-pro/
├── src/
│   ├── exif_analyzer.py      # EXIF extraction engine
│   └── data_processor.py     # Data analysis & statistics
├── web/
│   └── app.py                # Streamlit web application
|
└── README.md                 # This file
```

## Tips & Notes

* **Best results** with photos directly from your camera (EXIF data intact)
* **Social media photos** often have EXIF stripped - use originals
* **RAW support** works for metadata extraction (no image preview)
* **GPS mapping** only works if your camera records location data
* **Large collections** (1000+ photos) may take a few minutes to analyze

## Made with ❤️ in Toronto, Canada 🇨🇦

**By Alexander Wondwossen** ([@alxgraphy](https://github.com/alxgraphy))

Feel free to fork, modify, use, and share — open an issue/PR if you like it or want improvements!

## License

Copyright 2026 Alexander Wondwossen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
