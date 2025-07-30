# The update version of harmonypy.

from __future__ import annotations

import logging
from functools import partial

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# create logger
logger = logging.getLogger("harmonypy")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def run_continuous_harmony(
    data_mat: np.ndarray,
    meta_data: pd.DataFrame,
    vars_use: list[str] | str,
    theta: float | list[float] | None = None,
    lamb: float | list[float] | None = None,
    sigma: float | list[float] | None = 0.1,
    nclust: int | None = None,
    tau: float = 0,
    block_size: float = 0.05,
    max_iter_harmony: int = 10,
    max_iter_kmeans: int = 20,
    epsilon_cluster: float = 1e-5,
    epsilon_harmony: float = 1e-4,
    verbose: bool = True,
    random_state: int = 0,
    cluster_fn: str = "kmeans",
    remove_vars: list[str] | None = None,
) -> ContinuousHarmony:
    """Run Harmony with optional partial correction by specifying remove_vars.

    Parameters
    ----------
    data_mat : np.ndarray
        Shape: (cells x features) or (features x cells). If (features x cells),
        it's transposed internally to become (features, cells).
    meta_data : pd.DataFrame
        Per-cell meta information. Must have at least the columns in vars_use.
    vars_use : list or str
        Columns to use in building the design matrix (batch, condition, etc.).
    remove_vars : list or str or None
        Column name(s) in meta_data that we want to remove (i.e. batch effect).
        If None, all columns in vars_use are fully removed as before (original approach).
        If some columns are specified here, only those columns' one-hot
        representation is subtracted. Others remain uncorrected.
    theta, lamb, sigma : float or list
        Diversity penalty, ridge penalty, soft k-means slope, respectively.
        If single float, repeated for all categories. Otherwise must match the
        total number of categories across all columns in vars_use.
    nclust : int
        Number of clusters for soft k-means (default: min(N/30, 100)).
    tau : float
        Minimum number of cells per cluster if not zero (for discounting).
    block_size : float
        Fraction of cells to remove+reassign in each block update step.
    max_iter_harmony : int
        Maximum Harmony iterations.
    max_iter_kmeans : int
        Maximum k-means steps each iteration.
    epsilon_cluster : float
        Convergence tolerance for k-means steps.
    epsilon_harmony : float
        Convergence tolerance for Harmony iterations.
    random_state : int
        Random seed.
    cluster_fn : {'kmeans'} or callable
        Clustering method for initial centroid. Default: 'kmeans'.
    verbose : bool
        Print progress info.
    plot_convergence : bool
        Not implemented here (placeholder).

    Returns
    -------
    ho : Harmony
        Harmony object. The corrected matrix is in `ho.Z_corr`.

    Notes
    -----
    - If remove_vars is not None, any column in remove_vars that does not
      exist in meta_data will raise an error.
    - If remove_vars is provided, only that set of columns in `vars_use` is
      partially subtracted from the embedding. (Other columns remain.)

    """
    # 1) Check array dimensions
    N = meta_data.shape[0]
    if data_mat.shape[1] != N:
        data_mat = data_mat.T
    assert data_mat.shape[1] == N, "data_mat and meta_data do not have the same number of cells"

    # 2) Default nclust
    if nclust is None:
        nclust = np.min([np.round(N / 30.0), 100]).astype(int)

    # 3) Convert sigma to array if needed
    if isinstance(sigma, float) and nclust > 1:
        sigma = np.repeat(sigma, nclust)

    # 4) If vars_use is a single string, wrap it
    if isinstance(vars_use, str):
        vars_use = [vars_use]

    # 5) If remove_vars is a single string, wrap it
    if isinstance(remove_vars, str):
        remove_vars = [remove_vars]
    # Could be None, in which case partial = False (i.e. fully remove everything)

    # 6) Check remove_vars existence
    if remove_vars is not None:
        for col in remove_vars:
            if col not in meta_data.columns:
                raise ValueError(f"Column '{col}' specified in remove_vars not found in meta_data.")

    # 7) One-hotエンコードを自前で行い、各列のカテゴリ数を把握＆
    #    remove_varsに該当するワンホットの row-index を後で計算する
    phi_list = []
    cat_sizes = []
    col_info_list = []  # 記録用: [(col_name, start_idx, end_idx), ...]

    start_idx = 0
    # meta_data[vars_use]内の各列を順に処理
    for col in vars_use:
        if col not in meta_data.columns:
            raise ValueError(f"Column '{col}' not found in meta_data.")

        # One-hot
        dummies = pd.get_dummies(meta_data[col], prefix=col)
        # dummies: shape (N, n_cat)
        n_cat = dummies.shape[1]
        cat_sizes.append(n_cat)

        # collect
        phi_list.append(dummies.values.T)  # shape (n_cat, N)

        # info
        col_info_list.append((col, start_idx, start_idx + n_cat - 1))
        start_idx += n_cat

    # 結合: phi = shape(B, N)
    #   B = sum of n_cat for each column
    phi = np.concatenate(phi_list, axis=0)  # shape: (B, N)

    # 8) カテゴリ数の配列
    phi_n = np.array(cat_sizes, dtype=int)  # shape=(len(vars_use),)

    # 9) default theta, lamb
    #    例: theta=2.0 → 全カテゴリ2.0で埋める
    if theta is None:
        theta = np.repeat([1], np.sum(phi_n))
    elif isinstance(theta, (float, int)):
        theta = np.repeat(theta, np.sum(phi_n))
    else:
        # ユーザーが各列用に与える場合など
        pass
    assert len(theta) == np.sum(phi_n), "theta must match total number of categories"

    if lamb is None:
        lamb = np.repeat([1], np.sum(phi_n))
    elif isinstance(lamb, (float, int)):
        lamb = np.repeat(lamb, np.sum(phi_n))
    else:
        pass
    assert len(lamb) == np.sum(phi_n), "lamb must match total number of categories"

    # 10) N_b, Pr_b
    B = phi.shape[0]
    N_b = phi.sum(axis=1)  # shape(B,)
    Pr_b = N_b / N

    # 11) tauスケーリング
    if tau > 0:
        # Harmony論文の式に準拠
        # theta = theta * (1 - exp(-(N_b/(nclust*tau))^2))
        scale_fac = 1 - np.exp(-((N_b / (nclust * tau)) ** 2))
        theta = theta * scale_fac

    # 12) lamb_mat
    lamb_mat = np.diag(np.insert(lamb, 0, 0))  # (B+1, B+1)

    # 13) Phi_moe = [1; phi], shape (B+1, N)
    phi_moe = np.vstack([np.ones(N), phi])

    # 14) 部分的に除去する行インデックスの計算
    #     intercept=0番目は除去しない(強制),
    #     remove_vars に含まれる列が担当する one-hot 行のみを"除去対象"とする。
    partial_remove_idx = []
    if remove_vars is not None:
        # remove_vars が指定されているなら → partial correction
        for col, start_i, end_i in col_info_list:
            if col in remove_vars:
                # ここの行が除去対象
                # 例: intercept=0, batchのone-hotは1..n_cat, conditionは...
                # ここでは 1 + start_i ... 1 + end_i が実際のPhi_moe上の該当行
                r1 = 1 + start_i
                r2 = 1 + end_i
                partial_remove_idx.extend(range(r1, r2 + 1))
        partial_remove_idx = sorted(partial_remove_idx)
    else:
        # remove_vars=None → 従来どおり"全カテゴリ除去" (partialなし)
        partial_remove_idx = None

    # 15) 実行
    np.random.seed(random_state)

    # Harmonyオブジェクト生成
    ho = ContinuousHarmony(
        data_mat,
        phi,
        phi_moe,
        Pr_b,
        sigma,
        theta,
        max_iter_harmony,
        max_iter_kmeans,
        epsilon_cluster,
        epsilon_harmony,
        nclust,
        block_size,
        lamb_mat,
        verbose,
        random_state,
        cluster_fn,
        partial_remove_idx,
    )

    return ho


