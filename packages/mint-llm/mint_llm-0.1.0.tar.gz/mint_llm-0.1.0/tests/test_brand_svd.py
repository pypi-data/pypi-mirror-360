import time
import torch

from mint.brand_svd import (
    compute_error,
    compute_ortho_loss,
    run_isvd4,
    run_isvd4_cosine_sim,
    normalize_cosine_sim_factor,
)


def test_brand_incremental_svd():
    # === SETTINGS ===
    # m: number of samples, n: dimension of each sample, r: rank of underlying matrix
    device = "cpu"  # "cuda:0" if torch.cuda.is_available() else "cpu"
    # torch.set_default_device("cuda:0" if torch.cuda.is_available() else "cpu")
    torch.set_default_device(device)
    torch.set_default_dtype(torch.float64)

    num_rows, num_cols, true_rank = 100, 80, 30

    # Create a synthetic low-rank matrix: U = A @ B
    true_matrix = torch.rand(num_rows, true_rank) @ torch.rand(true_rank, num_cols)

    # === RUN TEST ===
    # Start timing
    start_time = time.time()
    Q, S, R = run_isvd4(true_matrix)
    # Stop timing
    end_time = time.time()

    # === BASELINE SVD FOR COMPARISON ===
    if torch.cuda.is_available() and torch.get_default_device().type == "cuda":
        torch.cuda.empty_cache()
    baseline_start = time.time()
    Q_b, S_b, Rh_b = torch.linalg.svd(true_matrix, full_matrices=False)
    baseline_end = time.time()

    # === RECONSTRUCTION ERROR ANALYSIS ===
    # Compare streaming SVD reconstruction vs built-in SVD
    svd_error = compute_error(Q @ (S @ R.T), true_matrix)
    torch_error = compute_error(Q_b @ (S_b.diag() @ Rh_b), true_matrix)
    ortho_loss = compute_ortho_loss(Q)
    ortho_loss_b = compute_ortho_loss(Q_b)

    # === RECONSTRUCTION ERROR ANALYSIS ===
    print("\n=========================================================")
    print("Input Matrix Size: {}x{}".format(true_matrix.shape[0], true_matrix.shape[1]))
    print("Precision: {}".format(Q.dtype))
    print("=========================================================")
    print("ISVD time:", end_time - start_time)
    print("ISVD rank:", S.shape[0])
    print("---------------------------------------------------------")
    print("ISVD error: {:.4f}%".format(svd_error * 100))
    print("ISVD Q ortho drift: {:.4f}%".format(ortho_loss * 100))
    print("=========================================================")
    print("Torch SVD time:", baseline_end - baseline_start)
    print("Torch SVD rank:", torch.linalg.matrix_rank(true_matrix).item())
    print("---------------------------------------------------------")
    print("Torch SVD error: {:.4f}%".format(torch_error * 100))
    print("Torch SVD Q ortho drift: {:.4f}%".format(ortho_loss_b * 100))
    print("=========================================================\n")

    assert svd_error < 1e-8
    assert ortho_loss < 1e-8


def test_brand_incremental_svd_cosine_sim(monkeypatch):
    # === SETTINGS ===
    # m: number of samples, n: dimension of each sample, r: rank of underlying matrix
    torch.set_default_device("cuda:0" if torch.cuda.is_available() else "cpu")
    torch.set_default_dtype(torch.float64)

    true_matrix = torch.randn(300, 3)
    Trn = normalize_cosine_sim_factor(true_matrix)
    cosine_sim_matrix = Trn @ Trn.T

    # === RUN TEST ===
    # Start timing
    start_time = time.time()
    Q, S, R = run_isvd4_cosine_sim(true_matrix)
    # Stop timing
    end_time = time.time()

    # === BASELINE SVD FOR COMPARISON ===
    if torch.cuda.is_available() and torch.get_default_device().type == "cuda":
        torch.cuda.empty_cache()
    baseline_start = time.time()
    Q_b, S_b, Rh_b = torch.linalg.svd(cosine_sim_matrix, full_matrices=False)
    baseline_end = time.time()

    # === RECONSTRUCTION ERROR ANALYSIS ===
    # Compare streaming SVD reconstruction vs built-in SVD
    svd_error = compute_error(Q @ (S @ R.T), cosine_sim_matrix)
    torch_error = compute_error(Q_b @ (S_b.diag() @ Rh_b), cosine_sim_matrix)
    ortho_loss = compute_ortho_loss(Q)
    ortho_loss_b = compute_ortho_loss(Q_b)

    # === RECONSTRUCTION ERROR ANALYSIS ===
    print("\n=========================================================")
    print("Input Column Size: {}".format(true_matrix.shape[0]))
    print(
        "Cosine Matrix Size: {}x{}".format(
            cosine_sim_matrix.shape[0], cosine_sim_matrix.shape[1]
        )
    )
    print("Precision: {}".format(Q.dtype))
    print("=========================================================")
    print("ISVD time:", end_time - start_time)
    print("ISVD rank:", S.shape[0])
    print("---------------------------------------------------------")
    print("ISVD error: {:.4f}%".format(svd_error * 100))
    print("ISVD Q ortho drift: {:.4f}%".format(ortho_loss * 100))
    print("=========================================================")
    print("Torch SVD time:", baseline_end - baseline_start)
    print("Torch SVD rank:", torch.linalg.matrix_rank(cosine_sim_matrix).item())
    print("---------------------------------------------------------")
    print("Torch SVD error: {:.4f}%".format(torch_error * 100))
    print("Torch SVD Q ortho drift: {:.4f}%".format(ortho_loss_b * 100))
    print("=========================================================\n")

    assert svd_error < 1e-8
    assert ortho_loss < 1e-8
