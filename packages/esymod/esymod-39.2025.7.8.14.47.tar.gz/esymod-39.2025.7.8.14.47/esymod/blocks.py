#%%
import torch
from torch import nn
from . import Model, manipulators

class ResConv(Model):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, stride: int = 1,
                 stimuli=nn.Hardswish):
        """
        conv block with res connection
        :param in_channels:
        :param out_channels:
        :param kernel_size:
        :param stride:
        """

        super().__init__()
        if isinstance(kernel_size, int):
            padding = kernel_size // 2
        else:
            padding = [k // 2 for k in kernel_size]
        self.res_conv = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=stride ** 2)
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride,
                      padding=padding),
            stimuli()
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=out_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride,
                      padding=padding),
            stimuli()
        )

    def get_output(self, x: torch.Tensor) -> torch.Tensor:
        direct = self.conv2(self.conv1(x))
        res = self.res_conv(x)
        return res + direct


class ResTConv(Model):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, stride: int = 1,
                 stimuli=nn.Hardswish):
        """
        conv block with res connection
        :param in_channels:
        :param out_channels:
        :param kernel_size:
        :param stride:
        """

        super().__init__()
        self.res_conv = nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1,
                                           stride=stride ** 2)
        self.conv1 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size,
                               stride=stride,
                               padding=kernel_size // 2),
            stimuli()
        )
        self.conv2 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=out_channels, out_channels=out_channels, kernel_size=kernel_size,
                               stride=stride,
                               padding=kernel_size // 2),
            stimuli()
        )

    def get_output(self, x: torch.Tensor) -> torch.Tensor:
        direct = self.conv2(self.conv1(x))
        res = self.res_conv(x)
        return res + direct

class MultiplyLayer(manipulators.Multiply):
    def __init__(self, input_dim, output_dim, bias=True):
        route1 = nn.Linear(input_dim, output_dim, bias=bias)
        route2 = nn.Linear(input_dim, output_dim, bias=bias)
        super().__init__(route1, route2)

class FullConnectedLayer(torch.nn.Sequential):
    def __init__(self, input_dim, output_dim, bias=True, stimuli=nn.Hardswish()):
        super().__init__(
            nn.Linear(input_dim, output_dim, bias=bias),
            stimuli
        )


class SparseLinear(torch.nn.Module):
    
    def __init__(self, in_features, out_features, stimuli=torch.nn.ReLU):
        super(SparseLinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = torch.nn.Parameter(torch.rand(out_features, in_features))
        self.bias = torch.nn.Parameter(torch.rand(out_features))
        self.stimuli = stimuli()
    
    def forward(self, din: torch.Tensor):
        x = din.to_sparse()
        
        indicies = x.indices()
        values = x.values()
        
        used_weights = self.weight.T
        used_weights = self.weight.unsqueeze(0).expand(x.size(0), -1, -1)
        used_weights = used_weights[indicies[0], indicies[1]]   
        
        used_bias = self.bias
        used_bias = used_bias.unsqueeze(0).expand(x.size(0), -1)
        used_bias = used_bias[indicies[0], indicies[1]]
        
        biased_values = values + used_bias
        
        r_values = (biased_values.unsqueeze(-1).expand(used_weights.size())*used_weights)
        
        batch_sum_r = torch.zeros(x.size(0), self.out_features).to(x.device)
        batch_sum_r = batch_sum_r.index_add(0, indicies[0], r_values)
        
        r = self.stimuli(batch_sum_r)
        return r
        

        
class VAE(Model):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        
    def get_output(self, x):
        mu, log_var = self.encoder(x).chunk(2, dim=1)
        z = mu + torch.randn_like(mu) * torch.exp(log_var / 2)
        self.mu = mu
        self.log_var = log_var
        self.din = x
        return self.decoder(z)
    
class unsqueeze(torch.nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim
    
    def get_output(self, x: torch.Tensor):
        return x.unsqueeze(self.dim)
    
class squeeze(torch.nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim
    
    def get_output(self, x: torch.Tensor):
        return x.squeeze(self.dim)
#%%