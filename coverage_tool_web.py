#!/usr/bin/env python3
"""
2D Network Coverage Tool - Web-based GUI
========================================
Flask-based web interface for the network coverage tool.
"""

from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import os
import json

from network_coverage_tool import (
    NetworkCoverageTool,
    TransmitParameters,
    GroundParameters
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Global storage
tool_instance = None
antenna_pattern = None


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/api/load_pattern', methods=['POST'])
def load_pattern():
    """Load antenna pattern from CSV file."""
    global tool_instance, antenna_pattern
    
    try:
        csv_filename = request.json.get('filename', 'sample_antenna_pattern.csv')
        
        if not os.path.exists(csv_filename):
            return jsonify({'success': False, 'error': f'File not found: {csv_filename}'})
        
        antenna_pattern = NetworkCoverageTool.read_antenna_pattern(csv_filename)
        tool_instance = NetworkCoverageTool(antenna_pattern)
        
        return jsonify({
            'success': True,
            'data_points': len(antenna_pattern.elevation_angles),
            'elevation_range': [float(antenna_pattern.elevation_angles[0]), 
                               float(antenna_pattern.elevation_angles[-1])],
            'gain_range': [float(antenna_pattern.gain_dbi.min()), 
                          float(antenna_pattern.gain_dbi.max())]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




@app.route('/api/calculate', methods=['POST'])
def calculate_fields():
    """Calculate electromagnetic fields."""
    global tool_instance, antenna_pattern
    
    if tool_instance is None or antenna_pattern is None:
        return jsonify({'success': False, 'error': 'Please load antenna pattern first'})
    
    try:
        data = request.json
        
        # Parse transmit parameters
        tx_params = TransmitParameters(
            power_h_dbm=float(data['power_h']),
            power_v_dbm=float(data['power_v']),
            phase_shift_deg=float(data['phase_shift']),
            frequency_hz=float(data['frequency']) * 1e6,  # MHz to Hz
            antenna_x=float(data['antenna_x']),
            antenna_y=float(data['antenna_y'])
        )
        
        # Parse ground parameters
        ground_params = GroundParameters(
            epsilon_r=float(data['epsilon_r']),
            sigma=float(data['sigma']),
            slope_m=float(data['slope_m']),
            intercept_c=float(data['intercept_c'])
        )
        
        # Receiver position
        rx_pos = (float(data['rx_x']), float(data['rx_y']))
        
        # Calculate
        result = tool_instance.calculate_fields(tx_params, rx_pos, ground_params)
        
        # Format results
        return jsonify({
            'success': True,
            'results': {
                'e_field_h_mag': float(abs(result.e_field_h)),
                'e_field_h_phase': float(np.angle(result.e_field_h, deg=True)),
                'e_field_v_mag': float(abs(result.e_field_v)),
                'e_field_v_phase': float(np.angle(result.e_field_v, deg=True)),
                'total_e_magnitude': float(result.total_e_magnitude),
                'total_e_db': float(20 * np.log10(result.total_e_magnitude)),
                'h_field': float(result.h_field),
                'h_field_db': float(20 * np.log10(result.h_field)),
                'reflection_point': [float(result.reflection_point[0]), 
                                    float(result.reflection_point[1])]
            },
            'tx_params': {
                'x': tx_params.antenna_x,
                'y': tx_params.antenna_y
            },
            'rx_pos': list(rx_pos),
            'ground': {
                'slope': ground_params.slope_m,
                'intercept': ground_params.intercept_c
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




@app.route('/api/plot_geometry', methods=['POST'])
def plot_geometry():
    """Generate geometry plot."""
    global tool_instance
    
    try:
        data = request.json
        
        # Extract data
        tx_pos = (data['tx_x'], data['tx_y'])
        rx_pos = (data['rx_x'], data['rx_y'])
        refl_point = tuple(data['reflection_point'])
        ground_slope = data['ground_slope']
        ground_intercept = data['ground_intercept']
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Coverage area
        ax.plot([0, 200, 200, 0, 0], [0, 0, 50, 50, 0], 'k--', linewidth=1, label='Coverage Area')
        
        # Ground surface
        if ground_slope == 0.0:
            x_ground = np.array([0, 200])
            y_ground = np.array([ground_intercept, ground_intercept])
        else:
            x_ground = np.linspace(0, 200, 100)
            y_ground = ground_slope * x_ground + ground_intercept
        
        ax.fill_between(x_ground, y_ground, -10, alpha=0.3, color='brown', label='Ground')
        ax.plot(x_ground, y_ground, 'brown', linewidth=2)
        
        # Transmitter, receiver, reflection point
        ax.plot(tx_pos[0], tx_pos[1], 'r^', markersize=15, label='Transmitter', zorder=5)
        ax.plot(rx_pos[0], rx_pos[1], 'bs', markersize=12, label='Receiver', zorder=5)
        ax.plot(refl_point[0], refl_point[1], 'go', markersize=10, label='Reflection Point', zorder=5)
        
        # Paths
        ax.plot([tx_pos[0], rx_pos[0]], [tx_pos[1], rx_pos[1]], 
                'b-', linewidth=2, label='Direct Path', alpha=0.6)
        ax.plot([tx_pos[0], refl_point[0]], [tx_pos[1], refl_point[1]], 
                'g--', linewidth=2, label='Reflected Path', alpha=0.6)
        ax.plot([refl_point[0], rx_pos[0]], [refl_point[1], rx_pos[1]], 
                'g--', linewidth=2, alpha=0.6)
        
        # Labels
        ax.text(tx_pos[0], tx_pos[1] + 2, f'TX ({tx_pos[0]:.1f}, {tx_pos[1]:.1f})', 
                ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        ax.text(rx_pos[0], rx_pos[1] + 2, f'RX ({rx_pos[0]:.1f}, {rx_pos[1]:.1f})', 
                ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        ax.text(refl_point[0], refl_point[1] - 2, f'Refl ({refl_point[0]:.1f}, {refl_point[1]:.1f})', 
                ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.set_xlabel('X Position (m)', fontsize=11)
        ax.set_ylabel('Y Position (m)', fontsize=11)
        ax.set_title('2D Network Coverage Tool - Ray Tracing Geometry', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        ax.set_aspect('equal')
        ax.set_xlim(-5, 205)
        ax.set_ylim(-5, 55)
        
        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return jsonify({'success': True, 'image': img_base64})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




@app.route('/api/plot_antenna', methods=['GET'])
def plot_antenna():
    """Generate antenna pattern plot."""
    global antenna_pattern
    
    if antenna_pattern is None:
        return jsonify({'success': False, 'error': 'No antenna pattern loaded'})
    
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Cartesian plot
        ax1.plot(antenna_pattern.elevation_angles, antenna_pattern.gain_dbi, 'b-', linewidth=2)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel('Elevation Angle (degrees)', fontsize=11)
        ax1.set_ylabel('Gain (dBi)', fontsize=11)
        ax1.set_title('Antenna Gain Pattern - Cartesian', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, 180)
        
        # Polar plot
        ax2 = plt.subplot(122, projection='polar')
        theta_rad = np.deg2rad(antenna_pattern.elevation_angles)
        gain_linear = 10**(antenna_pattern.gain_dbi / 10)
        
        ax2.plot(theta_rad, gain_linear, 'r-', linewidth=2)
        ax2.set_theta_zero_location('N')
        ax2.set_theta_direction(-1)
        ax2.set_title('Antenna Gain Pattern - Polar\n(Linear scale)', 
                     fontsize=12, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3)
        
        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return jsonify({'success': True, 'image': img_base64})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*60)
    print("2D Network Coverage Tool - Web Interface")
    print("="*60)
    print("\nStarting server...")
    print("Open your browser and navigate to:")
    print("  http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
