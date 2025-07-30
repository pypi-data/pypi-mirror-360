import torch.nn.functional as F
import torch
import numpy as np  

def gaussian_kernel1d(kernel_size: int, sigma: float):
    """
    Returns a 1D Gaussian kernel.
    """
    # Create a tensor with evenly spaced values centered at 0
    x = torch.linspace(-(kernel_size // 2), kernel_size // 2, kernel_size)
    # Calculate the Gaussian function
    kernel = torch.exp(-(x**2) / (2 * sigma**2))
    # Normalize the kernel to ensure the sum of all elements is 1
    kernel = kernel / kernel.sum()
    return kernel


def gaussian_smooth(tensor, kernel_size: int, sigma: float):
    """
    Apply Gaussian smoothing on the time dimension (first dimension) of the input tensor.

    Args:
    - tensor (torch.Tensor): Input tensor of shape (T, C, H, W) where T is the time dimension.
    - kernel_size (int): Size of the Gaussian kernel.
    - sigma (float): Standard deviation of the Gaussian kernel.

    Returns:
    - smoothed_tensor (torch.Tensor): Smoothed tensor.
    """
    if isinstance(tensor, np.ndarray):
        tensor = torch.from_numpy(tensor) 
    # Get the Gaussian kernel
    kernel = gaussian_kernel1d(kernel_size, sigma).to(tensor.device).view(1, 1, -1)

    # Prepare the tensor for convolution: (B, C, T) where B = C*H*W, C=1, T=102
    T, C, H, W = tensor.shape
    tensor = tensor.view(T, -1).permute(1, 0).unsqueeze(1)  # Shape: (C*H*W, 1, T)

    # Apply convolution
    padding = kernel_size // 2
    smoothed = F.conv1d(tensor, kernel, padding=padding, groups=1)

    # Reshape back to original shape
    smoothed = smoothed.squeeze(1).permute(1, 0).view(T, C, H, W)

    return smoothed