# Breathing Rate Analysis

A Python script that analyzes heart rate variability (HRV) data to extract breathing patterns and calculate breathing rates using respiratory sinus arrhythmia detection.

## Overview

This script processes heart rate monitor data (specifically Polar H10 format) to estimate breathing rates by analyzing RR interval variations. The breathing rate is derived from heart rate variability patterns, as breathing naturally modulates heart rate through the autonomic nervous system.

## Features

- **HRV-based breathing detection**: Uses peak detection in RR intervals to identify breathing patterns
- **Automatic filtering**: Removes unrealistic breathing intervals (outside 2-10 seconds)
- **Timezone conversion**: Converts UTC timestamps to PDT (Pacific Daylight Time)
- **CSV export**: Generates clean CSV output with time and breathing rate
- **Progress reporting**: Shows analysis statistics during processing

## Requirements

### Python Dependencies

```bash
pip install pandas numpy scipy
```

### Input Data Format

The script expects JSON files with the following structure:

```json
[
  {
    "ts": 1749699660.0082998,
    "hr": 76,
    "rr": [791]
  },
  {
    "ts": 1749699661.988418,
    "hr": 77,
    "rr": [751, 747]
  }
]
```

Where:

- `ts`: Unix timestamp (seconds)
- `hr`: Heart rate (beats per minute)
- `rr`: Array of RR intervals (milliseconds between heartbeats)

## Usage

### Basic Usage

```bash
python breathing_analyzer.py
```

This will process the default file `H10_log_20250611_2133.json` and create `breathing_rate_output.csv`.

### Custom Input/Output Files

```bash
python breathing_analyzer.py input_file.json output_file.csv
```

### Command Line Arguments

- **Argument 1** (optional): Input JSON file path
- **Argument 2** (optional): Output CSV file path

## Output Format

The script generates a CSV file with two columns:

| Column | Format            | Description                          |
| ------ | ----------------- | ------------------------------------ |
| `time` | HH:MM:SS          | Time in PDT timezone                 |
| `bpm`  | Float (1 decimal) | Breathing rate in breaths per minute |

### Example Output

```csv
time,bpm
21:33:15,12.5
21:33:22,14.3
21:33:28,13.8
21:33:35,15.2
```

## Methodology

### 1. Data Preprocessing

- Loads JSON heart rate data
- Calculates mean RR intervals for each timestamp
- Converts timestamps to PDT timezone

### 2. Peak Detection

- Applies peak detection algorithm to RR interval signal
- Uses 60th percentile height threshold
- Maintains minimum distance of 5 samples between peaks

### 3. Breathing Rate Calculation

- Calculates time intervals between detected peaks
- Filters intervals to realistic breathing range (2-10 seconds)
- Converts intervals to breaths per minute (60 / interval_seconds)

### 4. Output Generation

- Associates breathing rates with corresponding timestamps
- Rounds breathing rates to 1 decimal place
- Exports to CSV format

## Algorithm Parameters

| Parameter              | Value           | Description                          |
| ---------------------- | --------------- | ------------------------------------ |
| Height threshold       | 60th percentile | Minimum peak height for detection    |
| Peak distance          | 5 samples       | Minimum samples between peaks        |
| Min breathing interval | 2 seconds       | Fastest realistic breathing (30 BPM) |
| Max breathing interval | 10 seconds      | Slowest realistic breathing (6 BPM)  |

## Example Statistics Output

```
Loaded data with 3120 records
Time range: 20:41:00 to 21:32:59
Clean data points: 3089
Detected 847 peaks
Valid breathing intervals: 623
Filtered out: 224 intervals
Average breathing rate: 14.2 breaths/min
Range: 6.0 - 30.0 breaths/min

CSV file saved: breathing_rate_output.csv
Records in output: 623
```

## Technical Notes

### Respiratory Sinus Arrhythmia (RSA)

The analysis relies on RSA, a natural phenomenon where:

- Heart rate increases during inspiration
- Heart rate decreases during expiration
- This creates detectable patterns in RR interval data

### Peak Detection Algorithm

Uses `scipy.signal.find_peaks` with:

- Dynamic height threshold based on data distribution
- Distance constraint to prevent over-detection
- Robust filtering for physiologically plausible breathing rates

### Data Quality

The script automatically handles:

- Missing or invalid RR intervals
- Timezone conversion from UTC to PDT
- Outlier filtering for unrealistic breathing rates

## Troubleshooting

### Common Issues

**Error: 'rr_mean' not found**

- Ensure input JSON has `rr` arrays, not `rr_mean` values
- Script automatically calculates means from RR arrays

**Error: Input file not found**

- Check file path and name
- Ensure JSON file is in the correct location

**Empty output CSV**

- Check if RR interval data is valid
- Verify peak detection parameters are appropriate for your data

**Low breathing rate detection**

- May indicate poor signal quality
- Consider adjusting peak detection parameters

### Performance Notes

- Processing time scales with data size
- Memory usage is proportional to number of records
- Typical processing: ~1000 records per second

## Data Sources

This script is designed for:

- **Polar H10** heart rate monitor data
- **ANT+ / Bluetooth HRM** devices with RR interval recording
- Any heart rate data with millisecond-precision RR intervals

## Scientific Background

The breathing rate estimation is based on established physiological principles:

1. **Autonomic modulation**: Breathing affects heart rate through parasympathetic/sympathetic balance
2. **Frequency analysis**: Breathing patterns create detectable oscillations in heart rate
3. **Peak detection**: Local maxima in RR intervals often correspond to respiratory cycles

## Limitations

- Accuracy depends on signal quality and individual physiology
- May be less accurate during exercise or irregular breathing
- Requires consistent heart rate monitor contact
- Not suitable for medical diagnosis
