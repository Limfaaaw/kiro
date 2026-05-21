# 2D Network Coverage Tool

A Python application for calculating electric and magnetic fields in a 2D environment using ray-tracing with ground reflections. This tool is designed for network coverage analysis and electromagnetic field propagation modeling.

## Features

### Basic Features ✓
- **Antenna Gain Pattern Import**: Read antenna gain patterns from CSV files with elevation angles (0° - 180°) and corresponding gain values in dBi
- **User Input Collection**: Interactive interface for specifying:
  - Transmit signal power (Horizontal and Vertical polarization) in dBm
  - Phase shift between H and V polarization (V-pol as reference at 0°)
  - Transmit signal frequency in MHz
  - Antenna position (x, y coordinates)
  - Ground medium dielectric properties (permittivity and conductivity)
  - Receiver coordinates
- **Electromagnetic Field Calculations**: Compute electric and magnetic fields at receiver location using:
  - Direct path propagation
  - Ground-reflected path with Fresnel reflection coefficients
  - Complex permittivity accounting for conductivity
  - Antenna gain pattern interpolation
- **Geometry Visualization**: Display geometry including:
  - Antenna position
  - Receiver position
  - Direct propagation path
  - Reflected propagation path
  - Reflection point coordinates
  - Coverage area boundary (200m × 50m)

### Additional Features ✓
- **Sloped Ground Support**: Handle non-flat ground surfaces with equation y = mx + c
- **Dual Polarization**: Full support for horizontal and vertical polarization with phase relationships
- **Antenna Pattern Display**: Visualize gain patterns in both Cartesian and polar plots

## Installation

### Requirements
- Python 3.9 or higher
- Required packages:
  ```bash
  pip install numpy matplotlib scipy
  ```

### Files
- `network_coverage_tool.py` - Main application
- `sample_antenna_pattern.csv` - Example antenna gain pattern
- `test_coverage_tool.py` - Automated test suite

## Usage

### Interactive Mode

Run the main application:
```bash
python3 network_coverage_tool.py
```

Follow the prompts to:
1. Specify the antenna gain pattern CSV file
2. View the antenna pattern (optional)
3. Enter transmit parameters
4. Enter ground properties
5. Specify receiver coordinates
6. View calculated results and geometry

### Example Session
```
Enter antenna gain pattern CSV file path: sample_antenna_pattern.csv
✓ Antenna pattern loaded: 37 data points

Display antenna pattern? (y/n) [default=y]: y

--- Transmit Signal Parameters ---
Horizontal polarization power (dBm): 40
Vertical polarization power (dBm): 40
Phase shift between H and V (degrees, V-pol is reference): 0
Frequency (MHz): 2400

--- Antenna Position ---
Antenna X coordinate (m) [default=0]: 0
Antenna Y coordinate (m): 20

--- Ground Medium Properties ---
Relative permittivity (epsilon_r): 15
Conductivity (S/m): 0.01

Use sloped ground surface? (y/n) [default=n]: n

--- Receiver Position ---
Receiver X coordinate (m): 100
Receiver Y coordinate (m): 5

⏳ Calculating electromagnetic fields...

--- Electric Field ---
E-field (H-pol): 1.467646e-01 V/m ∠ -81.00°
E-field (V-pol): 9.254303e-02 V/m ∠ 115.23°
Total E-field magnitude: 1.735052e-01 V/m
Total E-field (dBV/m): -15.21 dB

--- Magnetic Field ---
H-field magnitude: 4.605559e-04 A/m
H-field (dBA/m): -66.74 dB

--- Reflection Point ---
Coordinates: (80.000 m, 0.000 m)

Display geometry plot? (y/n) [default=y]: y
```

### Automated Testing

Run the test suite:
```bash
python3 test_coverage_tool.py
```

This runs comprehensive tests including:
- Antenna pattern reading
- Flat ground scenario
- Sloped ground scenario
- Multiple receiver positions

## CSV File Format

The antenna gain pattern CSV file should have two columns:
```csv
elevation_angle,gain_dbi
0,8.5
5,8.7
10,9.2
...
180,-10.0
```

