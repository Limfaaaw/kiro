#!/usr/bin/env python3
"""
2D Network Coverage Tool
========================
Calculate electric and magnetic fields using ray-tracing with reflections.

This tool implements a simplified 2D electromagnetic field propagation model
for network coverage analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
import csv
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class AntennaPattern:
    """Stores antenna gain pattern data."""
    elevation_angles: np.ndarray  # degrees, 0-180
    gain_dbi: np.ndarray          # gain in dBi
    
    def get_gain(self, theta_deg: float) -> float:
        """
        Get antenna gain at specified elevation angle.
        
        Args:
            theta_deg: Elevation angle in degrees (0° = +y, 90° = +x)
            
        Returns:
            Gain in dBi
        """
        # Ensure angle is in valid range
        theta_deg = theta_deg % 360
        if theta_deg > 180:
            theta_deg = 360 - theta_deg
            
        # Linear interpolation
        return np.interp(theta_deg, self.elevation_angles, self.gain_dbi)


@dataclass
class TransmitParameters:
    """Transmit signal parameters."""
    power_h_dbm: float      # Horizontal polarization power (dBm)
    power_v_dbm: float      # Vertical polarization power (dBm)
    phase_shift_deg: float  # Phase shift between H and V (degrees)
    frequency_hz: float     # Frequency (Hz)
    antenna_x: float        # Antenna x-coordinate (m)
    antenna_y: float        # Antenna y-coordinate (m)


@dataclass
class GroundParameters:
    """Ground medium parameters."""
    epsilon_r: float        # Relative permittivity
    sigma: float            # Conductivity (S/m)
    slope_m: float = 0.0    # Slope for y = mx + c
    intercept_c: float = 0.0  # Intercept for y = mx + c


@dataclass
class FieldResult:
    """Results of field calculation."""
    e_field_h: complex      # Horizontal E-field (V/m)
    e_field_v: complex      # Vertical E-field (V/m)
    h_field: complex        # Magnetic field (A/m)
    total_e_magnitude: float  # Total E-field magnitude (V/m)
    reflection_point: Tuple[float, float]  # (x, y) of reflection point


class NetworkCoverageTool:
    """Main class for network coverage calculations."""
    
    # Constants
    C = 299792458.0  # Speed of light (m/s)
    MU_0 = 4 * np.pi * 1e-7  # Permeability of free space (H/m)
    EPSILON_0 = 8.854187817e-12  # Permittivity of free space (F/m)
    ETA_0 = 376.73  # Intrinsic impedance of free space (Ohms)
    
    # Coverage area limits
    X_MAX = 200.0  # meters
    Y_MAX = 50.0   # meters
    
    def __init__(self, antenna_pattern: AntennaPattern):
        """Initialize with antenna pattern."""
        self.antenna_pattern = antenna_pattern
        
    @staticmethod
    def read_antenna_pattern(filename: str) -> AntennaPattern:
        """
        Read antenna gain pattern from CSV file.
        
        CSV format: elevation_angle,gain_dbi
        Expected range: 0° to 180°
        
        Args:
            filename: Path to CSV file
            
        Returns:
            AntennaPattern object
        """
        elevations = []
        gains = []
        
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            # Skip header if present
            header = next(reader, None)
            if header and not header[0].replace('.', '').replace('-', '').isdigit():
                pass  # Header was skipped
            else:
                # First row was data, process it
                elevations.append(float(header[0]))
                gains.append(float(header[1]))
            
            for row in reader:
                elevations.append(float(row[0]))
                gains.append(float(row[1]))
        
        return AntennaPattern(
            elevation_angles=np.array(elevations),
            gain_dbi=np.array(gains)
        )
    
    def calculate_reflection_point(
        self,
        tx_pos: Tuple[float, float],
        rx_pos: Tuple[float, float],
        ground: GroundParameters
    ) -> Tuple[float, float]:
        """
        Calculate reflection point on ground surface.
        
        For flat ground (y = 0): Use image theory
        For sloped ground (y = mx + c): Use Snell's law in 2D
        
        Args:
            tx_pos: Transmitter position (x, y)
            rx_pos: Receiver position (x, y)
            ground: Ground parameters
            
        Returns:
            Reflection point coordinates (x, y)
        """
        tx_x, tx_y = tx_pos
        rx_x, rx_y = rx_pos
        
        if ground.slope_m == 0.0:
            # Flat ground: reflection point is where image ray intersects ground
            # Image transmitter at (tx_x, -tx_y + 2*ground.intercept_c)
            img_y = -tx_y + 2 * ground.intercept_c
            
            # Find intersection of line from image to receiver with ground
            # Line equation: y - img_y = m_line * (x - tx_x)
            if rx_x != tx_x:
                m_line = (rx_y - img_y) / (rx_x - tx_x)
                # Solve: ground.intercept_c = img_y + m_line * (x - tx_x)
                refl_x = tx_x + (ground.intercept_c - img_y) / m_line
            else:
                refl_x = tx_x
            
            refl_y = ground.intercept_c
            
        else:
            # Sloped ground: use Fermat's principle
            # Find point on line y = mx + c that minimizes total path length
            m = ground.slope_m
            c = ground.intercept_c
            
            # Parametric form of ground: (t, mt + c)
            # Minimize: sqrt((t-tx_x)^2 + (mt+c-tx_y)^2) + sqrt((t-rx_x)^2 + (mt+c-rx_y)^2)
            # Using derivative = 0, solve for t
            
            # Numerical solution using optimization
            from scipy.optimize import minimize_scalar
            
            def path_length(t):
                y = m * t + c
                d1 = np.sqrt((t - tx_x)**2 + (y - tx_y)**2)
                d2 = np.sqrt((t - rx_x)**2 + (y - rx_y)**2)
                return d1 + d2
            
            result = minimize_scalar(path_length, bounds=(min(tx_x, rx_x) - 10, max(tx_x, rx_x) + 10), method='bounded')
            refl_x = result.x
            refl_y = m * refl_x + c
        
        return (refl_x, refl_y)
    
    def calculate_fresnel_coefficients(
        self,
        incident_angle: float,
        ground: GroundParameters,
        frequency: float
    ) -> Tuple[complex, complex]:
        """
        Calculate Fresnel reflection coefficients for horizontal and vertical polarization.
        
        Args:
            incident_angle: Angle of incidence from normal (radians)
            ground: Ground parameters
            frequency: Frequency (Hz)
            
        Returns:
            (reflection_h, reflection_v) - Complex reflection coefficients
        """
        # Complex relative permittivity
        omega = 2 * np.pi * frequency
        epsilon_c = ground.epsilon_r - 1j * ground.sigma / (omega * self.EPSILON_0)
        
        cos_i = np.cos(incident_angle)
        sin_i = np.sin(incident_angle)
        
        # Transmitted angle (complex)
        sin_t_sq = sin_i**2 / epsilon_c
        cos_t = np.sqrt(1 - sin_t_sq)
        
        # Fresnel reflection coefficients
        # Horizontal polarization (perpendicular)
        gamma_h = (cos_i - np.sqrt(epsilon_c) * cos_t) / (cos_i + np.sqrt(epsilon_c) * cos_t)
        
        # Vertical polarization (parallel)
        gamma_v = (epsilon_c * cos_i - cos_t) / (epsilon_c * cos_i + cos_t)
        
        return gamma_h, gamma_v
    
    def calculate_path_loss(self, distance: float, frequency: float) -> float:
        """
        Calculate free-space path loss.
        
        Args:
            distance: Distance (m)
            frequency: Frequency (Hz)
            
        Returns:
            Path loss (dB)
        """
        wavelength = self.C / frequency
        path_loss_db = 20 * np.log10(4 * np.pi * distance / wavelength)
        return path_loss_db
    
    def calculate_fields(
        self,
        tx_params: TransmitParameters,
        rx_pos: Tuple[float, float],
        ground: GroundParameters
    ) -> FieldResult:
        """
        Calculate electric and magnetic fields at receiver position.
        
        Args:
            tx_params: Transmit parameters
            rx_pos: Receiver position (x, y)
            ground: Ground parameters
            
        Returns:
            FieldResult object with field values
        """
        tx_pos = (tx_params.antenna_x, tx_params.antenna_y)
        rx_x, rx_y = rx_pos
        
        # Calculate wavelength
        wavelength = self.C / tx_params.frequency_hz
        k = 2 * np.pi / wavelength  # Wave number
        
        # Convert powers from dBm to Watts
        power_h_w = 10**((tx_params.power_h_dbm - 30) / 10)
        power_v_w = 10**((tx_params.power_v_dbm - 30) / 10)
        
        # Phase shift (V-pol is reference at 0°)
        phase_h = np.deg2rad(tx_params.phase_shift_deg)
        phase_v = 0.0
        
        # Direct path
        direct_vec = np.array([rx_x - tx_params.antenna_x, rx_y - tx_params.antenna_y])
        direct_dist = np.linalg.norm(direct_vec)
        direct_unit = direct_vec / direct_dist
        
        # Elevation angle for direct path (from +y axis)
        direct_theta = np.rad2deg(np.arctan2(direct_unit[0], direct_unit[1]))
        if direct_theta < 0:
            direct_theta += 360
        
        # Get antenna gain for direct path
        direct_gain_dbi = self.antenna_pattern.get_gain(direct_theta)
        direct_gain_linear = 10**(direct_gain_dbi / 10)
        
        # Calculate E-field magnitude at receiver (direct path)
        # E = sqrt(30 * P * G) / d * exp(-jkd)
        e_direct_h = np.sqrt(30 * power_h_w * direct_gain_linear) / direct_dist * np.exp(-1j * k * direct_dist + 1j * phase_h)
        e_direct_v = np.sqrt(30 * power_v_w * direct_gain_linear) / direct_dist * np.exp(-1j * k * direct_dist + 1j * phase_v)
        
        # Reflected path
        refl_point = self.calculate_reflection_point(tx_pos, rx_pos, ground)
        
        # Path from TX to reflection point
        refl_vec1 = np.array([refl_point[0] - tx_params.antenna_x, refl_point[1] - tx_params.antenna_y])
        refl_dist1 = np.linalg.norm(refl_vec1)
        refl_unit1 = refl_vec1 / refl_dist1
        
        # Path from reflection point to RX
        refl_vec2 = np.array([rx_x - refl_point[0], rx_y - refl_point[1]])
        refl_dist2 = np.linalg.norm(refl_vec2)
        
        # Total reflected path distance
        refl_total_dist = refl_dist1 + refl_dist2
        
        # Elevation angle for reflected path (from TX)
        refl_theta = np.rad2deg(np.arctan2(refl_unit1[0], refl_unit1[1]))
        if refl_theta < 0:
            refl_theta += 360
        
        # Get antenna gain for reflected path
        refl_gain_dbi = self.antenna_pattern.get_gain(refl_theta)
        refl_gain_linear = 10**(refl_gain_dbi / 10)
        
        # Calculate incident angle from normal to ground surface
        if ground.slope_m == 0.0:
            # Normal is vertical
            incident_angle = np.arccos(abs(refl_unit1[1]))
        else:
            # Normal to sloped surface
            normal = np.array([-ground.slope_m, 1]) / np.sqrt(1 + ground.slope_m**2)
            incident_angle = np.arccos(abs(np.dot(-refl_unit1, normal)))
        
        # Fresnel reflection coefficients
        gamma_h, gamma_v = self.calculate_fresnel_coefficients(incident_angle, ground, tx_params.frequency_hz)
        
        # E-field from reflected path
        e_refl_h = gamma_h * np.sqrt(30 * power_h_w * refl_gain_linear) / refl_total_dist * np.exp(-1j * k * refl_total_dist + 1j * phase_h)
        e_refl_v = gamma_v * np.sqrt(30 * power_v_w * refl_gain_linear) / refl_total_dist * np.exp(-1j * k * refl_total_dist + 1j * phase_v)
        
        # Total fields (superposition)
        e_total_h = e_direct_h + e_refl_h
        e_total_v = e_direct_v + e_refl_v
        
        # Total E-field magnitude
        e_magnitude = np.sqrt(abs(e_total_h)**2 + abs(e_total_v)**2)
        
        # Magnetic field (H = E / eta_0 for plane wave)
        h_field = e_magnitude / self.ETA_0
        
        return FieldResult(
            e_field_h=e_total_h,
            e_field_v=e_total_v,
            h_field=h_field,
            total_e_magnitude=e_magnitude,
            reflection_point=refl_point
        )
    
    def plot_geometry(
        self,
        tx_params: TransmitParameters,
        rx_pos: Tuple[float, float],
        result: FieldResult,
        ground: GroundParameters
    ):
        """
        Display the geometry including antenna, receiver, paths, and reflection point.
        
        Args:
            tx_params: Transmit parameters
            rx_pos: Receiver position
            result: Field calculation results
            ground: Ground parameters
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        tx_pos = (tx_params.antenna_x, tx_params.antenna_y)
        refl_point = result.reflection_point
        
        # Plot coverage area boundary
        ax.plot([0, self.X_MAX, self.X_MAX, 0, 0], 
                [0, 0, self.Y_MAX, self.Y_MAX, 0], 
                'k--', linewidth=1, label='Coverage Area')
        
        # Plot ground surface
        if ground.slope_m == 0.0:
            x_ground = np.array([0, self.X_MAX])
            y_ground = np.array([ground.intercept_c, ground.intercept_c])
        else:
            x_ground = np.linspace(0, self.X_MAX, 100)
            y_ground = ground.slope_m * x_ground + ground.intercept_c
        
        ax.fill_between(x_ground, y_ground, -10, alpha=0.3, color='brown', label='Ground')
        ax.plot(x_ground, y_ground, 'brown', linewidth=2)
        
        # Plot transmit antenna
        ax.plot(tx_pos[0], tx_pos[1], 'r^', markersize=15, label='Transmitter', zorder=5)
        
        # Plot receiver
        ax.plot(rx_pos[0], rx_pos[1], 'bs', markersize=12, label='Receiver', zorder=5)
        
        # Plot reflection point
        ax.plot(refl_point[0], refl_point[1], 'go', markersize=10, label='Reflection Point', zorder=5)
        
        # Plot direct path
        ax.plot([tx_pos[0], rx_pos[0]], [tx_pos[1], rx_pos[1]], 
                'b-', linewidth=2, label='Direct Path', alpha=0.6)
        
        # Plot reflected path
        ax.plot([tx_pos[0], refl_point[0]], [tx_pos[1], refl_point[1]], 
                'g--', linewidth=2, label='Reflected Path (TX to Refl)', alpha=0.6)
        ax.plot([refl_point[0], rx_pos[0]], [refl_point[1], rx_pos[1]], 
                'g--', linewidth=2, alpha=0.6)
        
        # Annotations
        ax.text(tx_pos[0], tx_pos[1] + 2, f'TX ({tx_pos[0]:.1f}, {tx_pos[1]:.1f})', 
                ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.text(rx_pos[0], rx_pos[1] + 2, f'RX ({rx_pos[0]:.1f}, {rx_pos[1]:.1f})', 
                ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        ax.text(refl_point[0], refl_point[1] - 2, f'Refl ({refl_point[0]:.1f}, {refl_point[1]:.1f})', 
                ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title('2D Network Coverage Tool - Ray Tracing Geometry', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        ax.set_aspect('equal')
        ax.set_xlim(-5, self.X_MAX + 5)
        ax.set_ylim(-5, self.Y_MAX + 5)
        
        plt.tight_layout()
        plt.show()
    
    def display_antenna_pattern(self):
        """Display the antenna gain pattern."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Cartesian plot
        ax1.plot(self.antenna_pattern.elevation_angles, self.antenna_pattern.gain_dbi, 'b-', linewidth=2)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel('Elevation Angle (degrees)', fontsize=12)
        ax1.set_ylabel('Gain (dBi)', fontsize=12)
        ax1.set_title('Antenna Gain Pattern - Cartesian', fontsize=13, fontweight='bold')
        ax1.set_xlim(0, 180)
        
        # Polar plot
        theta_rad = np.deg2rad(self.antenna_pattern.elevation_angles)
        gain_linear = 10**(self.antenna_pattern.gain_dbi / 10)
        
        ax2 = plt.subplot(122, projection='polar')
        ax2.plot(theta_rad, gain_linear, 'r-', linewidth=2)
        ax2.set_theta_zero_location('N')  # 0° at top
        ax2.set_theta_direction(-1)  # Clockwise
        ax2.set_title('Antenna Gain Pattern - Polar\n(Linear scale)', fontsize=13, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


def get_user_inputs() -> Tuple[TransmitParameters, Tuple[float, float], GroundParameters]:
    """
    Collect user inputs for the simulation.
    
    Returns:
        (tx_params, rx_pos, ground_params)
    """
    print("\n" + "="*60)
    print("2D NETWORK COVERAGE TOOL - USER INPUT")
    print("="*60)
    
    print("\n--- Transmit Signal Parameters ---")
    power_h = float(input("Horizontal polarization power (dBm): "))
    power_v = float(input("Vertical polarization power (dBm): "))
    phase_shift = float(input("Phase shift between H and V (degrees, V-pol is reference): "))
    frequency_mhz = float(input("Frequency (MHz): "))
    frequency_hz = frequency_mhz * 1e6
    
    print("\n--- Antenna Position ---")
    antenna_x = float(input("Antenna X coordinate (m) [default=0]: ") or "0")
    antenna_y = float(input("Antenna Y coordinate (m): "))
    
    print("\n--- Ground Medium Properties ---")
    epsilon_r = float(input("Relative permittivity (epsilon_r): "))
    sigma = float(input("Conductivity (S/m): "))
    
    use_slope = input("\nUse sloped ground surface? (y/n) [default=n]: ").lower() == 'y'
    if use_slope:
        slope_m = float(input("Ground slope (m for y=mx+c): "))
        intercept_c = float(input("Ground intercept (c for y=mx+c): "))
    else:
        slope_m = 0.0
        intercept_c = 0.0
    
    print("\n--- Receiver Position ---")
    rx_x = float(input("Receiver X coordinate (m): "))
    rx_y = float(input("Receiver Y coordinate (m): "))
    
    tx_params = TransmitParameters(
        power_h_dbm=power_h,
        power_v_dbm=power_v,
        phase_shift_deg=phase_shift,
        frequency_hz=frequency_hz,
        antenna_x=antenna_x,
        antenna_y=antenna_y
    )
    
    ground_params = GroundParameters(
        epsilon_r=epsilon_r,
        sigma=sigma,
        slope_m=slope_m,
        intercept_c=intercept_c
    )
    
    rx_pos = (rx_x, rx_y)
    
    return tx_params, rx_pos, ground_params


def display_results(result: FieldResult):
    """
    Display calculation results.
    
    Args:
        result: Field calculation results
    """
    print("\n" + "="*60)
    print("CALCULATION RESULTS")
    print("="*60)
    
    print(f"\n--- Electric Field ---")
    print(f"E-field (H-pol): {abs(result.e_field_h):.6e} V/m ∠ {np.angle(result.e_field_h, deg=True):.2f}°")
    print(f"E-field (V-pol): {abs(result.e_field_v):.6e} V/m ∠ {np.angle(result.e_field_v, deg=True):.2f}°")
    print(f"Total E-field magnitude: {result.total_e_magnitude:.6e} V/m")
    print(f"Total E-field (dBV/m): {20*np.log10(result.total_e_magnitude):.2f} dB")
    
    print(f"\n--- Magnetic Field ---")
    print(f"H-field magnitude: {result.h_field:.6e} A/m")
    print(f"H-field (dBA/m): {20*np.log10(result.h_field):.2f} dB")
    
    print(f"\n--- Reflection Point ---")
    print(f"Coordinates: ({result.reflection_point[0]:.3f} m, {result.reflection_point[1]:.3f} m)")
    
    print("\n" + "="*60)


def main():
    """Main function to run the network coverage tool."""
    print("\n" + "="*60)
    print("2D NETWORK COVERAGE TOOL")
    print("="*60)
    print("This tool calculates electric and magnetic fields")
    print("using ray-tracing with ground reflections.")
    print("="*60)
    
    # Read antenna pattern
    csv_file = input("\nEnter antenna gain pattern CSV file path: ")
    
    try:
        antenna_pattern = NetworkCoverageTool.read_antenna_pattern(csv_file)
        print(f"✓ Antenna pattern loaded: {len(antenna_pattern.elevation_angles)} data points")
        print(f"  Elevation range: {antenna_pattern.elevation_angles[0]}° to {antenna_pattern.elevation_angles[-1]}°")
        print(f"  Gain range: {antenna_pattern.gain_dbi.min():.2f} to {antenna_pattern.gain_dbi.max():.2f} dBi")
    except FileNotFoundError:
        print(f"✗ Error: File '{csv_file}' not found!")
        return
    except Exception as e:
        print(f"✗ Error reading antenna pattern: {e}")
        return
    
    # Create tool instance
    tool = NetworkCoverageTool(antenna_pattern)
    
    # Display antenna pattern
    display_pattern = input("\nDisplay antenna pattern? (y/n) [default=y]: ").lower()
    if display_pattern != 'n':
        tool.display_antenna_pattern()
    
    # Get user inputs
    tx_params, rx_pos, ground_params = get_user_inputs()
    
    # Calculate fields
    print("\n⏳ Calculating electromagnetic fields...")
    result = tool.calculate_fields(tx_params, rx_pos, ground_params)
    
    # Display results
    display_results(result)
    
    # Plot geometry
    plot_geom = input("\nDisplay geometry plot? (y/n) [default=y]: ").lower()
    if plot_geom != 'n':
        tool.plot_geometry(tx_params, rx_pos, result, ground_params)
    
    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()
