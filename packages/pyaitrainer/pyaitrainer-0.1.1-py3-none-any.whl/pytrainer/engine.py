import torch
import torch.nn.functional as F
from .tokenizer.char_tokenizer import CharTokenizer
from .model.transformer import Transformer
from .config import *

class PyTrainerEngine:
    def __init__(self):
        self.model_path = None
        self.model_type = None
        self._prompt = ""
        self._response = ""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            with open("pytrainer/data/your_dataset.txt", "r", encoding="utf-8") as f:
                raw_text = f.read()
        except FileNotFoundError:
            raw_text = "User must provide dataset at pytrainer/data/your_dataset.txt"

        self.tokenizer = CharTokenizer(raw_text)

    @property
    def model(self):
        return self.model_path

    @model.setter
    def model(self, path):
        self.model_path = path
        self._load_model()

    @property
    def type(self):
        return self.model_type

    @type.setter
    def type(self, t):
        self.model_type = t

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self, value):
        self._prompt = value
        self._generate()

    @property
    def response(self):
        return self._response

    def _load_model(self):
        VOCAB_SIZE = len(self.tokenizer.vocab)
        model = Transformer(VOCAB_SIZE, embed_dim, num_heads, num_layers, seq_len).to(self.device)
        model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        model.eval()
        self._model = model

    def _generate(self):
        if self.model_type != "TextGen":
            self._response = "Only TextGen is supported currently."
            return

        input_ids = self.tokenizer.encode(self._prompt)
        if len(input_ids) > seq_len:
            input_ids = input_ids[:seq_len]

        input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)

        with torch.no_grad():
            for _ in range(100):
                out = self._model(input_tensor)
                logits = out[0, -1] / 0.8
                probs = F.softmax(logits, dim=-1)
                next_id = torch.multinomial(probs, num_samples=1).item()
                input_tensor = torch.cat([input_tensor, torch.tensor([[next_id]], device=self.device)], dim=1)
                if input_tensor.size(1) > seq_len:
                    input_tensor = input_tensor[:, -seq_len:]

        self._response = self.tokenizer.decode(input_tensor[0].tolist())

engine = PyTrainerEngine()
