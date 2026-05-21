#!/usr/bin/env python3
"""
Example usage of the 2D Network Coverage Tool
Demonstrates programmatic usage without interactive input
"""

from network_coverage_tool import (
    NetworkCoverageTool,
    TransmitParameters,
    GroundParameters
)
import numpy as np


def example_wifi_coverage():
    """Example: WiFi access point coverage analysis."""
    print("\n" + "="*60)
    print("EXAMPLE: WiFi Access Point Coverage")
    print("="*60)
    
    # Load antenna pattern
    antenna_pattern = NetworkCoverageTool.read_antenna_pattern('sample_antenna_pattern.csv')
    tool = NetworkCoverageTool(antenna_pattern)
    
    # Configure WiFi transmitter
    tx_params = TransmitParameters(
        power_h_dbm=20.0,       # 100 mW = 20 dBm
        power_v_dbm=20.0,
        phase_shift_deg=0.0,
        frequency_hz=2.4e9,     # 2.4 GHz
        antenna_x=0.0,
        antenna_y=3.0           # 3 meters high (ceiling mount)
    )
    
    # Ground properties (indoor floor)
    ground = GroundParameters(
        epsilon_r=5.0,          # Concrete/tile
        sigma=0.02,
        slope_m=0.0,
        intercept_c=0.0
    )
    
    # Calculate coverage at various distances
    print("\nCoverage Analysis:")
    print(f"{'Distance (m)':<15} {'Height (m)':<15} {'E-field (dBV/m)':<20} {'E-field (V/m)':<20}")
    print("-" * 70)
    
    distances = [10, 25, 50, 75, 100]
    for dist in distances:
        rx_pos = (dist, 1.5)  # 1.5m height (device on table)
        result = tool.calculate_fields(tx_params, rx_pos, ground)
        
        e_dbv = 20 * np.log10(result.total_e_magnitude)
        print(f"{dist:<15} {rx_pos[1]:<15} {e_dbv:<20.2f} {result.total_e_magnitude:<20.6e}")
    
    # Visualize geometry for 50m distance
    print("\nGenerating visualization for 50m distance...")
    rx_pos = (50, 1.5)
    result = tool.calculate_fields(tx_params, rx_pos, ground)
    tool.plot_geometry(tx_params, rx_pos, result, ground)


def example_cellular_base_station():
    """Example: Cellular base station coverage."""
    print("\n" + "="*60)
    print("EXAMPLE: Cellular Base Station (900 MHz)")
    print("="*60)
    
    # Load antenna pattern
    antenna_pattern = NetworkCoverageTool.read_antenna_pattern('sample_antenna_pattern.csv')
    tool = NetworkCoverageTool(antenna_pattern)
    
    # Configure base station
    tx_params = TransmitParameters(
        power_h_dbm=43.0,       # 20 W = 43 dBm
        power_v_dbm=43.0,
        phase_shift_deg=90.0,   # Circular polarization
        frequency_hz=900e6,     # 900 MHz (GSM)
        antenna_x=0.0,
        antenna_y=25.0          # 25 meters high (tower)
    )
    
    # Ground properties (rural/soil)
    ground = GroundParameters(
        epsilon_r=15.0,         # Moist soil
        sigma=0.01,
        slope_m=0.0,
        intercept_c=0.0
    )
    
    # Mobile device position
    rx_pos = (150.0, 1.5)       # 150m away, 1.5m high (handheld device)
    
    # Calculate fields
    result = tool.calculate_fields(tx_params, rx_pos, ground)
    
    print(f"\nTransmitter: Base station at ({tx_params.antenna_x}, {tx_params.antenna_y}) m")
    print(f"Receiver: Mobile device at {rx_pos} m")
    print(f"Frequency: {tx_params.frequency_hz/1e6:.0f} MHz")
    print(f"Power: {tx_params.power_h_dbm} dBm ({10**((tx_params.power_h_dbm-30)/10):.1f} W)")
    
    print(f"\nResults:")
    print(f"  Total E-field: {result.total_e_magnitude:.4e} V/m ({20*np.log10(result.total_e_magnitude):.2f} dBV/m)")
    print(f"  H-field: {result.h_field:.4e} A/m")
    print(f"  Reflection point: ({result.reflection_point[0]:.1f}, {result.reflection_point[1]:.1f}) m")
    
    # Visualize
    print("\nGenerating visualization...")
    tool.plot_geometry(tx_params, rx_pos, result, ground)


def example_sloped_terrain():
    """Example: Communication over sloped terrain."""
    print("\n" + "="*60)
    print("EXAMPLE: Communication over Sloped Terrain")
    print("="*60)
    
    # Load antenna pattern
    antenna_pattern = NetworkCoverageTool.read_antenna_pattern('sample_antenna_pattern.csv')
    tool = NetworkCoverageTool(antenna_pattern)
    
    # Configure transmitter
    tx_params = TransmitParameters(
        power_h_dbm=30.0,
        power_v_dbm=30.0,
        phase_shift_deg=0.0,
        frequency_hz=5.8e9,     # 5.8 GHz
        antenna_x=0.0,
        antenna_y=15.0          # 15 meters high
    )
    
    # Sloped ground (10% grade upward)
    ground = GroundParameters(
        epsilon_r=12.0,
        sigma=0.005,
        slope_m=0.1,            # 10% slope
        intercept_c=0.0
    )
    
    # Receiver on slope
    rx_x = 120.0
    rx_y = ground.slope_m * rx_x + ground.intercept_c + 2.0  # 2m above ground
    rx_pos = (rx_x, rx_y)
    
    # Calculate fields
    result = tool.calculate_fields(tx_params, rx_pos, ground)
    
    print(f"\nGround slope: {ground.slope_m} (y = {ground.slope_m}x + {ground.intercept_c})")
    print(f"Transmitter: ({tx_params.antenna_x}, {tx_params.antenna_y}) m")
    print(f"Receiver: ({rx_pos[0]:.1f}, {rx_pos[1]:.1f}) m")
    
    print(f"\nResults:")
    print(f"  E-field (H-pol): {abs(result.e_field_h):.4e} V/m ∠{np.angle(result.e_field_h, deg=True):.1f}°")
    print(f"  E-field (V-pol): {abs(result.e_field_v):.4e} V/m ∠{np.angle(result.e_field_v, deg=True):.1f}°")
    print(f"  Total E-field: {result.total_e_magnitude:.4e} V/m")
    print(f"  Reflection point: ({result.reflection_point[0]:.1f}, {result.reflection_point[1]:.1f}) m")
    
    # Visualize
    print("\nGenerating visualization...")
    tool.plot_geometry(tx_params, rx_pos, result, ground)


def main():
    """Run example scenarios."""
    print("\n" + "="*60)
    print("2D NETWORK COVERAGE TOOL - EXAMPLE USAGE")
    print("="*60)
    print("\nThis script demonstrates programmatic usage of the tool")
    print("with three realistic scenarios:")
    print("  1. WiFi Access Point")
    print("  2. Cellular Base Station")
    print("  3. Communication over Sloped Terrain")
    print("="*60)
    
    try:
        # Run examples
        example_wifi_coverage()
        
        print("\n" + "="*60)
        input("Press Enter to continue to next example...")
        
        example_cellular_base_station()
        
        print("\n" + "="*60)
        input("Press Enter to continue to next example...")
        
        example_sloped_terrain()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except FileNotFoundError:
        print("\n✗ Error: sample_antenna_pattern.csv not found!")
        print("Make sure the file is in the same directory as this script.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