class ContinuousHarmony:
    def __init__(
        self,
        Z,
        Phi,
        Phi_moe,
        Pr_b,
        sigma,
        theta,
        max_iter_harmony,
        max_iter_kmeans,
        epsilon_kmeans,
        epsilon_harmony,
        K,
        block_size,
        lamb,
        verbose,
        random_state=None,
        cluster_fn="kmeans",
        partial_remove_idx=None,
    ):
        self.Z_corr = np.array(Z)  # shape(d, N)
        self.Z_orig = np.array(Z)  # shape(d, N)

        # Cosine-normalized Z for cluster steps
        self.Z_cos = self.Z_orig / self.Z_orig.max(axis=0, initial=1e-9)
        self.Z_cos = self.Z_cos / np.linalg.norm(self.Z_cos, ord=2, axis=0, keepdims=True)

        self.Phi = Phi  # shape(B, N)
        self.Phi_moe = Phi_moe  # shape(B+1, N)
        self.N = self.Z_corr.shape[1]
        self.Pr_b = Pr_b
        self.B = self.Phi.shape[0]
        self.d = self.Z_corr.shape[0]

        self.window_size = 3
        self.epsilon_kmeans = epsilon_kmeans
        self.epsilon_harmony = epsilon_harmony

        self.lamb = lamb
        self.sigma = sigma
        self.sigma_prior = sigma
        self.block_size = block_size
        self.K = K
        self.max_iter_harmony = max_iter_harmony
        self.max_iter_kmeans = max_iter_kmeans
        self.verbose = verbose
        self.theta = theta

        # For tracking objectives
        self.objective_harmony = []
        self.objective_kmeans = []
        self.objective_kmeans_dist = []
        self.objective_kmeans_entropy = []
        self.objective_kmeans_cross = []
        self.kmeans_rounds = []

        # partial_remove_idx があれば部分的補正、それ以外(None)なら全部補正
        self.partial_remove_idx = partial_remove_idx

        self.allocate_buffers()

        if cluster_fn == "kmeans":
            cluster_fn = partial(ContinuousHarmony._cluster_kmeans, random_state=random_state)
        self.init_cluster(cluster_fn)
        self.harmonize(self.max_iter_harmony, self.verbose)

    def result(self):
        """Return the final corrected data (shape: d x N)."""
        return self.Z_corr

    def allocate_buffers(self):
        self._scale_dist = np.zeros((self.K, self.N))
        self.dist_mat = np.zeros((self.K, self.N))
        self.O = np.zeros((self.K, self.B))
        self.E = np.zeros((self.K, self.B))
        self.W = np.zeros((self.B + 1, self.d))
        self.Phi_Rk = np.zeros((self.B + 1, self.N))

    @staticmethod
    def _cluster_kmeans(data, K, random_state):
        logger.info("Computing initial centroids with sklearn.KMeans...")
        model = KMeans(n_clusters=K, init="k-means++", n_init=10, max_iter=25, random_state=random_state)
        model.fit(data)
        km_centroids = model.cluster_centers_
        logger.info("sklearn.KMeans initialization complete.")
        return km_centroids

    def init_cluster(self, cluster_fn):
        # 1) Initialize cluster centers: shape(d, K)
        self.Y = cluster_fn(self.Z_cos.T, self.K).T
        # 2) Normalize
        self.Y = self.Y / np.linalg.norm(self.Y, ord=2, axis=0, keepdims=True)
        # 3) Assign cluster probabilities R
        self.dist_mat = 2.0 * (1.0 - np.dot(self.Y.T, self.Z_cos))  # (K, N)
        self.R = -self.dist_mat / self.sigma[:, None]
        self.R -= np.max(self.R, axis=0)
        self.R = np.exp(self.R)
        self.R = self.R / np.sum(self.R, axis=0)
        # 4) Batch stats
        self.E = np.outer(np.sum(self.R, axis=1), self.Pr_b)  # (K,B)
        self.O = np.inner(self.R, self.Phi)  # (K,B)
        self.compute_objective()
        self.objective_harmony.append(self.objective_kmeans[-1])

    def compute_objective(self):
        # kmeans error
        kmeans_error = np.sum(self.R * self.dist_mat)
        # entropy
        _entropy = np.sum(safe_entropy(self.R) * self.sigma[:, None])
        # cross entropy
        x = self.R * self.sigma[:, None]  # (K,N)
        y = self.theta.reshape(1, -1)  # (K,B)
        y = np.tile(y, (self.K, 1))
        z = np.log((self.O + 1.0) / (self.E + 1.0))
        _cross_entropy = np.sum(x * np.dot(y * z, self.Phi))

        val = kmeans_error + _entropy + _cross_entropy
        self.objective_kmeans.append(val)
        self.objective_kmeans_dist.append(kmeans_error)
        self.objective_kmeans_entropy.append(_entropy)
        self.objective_kmeans_cross.append(_cross_entropy)

    def harmonize(self, iter_harmony=10, verbose=True):
        converged = False
        for i in range(1, iter_harmony + 1):
            if verbose:
                logger.info(f"Harmony iteration {i} of {iter_harmony}")

            # 1) cluster update
            self.cluster()

            # 2) regress out
            if self.partial_remove_idx is None:
                # 従来手法（全カテゴリ除去）
                self.Z_cos, self.Z_corr, self.W, self.Phi_Rk = moe_correct_ridge(self.Z_orig, self.Z_cos, self.Z_corr, self.R, self.W, self.K, self.Phi_Rk, self.Phi_moe, self.lamb)
            else:
                # 部分的手法
                self.Z_cos, self.Z_corr, self.W, self.Phi_Rk = moe_correct_ridge_partial(
                    self.Z_orig,
                    self.Z_cos,
                    self.Z_corr,
                    self.R,
                    self.W,
                    self.K,
                    self.Phi_Rk,
                    self.Phi_moe,
                    self.lamb,
                    self.partial_remove_idx,
                )

            # 3) convergence check
            converged = self.check_convergence(i_type=1)
            if converged and verbose:
                logger.info(f"Converged after {i} iteration(s).")
                break
        if verbose and not converged:
            logger.info("Stopped before convergence.")

    def cluster(self):
        # Recompute dist_mat from updated Z_cos
        self.dist_mat = 2.0 * (1.0 - np.dot(self.Y.T, self.Z_cos))
        for i in range(self.max_iter_kmeans):
            # 1) update Y
            self.Y = np.dot(self.Z_cos, self.R.T)
            self.Y = self.Y / np.linalg.norm(self.Y, ord=2, axis=0, keepdims=True)
            # 2) dist_mat
            self.dist_mat = 2.0 * (1.0 - np.dot(self.Y.T, self.Z_cos))
            # 3) update R
            self.update_R()
            # 4) check
            self.compute_objective()
            if i > self.window_size:
                if self.check_convergence(i_type=0):
                    break
        self.kmeans_rounds.append(i)
        self.objective_harmony.append(self.objective_kmeans[-1])

    def update_R(self):
        self._scale_dist = -self.dist_mat / self.sigma[:, None]
        self._scale_dist -= np.max(self._scale_dist, axis=0)
        self._scale_dist = np.exp(self._scale_dist)

        idx_all = np.arange(self.N)
        np.random.shuffle(idx_all)
        n_blocks = int(np.ceil(1.0 / self.block_size))
        blocks = np.array_split(idx_all, n_blocks)

        for block_cells in blocks:
            # remove old
            self.E -= np.outer(np.sum(self.R[:, block_cells], axis=1), self.Pr_b)
            self.O -= np.dot(self.R[:, block_cells], self.Phi[:, block_cells].T)
            # recompute R
            self.R[:, block_cells] = self._scale_dist[:, block_cells]
            # multiply by cross-entropy term
            self.R[:, block_cells] *= np.dot(np.power((self.E + 1) / (self.O + 1), self.theta), self.Phi[:, block_cells])
            # normalize
            self.R[:, block_cells] /= np.linalg.norm(self.R[:, block_cells], ord=1, axis=0, keepdims=True)
            # put back
            self.E += np.outer(np.sum(self.R[:, block_cells], axis=1), self.Pr_b)
            self.O += np.dot(self.R[:, block_cells], self.Phi[:, block_cells].T)

    def check_convergence(self, i_type):
        if i_type == 0:
            # cluster
            okl = len(self.objective_kmeans)
            if okl <= self.window_size:
                return False
            obj_old = sum(self.objective_kmeans[okl - 2 - self.window_size : okl - 2])
            obj_new = sum(self.objective_kmeans[okl - 1 - self.window_size : okl - 1])
            if abs(obj_old - obj_new) / abs(obj_old) < self.epsilon_kmeans:
                return True
            return False
        # harmony iteration
        oh = len(self.objective_harmony)
        if oh < 2:
            return False
        old_val = self.objective_harmony[-2]
        new_val = self.objective_harmony[-1]
        if abs(old_val - new_val) / abs(old_val) < self.epsilon_harmony:
            return True
        return False


