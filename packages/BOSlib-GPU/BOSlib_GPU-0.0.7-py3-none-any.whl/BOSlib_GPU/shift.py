import numpy as np
import torch
import torch.nn.functional as F
import pandas as pd
import cv2

def S_BOS_GPU(image_ref, image_exp, device, batch_size=5000):
    """
    Compute the phase shift (displacement field) between two images using 1D BOS processing.
    
    This function loads the reference and experimental images to the GPU, detects the fundamental
    frequency from a selected column of the reference image, processes the signals in batches using 
    bandpass filtering and amplitude normalization, computes the phase difference via a low-pass 
    filtered product, and finally converts the phase shift into a displacement field.
    
    Parameters:
        image_ref (numpy.ndarray): Reference image (grayscale or single channel).
        image_exp (numpy.ndarray): Experimental image (grayscale or single channel).
        device (torch.device or str): Device to perform computations (e.g., 'cuda' or 'cpu').
        batch_size (int, optional): Number of columns to process per batch. Default is 64.
        
    Returns:
        numpy.ndarray: Displacement field computed from the phase shift.
    """
    
    # Helper function to detect the dominant frequency using FFT
    def freq_finder(sig):
        """
        Find the dominant frequency of a 1D signal using FFT.
        
        Parameters:
            sig (numpy.ndarray): Input 1D signal.
            
        Returns:
            float: Dominant frequency (ignoring frequencies below 0.01 [1/px]).
        """
        # Create frequency axis
        freq = np.fft.fftfreq(sig.shape[0])
        # Compute FFT of the signal
        fk = np.fft.fft(sig)
        # Normalize amplitude (taking absolute value)
        fk = np.abs(fk / (sig.shape[0] / 2))
        # Combine frequency and amplitude in a 2D array and create a DataFrame
        fk2 = np.vstack([freq, fk]).T
        fk_df = pd.DataFrame(fk2, columns=["freq", "amp"])
        fk_df = fk_df.sort_values('freq')
        # Consider only non-negative frequencies
        fk_df = fk_df[fk_df["freq"] >= 0]
        # Ignore frequencies below 0.01 [1/px] and pick the frequency with maximum amplitude
        freq_search = fk_df[fk_df["freq"] >= 0.01].sort_values('amp', ascending=False)
        f1 = freq_search.iloc[0, 0]
        return f1

    # Helper function to apply a bandpass filter using FFT
    def bandpass_filter_1d(signal, low_cut, high_cut, sampling_rate=1):
        """
        Apply a bandpass filter on a 1D signal using FFT.
        
        Parameters:
            signal (torch.Tensor): Input signal with shape [batch, length].
            low_cut (float): Lower cutoff frequency (Hz).
            high_cut (float): Higher cutoff frequency (Hz).
            sampling_rate (float): Sampling rate (Hz).
            
        Returns:
            torch.Tensor: Bandpass filtered signal with shape [batch, length].
        """
        # Compute frequency axis on the same device as the signal
        freq = torch.fft.fftfreq(signal.shape[-1], d=1/sampling_rate).to(signal.device)
        # Compute FFT of the input signal
        fft_signal = torch.fft.fft(signal, dim=-1)
        # Create bandpass mask: pass frequencies between low_cut and high_cut (both positive and negative)
        bandpass_mask = ((freq >= low_cut) & (freq <= high_cut)) | ((freq <= -low_cut) & (freq >= -high_cut))
        bandpass_mask = bandpass_mask.to(signal.device).float()
        # Apply the mask to the FFT of the signal
        fft_filtered = fft_signal * bandpass_mask
        # Inverse FFT to return to the time domain (only real part is used)
        filtered_signal = torch.fft.ifft(fft_filtered, dim=-1).real
        return filtered_signal

    # Helper function to normalize the signal amplitude and add a sinusoidal signal in low-amplitude regions
    def signal_scale_normalize_torch(sig, f):
        """
        Normalize the amplitude of the signal and add a sinusoidal component where the amplitude is low.
        
        Parameters:
            sig (torch.Tensor): Input signal tensor.
            f (float): Fundamental frequency.
            
        Returns:
            torch.Tensor: Normalized signal tensor.
        """
        # Ensure signal is on the specified device
        sig = sig.to(device)
        # Determine the window size based on the fundamental frequency (ensuring an odd kernel size for max pooling)
        kernel_size = int(0.5 / f)
        if kernel_size % 2 == 0:
            kernel_size += 1
        # Compute the rolling maximum of the absolute value using max_pool1d
        sig_abs = torch.abs(sig).unsqueeze(1)  # Shape: [B, 1, L]
        sig_abs = F.max_pool1d(sig_abs, kernel_size, stride=1, padding=kernel_size // 2)
        sig_abs = sig_abs.squeeze(1)
        # Set regions with low amplitude (less than half the mean) to zero
        threshold = torch.nanmean(sig_abs) * 0.5
        sig = torch.where(sig_abs < threshold, torch.tensor(0.0, device=device), sig)
        # Add a sinusoidal signal in regions where the amplitude is below threshold
        y = torch.arange(0, sig.shape[1], device=device, dtype=torch.float32)
        S = torch.sin(2 * torch.pi * f * y)
        S1 = (1 - (sig_abs > threshold).float()) * S
        sig = sig + S1
        # Avoid division by zero by replacing low values with 1
        sig_abs = torch.where(sig_abs < threshold, torch.tensor(1.0, device=device), sig_abs)
        # Normalize the signal amplitude to 1
        sig_norm = sig / sig_abs
        # Replace any NaN values with zero
        sig_norm = torch.where(torch.isnan(sig_norm), torch.tensor(0.0, device=device), sig_norm)
        return sig_norm

    # Helper function to calculate the phase difference between reference and experimental signals
    def phase_calculate(ref, exp, f1):
        """
        Compute the phase difference between the reference and experimental signals.
        
        Parameters:
            ref (torch.Tensor): Reference signal with shape [B, N].
            exp (torch.Tensor): Experimental signal with shape [B, N].
            f1 (float): Fundamental frequency.
            
        Returns:
            torch.Tensor: Phase difference with shape [B, N].
        """
        # Ensure both signals are on the same device
        ref = ref.to(device)
        exp = exp.to(device)
        # Calculate the approximate gradient of the reference signal using finite differences
        cos_ref = torch.diff(ref, dim=1, append=ref[:, -1:]) / (f1 * 2 * torch.pi)
        # Compute modulation products for phase calculation
        cos_vive = ref * exp
        sin_vive = cos_ref * exp
        # Apply low-pass filtering to both products to reduce high-frequency noise
        cos_phi = bandpass_filter_1d(cos_vive, 0, f1)
        sin_phi = bandpass_filter_1d(sin_vive, 0, f1)
        # Calculate phase using the arctan2 function
        phi = torch.atan2(sin_phi, cos_phi)
        return phi

    # Helper function to process a batch of 1D signals for BOS phase calculation
    def phase_1DBOS_process_batch(sig_ref, sig_exp, f1):
        """
        Process a batch of 1D signals to compute the phase difference.
        
        Parameters:
            sig_ref (torch.Tensor): Batch of reference signals [batch, length].
            sig_exp (torch.Tensor): Batch of experimental signals [batch, length].
            f1 (float): Fundamental frequency.
            
        Returns:
            torch.Tensor: Phase difference for the batch with shape [batch, length].
        """
        # Isolate the fundamental frequency component via bandpass filtering
        separate_sig_ref = bandpass_filter_1d(sig_ref, f1 * 0.7, f1 * 1.5)
        separate_sig_exp = bandpass_filter_1d(sig_exp, f1 * 0.7, f1 * 1.5)
        # Normalize the filtered signals
        separate_sig_ref = signal_scale_normalize_torch(separate_sig_ref, f1)
        separate_sig_exp = signal_scale_normalize_torch(separate_sig_exp, f1)
        # Calculate and return the phase difference
        phi = phase_calculate(separate_sig_ref, separate_sig_exp, f1)
        return phi

    # ----------------- Main computation begins here -----------------
    
    # Convert images to torch tensors and move them to the specified device
    image_ref_torch = torch.from_numpy(image_ref).float().to(device)
    image_exp_torch = torch.from_numpy(image_exp).float().to(device)
    
    # Get the dimensions of the images (height, width)
    height, width = image_ref_torch.shape[:2]
    
    # Permute the images so that each column becomes a 1D signal for batch processing
    sig_ref_all = image_ref_torch.permute(1, 0)  # Shape: [width, height]
    sig_exp_all = image_exp_torch.permute(1, 0)  # Shape: [width, height]
    
    # Detect the fundamental frequency using a selected column (e.g., column 100) of the reference image
    f1 = freq_finder(image_ref[:, 100])
    
    # Initialize a tensor to store the phase results for the entire image
    phi_2D_torch = torch.zeros((height, width), dtype=torch.float32, device=device)
    
    # Process the image in batches (column-wise)
    for start in range(0, width, batch_size):
        end = min(start + batch_size, width)
        # Extract a batch of columns
        sig_ref_b = sig_ref_all[start:end]
        sig_exp_b = sig_exp_all[start:end]
        # Compute the phase shift for the current batch
        phi_b = phase_1DBOS_process_batch(sig_ref_b, sig_exp_b, f1)
        # Store the phase result (transpose to match the original image orientation)
        phi_2D_torch[:, start:end] = phi_b.transpose(0, 1)
    
    # Move the computed phase data back to CPU and convert to a numpy array
    phi_2D = phi_2D_torch.cpu().numpy()
    
    # Convert the phase shift to a displacement field (delta_h)
    delta_h = phi_2D / (2 * np.pi * f1)
    
    return delta_h

def SP_BOS_GPU(ref,exp,kernel_height,batch_size=1000000):
    # Make sure that GPU is available 
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu') 
    print(device)
    # 画像の読み込み (Grayscale)
    ref_image = torch.tensor(ref, dtype=torch.float32, device=device)
    exp_image = torch.tensor(exp, dtype=torch.float32, device=device)

    # 二値化

    def filter_image_gpu(img: torch.Tensor, window_size: int = 20) -> torch.Tensor:
        """
        入力画像の各縦列に対してGPU上でFFT処理を行い、
        主成分周波数付近のみを抽出・正規化してフィルタリングを行う関数。
        
        Parameters:
            img (torch.Tensor): 入力画像（形状 [H, W]、グレースケール、dtype uint8 または float32）。
            window_size (int): 主成分周波数の前後に保持するサンプル数（デフォルト20）。
        
        Returns:
            torch.Tensor: フィルタリング後の画像（形状 [H, W]、dtype uint8）をGPU上に保持。
        """
        device = img.device
        # 入力がuint8の場合はfloat32にキャスト
        if img.dtype != torch.float32:
            img = img.float()
        
        H, W = img.shape

        # FFT: 各縦列（dim=0）について並列にFFTを計算
        # fft_signal の形状は [H, W]（複素数）
        fft_signal = torch.fft.fft(img, dim=0)

        # 振幅スペクトルの計算
        mag = torch.abs(fft_signal)
        # 各列のDC成分（index=0）は除外
        mag[0, :] = 0.0

        # 各列ごとに、最大振幅（主成分周波数）のインデックスを取得
        # dominant_index の形状は [W]
        dominant_index = torch.argmax(mag, dim=0)

        # 各周波数軸上のインデックス [0, 1, ..., H-1] を生成して、[H, 1]に変換
        indices = torch.arange(H, device=device).unsqueeze(1)  # shape: [H, 1]
        
        # 各列ごとに、主成分周波数からの差分を計算
        # diff1: [H, W] 各要素が |i - dominant_index[col]| となる
        diff1 = torch.abs(indices - dominant_index.unsqueeze(0))
        mask1 = diff1 <= window_size

        # 複素共役対称側の周波数は、各列で H - dominant_index に対応
        sym_index = H - dominant_index
        diff2 = torch.abs(indices - sym_index.unsqueeze(0))
        mask2 = diff2 <= window_size

        # 両方のマスクを論理和で合成
        mask = mask1 | mask2  # shape: [H, W]
        
        # マスクを fft_signal と同じ複素数型に変換して乗算
        fft_filtered = fft_signal * mask.to(fft_signal.dtype)

        # 逆FFTで空間領域へ戻す（各縦列について並列に処理）
        filtered_signal = torch.fft.ifft(fft_filtered, dim=0).real

        # 各縦列ごとに正規化 (0～255) する：
        # 各列で最小値と最大値を計算
        min_vals = torch.amin(filtered_signal, dim=0, keepdim=True)
        max_vals = torch.amax(filtered_signal, dim=0, keepdim=True)
        denom = max_vals - min_vals
        # ゼロ割を回避
        denom[denom == 0] = 1.0
        norm_signal = (filtered_signal - min_vals) / denom * 255.0

        # 値を0-255の範囲にクリップして、uint8 に変換
        norm_signal = torch.clamp(norm_signal, 0, 255)
        return norm_signal.to(torch.uint8)


    ref_bin=filter_image_gpu(ref_image)
    exp_bin=filter_image_gpu(exp_image)

    # エッジ検出 (Canny) を模倣 (PyTorchには直接的なCanny関数がないため、OpenCVを活用後テンソルに変換)
    ref_edges = torch.tensor(cv2.Canny(ref_bin.cpu().numpy().astype(np.uint8), 100, 200), dtype=torch.float32, device=device)
    exp_edges = torch.tensor(cv2.Canny(exp_bin.cpu().numpy().astype(np.uint8), 100, 200), dtype=torch.float32, device=device)

    # エッジを1.0、それ以外を0にする
    ref_edge_bin = (ref_edges > 0).float()
    exp_edge_bin = (exp_edges > 0).float()

    # location_embedding_vector の計算
    location_embedding_vector = torch.arange(1, kernel_height + 1, device=device).flip(0)

    # カーネルサイズ
    kernel_size = (kernel_height, 1)

    # カーネルごとに分割 (パディングなし)
    micro_unfolded_ref = torch.tensor(ref_edge_bin).unfold(0, kernel_size[0], 1).unfold(1, kernel_size[1], 1).to(device)  # (H-2, W, kernel_height, kernel_width)
    micro_unfolded_exp = torch.tensor(exp_edge_bin).unfold(0, kernel_size[0], 1).unfold(1, kernel_size[1], 1).to(device)  # (H-2, W, kernel_height, kernel_width)

    # カーネルごとのデータを取得
    micro_kernels_ref = micro_unfolded_ref.contiguous().view(-1, kernel_size[0] * kernel_size[1])  # (新しいH*W, kernel_height*kernel_width)
    micro_kernels_exp = micro_unfolded_exp.contiguous().view(-1, kernel_size[0] * kernel_size[1])  # (新しいH*W, kernel_height*kernel_width)

    # ミニバッチサイズの設定
    num_batches = (micro_kernels_ref.size(0) + batch_size - 1) // batch_size  # バッチ数の計算

    # 結果を格納するリスト
    micro_refs = []
    micro_exps = []

    for i in range(num_batches):
        # バッチの開始と終了インデックス
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, micro_kernels_ref.size(0))
        
        # ミニバッチを切り出し
        batch_kernels_ref = micro_kernels_ref[start_idx:end_idx]
        batch_kernels_exp = micro_kernels_exp[start_idx:end_idx]
        
        # 各バッチでの計算
        batch_located_ref = batch_kernels_ref * location_embedding_vector.to(device)
        batch_located_exp = batch_kernels_exp * location_embedding_vector.to(device)

        
        # NaN を考慮した平均計算
        batch_micro_ref = torch.where(
            batch_located_ref != 0, batch_located_ref, torch.tensor(float('nan'), device=device)
        ).nanmean(dim=1)
        batch_micro_exp = torch.where(
            batch_located_exp != 0, batch_located_exp, torch.tensor(float('nan'), device=device)
        ).nanmean(dim=1)
        
        # 結果をリストに追加
        micro_refs.append(batch_micro_ref)
        micro_exps.append(batch_micro_exp)

    # バッチごとの結果を結合
    micro_ref = torch.cat(micro_refs, dim=0)
    micro_exp = torch.cat(micro_exps, dim=0)

    # シフト計算
    shift_micro = micro_exp - micro_ref

    # stripe_idx の計算
    stripe_idx = ref_edge_bin.shape[0] / torch.sum(ref_edge_bin[:, 0])
    # 累積和 (cumsum)
    cumsum_array_ref = torch.cumsum(ref_edge_bin, dim=0)
    cumsum_array_exp = torch.cumsum(exp_edge_bin, dim=0)
    # numbered_ref, numbered_exp の計算
    numbered_ref = ref_edge_bin * cumsum_array_ref * stripe_idx
    numbered_exp = exp_edge_bin * cumsum_array_exp * stripe_idx
    # stripe_idx の値を表示
    print(stripe_idx.item())

    # カーネルごとに分割 (パディングなし)
    macro_unfolded_ref = numbered_ref.unfold(0, kernel_size[0], 1).unfold(1, kernel_size[1], 1).to(device)  # (H-2, W, kernel_height, kernel_width)
    macro_unfolded_exp = numbered_exp.unfold(0, kernel_size[0], 1).unfold(1, kernel_size[1], 1).to(device)  # (H-2, W, kernel_height, kernel_width)

    # カーネルごとのデータを取得
    macro_kernels_ref = macro_unfolded_ref.contiguous().view(-1, kernel_size[0] * kernel_size[1])  # (新しいH*W, kernel_height*kernel_width)
    macro_kernels_exp = macro_unfolded_exp.contiguous().view(-1, kernel_size[0] * kernel_size[1])  # (新しいH*W, kernel_height*kernel_width)

    # 結果を格納するリスト
    macro_refs = []
    macro_exps = []

    for i in range(num_batches):
        # バッチの開始と終了インデックス
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, macro_kernels_ref.size(0))
        
        # ミニバッチを切り出し
        macro_batch_kernels_ref = macro_kernels_ref[start_idx:end_idx]
        macro_batch_kernels_exp = macro_kernels_exp[start_idx:end_idx]
        
        # NaN を考慮した平均計算
        batch_macro_ref = torch.where(
            macro_batch_kernels_ref != 0, macro_batch_kernels_ref, torch.tensor(float('nan'), device=device)
        ).nanmean(dim=1)
        batch_macro_exp = torch.where(
            macro_batch_kernels_exp != 0, macro_batch_kernels_exp, torch.tensor(float('nan'), device=device)
        ).nanmean(dim=1)
        
        # 結果をリストに追加
        macro_refs.append(batch_macro_ref)
        macro_exps.append(batch_macro_exp)

    # バッチごとの結果を結合
    macro_ref = torch.cat(macro_refs, dim=0)
    macro_exp = torch.cat(macro_exps, dim=0)

    # シフト計算
    shift_macro = macro_exp - macro_ref

    shift=shift_micro+shift_macro
    # 結果を元の形に戻す
    result_height = ref_edge_bin.shape[0] - kernel_size[0] + 1
    result_width = ref_edge_bin.shape[1]
    result = shift.view(result_height, result_width)

    # 各列の最初の10行の平均を計算
    column_means = result[:500, :].mean(dim=0)

    # 各列から平均を引き算
    adjusted_data = result - column_means

    result_gpu1_reconstructed = adjusted_data.view(adjusted_data.shape[0], adjusted_data.shape[1])

    return result_gpu1_reconstructed.cpu().numpy()