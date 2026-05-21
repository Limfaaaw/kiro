#!/usr/bin/env python3
"""
Test script for the 2D Network Coverage Tool
Runs automated tests with predefined inputs
"""

import sys
import numpy as np
from network_coverage_tool import (
    NetworkCoverageTool,
    TransmitParameters,
    GroundParameters,
    AntennaPattern
)


def test_antenna_pattern_reading():
    """Test reading antenna pattern from CSV."""
    print("\n" + "="*60)
    print("TEST 1: Reading Antenna Pattern")
    print("="*60)
    
    try:
        pattern = NetworkCoverageTool.read_antenna_pattern('sample_antenna_pattern.csv')
        print(f"✓ Pattern loaded successfully")
        print(f"  - Data points: {len(pattern.elevation_angles)}")
        print(f"  - Elevation range: {pattern.elevation_angles[0]}° to {pattern.elevation_angles[-1]}°")
        print(f"  - Gain range: {pattern.gain_dbi.min():.2f} to {pattern.gain_dbi.max():.2f} dBi")
        
        # Test interpolation
        test_angle = 42.5
        gain = pattern.get_gain(test_angle)
        print(f"  - Gain at {test_angle}°: {gain:.2f} dBi (interpolated)")
        
        return pattern
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return None


def test_flat_ground_scenario(tool):
    """Test scenario with flat ground."""
    print("\n" + "="*60)
    print("TEST 2: Flat Ground Scenario")
    print("="*60)
    
    # Define parameters
    tx_params = TransmitParameters(
        power_h_dbm=40.0,      # 40 dBm horizontal
        power_v_dbm=40.0,      # 40 dBm vertical
        phase_shift_deg=0.0,   # No phase shift
        frequency_hz=2.4e9,    # 2.4 GHz (WiFi)
        antenna_x=0.0,         # At origin
        antenna_y=20.0         # 20 meters high
    )
    
    ground_params = GroundParameters(
        epsilon_r=15.0,        # Typical soil
        sigma=0.01,            # Typical soil conductivity
        slope_m=0.0,           # Flat ground
        intercept_c=0.0        # Ground at y=0
    )
    
    rx_pos = (100.0, 5.0)      # Receiver at 100m horizontal, 5m high
    
    print(f"\nTransmitter: ({tx_params.antenna_x}, {tx_params.antenna_y}) m")
    print(f"Receiver: {rx_pos} m")
    print(f"Frequency: {tx_params.frequency_hz/1e9:.1f} GHz")
    print(f"Power (H/V): {tx_params.power_h_dbm}/{tx_params.power_v_dbm} dBm")
    print(f"Ground: epsilon_r={ground_params.epsilon_r}, sigma={ground_params.sigma} S/m")
    
    try:
        result = tool.calculate_fields(tx_params, rx_pos, ground_params)
        
        print(f"\n--- Results ---")
        print(f"E-field (H-pol): {abs(result.e_field_h):.6e} V/m")
        print(f"E-field (V-pol): {abs(result.e_field_v):.6e} V/m")
        print(f"Total E-field: {result.total_e_magnitude:.6e} V/m ({20*np.log10(result.total_e_magnitude):.2f} dBV/m)")
        print(f"H-field: {result.h_field:.6e} A/m")
        print(f"Reflection point: ({result.reflection_point[0]:.2f}, {result.reflection_point[1]:.2f}) m")
        
        print("\n✓ Test passed")
        return result, tx_params, rx_pos, ground_params
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_sloped_ground_scenario(tool):
    """Test scenario with sloped ground."""
    print("\n" + "="*60)
    print("TEST 3: Sloped Ground Scenario")
    print("="*60)
    
    # Define parameters
    tx_params = TransmitParameters(
        power_h_dbm=43.0,      # 43 dBm horizontal
        power_v_dbm=43.0,      # 43 dBm vertical
        phase_shift_deg=90.0,  # 90° phase shift (circular polarization)
        frequency_hz=900e6,    # 900 MHz (GSM)
        antenna_x=0.0,
        antenna_y=25.0         # 25 meters high
    )
    
    ground_params = GroundParameters(
        epsilon_r=12.0,        # Dry soil
        sigma=0.005,
        slope_m=0.1,           # 10% slope upward
        intercept_c=0.0
    )
    
    rx_pos = (150.0, 10.0)
    
    print(f"\nTransmitter: ({tx_params.antenna_x}, {tx_params.antenna_y}) m")
    print(f"Receiver: {rx_pos} m")
    print(f"Frequency: {tx_params.frequency_hz/1e6:.0f} MHz")
    print(f"Power (H/V): {tx_params.power_h_dbm}/{tx_params.power_v_dbm} dBm")
    print(f"Phase shift: {tx_params.phase_shift_deg}°")
    print(f"Ground: slope={ground_params.slope_m} (y = {ground_params.slope_m}x + {ground_params.intercept_c})")
    
    try:
        result = tool.calculate_fields(tx_params, rx_pos, ground_params)
        
        print(f"\n--- Results ---")
        print(f"E-field (H-pol): {abs(result.e_field_h):.6e} V/m ∠{np.angle(result.e_field_h, deg=True):.1f}°")
        print(f"E-field (V-pol): {abs(result.e_field_v):.6e} V/m ∠{np.angle(result.e_field_v, deg=True):.1f}°")
        print(f"Total E-field: {result.total_e_magnitude:.6e} V/m ({20*np.log10(result.total_e_magnitude):.2f} dBV/m)")
        print(f"H-field: {result.h_field:.6e} A/m")
        print(f"Reflection point: ({result.reflection_point[0]:.2f}, {result.reflection_point[1]:.2f}) m")
        
        print("\n✓ Test passed")
        return result, tx_params, rx_pos, ground_params
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_multiple_receiver_positions(tool):
    """Test calculating fields at multiple receiver positions."""
    print("\n" + "="*60)
    print("TEST 4: Multiple Receiver Positions")
    print("="*60)
    
    tx_params = TransmitParameters(
        power_h_dbm=40.0,
        power_v_dbm=40.0,
        phase_shift_deg=0.0,
        frequency_hz=1.8e9,    # 1.8 GHz
        antenna_x=0.0,
        antenna_y=30.0
    )
    
    ground_params = GroundParameters(
        epsilon_r=10.0,
        sigma=0.01,
        slope_m=0.0,
        intercept_c=0.0
    )
    
    # Test at multiple positions
    test_positions = [
        (50.0, 2.0),
        (100.0, 5.0),
        (150.0, 10.0),
        (180.0, 15.0)
    ]
    
    print(f"\nCalculating fields at {len(test_positions)} positions...")
    print(f"Transmitter at ({tx_params.antenna_x}, {tx_params.antenna_y}) m")
    
    try:
        results = []
        for i, rx_pos in enumerate(test_positions, 1):
            result = tool.calculate_fields(tx_params, rx_pos, ground_params)
            results.append(result)
            print(f"\n  Position {i}: ({rx_pos[0]}, {rx_pos[1]}) m")
            print(f"    E-field: {result.total_e_magnitude:.4e} V/m ({20*np.log10(result.total_e_magnitude):.2f} dBV/m)")
            print(f"    Reflection: ({result.reflection_point[0]:.1f}, {result.reflection_point[1]:.1f}) m")
        
        print("\n✓ Test passed")
        return results
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("2D NETWORK COVERAGE TOOL - AUTOMATED TESTS")
    print("="*60)
    
    # Test 1: Read antenna pattern
    pattern = test_antenna_pattern_reading()
    if pattern is None:
        print("\n✗ Cannot continue without antenna pattern")
        return 1
    
    # Create tool instance
    tool = NetworkCoverageTool(pattern)
    
    # Test 2: Flat ground scenario
    flat_result = test_flat_ground_scenario(tool)
    if flat_result is None:
        print("\n⚠ Flat ground test failed")
        return 1
    
    # Test 3: Sloped ground scenario
    sloped_result = test_sloped_ground_scenario(tool)
    if sloped_result is None:
        print("\n⚠ Sloped ground test failed")
        return 1
    
    # Test 4: Multiple positions
    multi_results = test_multiple_receiver_positions(tool)
    if multi_results is None:
        print("\n⚠ Multiple positions test failed")
        return 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✓ All tests passed successfully!")
    print("\nThe tool is ready for use. Run:")
    print("  python network_coverage_tool.py")
    print("\nTo use the interactive interface with custom inputs.")
    print("="*60 + "\n")
    
    # Optional: Create visualization for one scenario
    print("Generating visualization for flat ground scenario...")
    result, tx_params, rx_pos, ground_params = flat_result
    try:
        tool.plot_geometry(tx_params, rx_pos, result, ground_params)
    except Exception as e:
        print(f"Note: Visualization skipped (requires display): {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