def safe_entropy(x: np.array):
    y = np.multiply(x, np.log(x))
    y[~np.isfinite(y)] = 0.0
    return y


def moe_correct_ridge(Z_orig, Z_cos, Z_corr, R, W, K, Phi_Rk, Phi_moe, lamb):
    """Original approach: remove all categories (batch + condition, etc.).
    For each cluster i, solve for W, then subtract W^T @ Phi_Rk from Z_corr.
    """
    Z_corr = Z_orig.copy()
    N = Z_orig.shape[1]
    for i in range(K):
        Phi_Rk = np.multiply(Phi_moe, R[i, :])  # shape(B+1, N)
        x = np.dot(Phi_Rk, Phi_moe.T) + lamb  # (B+1, B+1)
        W_full = np.linalg.inv(x) @ (Phi_Rk @ Z_orig.T)
        # intercept行(0)は除去しない
        W_full[0, :] = 0
        # すべてのカテゴリ行をそのまま差し引く
        Z_corr -= W_full.T @ Phi_Rk
    Z_cos = Z_corr / np.linalg.norm(Z_corr, ord=2, axis=0, keepdims=True)
    return Z_cos, Z_corr, W_full, Phi_Rk


def moe_correct_ridge_partial(Z_orig, Z_cos, Z_corr, R, W, K, Phi_Rk, Phi_moe, lamb, partial_remove_idx):
    """Partial correction version:
      - W is fit using *all* variables (batch + condition).
      - Only the rows of W corresponding to 'partial_remove_idx' are subtracted.
      - Condition rows are not subtracted.

    partial_remove_idx : list of integers
      The row indices in [1..B] (excluding 0 for intercept) that correspond
      to the batch variables we want to remove.
    """
    Z_corr = Z_orig.copy()
    N = Z_orig.shape[1]
    for i in range(K):
        Phi_Rk = np.multiply(Phi_moe, R[i, :])  # shape(B+1, N)
        x = np.dot(Phi_Rk, Phi_moe.T) + lamb
        W_full = np.linalg.inv(x) @ (Phi_Rk @ Z_orig.T)
        # interceptは除外(=差し引かない)
        W_full[0, :] = 0

        # 部分的に差し引く行だけ抽出
        # 例: partial_remove_idx=[1,2] => W_tempは1,2行のみW_fullが入り、他は0
        W_temp = np.zeros_like(W_full)
        W_temp[partial_remove_idx, :] = W_full[partial_remove_idx, :]

        Z_corr -= W_temp.T @ Phi_Rk

    Z_cos = Z_corr / np.linalg.norm(Z_corr, ord=2, axis=0, keepdims=True)
    return Z_cos, Z_corr, W_full, Phi_Rk
