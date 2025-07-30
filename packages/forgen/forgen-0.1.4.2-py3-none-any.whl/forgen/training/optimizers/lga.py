import torch
import torch.nn as nn
from collections import defaultdict

class LearnableGradientAccumulator(nn.Module):
    def __init__(self, model, mode='global', clamp_values=None, selective_mask=None):
        super().__init__()
        self.model = model
        self.mode = mode.lower()
        self.clamp_values = clamp_values  # (min_val, max_val)
        self.selective_mask = selective_mask or {}

        self.a = nn.ParameterDict()
        self.b = nn.ParameterDict()
        self.accum_grads = {}

        if self.mode == 'global':
            self.a['global'] = nn.Parameter(torch.tensor(1.0))
            self.b['global'] = nn.Parameter(torch.tensor(0.0))
        elif self.mode == 'per_layer':
            for name, _ in model.named_parameters():
                layer_name = name.split('.')[0]
                if layer_name not in self.a:
                    self.a[layer_name] = nn.Parameter(torch.tensor(1.0))
                    self.b[layer_name] = nn.Parameter(torch.tensor(0.0))
        elif self.mode == 'per_param':
            for name, param in model.named_parameters():
                self.a[name] = nn.Parameter(torch.ones_like(param))
                self.b[name] = nn.Parameter(torch.zeros_like(param))
        else:
            raise ValueError("mode must be one of: 'global', 'per_layer', 'per_param'")

        for name, param in model.named_parameters():
            self.register_buffer(f'accum_{name}', torch.zeros_like(param))
            self.accum_grads[name] = getattr(self, f'accum_{name}')

    def accumulate(self):
        for name, param in self.model.named_parameters():
            if param.grad is None or name not in self.accum_grads:
                continue

            # Skip if selective masking excludes this param
            if name in self.selective_mask and not self.selective_mask[name]:
                self.accum_grads[name] += param.grad.detach()
                continue

            with torch.no_grad():
                if self.mode == 'global':
                    a = self.a['global']
                    b = self.b['global']
                elif self.mode == 'per_layer':
                    layer = name.split('.')[0]
                    a = self.a[layer]
                    b = self.b[layer]
                elif self.mode == 'per_param':
                    a = self.a[name]
                    b = self.b[name]
                    if self.clamp_values:
                        min_val, max_val = self.clamp_values
                        a.clamp_(min_val, max_val)
                        b.clamp_(min_val, max_val)

                transformed = a * param.grad + b
                self.accum_grads[name] += transformed.detach()

    def apply(self, optimizer):
        for name, param in self.model.named_parameters():
            if name in self.accum_grads:
                param.grad = self.accum_grads[name]
        optimizer.step()
        optimizer.zero_grad()
        self._clear()

    def _clear(self):
        for buffer in self.accum_grads.values():
            buffer.zero_()

    def lga_parameters(self):
        return self.parameters()

    def state_dict(self, destination=None, prefix='', keep_vars=False):
        state = super().state_dict(destination, prefix, keep_vars)
        return state

    def load_state_dict(self, state_dict, strict=True):
        super().load_state_dict(state_dict, strict)

    def log_state(self, top_k=5):
        print("=== LGA Parameters Snapshot ===")
        if self.mode == 'global':
            print(f"a: {self.a['global'].item():.4f}, b: {self.b['global'].item():.4f}")
        else:
            items = self.a.items() if self.mode == 'per_layer' else list(self.a.items())[:top_k]
            for k, v in items:
                a_val = v.data.mean().item() if v.ndim > 0 else v.item()
                b_val = self.b[k].data.mean().item() if self.b[k].ndim > 0 else self.b[k].item()
                print(f"{k}: a={a_val:.4f}, b={b_val:.4f}")
        print("================================")
