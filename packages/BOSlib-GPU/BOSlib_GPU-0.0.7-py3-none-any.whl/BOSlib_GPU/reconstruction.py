import numpy as np
from tqdm import tqdm
import torch      
from .reconstruction_utils import ART_torch  
from tqdm.contrib import tzip


def abel_transform_GPU(angle: np.ndarray, center: int, winy0: int, winy1: int, winx0: int, winx1: int, device, batch_size=100) -> np.ndarray:
    """
    Perform the Abel transform using PyTorch tensors with GPU parallelization and memory optimization.

    Parameters
    ----------
    angle : np.ndarray
        A 2D numpy array representing refractive angles for each pixel.
    center : int
        The index along the y-axis corresponding to the central axis of the transform.
    winy0 : int
        The starting index along the y-axis for the region used to calculate the background mean.
    winy1 : int
        The ending index along the y-axis for the region used to calculate the background mean.
    winx0 : int
        The starting index along the x-axis for the region used to calculate the background mean.
    winx1 : int
        The ending index along the x-axis for the region used to calculate the background mean.
    device : torch.device
        Device to use for computation (e.g., 'cuda' or 'cpu').
    batch_size : int
        Number of radii (`r`) to process simultaneously for memory optimization.

    Returns
    -------
    np.ndarray
        A 2D array of refractive index differences derived from the Abel transform.
    """
    # Convert angle to a torch tensor and move to GPU
    angle = torch.tensor(angle, dtype=torch.float32, device=device)
    
    # Offset the angle values by subtracting the mean value at the reference x-coordinate
    mean_value = torch.mean(angle[winy0:winy1, winx0:winx1])
    angle = angle - mean_value
    
    # Remove values below the center since they are not used in the calculation
    angle = angle[:center, :]
    
    # Reverse the angle array so that the upper end becomes the central axis
    angle = angle.flip(dims=[0])
    
    # Calculate the distance from the central axis (η)
    eta = torch.arange(angle.shape[0], dtype=torch.float32, device=device)
    eta_squared = eta**2  # Precompute 

    # Compute r² for all radii
    r = torch.arange(center, dtype=torch.float32, device=device)
    r_squared = r**2  # Precompute r²

    # Initialize an empty tensor to store the results
    ans = torch.zeros((center, angle.shape[1]), dtype=torch.float32, device=device)

    # Process in batches to save memory
    for start in tqdm(range(0, center, batch_size), desc="Processing batches"):
        end = min(start + batch_size, center)
        r_batch = r[start:end]
        r_squared_batch = r_squared[start:end]
        
        # Compute η² - r² for the current batch
        eta_r_diff = eta_squared.unsqueeze(0) - r_squared_batch.unsqueeze(1)
        
        # Create a mask to filter out invalid values (η² - r² < 0)
        valid_mask = eta_r_diff > 0
        
        # Apply the mask and calculate sqrt(η² - r²)
        epsilon = 1e-8
        sqrt_eta_r_diff = torch.sqrt(eta_r_diff.clamp(min=epsilon))  # Clamp ensures no negative sqrt values

        # Compute the integrand (angle / (sqrt(η² - r²) * π))
        angle_expanded = angle.unsqueeze(0).expand(r_batch.size(0), -1, -1)  # Expand angle for batch
        integrand = angle_expanded / (sqrt_eta_r_diff.unsqueeze(2) * np.pi)

        # Mask invalid values in the integrand
        integrand = integrand * valid_mask.unsqueeze(2)
        
        # Perform integration by summing along η (dimension 1)
        ans[start:end, :] = integrand.sum(dim=1)
    
    # Return result as numpy array
    return ans.cpu().numpy()


