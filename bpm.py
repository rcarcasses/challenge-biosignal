#!/usr/bin/env python3
"""
Breathing Rate Analysis Script
Analyzes heart rate variability data to extract breathing rates and exports to CSV.
"""

import json
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import sys
import os

def analyze_breathing_rate(json_file_path, output_csv_path='breathing_rate_output.csv'):
    """
    Analyze heart rate variability data to extract breathing rates.
    
    Args:
        json_file_path (str): Path to the JSON file containing HRV data
        output_csv_path (str): Path for the output CSV file
    
    Returns:
        pd.DataFrame: DataFrame with time and bpm columns
    """
    
    # Check if input file exists
    if not os.path.exists(json_file_path):
        print(f"Error: Input file '{json_file_path}' not found.")
        sys.exit(1)
    
    try:
        # Parse the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Create pandas DataFrame
        df = pd.DataFrame(data)
        
        # Calculate mean RR intervals for each record
        df['rr_mean'] = df['rr'].apply(lambda x: np.mean(x) if isinstance(x, list) and len(x) > 0 else np.nan)
        
        # Convert timestamp to datetime and localize to PDT
        df['datetime'] = pd.to_datetime(df['ts'], unit='s', utc=True).dt.tz_convert('US/Pacific')
        df['time'] = df['datetime'].dt.strftime('%H:%M:%S')
        
        print(f"Loaded data with {len(df)} records")
        print(f"Time range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
        
        # Remove NaN values and get clean RR data
        clean_mask = df['rr_mean'].notna()
        clean_rr = df['rr_mean'][clean_mask].values
        clean_time = df['datetime'][clean_mask]
        clean_time_formatted = df['time'][clean_mask]
        
        print(f"Clean data points: {len(clean_rr)}")
        
        # Find peaks in the RR signal
        # Adjust height and distance parameters as needed
        peaks, properties = find_peaks(clean_rr, 
                                      height=np.percentile(clean_rr, 60),  # Only peaks above 60th percentile
                                      distance=5)  # Minimum 5 samples between peaks
        
        print(f"Detected {len(peaks)} peaks")
        
        # Calculate time intervals between peaks (in seconds)
        peak_times = clean_time.iloc[peaks]
        peak_time_diffs = np.diff(peak_times).astype('timedelta64[s]').astype(float)
        
        # Filter out unrealistic breathing intervals (2-10 seconds)
        min_interval = 2
        max_interval = 10
        
        # Create arrays for valid intervals and corresponding times
        valid_mask = (peak_time_diffs >= min_interval) & (peak_time_diffs <= max_interval)
        valid_intervals = peak_time_diffs[valid_mask]
        
        # For each breathing rate, use the time of the second peak (end of the interval)
        # Skip the first peak since we need pairs for intervals
        valid_peak_indices = np.arange(1, len(peaks))[valid_mask]
        valid_times = clean_time_formatted.iloc[peaks[valid_peak_indices]]
        
        # Convert to breaths per minute
        valid_bpm = 60 / valid_intervals
        
        print(f"Valid breathing intervals: {len(valid_intervals)}")
        print(f"Filtered out: {len(peak_time_diffs) - len(valid_intervals)} intervals")
        print(f"Average breathing rate: {np.mean(valid_bpm):.1f} breaths/min")
        print(f"Range: {np.min(valid_bpm):.1f} - {np.max(valid_bpm):.1f} breaths/min")
        
        # Create output DataFrame
        output_df = pd.DataFrame({
            'time': valid_times.values,
            'bpm': np.round(valid_bpm, 1)
        })
        
        # Sort by time to ensure chronological order
        output_df = output_df.sort_values('time').reset_index(drop=True)
        
        # Save to CSV
        output_df.to_csv(output_csv_path, index=False)
        print(f"\nCSV file saved: {output_csv_path}")
        print(f"Records in output: {len(output_df)}")
        
        # Display first few rows
        print(f"\nFirst 10 rows of output:")
        print(output_df.head(10))
        
        return output_df
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        sys.exit(1)

def main():
    """Main function to run the analysis."""
    
    # Default input file name (can be modified or passed as argument)
    default_input = 'H10_log_20250611_2133.json'
    
    # Check if input file name is provided as command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = default_input
    
    # Check if output file name is provided as command line argument
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = 'breathing_rate_output.csv'
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    # Run the analysis
    result_df = analyze_breathing_rate(input_file, output_file)
    
    print("-" * 50)
    print("Analysis complete!")

if __name__ == "__main__":
    main()