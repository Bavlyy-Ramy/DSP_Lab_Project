import matplotlib.pyplot as plt
import math

def read_signal(filename):
    """Read supported DSP signal text formats.

    Supported formats:
    1) Task 1: first line is the sample count, followed by index/value pairs.
    2) Quantization test format 1: index/value pairs only.
    3) Quantization test format 2: three one-value header lines, then pairs;
       the third header value is the number of samples.
    """
    with open(filename, "r", encoding="utf-8-sig") as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        raise ValueError("The signal file is empty.")

    tokenized = [line.split() for line in lines]

    def parse_pairs(pair_lines):
        indices, samples = [], []
        for line_number, tokens in enumerate(pair_lines, start=1):
            if len(tokens) != 2:
                raise ValueError(f"Invalid signal data at data line {line_number}: expected index and sample value.")
            indices.append(int(tokens[0]))
            samples.append(float(tokens[1]))
        if not samples:
            raise ValueError("The signal file contains no samples.")
        return indices, samples

    # Format 2: three scalar header lines; third value is sample count.
    if (len(tokenized) >= 4
            and all(len(tokens) == 1 for tokens in tokenized[:3])
            and tokenized[2][0].lstrip("+-").isdigit()):
        declared_count = int(tokenized[2][0])
        remaining = tokenized[3:]
        if declared_count == len(remaining) and all(len(row) == 2 for row in remaining):
            return parse_pairs(remaining)

    # Task 1 format: one sample-count header followed by that many pairs.
    if len(tokenized[0]) == 1 and tokenized[0][0].lstrip("+-").isdigit():
        declared_count = int(tokenized[0][0])
        remaining = tokenized[1:]
        if declared_count == len(remaining) and all(len(row) == 2 for row in remaining):
            return parse_pairs(remaining)

    # Pair-only format used by Quantization Test Case 1.
    if all(len(row) == 2 for row in tokenized):
        return parse_pairs(tokenized)

    raise ValueError("Unrecognized signal file format. Expected sample index/value pairs, optionally preceded by a supported header.")

def add_signals(*signals):
    result_dict = {}

    for signal in signals:
        indices, samples = signal

        for index, sample in zip(indices, samples):
            if index in result_dict:
                result_dict[index] += sample
            else:
                result_dict[index] = sample

    result_indices = sorted(result_dict.keys())

    result_samples = []

    for index in result_indices:
        result_samples.append(result_dict[index])

    return result_indices, result_samples

def plot_signal(indices, samples, title="Signal"):
    plt.figure(figsize=(8, 5))
    plt.stem(indices, samples)
    plt.xlabel("n")
    plt.ylabel("x[n]")
    plt.title(title)
    plt.grid(True)
    plt.show()

def multiply_signal(signal, constant):
    indices, samples = signal

    result_samples = []

    for sample in samples:
        result_samples.append(sample * constant)

    return indices.copy(), result_samples

def subtract_signals(signal1, signal2):
    negative_signal2 = multiply_signal(signal2, -1)
    result = add_signals(signal1, negative_signal2)

    return result

def shift_signal(signal, shift):
    indices, samples = signal

    new_indices = []

    for index in indices:
        new_indices.append(index - shift)

    return new_indices, samples.copy()

def fold_signal(signal):
    indices, samples = signal

    folded = []

    for index, sample in zip(indices, samples):
        folded.append((-index, sample))

    folded.sort(key=lambda pair: pair[0])

    new_indices = []
    new_samples = []

    for index, sample in folded:
        new_indices.append(index)
        new_samples.append(sample)

    return new_indices, new_samples

def generate_sine_signal(amplitude, phase, analog_frequency,sampling_frequency, num_samples=100):

    if not all(math.isfinite(v) for v in (amplitude, phase, analog_frequency, sampling_frequency)):
        raise ValueError("All parameters must be finite numbers.")

    if analog_frequency < 0:
        raise ValueError("Analog frequency cannot be negative.")

    if sampling_frequency <= 0:
        raise ValueError("Sampling frequency must be positive.")

    if sampling_frequency <= 2 * analog_frequency:
        raise ValueError(
            "Sampling frequency must be greater than "
            "twice the analog frequency."
        )

    if not isinstance(num_samples, int) or isinstance(num_samples, bool) or num_samples <= 0:
        raise ValueError("Number of samples must be a positive integer.")

    indices = []
    samples = []

    for n in range(num_samples):
        value = amplitude * math.sin(
            2 * math.pi * analog_frequency / sampling_frequency * n
            + phase
        )

        indices.append(n)
        samples.append(value)

    return indices, samples

def generate_cosine_signal(amplitude, phase, analog_frequency,sampling_frequency, num_samples=100):
    if not all(math.isfinite(v) for v in (
        amplitude, phase, analog_frequency, sampling_frequency
    )):
        raise ValueError("All parameters must be finite numbers.")

    if analog_frequency < 0:
        raise ValueError("Analog frequency cannot be negative.")

    if sampling_frequency <= 0:
        raise ValueError("Sampling frequency must be positive.")

    if sampling_frequency <= 2 * analog_frequency:
        raise ValueError(
            "Sampling frequency must be greater than "
            "twice the analog frequency."
        )

    if not isinstance(num_samples, int) or isinstance(num_samples, bool) or num_samples <= 0:
        raise ValueError("Number of samples must be a positive integer.")

    indices = []
    samples = []

    for n in range(num_samples):
        value = amplitude * math.cos(
            2 * math.pi * analog_frequency / sampling_frequency * n
            + phase
        )

        indices.append(n)
        samples.append(value)

    return indices, samples