def ART_GPU(sinogram: np.ndarray, batch_size: int, device:str,reconstruction_angle : float, eps: float,tolerance:float =1e-24,max_stable_iters:int=1000000):
    """
    Perform Algebraic Reconstruction Technique (ART) on a sinogram using GPU.

    This function implements the ART algorithm for tomographic image reconstruction. 
    It iteratively refines the predicted reconstruction to minimize the difference 
    (residual) between the forward projection of the current prediction and the input sinogram.
    The process can utilize GPU acceleration for efficiency.

    Parameters:
        sinogram (np.ndarray): 
            Input sinogram with shape [N, Size, Angle], where:
            - N: Number of sinogram slices.
            - Size: Number of detector bins per projection.
            - Angle: Number of projections (angles).
            
        batch_size (int): 
            Number of slices processed in each batch. A batch size of 1 is recommended 
            if the CPU is used to avoid excessive memory usage.
            
        device (str): 
            Device for computation, either 'cuda' (for GPU) or 'cpu'.
            
        reconstruction_angle (float): 
            The angle spacing (in degrees) between consecutive projections in the sinogram.
            
        eps (float): 
            Convergence criterion for the iterative process. Iterations stop when the 
            maximum residual error across all pixels is below this value.
            
        tolerance (float): 
            Threshold for the change in residual error between iterations to consider 
            the convergence as stable. When the residual change remains below this 
            threshold for `max_stable_iters` iterations, the process is deemed stable.
            
        max_stable_iters (int): 
            Maximum number of iterations allowed with stable residuals (i.e., change in 
            residual error below the `tolerance` threshold) before stopping.

    Returns:
        torch.Tensor: 
            A reconstructed image tensor with shape [N, Image_Size, Image_Size], where 
            N corresponds to the number of input sinogram slices, and Image_Size is the 
            spatial resolution of the reconstructed image.
    """


    # Convert sinogram to a torch tensor and move it to the selected device
    sinogram_tensor = torch.FloatTensor(sinogram).permute(0, 2, 1).to(device)

    # Create data loaders for target and initial predictions
    target_dataloader = torch.utils.data.DataLoader(sinogram_tensor, batch_size=batch_size, shuffle=False)
    predict_dataloader = torch.utils.data.DataLoader(torch.zeros_like(sinogram_tensor), batch_size=batch_size, shuffle=False)

    dataloaders_dict = {"target": target_dataloader, "predict": predict_dataloader}

    # Initialize the ART model with the input sinogram
    reconstruction_angle_radian = reconstruction_angle*np.pi/180
    model = ART_torch(sinogram=sinogram,reconstruction_angle=reconstruction_angle_radian)

    # Extract data loaders
    predict_dataloader = dataloaders_dict["predict"]
    target_dataloader = dataloaders_dict["target"]

    processed_batches = []

    # Convergence parameters

    prev_loss = float('inf')

    # Iterate through the data loader batches
    for i, (predict_batch, target_batch) in enumerate(tzip(predict_dataloader, target_dataloader)):
        # Move batches to the device
        predict_batch = predict_batch.to(model.device)
        target_batch = target_batch.to(model.device)
        stable_count = 0  # Counter for stable iterations

        iter_count = 0
        ATA = model.AT(model.A(torch.ones_like(predict_batch)))  # Precompute ATA for normalization
        ave_loss = torch.inf  # Initialize average loss

        # Initial loss calculation
        loss = torch.divide(model.AT(target_batch - model.A(predict_batch)), ATA)
        ave_loss = torch.max(torch.abs(loss)).item()

        # ART Iterative Reconstruction Loop
        while ave_loss > eps and stable_count < max_stable_iters:
            predict_batch = predict_batch + loss  # Update prediction
            ave_loss = torch.max(torch.abs(loss)).item()
            print("\r", f'Iteration: {iter_count}, Residual: {ave_loss}, Stable Count: {stable_count}', end="")
            iter_count += 1

            # Recalculate loss
            loss = torch.divide(model.AT(target_batch - model.A(predict_batch)), ATA)

            # Check residual change to update stable count
            if abs(ave_loss - prev_loss) < tolerance:
                stable_count += 1
            else:
                stable_count = 0

            prev_loss = ave_loss

        processed_batches.append(predict_batch)

    # Concatenate all processed batches along the batch dimension and return
    return torch.cat(processed_batches, dim=0)




