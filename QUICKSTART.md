# Quick Start Guide - 2D Network Coverage Tool

## Installation (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install numpy matplotlib scipy
```

### 2. Verify Installation
```bash
python3 test_coverage_tool.py
```

Expected output: "✓ All tests passed successfully!"

## Usage Options

### Option 1: Interactive Mode (Recommended for First-Time Users)

```bash
python3 network_coverage_tool.py
```

Follow the prompts to enter your parameters. Example inputs for a WiFi scenario:

```
Enter antenna gain pattern CSV file path: sample_antenna_pattern.csv
Display antenna pattern? (y/n): y

Horizontal polarization power (dBm): 20
Vertical polarization power (dBm): 20
Phase shift between H and V (degrees): 0
Frequency (MHz): 2400

Antenna X coordinate (m): 0
Antenna Y coordinate (m): 3

Relative permittivity (epsilon_r): 5
Conductivity (S/m): 0.02

Use sloped ground surface? (y/n): n

Receiver X coordinate (m): 50
Receiver Y coordinate (m): 1.5
```

### Option 2: Programmatic Usage (For Automation)

```bash
python3 example_usage.py
```

This runs three pre-configured scenarios:
- WiFi coverage analysis
- Cellular base station
- Sloped terrain communication

### Option 3: Python Script/Module

```python
from network_coverage_tool import NetworkCoverageTool, TransmitParameters, GroundParameters

# Load antenna pattern
pattern = NetworkCoverageTool.read_antenna_pattern('sample_antenna_pattern.csv')
tool = NetworkCoverageTool(pattern)

# Configure transmitter
tx_params = TransmitParameters(
    power_h_dbm=40.0,
    power_v_dbm=40.0,
    phase_shift_deg=0.0,
    frequency_hz=2.4e9,
    antenna_x=0.0,
    antenna_y=20.0
)

# Configure ground
ground = GroundParameters(
    epsilon_r=15.0,
    sigma=0.01,
    slope_m=0.0,
    intercept_c=0.0
)

# Calculate fields at receiver position
rx_pos = (100.0, 5.0)
result = tool.calculate_fields(tx_params, rx_pos, ground)

# Display results
print(f"E-field: {result.total_e_magnitude:.4e} V/m")
print(f"Reflection point: {result.reflection_point}")

# Visualize geometry
tool.plot_geometry(tx_params, rx_pos, result, ground)
```

## Common Scenarios

### WiFi (2.4 GHz)
- **Power**: 20 dBm
- **Frequency**: 2400 MHz
- **Antenna height**: 3m
- **Ground**: ε_r = 5, σ = 0.02 S/m

### Cellular (900 MHz)
- **Power**: 43 dBm
- **Frequency**: 900 MHz
- **Antenna height**: 25m
- **Ground**: ε_r = 15, σ = 0.01 S/m

### 5G (3.5 GHz)
- **Power**: 46 dBm
- **Frequency**: 3500 MHz
- **Antenna height**: 30m
- **Ground**: ε_r = 10, σ = 0.005 S/m

## Typical Ground Properties

| Material | Permittivity (ε_r) | Conductivity (σ S/m) |
|----------|-------------------|---------------------|
| Dry soil | 3-5 | 0.001-0.01 |
| Moist soil | 10-20 | 0.01-0.1 |
| Concrete | 4-8 | 0.01-0.02 |
| Seawater | 80 | 4.0 |
| Fresh water | 80 | 0.01 |
| Urban ground | 5-15 | 0.01-0.05 |

## Understanding the Output

### Electric Field Values
- **E-field (H-pol)**: Horizontal polarization component (V/m)
- **E-field (V-pol)**: Vertical polarization component (V/m)
- **Total E-field**: Combined magnitude (V/m or dBV/m)
  - Typical values: 0.001 - 1 V/m for communication systems

### Magnetic Field
- **H-field**: Related to E-field by free-space impedance (377Ω)
- H = E / 377 (A/m)

### Reflection Point
- Location where signal reflects off ground
- Used to visualize propagation paths

## Interpreting Plots

### Antenna Pattern Plot
- **Left (Cartesian)**: Shows gain vs elevation angle
- **Right (Polar)**: Shows directional radiation pattern
- Peak gain typically at 30-40° elevation

### Geometry Plot
- **Red triangle**: Transmitter location
- **Blue square**: Receiver location
- **Green circle**: Reflection point
- **Blue line**: Direct path
- **Green dashed lines**: Reflected path
- **Brown area**: Ground surface

## Troubleshooting

### "FileNotFoundError"
- Ensure `sample_antenna_pattern.csv` is in the same directory
- Check the file path you entered

### "ModuleNotFoundError: numpy/matplotlib/scipy"
- Run: `pip install -r requirements.txt`

### Plots don't display
- In headless environment: Plots are generated but may not display
- Save plots: Modify code to use `plt.savefig('filename.png')`

### Unrealistic field values
- Check that power is in dBm (not Watts)
- Verify frequency is in Hz (not MHz)
- Ensure receiver is within coverage area (0-200m horizontal, 0-50m vertical)

## Tips

1. **Start Simple**: Use flat ground (slope=0) first
2. **Validate Results**: Compare direct path with known formulas
3. **Experiment**: Try different frequencies, powers, positions
4. **Ground Properties**: Use table above for realistic values
5. **Phase Shift**: 0° for linear, 90° for circular polarization

## Next Steps

1. ✓ Run test suite: `python3 test_coverage_tool.py`
2. ✓ Try interactive mode: `python3 network_coverage_tool.py`
3. ✓ Run examples: `python3 example_usage.py`
4. → Create your own antenna pattern CSV
5. → Modify for your specific use case
6. → Extend with additional features

## Support

For detailed information, see `README.md`

For technical details on electromagnetic calculations, refer to comments in `network_coverage_tool.py`