def quantize_signal(signal, levels):
    """Uniform mid-rise quantization.

    Returns: sample indices, quantized values, 1-based interval indices,
    zero-based integer codes, encoded binary strings, errors (quantized-original),
    and quantization step size.
    """
    indices, samples = signal

    if not isinstance(levels, int) or isinstance(levels, bool) or levels < 2:
        raise ValueError("Number of quantization levels must be an integer of at least 2.")
    if len(indices) != len(samples):
        raise ValueError("Signal indices and samples must have the same length.")
    if not samples:
        raise ValueError("Cannot quantize an empty signal.")
    if not all(math.isfinite(value) for value in samples):
        raise ValueError("Signal samples must all be finite numbers.")

    minimum = min(samples)
    maximum = max(samples)
    bit_width = max(1, math.ceil(math.log2(levels)))

    if math.isclose(minimum, maximum, rel_tol=0.0, abs_tol=1e-15):
        count = len(samples)
        return (indices.copy(), samples.copy(), [1] * count, [0] * count,
                [format(0, f"0{bit_width}b")] * count, [0.0] * count, 0.0)

    step_size = (maximum - minimum) / levels
    quantized_samples = []
    interval_indices = []
    integer_codes = []
    encoded_values = []
    errors = []

    for sample in samples:
        # Zero-based code identifies the interval; clamp the maximum endpoint.
        code = int((sample - minimum) / step_size)
        code = max(0, min(levels - 1, code))

        # Representative amplitude is the midpoint of the selected interval.
        quantized = minimum + (code + 0.5) * step_size

        quantized_samples.append(quantized)
        interval_indices.append(code + 1)  # Test-case interval numbering starts at 1.
        integer_codes.append(code)
        encoded_values.append(format(code, f"0{bit_width}b"))
        errors.append(quantized - sample)  # Required test-case sign: quantized - original.

    return (indices.copy(), quantized_samples, interval_indices,
            integer_codes, encoded_values, errors, step_size)



# ============================================================
# TASK 5 - MOVING AVERAGE, DERIVATIVES, AND CONVOLUTION
# ============================================================

def moving_average(signal, window_size):
    """Calculate a trailing moving average using complete windows only.

    The output index starts at the input signal's first index and advances
    by one for each complete window. Output length is N - window_size + 1.
    """
    indices, samples = signal
    if len(indices) != len(samples):
        raise ValueError("Signal indices and samples must have the same length.")
    if not isinstance(window_size, int) or isinstance(window_size, bool) or window_size <= 0:
        raise ValueError("Window size must be a positive integer.")
    if window_size > len(samples):
        raise ValueError("Window size cannot be greater than the number of samples.")

    result_indices = []
    result_samples = []
    for start in range(len(samples) - window_size + 1):
        window = samples[start:start + window_size]
        result_indices.append(indices[start])
        result_samples.append(sum(window) / window_size)
    return result_indices, result_samples


def first_derivative(signal):
    """Calculate the first forward difference x[n+1] - x[n]."""
    indices, samples = signal
    if len(indices) != len(samples):
        raise ValueError("Signal indices and samples must have the same length.")
    if len(samples) < 2:
        raise ValueError("At least two samples are required for the first derivative.")

    result_indices = indices[:-1].copy()
    result_samples = [
        samples[i + 1] - samples[i]
        for i in range(len(samples) - 1)
    ]
    return result_indices, result_samples


def second_derivative(signal):
    """Calculate the second forward difference x[n+2] - 2*x[n+1] + x[n]."""
    indices, samples = signal
    if len(indices) != len(samples):
        raise ValueError("Signal indices and samples must have the same length.")
    if len(samples) < 3:
        raise ValueError("At least three samples are required for the second derivative.")

    result_indices = indices[:-2].copy()
    result_samples = [
        samples[i + 2] - 2 * samples[i + 1] + samples[i]
        for i in range(len(samples) - 2)
    ]
    return result_indices, result_samples


def convolve_signals(signal1, signal2):
    """Perform full linear convolution and preserve the summed index origin."""
    indices1, samples1 = signal1
    indices2, samples2 = signal2
    if len(indices1) != len(samples1) or len(indices2) != len(samples2):
        raise ValueError("Each signal's indices and samples must have the same length.")
    if not samples1 or not samples2:
        raise ValueError("Cannot convolve an empty signal.")

    output = [0.0] * (len(samples1) + len(samples2) - 1)
    for i, value1 in enumerate(samples1):
        for j, value2 in enumerate(samples2):
            output[i + j] += value1 * value2

    start_index = indices1[0] + indices2[0]
    output_indices = list(range(start_index, start_index + len(output)))
    return output_indices, output


def compare_signals(actual_signal, expected_signal, tolerance=1e-3):
    """Compare two (indices, samples) signals, returning True when they match."""
    actual_indices, actual_samples = actual_signal
    expected_indices, expected_samples = expected_signal

    if actual_indices != expected_indices or len(actual_samples) != len(expected_samples):
        return False
    return all(
        math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tolerance)
        for actual, expected in zip(actual_samples, expected_samples)
    )


# Backward-friendly singular alias for lab test harnesses that use this name.
compare_signal = compare_signals
