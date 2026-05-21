# Using the 2D Network Coverage Tool GUI

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
cd kiro
pip install -r requirements.txt
```

### Step 2: Start the GUI
```bash
python3 coverage_tool_web.py
```

Or use the launcher:
```bash
./run_gui.sh
```

### Step 3: Open Your Browser
Navigate to: **http://localhost:5000**

## 📋 Complete Walkthrough

### The Interface

You'll see a professional tabbed interface with the header:
**"EEE3089F Project 4 - Network Coverage - VSCETH003"**

Five tabs across the top:
1. **Antenna Pattern**
2. **Input Parameters**
3. **Results**
4. **Geometry Plot**
5. **Antenna Pattern Plot**

### Tab 1: Antenna Pattern

**What it does**: Loads the antenna gain pattern from a CSV file

**How to use**:
1. The default pattern (`sample_antenna_pattern.csv`) loads automatically
2. To use a different file:
   - Type the filename in the text box
   - Click "Load Pattern"
3. View status showing:
   - Number of data points
   - Elevation angle range (0-180°)
   - Gain range (dBi)

**Status message** when loaded:
```
✓ Antenna pattern loaded successfully!

File: sample_antenna_pattern.csv
Data points: 37
Elevation range: 0.0° to 180.0°
Gain range: -13.00 to 11.20 dBi

You can now:
  • View pattern in 'Antenna Pattern Plot' tab
  • Enter parameters in 'Input Parameters' tab
  • Calculate fields
```

### Tab 2: Input Parameters

**What it does**: Collects all parameters for the electromagnetic field calculation

**Sections**:

**1. Transmit Signal Parameters**
- **Horizontal Polarization Power (dBm)**: Default 40.0
  - Example: WiFi = 20, Cellular = 43
- **Vertical Polarization Power (dBm)**: Default 40.0
- **Phase Shift (H-V) [degrees]**: Default 0.0
  - 0° = Linear polarization
  - 90° = Circular polarization
- **Frequency (MHz)**: Default 2400
  - WiFi 2.4GHz = 2400
  - WiFi 5GHz = 5800
  - GSM = 900
  - LTE = 1800

**2. Antenna Position**
- **X-coordinate (m)**: Default 0.0 (usually keep at 0)
- **Y-coordinate (m)**: Default 20.0 (height above ground)
  - Indoor: 3m
  - Base station: 25-30m

**3. Ground Medium Properties**
- **Relative Permittivity (εᵣ)**: Default 15.0
  - Dry soil: 3-5
  - Moist soil: 10-20
  - Concrete: 4-8
  - Water: 80
- **Conductivity (S/m)**: Default 0.01
  - Dry soil: 0.001-0.01
  - Moist soil: 0.01-0.1
  - Concrete: 0.01-0.02
  - Seawater: 4.0
- **Ground Slope (m)**: Default 0.0 (flat ground)
  - For sloped terrain, enter slope value (e.g., 0.1 = 10%)
- **Ground Intercept (c)**: Default 0.0
  - For y = mx + c equation

**4. Receiver Position**
- **X-coordinate (m)**: Default 100.0 (horizontal distance)
  - Range: 0-200m
- **Y-coordinate (m)**: Default 5.0 (height above ground)
  - Handheld device: 1.5m
  - Mounted antenna: higher

**Big Blue Button**: ⚡ **Calculate Fields**
- Click this to run the calculation
- Results will appear in the Results tab automatically

### Tab 3: Results

**What it shows**: Calculated electromagnetic field values

**Left Column - Electric Field Results**:
```
==============================================================
ELECTRIC FIELD RESULTS
==============================================================

Transmitter Position: (0.00, 20.00) m
Receiver Position: (100.00, 5.00) m
Frequency: 2.400 GHz

--------------------------------------------------------------
E-Field Components:
--------------------------------------------------------------
H-polarization:
  Magnitude: 1.467646e-01 V/m
  Phase: -81.00°
  dBV/m: -16.67 dB

V-polarization:
  Magnitude: 9.254303e-02 V/m
  Phase: 115.23°
  dBV/m: -20.67 dB

--------------------------------------------------------------
Total E-Field:
--------------------------------------------------------------
Magnitude: 1.735052e-01 V/m
dBV/m: -15.21 dB
```

**Right Column - Magnetic Field & Reflection Point**:
```
==============================================================
MAGNETIC FIELD RESULTS
==============================================================

H-Field Magnitude: 4.605559e-04 A/m
H-Field (dBA/m): -66.74 dB

==============================================================
REFLECTION POINT
==============================================================

Coordinates: (80.000, 0.000) m

==============================================================
GROUND PROPERTIES
==============================================================

