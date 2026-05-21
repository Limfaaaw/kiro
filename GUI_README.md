# 2D Network Coverage Tool - GUI Version

## Overview

The 2D Network Coverage Tool now includes a **web-based graphical user interface (GUI)** for easy interaction. The GUI provides a tabbed interface matching professional RF design tools, making it simple to:

- Load antenna patterns
- Enter parameters through intuitive forms
- Calculate electromagnetic fields
- Visualize ray-tracing geometry
- View antenna gain patterns

## Running the GUI

### Quick Start

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the web interface**:
   ```bash
   python3 coverage_tool_web.py
   ```
   
   Or use the launcher script:
   ```bash
   ./run_gui.sh
   ```

3. **Open your browser**:
   Navigate to `http://localhost:5000`

4. **Use the application**:
   The GUI will automatically load the default antenna pattern (`sample_antenna_pattern.csv`)

## GUI Features

### Tab 1: Antenna Pattern
- **Load CSV files** containing antenna gain patterns
- **View status** of loaded pattern (data points, gain range, etc.)
- Browse for files or use the default sample pattern

### Tab 2: Input Parameters
Organized sections for entering all calculation parameters:

**Transmit Signal Parameters:**
- Horizontal polarization power (dBm)
- Vertical polarization power (dBm)
- Phase shift between H and V (degrees)
- Frequency (MHz)

**Antenna Position:**
- X-coordinate (m)
- Y-coordinate (m)

**Ground Medium Properties:**
- Relative permittivity (εᵣ)
- Conductivity (S/m)
- Ground slope (m for y=mx+c)
- Ground intercept (c for y=mx+c)

**Receiver Position:**
- X-coordinate (m)
- Y-coordinate (m)

**Calculate Button:** Click to compute electromagnetic fields

### Tab 3: Results
Dual-column display showing:

**Left Column - Electric Field Results:**
- Transmitter and receiver positions
- Frequency
- H-polarization component (magnitude, phase, dBV/m)
- V-polarization component (magnitude, phase, dBV/m)
- Total E-field magnitude

**Right Column - Additional Results:**
- Magnetic field (magnitude and dB)
- Reflection point coordinates
- Ground properties summary

### Tab 4: Geometry Plot
- **Visual representation** of ray-tracing geometry
- Shows transmitter, receiver, and reflection point
- Displays direct and reflected propagation paths
- Shows ground surface (flat or sloped)
- Interactive plot with pan/zoom capabilities

### Tab 5: Antenna Pattern Plot
- **Cartesian plot**: Gain vs elevation angle
- **Polar plot**: Directional radiation pattern
- Both plots displayed side-by-side

## Default Values

The GUI comes pre-loaded with sensible defaults for a typical scenario:

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| Power (H/V) | 40 dBm | 10 W transmit power |
| Phase Shift | 0° | Linear polarization |
| Frequency | 2400 MHz | 2.4 GHz (WiFi) |
| Antenna Position | (0, 20) m | 20m high |
| εᵣ | 15.0 | Typical soil |
| σ | 0.01 S/m | Typical soil |
| Ground Slope | 0.0 | Flat ground |
| Receiver | (100, 5) m | 100m away, 5m high |

## Workflow

### Typical Usage Flow:

1. **Start the application** → Antenna pattern loads automatically
2. **Go to "Input Parameters" tab** → Modify values as needed
3. **Click "Calculate Fields"** → Results appear in Results tab
4. **Go to "Geometry Plot" tab** → Click "Plot Geometry"
5. **Go to "Antenna Pattern Plot" tab** → Click "Plot Antenna Pattern"

### Example Scenarios:

**WiFi Coverage Analysis:**
- Power: 20 dBm
- Frequency: 2400 MHz
- Antenna height: 3m
- εᵣ: 5, σ: 0.02 S/m (indoor)

**Cellular Base Station:**
- Power: 43 dBm
- Frequency: 900 MHz
- Antenna height: 25m
- εᵣ: 15, σ: 0.01 S/m (outdoor)

**Point-to-Point Link:**
- Power: 30 dBm
- Frequency: 5800 MHz
- Antenna height: 15m
- Sloped terrain: m = 0.1

## Technical Details

### Architecture

The GUI uses a **Flask** web framework with:
- **Backend**: Python Flask server (`coverage_tool_web.py`)
- **Frontend**: HTML/CSS/JavaScript (`templates/index.html`)
- **Calculations**: Original `network_coverage_tool.py` module
- **Plots**: Matplotlib with base64 encoding for web display

### API Endpoints

- `GET /` - Serve main HTML page
- `POST /api/load_pattern` - Load antenna CSV file
- `POST /api/calculate` - Calculate electromagnetic fields
- `POST /api/plot_geometry` - Generate geometry plot
- `GET /api/plot_antenna` - Generate antenna pattern plot

### Browser Compatibility

Tested and works on:
- Chrome/Chromium
- Firefox
- Safari
- Edge

## Troubleshooting

### Server won't start
- **Error**: `Port 5000 already in use`
- **Solution**: Stop other Flask apps or change port in `coverage_tool_web.py`

### Can't see plots
- **Issue**: Plots not displaying
- **Solution**: Make sure calculations are complete before plotting
- Check browser console for JavaScript errors

### Pattern not loading
- **Issue**: CSV file not found
- **Solution**: Ensure `sample_antenna_pattern.csv` is in the same directory
- Use full path or browse to file location

### Calculations fail
- **Issue**: Invalid input values
- **Solution**: Check all fields have valid numbers
- Ensure antenna pattern is loaded first

## Files

### GUI Files:
- `coverage_tool_web.py` - Flask web server
- `templates/index.html` - Web interface HTML/CSS/JavaScript
- `run_gui.sh` - Launcher script

### Backend Files:
- `network_coverage_tool.py` - Core calculation engine
- `sample_antenna_pattern.csv` - Default antenna pattern

### Documentation:
- `GUI_README.md` - This file
- `README.md` - Original command-line documentation
- `QUICKSTART.md` - Quick start guide

## Advantages of Web GUI

✅ **No Tkinter required** - Works in any browser  
✅ **Modern interface** - Clean, professional design  
✅ **Easy to use** - Intuitive tabbed layout  
✅ **Responsive** - Works on different screen sizes  
✅ **Portable** - Can run on remote servers  
✅ **Cross-platform** - Windows, Mac, Linux  

## Command-Line Version

The original command-line tool is still available:
```bash
python3 network_coverage_tool.py
```

For automated/batch processing:
```bash
python3 example_usage.py
```

## Support

For technical details on the electromagnetic calculations, see `README.md`

For quick start instructions, see `QUICKSTART.md`

For testing, run: `python3 test_coverage_tool.py`
