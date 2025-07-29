import torch
import torch.nn as nn
import torch.optim as optim
from .config import *
from .tokenizer.char_tokenizer import CharTokenizer
from .model.transformer import Transformer
from .utils import get_batch

def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    with open("pytrainer/data/your_dataset.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    tokenizer = CharTokenizer(raw_text)
    encoded_data = tokenizer.encode(raw_text)

    if len(encoded_data) < seq_len + 2:
        raise ValueError("Dataset too small.")

    vocab_size = len(tokenizer.vocab)
    model = Transformer(vocab_size, embed_dim, num_heads, num_layers, seq_len).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    batch_gen = get_batch(encoded_data, batch_size, seq_len)

    for epoch in range(epochs):
        total_loss = 0
        for _ in range(100):
            x, y = next(batch_gen)
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits.view(-1, vocab_size), y.view(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}: Loss {total_loss / 100:.4f}")

    torch.save(model.state_dict(), "model.pth")
    print("Model saved as model.pth")