Relative Permittivity: 15.00
Conductivity: 0.0100 S/m
Ground: Flat (y = 0.0)
```

### Tab 4: Geometry Plot

**What it shows**: Visual representation of the ray-tracing geometry

**How to use**:
1. Click "📊 Plot Geometry" button
2. Wait a moment for the plot to generate
3. The plot displays:
   - **Red triangle** (^) = Transmitter position
   - **Blue square** (□) = Receiver position
   - **Green circle** (○) = Reflection point on ground
   - **Blue solid line** = Direct propagation path
   - **Green dashed lines** = Reflected propagation path
   - **Brown shaded area** = Ground surface
   - **Black dashed rectangle** = Coverage area boundary (200m × 50m)

**Labels show coordinates** for each point

**The plot is interactive**: You can zoom and pan using the toolbar

### Tab 5: Antenna Pattern Plot

**What it shows**: Visualization of the loaded antenna gain pattern

**How to use**:
1. Click "📊 Plot Antenna Pattern" button
2. Two plots appear side-by-side:

**Left plot (Cartesian)**:
- X-axis: Elevation angle (0-180 degrees)
- Y-axis: Gain (dBi)
- Shows how gain varies with angle

**Right plot (Polar)**:
- Circular plot showing directional pattern
- 0° points upward (+y direction)
- 90° points right (+x direction)
- Radial distance = gain (linear scale)

## 💡 Example Usage Scenarios

### Scenario 1: WiFi Access Point Coverage

**Goal**: Analyze WiFi coverage at 50m distance

1. **Antenna Pattern tab**: Pattern loads automatically ✓
2. **Input Parameters tab**:
   - Power: 20 dBm (both H & V)
   - Frequency: 2400 MHz
   - Antenna height: 3m
   - εᵣ: 5, σ: 0.02 (indoor concrete)
   - Receiver: (50, 1.5)
   - Click **Calculate Fields**
3. **Results tab**: View E-field strength
4. **Geometry Plot tab**: Visualize propagation paths

**Expected result**: E-field around 10⁻⁴ to 10⁻³ V/m at 50m

### Scenario 2: Cellular Base Station

**Goal**: Calculate field strength 150m from base station

1. **Input Parameters tab**:
   - Power: 43 dBm
   - Frequency: 900 MHz
   - Antenna height: 25m
   - εᵣ: 15, σ: 0.01 (outdoor soil)
   - Receiver: (150, 1.5)
   - Click **Calculate Fields**
2. **Results tab**: Check coverage level
3. **Geometry Plot tab**: See reflection point location

**Expected result**: Strong signal, E-field > 10⁻² V/m

### Scenario 3: Sloped Terrain

**Goal**: Model propagation over hillside

1. **Input Parameters tab**:
   - Use any transmit power/frequency
   - Antenna height: 15m
   - Ground slope: 0.1 (10% upward)
   - Ground intercept: 0
   - Receiver: (120, calculated height)
   - Click **Calculate Fields**
2. **Geometry Plot tab**: See how reflection occurs on slope

**Observation**: Reflection point will be on the sloped surface

## 🎓 Understanding the Results

### E-Field Values

**Typical ranges for communication systems**:
- Strong signal: > 1 V/m
- Good signal: 0.1 - 1 V/m
- Weak signal: 0.01 - 0.1 V/m
- Very weak: < 0.01 V/m

**In dBV/m**:
- 0 dBV/m = 1 V/m
- -20 dBV/m = 0.1 V/m
- -40 dBV/m = 0.01 V/m

### Reflection Point

**What it means**: Where the reflected signal bounces off the ground

**Observations**:
- For flat ground: Between transmitter and receiver
- Higher antenna → reflection point closer to receiver
- Shows where ground properties matter most

### H-pol vs V-pol

**Difference**:
- H-polarization: Horizontal electric field
- V-polarization: Vertical electric field

**Reflection**:
- V-pol typically reflects more strongly
- Different reflection coefficients (Fresnel)

## 🔧 Tips & Tricks

### Getting Realistic Results

1. **Match frequency to antenna**: Use appropriate antenna pattern for your frequency
2. **Realistic powers**: WiFi = 20dBm, Cellular = 40-50dBm
3. **Appropriate ground**: Indoor (low εᵣ), Outdoor (higher εᵣ)
4. **Receiver height**: Handheld ~1.5m, Mounted higher

### Common Issues

**"Please load antenna pattern first"**
- Solution: Go to Antenna Pattern tab and load CSV

**Very small E-field values**
- Normal! Distances and power levels matter
- Check frequency and power are realistic

**Reflection point seems wrong**
- Check ground slope settings
- Verify antenna and receiver positions

### Experimenting

**Try varying**:
1. **Distance**: Move receiver closer/farther
2. **Height**: Change antenna or receiver height
3. **Frequency**: See how wavelength affects results
4. **Ground**: Dry soil vs moist soil vs concrete
5. **Slope**: Flat vs 5% vs 10% incline

**Compare**:
- Direct vs total field (see reflection effect)
- H-pol vs V-pol (polarization effects)
- Different frequencies (path loss)

## 🖥️ Browser Tips

- **Zoom plots**: Use browser zoom (Ctrl/Cmd +/-)
- **Copy results**: Select text in Results tab and copy
- **Multiple tabs**: Open multiple browser tabs for comparison
- **Refresh**: F5 to restart with default values

## ⚙️ Advanced Features

### Custom Antenna Patterns

Create your own CSV file:
```csv
elevation_angle,gain_dbi
0,8.5
10,9.2
20,10.5
...
180,-10.0
```

Load it in the Antenna Pattern tab

### API Usage

The server also has a REST API:
- `POST /api/load_pattern` - Load antenna pattern
- `POST /api/calculate` - Calculate fields
- `POST /api/plot_geometry` - Get geometry plot
- `GET /api/plot_antenna` - Get antenna plot

Can be used for automation/scripting

## 🛑 Stopping the Server

In the terminal where the server is running:
Press **Ctrl + C**

## 📚 More Information

- **Technical details**: See `README.md`
- **GUI documentation**: See `GUI_README.md`
- **Quick start**: See `QUICKSTART.md`
- **Testing**: Run `python3 test_coverage_tool.py`

---

**Enjoy using the 2D Network Coverage Tool!** 🎉
