import os
import wfdb
import neurokit2 as nk
import numpy as np
import pandas as pd
import tensorflow as tf

import neurokit2 as nk
from neurokit2 import ecg_peaks


def calculate_bpm(record) -> int:
    """
    Calculate the heart rate in beats per minute (BPM) from an ECG record.

    Parameters:
    - record (wfdb.Record): The ECG record.

    Returns:
    - int: Heart rate in BPM.
    """
    # Extract the ECG signal and sampling frequency
    ecg_signal = record.p_signal[:, 0]  # the leadI value is the same as portable ecg device and included with annotation     
    sampfreq = record.fs

    # Detect R-peaks using NeuroKit
    _, rpeaks = nk.ecg_peaks(ecg_signal, sampfreq)
    
    # Calculate the duration of the record
    duration_of_record = len(ecg_signal) / sampfreq
    
    # Calculate heart rate in BPM
    heart_rate = (len(rpeaks['ECG_R_Peaks']) * 60) / duration_of_record
    
    # Convert to integer since it is beat per minute 
    return int(heart_rate)


def segment_cardiac_epoch(bpm):

    """
    Segments a cardiac epoch based on the given heart rate (bpm).

    Parameters:
    - bpm (float): Heart rate in beats per minute.

    Returns:
    - Tuple(float, float): Start and end of the cardiac epoch.
    """
    # Validate input
    if bpm <= 0:
        raise ValueError("Heart rate (bpm) must be a positive value.")

    epoch_width = bpm / 60
    epoch_start = -0.3 / epoch_width
    epoch_end = 0.45 / epoch_width

    # Adjust for higher bpm:
    if bpm >= 90:
        c = 0.15
        epoch_start -= c
        epoch_end += c

    return epoch_start, epoch_end


def scan_with_slidingwindow(record, annotation, window_width):
    """
    Scan an ECG record with a sliding window and extract segments of data.

    Parameters:
    - record (wfdb.Record): The ECG record.
    - annotation (wfdb.Annotation): Annotation of the ECG record.
    - window_width (float): Width of the sliding window in seconds.

    Returns:
    - pd.DataFrame: DataFrame containing segments of ECG data and associated information.
    """
    ecg_signal = record.p_signal[:, 0]
    sampfreq = record.fs
    label = record.comments[0]
    parent_record = record.record_name

    # Initialize variables
    left_end = 0
    right_end = int(window_width * sampfreq)
    heart_rate = calculate_bpm(record)
    heart_cycle = heart_rate / 60
    window_step = int(heart_cycle * sampfreq)
 
    ecg_signals = []
    beat_annotations = []
    count_beat_annotations = []
    beat_annotated_points = []
    pac_percentages = []
    pvc_percentages = []

    while (left_end + right_end) <= len(ecg_signal):
        segment_signal = ecg_signal[left_end:right_end].round(4).tolist()
        ecg_signals.append(segment_signal)

        # Extract beat annotations within the window
        annotated_index = np.intersect1d(np.where(left_end <= annotation.sample),
                                         np.where(annotation.sample <= right_end))
        segment_beat_annotation = [annotation.symbol[i] for i in annotated_index]
        beat_annotations.append(segment_beat_annotation)

        # Count occurrences of each beat type
        symbol, count = np.unique(segment_beat_annotation, return_counts=True)
        segment_beat_annotation_count = dict(zip(symbol, count))
        count_beat_annotations.append(segment_beat_annotation_count)

        # Calculate percentages of PACs and PVCs in the window
        total_count = sum(segment_beat_annotation_count.values())
        pac_percentage = (segment_beat_annotation_count.get('A', 0) / total_count) * 100
        pac_percentages.append(pac_percentage)
        pvc_percentage = (segment_beat_annotation_count.get('V', 0) / total_count) * 100
        pvc_percentages.append(pvc_percentage)

        # Store annotated points
        segment_beat_annotated_pt = [annotation.sample[i] - left_end for i in annotated_index]
        beat_annotated_points.append(segment_beat_annotated_pt)

        # Move the window according to the presence of PACs or PVCs
        if (pac_percentage >= 20) and (pvc_percentage == 0):
            left_end = left_end + int(window_width * sampfreq)
        elif (pac_percentage == 0) and (pvc_percentage >= 20):
            left_end = left_end + int(window_width * sampfreq)
        else:
            left_end += window_step

        right_end = left_end + int(window_width * sampfreq)

    # Repeat parent_record and label for each segment
    parent_record_repeated = [parent_record] * len(ecg_signals)
    label_repeated = [label] * len(ecg_signals)
    heart_rate_repeated = [heart_rate] * len(ecg_signals)

    # Create the DataFrame
    data_within_window = pd.DataFrame({
        'parent_record': parent_record_repeated,
        'label': label_repeated,
        'avg_heart_rate': heart_rate_repeated,
        'signals': ecg_signals,
        'beat_annotation_symbols': beat_annotations,
        'annotated_samples': beat_annotated_points,
        'beat_occurrence': count_beat_annotations,
        'pac_percent': pac_percentages,
        'pvc_percent': pvc_percentages
    })

    print(f"There are {data_within_window.shape[0]} segments in the record")

    return data_within_window

                                                                                                                                                                                                                                                                       