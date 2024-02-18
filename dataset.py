def split_training_validation_data(data: list, ratio: float) -> tuple[list, list]:
    split_index = int(len(data) * ratio)
    return data[:split_index], data[split_index:]
