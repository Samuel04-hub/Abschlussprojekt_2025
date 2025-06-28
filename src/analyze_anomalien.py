import wfdb
import pandas as pd
from collections import Counter

def analyze_ecg_anomalies(record_name='208', data_dir='mitdb/1.0.0'):
    """
    Analyzes ECG data from MIT-BIH dataset for anomalies based on annotations.
    Returns signal data, annotations, and anomaly summary.
    """
    # Load the record and annotations
    record = wfdb.rdrecord(record_name, sampfrom=0, sampto=None, physical=True, channels=[0, 1], pn_dir=data_dir)
    annotation = wfdb.rdann(record_name, 'atr', sampfrom=0, sampto=None, pn_dir=data_dir)
    
    # Extract signals and time vector
    signals = record.p_signal  # Shape: (samples, channels)
    fs = record.fs  # Sampling frequency (360 Hz for MIT-BIH)
    time = [i / fs for i in range(len(signals))]
    
    # Extract annotations
    sample_indices = annotation.sample  # Sample indices of annotated beats
    symbols = annotation.symbol  # Annotation symbols (e.g., N, V, S, F)
    
    # Map annotation symbols to descriptions
    annotation_map = {
        'N': 'Normal beat',
        'V': 'Ventricular ectopic beat (VEB)',
        'S': 'Supraventricular ectopic beat (SVEB)',
        'F': 'Fusion beat',
        '/': 'Paced beat',
        'Q': 'Unclassifiable beat',
        '|': 'Missed beat'
    }
    
    # Summarize anomalies
    anomaly_counts = Counter(symbols)
    anomaly_summary = {
        symbol: {'count': count, 'description': annotation_map.get(symbol, 'Unknown'), 'times': []}
        for symbol, count in anomaly_counts.items()
        if symbol != 'N'  # Exclude normal beats from anomalies
    }
    
    # Collect time points for each anomaly
    for sample, symbol in zip(sample_indices, symbols):
        if symbol != 'N':
            time_sec = sample / fs
            anomaly_summary[symbol]['times'].append(time_sec)
    
    # Prepare data for visualization
    signal_df = pd.DataFrame({
        'Time (s)': time,
        'MLII (mV)': signals[:, 0],
        'V1 (mV)': signals[:, 1]
    })
    
    annotation_df = pd.DataFrame({
        'Sample': sample_indices,
        'Time (s)': [s / fs for s in sample_indices],
        'Symbol': symbols,
        'Description': [annotation_map.get(s, 'Unknown') for s in symbols]
    })
    
    return signal_df, annotation_df, anomaly_summary

if __name__ == '__main__':
    # Example usage
    signal_df, annotation_df, anomaly_summary = analyze_ecg_anomalies('208')
    print("Anomaly Summary:")
    for symbol, info in anomaly_summary.items():
        print(f"{symbol} ({info['description']}): {info['count']} occurrences at times {info['times'][:5]}...")
    print("\nFirst few rows of signal data:")
    print(signal_df.head())
    print("\nFirst few annotations:")
    print(annotation_df.head())