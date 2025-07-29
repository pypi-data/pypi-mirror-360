import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-8):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def _norm(self, x):
        return x * torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)

    def forward(self, x):
        output = self._norm(x.float()).type_as(x)
        return output * self.weight

class RotaryEmbedding(nn.Module):
    def __init__(self, dim):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        
    def forward(self, x):
        seq_len = x.shape[-2]
        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        cos = emb.cos()[None, None, :, :]
        sin = emb.sin()[None, None, :, :]
        x1 = x[..., ::2]
        x2 = x[..., 1::2]
        x_rot = torch.stack((-x2, x1), dim=-1).flatten(-2)
        return x * cos + x_rot * sin

class Retention(nn.Module):
    def __init__(self, embed_dim, heads, dropout=0.1):
        super().__init__()
        self.heads = heads
        self.head_dim = embed_dim // heads
        self.scale = math.sqrt(self.head_dim)
        self.w_q = nn.Linear(embed_dim, embed_dim)
        self.w_k = nn.Linear(embed_dim, embed_dim)
        self.w_v = nn.Linear(embed_dim, embed_dim)
        self.gate = nn.Linear(embed_dim, embed_dim)
        self.gamma_param = nn.Parameter(torch.randn(heads))
        self.dropout = nn.Dropout(dropout)
        self.rotary = RotaryEmbedding(self.head_dim)

    def forward(self, x):
        B, T, _ = x.shape
        Q = self.w_q(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)
        K = self.w_k(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)
        V = self.w_v(x).view(B, T, self.heads, self.head_dim).transpose(1, 2)

        Q = self.rotary(Q)
        K = self.rotary(K)

        gamma = torch.sigmoid(self.gamma_param)
        idx = torch.arange(T, device=x.device)
        diff = (idx.unsqueeze(1) - idx.unsqueeze(0)).clamp(min=0)
        t_w = torch.exp(-gamma.view(self.heads, 1, 1) * diff)
        
        scores = torch.matmul(Q, K.transpose(-1, -2)) / self.scale
        weighted_scores = scores * t_w.unsqueeze(0)
        out = torch.matmul(weighted_scores, V)

        out = out.transpose(1, 2).reshape(B, T, -1)
        out = self.dropout(F.silu(self.gate(x)) * out)
        return out

class DillNetBlock(nn.Module):
    def __init__(self, embed_dim, heads, ffn_dim=None, dropout=0.1):
        super().__init__()
        if ffn_dim is None:
            ffn_dim = embed_dim * 4
        
        self.norm1 = RMSNorm(embed_dim)
        self.attention_layer = Retention(embed_dim, heads, dropout)
        self.norm2 = RMSNorm(embed_dim)
        
        self.w1 = nn.Linear(embed_dim, ffn_dim)
        self.w2 = nn.Linear(embed_dim, ffn_dim)
        self.w3 = nn.Linear(ffn_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = x + self.attention_layer(self.norm1(x))
        normed_x = self.norm2(x)
        ffn_out = self.w3(F.silu(self.w1(normed_x)) * self.w2(normed_x))
        x = x + self.dropout(ffn_out)
        return x

class DillNet(nn.Module):
    def __init__(self, embed_dim, depth, heads=8, ffn_dim=None):
        super().__init__()
        self.blocks = nn.ModuleList([
            DillNetBlock(embed_dim, heads, ffn_dim=ffn_dim, dropout=0.1)
            for _ in range(depth)
        ])
        self.final_norm = RMSNorm(embed_dim)

    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        return self.final_norm(x)