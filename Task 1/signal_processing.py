import matplotlib.pyplot as plt

def read_signal(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    n = int(lines[0].strip())

    indices = []
    samples = []

    for i in range(1, n + 1):
        index, value = lines[i].split()
        indices.append(int(index))
        samples.append(float(value))

    return indices, samples


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