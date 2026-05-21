#!/usr/bin/env python3
"""
2D Network Coverage Tool - GUI Application
==========================================
Graphical user interface for the network coverage tool with tabbed layout.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import os

from network_coverage_tool import (
    NetworkCoverageTool,
    TransmitParameters,
    GroundParameters,
    AntennaPattern
)


class CoverageToolGUI:
    """Main GUI application for the 2D Network Coverage Tool."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("EEE3089F Project 4 - Network Coverage - VSCETH003")
        self.root.geometry("1200x800")
        
        # Initialize tool and data storage
        self.tool = None
        self.antenna_pattern = None
        self.last_result = None
        self.last_tx_params = None
        self.last_rx_pos = None
        self.last_ground = None
        
        # Create main UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_antenna_tab()
        self.create_input_tab()
        self.create_results_tab()
        self.create_geometry_tab()
        self.create_antenna_plot_tab()
        
    def create_antenna_tab(self):

        """Create the Antenna Pattern tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Antenna Pattern")
        
        # Title
        title_label = tk.Label(tab, text="Load Antenna Gain Pattern", 
                               font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white', pady=10)
        title_label.pack(fill='x')
        
        # Main frame
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="CSV File Selection", padding=10)
        file_frame.pack(fill='x', pady=10)
        
        self.csv_path_var = tk.StringVar(value="sample_antenna_pattern.csv")
        
        ttk.Label(file_frame, text="Antenna Pattern File:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(file_frame, textvariable=self.csv_path_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_csv).grid(row=0, column=2, padx=5)
        ttk.Button(file_frame, text="Load Pattern", command=self.load_antenna_pattern).grid(row=0, column=3, padx=5)
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Pattern Status", padding=10)
        status_frame.pack(fill='x', pady=10)
        
        self.pattern_status_text = scrolledtext.ScrolledText(status_frame, height=8, width=80, 
                                                              font=('Courier', 10))
        self.pattern_status_text.pack(fill='both', expand=True)
        self.pattern_status_text.insert('1.0', 'No antenna pattern loaded.\n\nPlease load a CSV file.')
        self.pattern_status_text.config(state='disabled')
        
        # Preview button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Preview Pattern", 
                  command=self.preview_pattern, style='Accent.TButton').pack()
    
    def create_input_tab(self):

        """Create the Input Parameters tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Input Parameters")
        
        # Title
        title_label = tk.Label(tab, text="Transmit and Receiver Parameters", 
                               font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white', pady=10)
        title_label.pack(fill='x')
        
        # Scrollable frame
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Transmit Signal Parameters
        tx_frame = ttk.LabelFrame(scrollable_frame, text="Transmit Signal Parameters", padding=15)
        tx_frame.grid(row=0, column=0, padx=20, pady=10, sticky='ew')
        
        self.power_h_var = tk.StringVar(value="40.0")
        self.power_v_var = tk.StringVar(value="40.0")
        self.phase_shift_var = tk.StringVar(value="0.0")
        self.frequency_var = tk.StringVar(value="2400")
        
        ttk.Label(tx_frame, text="Horizontal Polarization Power (dBm):").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(tx_frame, textvariable=self.power_h_var, width=20).grid(row=0, column=1, padx=10)
        
        ttk.Label(tx_frame, text="Vertical Polarization Power (dBm):").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(tx_frame, textvariable=self.power_v_var, width=20).grid(row=1, column=1, padx=10)
        
        ttk.Label(tx_frame, text="Phase Shift (H-V) [degrees]:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(tx_frame, textvariable=self.phase_shift_var, width=20).grid(row=2, column=1, padx=10)
        ttk.Label(tx_frame, text="(V-pol is reference at 0°)", font=('Arial', 8, 'italic')).grid(row=2, column=2, sticky='w')
        
        ttk.Label(tx_frame, text="Frequency (MHz):").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Entry(tx_frame, textvariable=self.frequency_var, width=20).grid(row=3, column=1, padx=10)

        
        # Antenna Position
        ant_frame = ttk.LabelFrame(scrollable_frame, text="Antenna Position", padding=15)
        ant_frame.grid(row=1, column=0, padx=20, pady=10, sticky='ew')
        
        self.antenna_x_var = tk.StringVar(value="0.0")
        self.antenna_y_var = tk.StringVar(value="20.0")
        
        ttk.Label(ant_frame, text="Antenna X-coordinate (m):").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(ant_frame, textvariable=self.antenna_x_var, width=20).grid(row=0, column=1, padx=10)
        
        ttk.Label(ant_frame, text="Antenna Y-coordinate (m):").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(ant_frame, textvariable=self.antenna_y_var, width=20).grid(row=1, column=1, padx=10)
        
        # Ground Properties
        ground_frame = ttk.LabelFrame(scrollable_frame, text="Ground Medium Properties", padding=15)
        ground_frame.grid(row=2, column=0, padx=20, pady=10, sticky='ew')
        
        self.epsilon_r_var = tk.StringVar(value="15.0")
        self.sigma_var = tk.StringVar(value="0.01")
        self.slope_m_var = tk.StringVar(value="0.0")
        self.intercept_c_var = tk.StringVar(value="0.0")
        
        ttk.Label(ground_frame, text="Relative Permittivity (εᵣ):").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(ground_frame, textvariable=self.epsilon_r_var, width=20).grid(row=0, column=1, padx=10)
        
        ttk.Label(ground_frame, text="Conductivity (S/m):").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(ground_frame, textvariable=self.sigma_var, width=20).grid(row=1, column=1, padx=10)
        
        ttk.Label(ground_frame, text="Ground Slope (m for y=mx+c):").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(ground_frame, textvariable=self.slope_m_var, width=20).grid(row=2, column=1, padx=10)
        
        ttk.Label(ground_frame, text="Ground Intercept (c for y=mx+c):").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Entry(ground_frame, textvariable=self.intercept_c_var, width=20).grid(row=3, column=1, padx=10)
        
        # Receiver Position
        rx_frame = ttk.LabelFrame(scrollable_frame, text="Receiver Position", padding=15)
        rx_frame.grid(row=3, column=0, padx=20, pady=10, sticky='ew')
        
        self.rx_x_var = tk.StringVar(value="100.0")
        self.rx_y_var = tk.StringVar(value="5.0")
        
        ttk.Label(rx_frame, text="Receiver X-coordinate (m):").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(rx_frame, textvariable=self.rx_x_var, width=20).grid(row=0, column=1, padx=10)

        
        ttk.Label(rx_frame, text="Receiver Y-coordinate (m):").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(rx_frame, textvariable=self.rx_y_var, width=20).grid(row=1, column=1, padx=10)
        
        # Calculate Button
        calc_frame = ttk.Frame(scrollable_frame)
        calc_frame.grid(row=4, column=0, pady=20)
        
        ttk.Button(calc_frame, text="⚡ Calculate Fields", 
                  command=self.calculate_fields, 
                  style='Accent.TButton',
                  width=25).pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_results_tab(self):
        """Create the Results tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Results")
        
        # Title
        title_label = tk.Label(tab, text="Calculation Results", 
                               font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white', pady=10)
        title_label.pack(fill='x')
        
        # Main frame with two columns
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Left column - Electric Field Results
        left_frame = ttk.LabelFrame(main_frame, text="Electric Field Results", padding=15)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        self.results_text = scrolledtext.ScrolledText(left_frame, height=20, width=50, 
                                                       font=('Courier', 10))
        self.results_text.pack(fill='both', expand=True)
        self.results_text.insert('1.0', 'No calculations performed yet.\n\nGo to "Input Parameters" tab and click "Calculate Fields".')
        self.results_text.config(state='disabled')
        
        # Right column - Magnetic Field and Reflection Point
        right_frame = ttk.LabelFrame(main_frame, text="Additional Results", padding=15)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        self.additional_text = scrolledtext.ScrolledText(right_frame, height=20, width=50, 
                                                          font=('Courier', 10))
        self.additional_text.pack(fill='both', expand=True)
        self.additional_text.config(state='disabled')
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    
    def create_geometry_tab(self):
        """Create the Geometry Plot tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Geometry Plot")
        
        # Title
        title_label = tk.Label(tab, text="Ray Tracing Geometry", 
                               font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white', pady=10)
        title_label.pack(fill='x')
        
        # Button frame
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(button_frame, text="📊 Plot Geometry", 
                  command=self.plot_geometry).pack(side='left', padx=5)
        ttk.Button(button_frame, text="💾 Save Plot", 
                  command=self.save_geometry_plot).pack(side='left', padx=5)
        
        # Plot frame
        plot_frame = ttk.Frame(tab)
        plot_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.geometry_figure = Figure(figsize=(10, 5), dpi=100)
        self.geometry_canvas = FigureCanvasTkAgg(self.geometry_figure, plot_frame)
        self.geometry_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Toolbar
        toolbar_frame = ttk.Frame(tab)
        toolbar_frame.pack(fill='x', padx=20)
        toolbar = NavigationToolbar2Tk(self.geometry_canvas, toolbar_frame)
        toolbar.update()
    
    def create_antenna_plot_tab(self):
        """Create the Antenna Pattern Plot tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Antenna Pattern Plot")
        
        # Title
        title_label = tk.Label(tab, text="Antenna Gain Pattern Visualization", 
                               font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white', pady=10)
        title_label.pack(fill='x')
        
        # Button frame
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(button_frame, text="📊 Plot Pattern", 
                  command=self.plot_antenna_pattern).pack(side='left', padx=5)
        ttk.Button(button_frame, text="💾 Save Plot", 
                  command=self.save_antenna_plot).pack(side='left', padx=5)
        
        # Plot frame
        plot_frame = ttk.Frame(tab)
        plot_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.antenna_figure = Figure(figsize=(12, 5), dpi=100)
        self.antenna_canvas = FigureCanvasTkAgg(self.antenna_figure, plot_frame)
        self.antenna_canvas.get_tk_widget().pack(fill='both', expand=True)

        
        # Toolbar
        toolbar_frame = ttk.Frame(tab)
        toolbar_frame.pack(fill='x', padx=20)
        toolbar = NavigationToolbar2Tk(self.antenna_canvas, toolbar_frame)
        toolbar.update()
    
    # Callback methods
    def browse_csv(self):
        """Open file dialog to browse for CSV file."""
        filename = filedialog.askopenfilename(
            title="Select Antenna Pattern CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_path_var.set(filename)
    
    def load_antenna_pattern(self):
        """Load antenna pattern from CSV file."""
        csv_path = self.csv_path_var.get()
        
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", f"File not found: {csv_path}")
            return
        
        try:
            self.antenna_pattern = NetworkCoverageTool.read_antenna_pattern(csv_path)
            self.tool = NetworkCoverageTool(self.antenna_pattern)
            
            # Update status
            status_msg = f"✓ Antenna pattern loaded successfully!\n\n"
            status_msg += f"File: {os.path.basename(csv_path)}\n"
            status_msg += f"Data points: {len(self.antenna_pattern.elevation_angles)}\n"
            status_msg += f"Elevation range: {self.antenna_pattern.elevation_angles[0]:.1f}° to {self.antenna_pattern.elevation_angles[-1]:.1f}°\n"
            status_msg += f"Gain range: {self.antenna_pattern.gain_dbi.min():.2f} to {self.antenna_pattern.gain_dbi.max():.2f} dBi\n\n"
            status_msg += "You can now:\n"
            status_msg += "  • View pattern in 'Antenna Pattern Plot' tab\n"
            status_msg += "  • Enter parameters in 'Input Parameters' tab\n"
            status_msg += "  • Calculate fields"
            
            self.pattern_status_text.config(state='normal')
            self.pattern_status_text.delete('1.0', tk.END)
            self.pattern_status_text.insert('1.0', status_msg)
            self.pattern_status_text.config(state='disabled')
            
            messagebox.showinfo("Success", "Antenna pattern loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load antenna pattern:\n{str(e)}")
    
    def preview_pattern(self):
        """Preview antenna pattern in a popup window."""
        if self.antenna_pattern is None:
            messagebox.showwarning("Warning", "Please load an antenna pattern first!")
            return
        
        # Switch to antenna pattern plot tab
        self.notebook.select(4)  # Index of Antenna Pattern Plot tab
        self.plot_antenna_pattern()

    
    def calculate_fields(self):
        """Calculate electromagnetic fields."""
        if self.tool is None or self.antenna_pattern is None:
            messagebox.showwarning("Warning", "Please load an antenna pattern first!")
            return
        
        try:
            # Get transmit parameters
            tx_params = TransmitParameters(
                power_h_dbm=float(self.power_h_var.get()),
                power_v_dbm=float(self.power_v_var.get()),
                phase_shift_deg=float(self.phase_shift_var.get()),
                frequency_hz=float(self.frequency_var.get()) * 1e6,  # Convert MHz to Hz
                antenna_x=float(self.antenna_x_var.get()),
                antenna_y=float(self.antenna_y_var.get())
            )
            
            # Get ground parameters
            ground_params = GroundParameters(
                epsilon_r=float(self.epsilon_r_var.get()),
                sigma=float(self.sigma_var.get()),
                slope_m=float(self.slope_m_var.get()),
                intercept_c=float(self.intercept_c_var.get())
            )
            
            # Get receiver position
            rx_pos = (float(self.rx_x_var.get()), float(self.rx_y_var.get()))
            
            # Calculate fields
            result = self.tool.calculate_fields(tx_params, rx_pos, ground_params)
            
            # Store results
            self.last_result = result
            self.last_tx_params = tx_params
            self.last_rx_pos = rx_pos
            self.last_ground = ground_params
            
            # Display results
            self.display_results(result, tx_params, rx_pos, ground_params)
            
            # Switch to results tab
            self.notebook.select(2)  # Index of Results tab
            
            messagebox.showinfo("Success", "Field calculation completed!\n\nView results in the 'Results' tab.")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input value:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error during calculation:\n{str(e)}")
    
    def display_results(self, result, tx_params, rx_pos, ground_params):
        """Display calculation results in the Results tab."""
        # Format electric field results
        e_results = "=" * 60 + "\n"
        e_results += "ELECTRIC FIELD RESULTS\n"
        e_results += "=" * 60 + "\n\n"
        e_results += f"Transmitter Position: ({tx_params.antenna_x:.2f}, {tx_params.antenna_y:.2f}) m\n"
        e_results += f"Receiver Position: ({rx_pos[0]:.2f}, {rx_pos[1]:.2f}) m\n"
        e_results += f"Frequency: {tx_params.frequency_hz/1e9:.3f} GHz\n"
        e_results += f"Power (H/V): {tx_params.power_h_dbm:.1f}/{tx_params.power_v_dbm:.1f} dBm\n\n"

        e_results += "-" * 60 + "\n"
        e_results += "E-Field Components:\n"
        e_results += "-" * 60 + "\n"
        e_results += f"H-polarization:\n"
        e_results += f"  Magnitude: {abs(result.e_field_h):.6e} V/m\n"
        e_results += f"  Phase: {np.angle(result.e_field_h, deg=True):.2f}°\n"
        e_results += f"  dBV/m: {20*np.log10(abs(result.e_field_h)):.2f} dB\n\n"
        
        e_results += f"V-polarization:\n"
        e_results += f"  Magnitude: {abs(result.e_field_v):.6e} V/m\n"
        e_results += f"  Phase: {np.angle(result.e_field_v, deg=True):.2f}°\n"
        e_results += f"  dBV/m: {20*np.log10(abs(result.e_field_v)):.2f} dB\n\n"
        
        e_results += "-" * 60 + "\n"
        e_results += "Total E-Field:\n"
        e_results += "-" * 60 + "\n"
        e_results += f"Magnitude: {result.total_e_magnitude:.6e} V/m\n"
        e_results += f"dBV/m: {20*np.log10(result.total_e_magnitude):.2f} dB\n"
        
        # Format magnetic field and reflection point
        add_results = "=" * 60 + "\n"
        add_results += "MAGNETIC FIELD RESULTS\n"
        add_results += "=" * 60 + "\n\n"
        add_results += f"H-Field Magnitude: {result.h_field:.6e} A/m\n"
        add_results += f"H-Field (dBA/m): {20*np.log10(result.h_field):.2f} dB\n\n"
        
        add_results += "=" * 60 + "\n"
        add_results += "REFLECTION POINT\n"
        add_results += "=" * 60 + "\n\n"
        add_results += f"Coordinates: ({result.reflection_point[0]:.3f}, {result.reflection_point[1]:.3f}) m\n\n"
        
        add_results += "=" * 60 + "\n"
        add_results += "GROUND PROPERTIES\n"
        add_results += "=" * 60 + "\n\n"
        add_results += f"Relative Permittivity: {ground_params.epsilon_r:.2f}\n"
        add_results += f"Conductivity: {ground_params.sigma:.4f} S/m\n"
        
        if ground_params.slope_m != 0.0:
            add_results += f"Ground Equation: y = {ground_params.slope_m}x + {ground_params.intercept_c}\n"
        else:
            add_results += f"Ground: Flat (y = {ground_params.intercept_c})\n"
        
        # Update text widgets
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', e_results)
        self.results_text.config(state='disabled')
        
        self.additional_text.config(state='normal')
        self.additional_text.delete('1.0', tk.END)
        self.additional_text.insert('1.0', add_results)
        self.additional_text.config(state='disabled')

    
    def plot_geometry(self):
        """Plot the ray tracing geometry."""
        if self.last_result is None:
            messagebox.showwarning("Warning", "Please calculate fields first!")
            return
        
        try:
            self.geometry_figure.clear()
            ax = self.geometry_figure.add_subplot(111)
            
            tx_pos = (self.last_tx_params.antenna_x, self.last_tx_params.antenna_y)
            rx_pos = self.last_rx_pos
            refl_point = self.last_result.reflection_point
            ground = self.last_ground
            
            # Plot coverage area boundary
            ax.plot([0, self.tool.X_MAX, self.tool.X_MAX, 0, 0], 
                    [0, 0, self.tool.Y_MAX, self.tool.Y_MAX, 0], 
                    'k--', linewidth=1, label='Coverage Area')
            
            # Plot ground surface
            if ground.slope_m == 0.0:
                x_ground = np.array([0, self.tool.X_MAX])
                y_ground = np.array([ground.intercept_c, ground.intercept_c])
            else:
                x_ground = np.linspace(0, self.tool.X_MAX, 100)
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
                    'g--', linewidth=2, label='Reflected Path', alpha=0.6)
            ax.plot([refl_point[0], rx_pos[0]], [refl_point[1], rx_pos[1]], 
                    'g--', linewidth=2, alpha=0.6)
            
            # Annotations
            ax.text(tx_pos[0], tx_pos[1] + 2, f'TX\n({tx_pos[0]:.1f}, {tx_pos[1]:.1f})', 
                    ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            ax.text(rx_pos[0], rx_pos[1] + 2, f'RX\n({rx_pos[0]:.1f}, {rx_pos[1]:.1f})', 
                    ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

            ax.text(refl_point[0], refl_point[1] - 2, f'Refl\n({refl_point[0]:.1f}, {refl_point[1]:.1f})', 
                    ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
            
            ax.set_xlabel('X Position (m)', fontsize=11)
            ax.set_ylabel('Y Position (m)', fontsize=11)
            ax.set_title('2D Network Coverage Tool - Ray Tracing Geometry', fontsize=13, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right', fontsize=9)
            ax.set_aspect('equal')
            ax.set_xlim(-5, self.tool.X_MAX + 5)
            ax.set_ylim(-5, self.tool.Y_MAX + 5)
            
            self.geometry_figure.tight_layout()
            self.geometry_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error plotting geometry:\n{str(e)}")
    
    def plot_antenna_pattern(self):
        """Plot the antenna gain pattern."""
        if self.antenna_pattern is None:
            messagebox.showwarning("Warning", "Please load an antenna pattern first!")
            return
        
        try:
            self.antenna_figure.clear()
            
            # Cartesian plot
            ax1 = self.antenna_figure.add_subplot(121)
            ax1.plot(self.antenna_pattern.elevation_angles, self.antenna_pattern.gain_dbi, 
                    'b-', linewidth=2)
            ax1.grid(True, alpha=0.3)
            ax1.set_xlabel('Elevation Angle (degrees)', fontsize=11)
            ax1.set_ylabel('Gain (dBi)', fontsize=11)
            ax1.set_title('Antenna Gain Pattern - Cartesian', fontsize=12, fontweight='bold')
            ax1.set_xlim(0, 180)
            
            # Polar plot
            ax2 = self.antenna_figure.add_subplot(122, projection='polar')
            theta_rad = np.deg2rad(self.antenna_pattern.elevation_angles)
            gain_linear = 10**(self.antenna_pattern.gain_dbi / 10)
            
            ax2.plot(theta_rad, gain_linear, 'r-', linewidth=2)
            ax2.set_theta_zero_location('N')  # 0° at top
            ax2.set_theta_direction(-1)  # Clockwise
            ax2.set_title('Antenna Gain Pattern - Polar\n(Linear scale)', 
                         fontsize=12, fontweight='bold', pad=20)
            ax2.grid(True, alpha=0.3)
            
            self.antenna_figure.tight_layout()
            self.antenna_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error plotting antenna pattern:\n{str(e)}")

    
    def save_geometry_plot(self):
        """Save the geometry plot to file."""
        if self.last_result is None:
            messagebox.showwarning("Warning", "No plot to save. Please plot geometry first!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.geometry_figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")
    
    def save_antenna_plot(self):
        """Save the antenna pattern plot to file."""
        if self.antenna_pattern is None:
            messagebox.showwarning("Warning", "No plot to save. Please plot antenna pattern first!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.antenna_figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Custom accent button style
    style.configure('Accent.TButton', 
                   font=('Arial', 11, 'bold'),
                   foreground='white',
                   background='#3498db',
                   padding=10)
    
    app = CoverageToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
