import torch
import random

def get_batch(data, batch_size, seq_len):
    data_len = len(data)
    while True:
        x_batch = []
        y_batch = []
        for _ in range(batch_size):
            start_idx = random.randint(0, data_len - seq_len - 2)
            x = data[start_idx:start_idx+seq_len]
            y = data[start_idx+1:start_idx+1+seq_len]
            x_batch.append(x)
            y_batch.append(y)
        yield torch.tensor(x_batch), torch.tensor(y_batch)