- **elevation_angle**: Angle in degrees from 0° to 180°
  - 0° points in the positive y direction (upward)
  - 90° points in the positive x direction (horizontal right)
  - 180° points in the negative y direction (downward)
- **gain_dbi**: Antenna gain in dBi

## Technical Details

### Coordinate System
- **Origin**: Bottom left corner of coverage area
- **X-axis**: Horizontal, pointing right (200m range)
- **Y-axis**: Vertical, pointing upward (50m range)
- **Antenna**: Point source at x = 0 (default), user-specified y coordinate

### Simplifications
This tool implements a simplified 2D model with the following assumptions:
- Antenna treated as point source with specified gain pattern
- Near-field/far-field considerations ignored
- Ray-tracing for reflections (treat reflection as point source)
- Coverage area restricted to 200m × 50m rectangle
- Gain pattern as function of elevation angle only

### Physics Implementation

#### Free-Space Propagation
Electric field magnitude at distance d:
```
E = sqrt(30 * P * G) / d * exp(-j * k * d)
```
where:
- P = transmit power (W)
- G = antenna gain (linear)
- k = wave number (2π/λ)
- d = distance (m)

#### Fresnel Reflection Coefficients
For horizontal polarization (perpendicular):
```
Γ_h = (cos θ_i - sqrt(ε_c) * cos θ_t) / (cos θ_i + sqrt(ε_c) * cos θ_t)
```

For vertical polarization (parallel):
```
Γ_v = (ε_c * cos θ_i - cos θ_t) / (ε_c * cos θ_i + cos θ_t)
```

where:
- ε_c = ε_r - j(σ/ωε_0) = complex relative permittivity
- θ_i = incident angle from normal
- θ_t = transmitted angle (complex)

#### Reflection Point Calculation
- **Flat ground**: Image theory with analytical solution
- **Sloped ground**: Fermat's principle using numerical optimization to minimize total path length

#### Total Field
Superposition of direct and reflected paths:
```
E_total = E_direct + Γ * E_reflected
```

### Constants
- Speed of light: c = 299,792,458 m/s
- Permeability of free space: μ₀ = 4π × 10⁻⁷ H/m
- Permittivity of free space: ε₀ = 8.854 × 10⁻¹² F/m
- Intrinsic impedance of free space: η₀ = 376.73 Ω

## Example Use Cases

### 1. WiFi Coverage Analysis
```
Power: 20 dBm (both polarizations)
Frequency: 2400 MHz
Antenna height: 3m
Ground: ε_r = 15, σ = 0.01 S/m (typical soil)
```

### 2. Cellular Base Station
```
Power: 43 dBm (both polarizations)
Frequency: 900 MHz (GSM) or 1800 MHz (LTE)
Antenna height: 25-30m
Ground: ε_r = 10-15, σ = 0.005-0.02 S/m
```

### 3. Point-to-Point Link
```
Power: 30-40 dBm
Frequency: 5800 MHz
Antenna heights: Variable
Flat or sloped terrain
```

## Output

The tool provides:
1. **Field Values**:
   - E-field for H and V polarization (magnitude and phase)
   - Total E-field magnitude (V/m and dBV/m)
   - H-field magnitude (A/m and dBA/m)

2. **Geometry Information**:
   - Reflection point coordinates
   - Visual representation of propagation paths

3. **Plots**:
   - Antenna gain pattern (Cartesian and polar)
   - 2D geometry with paths and positions

## Limitations

- 2D model only (no azimuthal variation)
- Single ground reflection (no multiple bounces)
- Homogeneous ground properties
- No diffraction or scattering
- No atmospheric effects
- Point source antenna (no physical dimensions)
- Coverage area limited to 200m × 50m

## Development and Testing

The tool includes comprehensive unit tests in `test_coverage_tool.py`:

```bash
# Run all tests
python3 test_coverage_tool.py

# Expected output: All tests passed
```

Tests cover:
- CSV file reading
- Flat ground calculations
- Sloped ground calculations
- Multiple receiver positions
- Edge cases

## Author

Developed for network coverage analysis and electromagnetic field calculations in educational and professional contexts.

## License

This tool is provided for educational and professional use.
