"""ContinuousVI module for scRNA-seq data analysis.

This module provides classes and methods to train and utilize scVI models for
single-cell RNA-seq data. It supports the inclusion of continuous covariates
(e.g., pseudotime in trajectory analysis, aging or other continuous measurements) while correcting for batch
effects. The main classes are:

- ContinuousVI: Sets up the anndata object and trains multiple scVI models.
- TrainedContinuousVI: Manages one or more trained scVI models, provides methods
  for generating embeddings, sampling expression parameters, and performing
  regression analysis.
"""

from __future__ import annotations

import math
import os
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import patsy
import pyro
import pyro.distributions as dist
import scanpy as sc
import scipy.sparse as sp
import scipy.stats
import scvi
import statsmodels.api as sm
import torch
from pygam import LinearGAM, s
from pyro.infer import MCMC, NUTS
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
from statsmodels.nonparametric.smoothers_lowess import lowess
from tqdm import tqdm
from tqdm.auto import tqdm
from lightning.pytorch.accelerators import Accelerator
from .continuous_harmony import run_continuous_harmony

if TYPE_CHECKING:
    from scvi.distributions import ZeroInflatedNegativeBinomial


class ContinuousVI:
    """ContinuousVI module for scRNA-seq data analysis.

    This class is responsible for configuring the input data (AnnData object)
    and training multiple scVI models to account for batch effects, label keys,
    and one optional continuous covariate. Use the `train` method to train
    multiple scVI models. The trained models can be accessed via the returned
    `TrainedContinuousVI` instance.
    """

    def __init__(
        self,
        adata: sc.AnnData,
        batch_key: str,
        label_key: str | None,
        continuous_key: str | None,
        devices: int | list[int] | str = "auto",
        accelerator: str | Accelerator | None = None,
    ) -> None:
        """Initialize a ContinuousVI object.

        Parameters
        ----------
        adata : sc.AnnData
            The annotated data matrix with cells (observations) and genes (variables).
        batch_key : str
            The column name in `adata.obs` that contains batch information.
        label_key : str or None
            The column name in `adata.obs` that contains label or cell-type information.
            If None, no label covariate is used.
        continuous_key : str or None
            The column name in `adata.obs` that contains a single continuous covariate
            (e.g., pseudotime). If None, no continuous covariate is used.

        """
        self.adata: sc.AnnData = adata
        self.batch_key: str = batch_key
        self.label_key: str | None = label_key
        self.continuous_key: str | None = continuous_key
        self.devices: int | list[int] | str = devices
        self.accelerator: str | Accelerator | None = accelerator

    def train(
        self,
        n_train: int = 5,
        n_latent: int = 30,
        max_epochs: int = 800,
        early_stopping: bool = True,
        weight_decay: float | None = None,
    ) -> TrainedContinuousVI:
        """Train multiple scVI models (n_train times) and return a TrainedContinuousVI object.

        This method sets up the scVI anndata configuration once per training run
        and trains `n_train` scVI models with the same hyperparameters but
        potentially different random initializations.

        Parameters
        ----------
        n_train : int, default=5
            The number of times to train scVI with the same setup.
        n_latent : int, default=30
            The dimensionality of the scVI latent space (z).
        max_epochs : int, default=800
            The maximum number of training epochs.
        early_stopping : bool, default=True
            Whether to apply early stopping based on validation loss improvements.

        Returns
        -------
        TrainedContinuousVI
            A TrainedContinuousVI object containing the trained scVI models,
            allowing further analysis and model usage.

        """
        _trained_models: list[scvi.model.SCVI] = []
        plan_kw = {"weight_decay": weight_decay} if weight_decay is not None else None
        for i in range(n_train):
            print(f"Training model {i+1}/{n_train}...")
            scvi.model.SCVI.setup_anndata(
                self.adata,
                batch_key=self.batch_key,
                labels_key=self.label_key,
                continuous_covariate_keys=[self.continuous_key] if self.continuous_key else None,
            )
            model = scvi.model.SCVI(
                self.adata,
                n_latent=n_latent,
                encode_covariates=True,
            )
            model.train(
                max_epochs=max_epochs,
                early_stopping=early_stopping,
                devices=self.devices, accelerator=self.accelerator,
                plan_kwargs=plan_kw,
            )
            _trained_models.append(model)
        return TrainedContinuousVI(adata=self.adata, batch_key=self.batch_key, label_key=self.label_key, continuous_key=self.continuous_key, trained_models=_trained_models, devices=self.devices, accelerator=self.accelerator)


class TrainedContinuousVI:
    """TrainedContinuousVI manages one or more trained scVI models for scRNA-seq data.

    This class provides methods to:
    - Load or store multiple trained scVI models.
    - Calculate embeddings (UMAP, clusters) using the latent representation.
    - Perform regressions against the continuous covariate.
    - Sample parameters from the generative model (px).
    - Save the trained models to disk.
    """

    @overload
    def __init__(
        self,
        adata: sc.AnnData,
        batch_key: str,
        label_key: str | None,
        continuous_key: str | None,
        trained_models: list[scvi.model.SCVI],
        devices: int | list[int] | str = "auto",
        accelerator: str | Accelerator | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        adata: sc.AnnData,
        batch_key: str,
        label_key: str | None,
        continuous_key: str | None,
        trained_model_path: Path | str,
        devices: int | list[int] | str = "auto",
        accelerator: str | Accelerator | None = None,
    ) -> None: ...

    def __init__(
        self,
        adata: sc.AnnData,
        batch_key: str,
        label_key: str | None,
        continuous_key: str | None,
        trained_models: list[scvi.model.SCVI] | None = None,
        trained_model_path: Path | str | None = None,
        devices: int | list[int] | str = "auto",
        accelerator: str | Accelerator | None = None,
    ) -> None:
        """Initialize a TrainedContinuousVI object with trained scVI models or a path to load them.

        Parameters
        ----------
        adata : sc.AnnData
            The annotated data matrix used for model training or inference.
        batch_key : str
            The column name in `adata.obs` for batch information.
        label_key : str or None
            The column name in `adata.obs` for label or cell-type information.
        continuous_key : str or None
            The column name in `adata.obs` for continuous covariate information.
        trained_models : list[scvi.model.SCVI], optional
            A list of scVI models that have already been trained.
        trained_model_path : Path or str, optional
            Path to a directory that contains one or more trained scVI models.
            If provided, the models at this path will be loaded instead of using
            `trained_models`.

        Raises
        ------
        ValueError
            If both `trained_models` and `trained_model_path` are None.

        """
        self.adata = adata
        self.batch_key: str = batch_key
        self.label_key: str | None = label_key
        self.continuous_key: str | None = continuous_key
        self.devices = devices
        self.accelerator = accelerator
        scvi.model.SCVI.setup_anndata(
            adata=adata,
            batch_key=batch_key,
            labels_key=label_key,
            continuous_covariate_keys=[continuous_key] if continuous_key is not None else None,
        )

        if trained_models is None and trained_model_path is None:
            raise ValueError(
                "`trained_models` or `trained_model_path` is required. Both are None.",
            )

        if trained_models is None and trained_model_path is not None:
            _trained_model_paths = [p for p in (trained_model_path if isinstance(trained_model_path, Path) else Path(trained_model_path)).rglob("*") if p.is_dir()]
            _trained_models: list[scvi.model.SCVI] = [scvi.model.SCVI.load(str(p), adata) for p in _trained_model_paths]
            print(f"Loaded {len(_trained_models)} pre-trained models")
        else:
            _trained_models = trained_models

        self.trained_models = _trained_models
        # ── patches for deprecated aliases used by pygam ───────────────────────────
        for _al, _py in {"int": int, "float": float, "bool": bool}.items():
            if not hasattr(np, _al):
                setattr(np, _al, _py)
        if not hasattr(sp.spmatrix, "A"):
            sp.spmatrix.A = property(lambda self: self.toarray())
        self._embeddings: TrainedContinuousVI.Embeddings | None = None

    @property
    def embeddings(self) -> TrainedContinuousVI.Embeddings:
        """Return the Embeddings object for visualizations and further downstream analyses.

        Returns
        -------
        TrainedContinuousVI.Embeddings
            An Embeddings object that provides methods such as `umap` for
            generating UMAP plots.

        Raises
        ------
        ValueError
            If embeddings have not been computed yet. Please call
            `calc_embeddings()` first.

        """
        if self._embeddings is None:
            raise ValueError(
                "No Embeddings object found. Please execute `calc_embeddings()` first.",
            )
        return self._embeddings

    def latent_coord(
        self,
        n_use_model: int = 0,
        use_clusteringbased_correction: bool = False,
    ) -> np.ndarray:
        """Return the latent coordinates from one of the trained scVI models.

        Parameters
        ----------
        n_use_model : int, default=0
            The index of the trained model in `self.trained_models` to use for
            obtaining the latent representation.

        Returns
        -------
        numpy.ndarray
            A 2D array of shape (n_cells, n_latent) containing the latent representation.

        """
        arr: np.ndarray = self.trained_models[n_use_model].get_latent_representation(
            adata=self.adata,
        )
        if use_clusteringbased_correction:
            if self.continuous_key is None:
                ho = run_continuous_harmony(
                    data_mat=arr.T,
                    meta_data=self.adata.obs,
                    vars_use=[self.batch_key],
                    remove_vars=[self.batch_key],
                )
            else:
                ho = run_continuous_harmony(
                    data_mat=arr.T,
                    meta_data=self.adata.obs,
                    vars_use=[self.batch_key, self.continuous_key],
                    remove_vars=[self.batch_key],
                )
            arr = ho.result().T
        return arr

    def calc_embeddings(
        self,
        resolution: float = 0.5,
        n_neighbors: int = 10,
        n_pcs: int = 30,
        n_use_model: int = 0,
        use_clusteringbased_correction: bool = False,
    ) -> TrainedContinuousVI:
        """Calculate embeddings and cluster labels using the latent space.

        This method:
        - Stores the latent coordinates in `adata.obsm["X_latent"]`.
        - Computes neighborhood graphs using `scanpy.pp.neighbors`.
        - Performs draw_graph, leiden clustering, paga, and UMAP embedding.
        - Creates an `Embeddings` object that can be used for plotting.

        Parameters
        ----------
        resolution : float, default=0.5
            Resolution parameter for the leiden clustering. Higher values lead to
            more granular clustering.
        n_neighbors : int, default=10
            Number of neighbors to use for building the k-NN graph.
        n_pcs : int, default=30
            Number of principal components to use for neighborhood computation (if applicable).
        n_use_model : int, default=0
            The index of the trained model to use when extracting latent coordinates.
        use_clusteringbased_correction : bool, default = False
            Use clustering based (harmony) correction?

        Returns
        -------
        TrainedContinuousVI
            The TrainedContinuousVI instance with updated embeddings in `adata.obsm`
            and a newly created `Embeddings` object (`self._embeddings`).

        """
        KEY_LATENT = "X_latent"
        KEY_CLUSTER = "clusters"
        self.adata.obsm[KEY_LATENT] = self.latent_coord(
            n_use_model,
            use_clusteringbased_correction,
        )
        sc.pp.neighbors(
            self.adata,
            n_neighbors=n_neighbors,
            n_pcs=n_pcs,
            use_rep=KEY_LATENT,
        )
        sc.tl.draw_graph(self.adata)
        sc.tl.leiden(
            self.adata,
            key_added=KEY_CLUSTER,
            resolution=resolution,
            directed=False,
        )
        sc.tl.paga(self.adata, groups=KEY_CLUSTER)
        sc.tl.umap(self.adata)
        self._embeddings = TrainedContinuousVI.Embeddings(self)
        return self

    def save(
        self,
        dir_path: Path | str,
        overwrite: bool = False,
    ) -> TrainedContinuousVI:
        """Save the trained models to the specified directory.

        Each model is saved in a subdirectory named `model_{i}` where `i`
        is the index of the model. For example, if there are 5 models in
        `self.trained_models`, subdirectories `model_0, model_1, ... model_4`
        will be created.

        Parameters
        ----------
        dir_path : Path or str
            The directory path where the models will be saved.
        overwrite : bool, default=False
            Whether to overwrite existing models at the target path if a
            model directory already exists.

        Returns
        -------
        TrainedContinuousVI
            The TrainedContinuousVI instance (self) for chained operations.

        """
        _base_path = dir_path if isinstance(dir_path, Path) else Path(dir_path)
        for n in range(len(self.trained_models)):
            print(f"Saving model {n+1}/{len(self.trained_models)}...")
            _path = _base_path / Path(f"model_{n}")
            self.trained_models[n].save(_path, overwrite=overwrite)
        return self

    def sample_px(
        self,
        transform_batch: int = 0,
        use_inference_library: bool = True,
        n_draw: int = 25,
        batch_size: int = 512,
        mean: bool = True,
        device: str | torch.device | None = None,
        predict_age: float | np.ndarray | None = None,
        library_size: int = 1e4,
    ) -> torch.Tensor:
        """Return model-corrected `px` means for every cell.

            The function removes **both** batch effects and library-size variation,
            making the output directly comparable across projects/batches.

        Parameters
        ----------
            transform_batch : int, default = 0
                Index of the reference batch to which *all* cells are virtually
                transformed during the generative step.
            n_draw : int, default = 25
                Number of Monte-Carlo stochastic forward passes.  Larger values
                reduce sampling noise at the cost of runtime.
            batch_size : int, default = 512
                Mini-batch size for inference / generative forward passes.  Choose a
                value that fits comfortably in GPU/CPU memory.
            mean : bool, default = True
                If ``True`` (default) the function returns the average over all
                draws with shape ``(n_cells, n_genes)``.  If ``False`` the full
                tensor with shape ``(n_draw, n_cells, n_genes)`` is returned.
                use_inference_library : bool, default = False
            True  : generative step uses the **cell-specific library size**
                    estimated in the inference step (μ is in *count* scale).
            False : generative step replaces the library with its **median**
                    across the mini-batch (μ is a *gene fraction*, sum≈1).
        library_size : int, default = 10000
            Constant multiplier applied to the returned tensor so that every
            model (Raw/scVI/ContinuousVI) can be compared on a common
            “counts per 10 k” scale.

        Returns
        -------
            torch.Tensor
                * shape ``(n_cells, n_genes)`` when ``mean=True``
                * shape ``(n_draw, n_cells, n_genes)`` when ``mean=False``

        Notes
        -----
            1. **Inference** is executed with each cell’s *original* batch index so
            that the latent variables `z` and the cell-specific library size
            estimate are consistent with the raw data.
            2. **Generative** step uses:
                • ``batch_index = transform_batch`` (batch effects removed)
                • ``library = median(inference_library)`` (library-size normalised)
            3. If multiple models are held in ``self.trained_models`` their outputs
            are averaged first, then the `n_draw` draws are averaged when
            ``mean=True``.

        """
        # ----------------------------- device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        device = torch.device(device)

        # ----------------------------- move models
        for m in self.trained_models:
            if m.module is None:
                raise ValueError("Found an un-initialised model.")
            m.module.to(device).eval()

        # ----------------------------- data on device
        adata = self.adata
        n_cells, n_genes = adata.n_obs, adata.n_vars
        cont_key = "_scvi_extra_continuous_covs"

        x_arr = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
        x_full = torch.as_tensor(x_arr, dtype=torch.float32, device=device)

        b_arr = adata.obs["_scvi_batch"].to_numpy()
        batch_idx = torch.as_tensor(b_arr, dtype=torch.int64, device=device).unsqueeze(1)

        cont_arr = adata.obsm[cont_key]
        if not isinstance(cont_arr, np.ndarray):
            cont_arr = cont_arr.to_numpy()
        cont_covs = torch.as_tensor(cont_arr, dtype=torch.float32, device=device)

        # ----------------------------- age override ★
        if predict_age is not None:
            if np.isscalar(predict_age):
                cont_covs[:, 0] = float(predict_age)  # age = 1 列目想定
            else:
                if len(predict_age) != n_cells:
                    raise ValueError("predict_age length mismatch.")
                cont_covs[:, 0] = torch.as_tensor(np.asarray(predict_age, dtype=np.float32), device=device)

        # ----------------------------- output buffer
        px_samples = torch.empty((n_draw, n_cells, n_genes), dtype=torch.float32, device=device)
        all_idx = torch.arange(n_cells, device=device)

        # ----------------------------- sampling loop
        for d in range(n_draw):
            acc = torch.zeros((n_cells, n_genes), dtype=torch.float32, device=device)

            for model in self.trained_models:
                for st in range(0, n_cells, batch_size):
                    ed = min(st + batch_size, n_cells)
                    idx = all_idx[st:ed]

                    with torch.no_grad():
                        # ----- inference
                        inf = model.module.inference(
                            x=x_full[idx],
                            batch_index=batch_idx[idx],
                            cont_covs=cont_covs[idx],  # age 上書き適用
                            cat_covs=None,
                        )
                        z = inf["z"]
                        lib_infer = inf["library"]

                        # ----- generative
                        if use_inference_library:
                            lib_use = lib_infer  # ★ ここが変更点
                        else:
                            lib_med = torch.median(lib_infer).item()
                            lib_use = torch.full_like(lib_infer, lib_med)
                        # lib_med = torch.median(inf["library"]).item()
                        gen = model.module.generative(
                            z=z,
                            library=lib_use,
                            batch_index=torch.full_like(batch_idx[idx], transform_batch),
                            cont_covs=cont_covs[idx],  # age 上書き適用
                            cat_covs=None,
                        )

                    acc[idx] += gen["px"].mean

            px_samples[d] = acc / len(self.trained_models)

        out = px_samples.mean(0) if mean else px_samples
        return out.cpu() * library_size

    @staticmethod
    def _default_params(method: str, n: int) -> dict[str, Any]:
        """Return robust defaults even when n is very small (≥ 3)."""
        if n < 3:  # cannot smooth < 3 points
            return {"force_raw": True}

        if method == "moving_average":
            win = int(np.clip(round(n * 0.15), 3, n))  # allow even window
            return {"window": win}

        if method == "savitzky":
            # window must be odd and > polyorder
            win = int(np.clip(round(n * 0.15) | 1, 5, n if n % 2 else n - 1))
            poly = 2 if win > 2 else 1
            return {"window": win, "polyorder": poly}

        if method == "loess":
            # span so that at least 3 pts are used
            frac = max(3 / n, 0.1)
            return {"frac": min(frac, 0.8)}

        if method == "gam":
            n_spl = max(4, min(n - 1, 25))
            return {"gam_splines": n_spl, "lam": 0.6}

        if method == "glm":
            return {}

        return {}

    @staticmethod
    def apply_smoothing(
        y: np.ndarray,
        *,
        x: np.ndarray | None = None,
        method: Literal[None, "moving_average", "savitzky", "loess", "gam", "glm"] | None = None,
        **kw: Any,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """Return (smoothed, se). *se* is only for GLM."""
        if method is None or np.isnan(y).all():
            return y, None

        n = y.size
        defaults = TrainedContinuousVI._default_params(method, n)
        if defaults.get("force_raw"):
            return y, None

        for k, v in defaults.items():
            kw.setdefault(k, v)

        x_idx = np.asarray(x if x is not None else np.arange(n), float)

        # interpolation for local smoothers
        if method in {"moving_average", "savitzky", "loess", "gam"}:
            y_fill = pd.Series(y).interpolate("linear").bfill().ffill().to_numpy()

        if method == "moving_average":
            w = kw["window"]
            pad = w // 2
            ker = np.full(w, 1 / w)
            y_sm = np.convolve(np.pad(y_fill, (pad, pad), mode="edge"), ker, mode="valid")
            se = None

        elif method == "savitzky":
            y_sm = savgol_filter(y_fill, kw["window"], kw["polyorder"])
            se = None

        elif method == "loess":
            y_sm = lowess(y_fill, x_idx, frac=kw["frac"], return_sorted=False)
            se = None

        elif method == "gam":
            gam = LinearGAM(s(0, n_splines=kw["gam_splines"]), lam=kw["lam"]).fit(x_idx[:, None], y_fill)
            y_sm = gam.predict(x_idx[:, None])
            se = None

        elif method == "glm":
            mask = ~np.isnan(y)
            x_non, y_non = x_idx[mask], y[mask]
            shift = max(0.0, 1e-6 - x_non.min())  # log safety
            X = sm.add_constant(np.log(x_non + shift))
            res = sm.GLM(y_non, X, family=sm.families.Gaussian()).fit()
            X_all = sm.add_constant(np.log(x_idx + shift))
            pred = res.get_prediction(X_all)
            y_sm, se = pred.predicted_mean, pred.se_mean

        else:  # pragma: no cover
            raise ValueError("Unknown method")

        y_sm[np.isnan(y)] = np.nan
        if se is not None:
            se[np.isnan(y)] = np.nan
        return y_sm, se

    def plot_px_expression(
        self,
        target_genes: Sequence[str],
        *,
        mode: Literal["px", "raw"] = "px",
        continuous_key: str = "age",
        batch_key: str = "project",
        transform_batch: str | None = None,
        n_draws: int = 25,
        stabilize_log1p: bool = False,
        summary_stat: Literal["median", "mean"] = "median",
        ci: float = 0.80,
        ribbon_source: Literal["ci", "quantile"] = "ci",
        ci_method: Literal["t", "bootstrap"] = "t",
        n_bootstrap: int = 2000,
        ribbon_style: Literal["uniform", "gradient"] = "gradient",
        n_quantile_bands: int = 5,
        cmap_name: str = "viridis",
        line_color: str = "black",
        line_width: float = 2.5,
        outline: bool = True,
        outline_width: float = 5,
        outline_color: str = "white",
        marker_size: int = 50,
        summarise: bool = False,
        summarise_label: str | None = None,
        summarise_fn: Literal["sum", "mean"] = "sum",
        smoothing: Literal[None, "moving_average", "savitzky", "loess", "gam", "glm"] | None = None,
        smoothing_kwargs: dict[str, Any] | None = None,
        extrapolate_grid: Sequence[float] | None = None,
        device: str | torch.device | None = None,
    ) -> None:
        """Plot expression vs. covariate with adaptive smoothing and confidence intervals.

        Parameters
        ----------
        target_genes : Sequence[str]
            Gene names to plot.
        mode : Literal["px", "raw"], default="px"
            Expression mode - "px" for model-corrected expression, "raw" for raw counts.
        continuous_key : str, default="age"
            Column name in adata.obs for continuous covariate.
        batch_key : str, default="project"
            Column name in adata.obs for batch information.
        transform_batch : str, optional
            Batch to transform to for px mode.
        n_draws : int, default=25
            Number of draws for px sampling.
        stabilize_log1p : bool, default=False
            Whether to apply log1p transformation.
        summary_stat : Literal["median", "mean"], default="median"
            Central tendency statistic to plot.
        ci : float, default=0.80
            Confidence level for ribbons (0.80 = 80% confidence).
        ribbon_source : Literal["ci", "quantile"], default="ci"
            Source of ribbon bounds:
            - "ci": Confidence intervals for the central statistic
            - "quantile": Quantile bands showing data distribution
        ci_method : Literal["t", "bootstrap"], default="t"
            Method for calculating confidence intervals:
            - "t": Student's t-distribution (mean only)
            - "bootstrap": Non-parametric bootstrap (mean or median)
        n_bootstrap : int, default=2000
            Number of bootstrap resamples when using bootstrap CI.
        ribbon_style : Literal["uniform", "gradient"], default="gradient"
            Style of ribbon visualization:
            - "uniform": Single ribbon band
            - "gradient": Multiple gradient bands (quantile source only)
        n_quantile_bands : int, default=5
            Number of quantile bands for gradient style.
        cmap_name : str, default="viridis"
            Colormap name for gradient ribbons.
        line_color : str, default="black"
            Color for central line.
        line_width : float, default=2.5
            Width of central line.
        outline : bool, default=True
            Whether to draw outline around central line.
        outline_width : float, default=5
            Width of outline.
        outline_color : str, default="white"
            Color of outline.
        marker_size : int, default=50
            Size of raw data markers.
        summarise : bool, default=False
            Whether to summarise multiple genes.
        summarise_label : str, optional
            Label for summarised gene set.
        summarise_fn : Literal["sum", "mean"], default="sum"
            Function for gene summarisation.
        smoothing : Literal[None, "moving_average", "savitzky", "loess", "gam", "glm"], optional
            Smoothing method for central line.
        smoothing_kwargs : dict, optional
            Additional arguments for smoothing method.
        extrapolate_grid : Sequence[float], optional
            Grid points for model extrapolation.
        device : str or torch.device, optional
            Device for computation.

        Notes
        -----
        - Default behavior uses confidence intervals (ribbon_source="ci") with t-distribution method
        - For median summary statistics, use bootstrap method for proper CI calculation
        - Gradient ribbon style only works with quantile source
        - CI ribbons show uncertainty in the central statistic estimate
        - Quantile ribbons show the distribution of individual data points
        """
        smoothing_kwargs = smoothing_kwargs or {}

        # Input validation
        if ribbon_source not in {"ci", "quantile"}:
            raise ValueError(f"ribbon_source must be 'ci' or 'quantile', got {ribbon_source!r}")
        if ci_method not in {"t", "bootstrap"}:
            raise ValueError(f"ci_method must be 't' or 'bootstrap', got {ci_method!r}")
        if ribbon_source == "ci" and ribbon_style == "gradient":
            import warnings
            warnings.warn("Gradient style not supported for CI ribbons; falling back to uniform.", UserWarning)
            ribbon_style = "uniform"

        adata = self.adata
        x_vals = adata.obs[continuous_key].to_numpy()
        idx = [int(np.where(adata.var_names == g)[0][0]) for g in target_genes]

        # ========== expression matrix (raw) ========================
        if mode == "px":
            tb_idx = 0
            if transform_batch is not None:
                cats = list(pd.Categorical(adata.obs[batch_key]).categories)
                if transform_batch not in cats:
                    raise ValueError(f"{transform_batch!r} not in '{batch_key}'.")
                tb_idx = cats.index(transform_batch)
            px = self.sample_px(transform_batch=tb_idx, n_draw=n_draws, batch_size=512, device=device)
            expr = (px.cpu().numpy() if hasattr(px, "cpu") else np.asarray(px))[:, idx]
        else:
            sub = adata[:, idx].X
            expr = sub.toarray() if sp.issparse(sub) else np.asarray(sub)

        if stabilize_log1p:
            expr = np.log1p(expr)
            y_label = "log1p(px)" if mode == "px" else "log1p(raw)"
        else:
            y_label = "px mean" if mode == "px" else "raw counts"

        # ========== summarise gene set =============================
        if summarise:
            collapsed = expr.sum(axis=1) if summarise_fn == "sum" else expr.mean(axis=1)
            expr = collapsed[:, None]
            target_genes = [summarise_label or f"{summarise_fn.capitalize()} ({len(idx)} genes)"]

        # ========== figure grid ====================================
        n_genes = len(target_genes)
        ncols = 3 if not summarise else 1
        nrows = math.ceil(n_genes / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), squeeze=False)
        axes = axes.ravel()

        cmap = mpl.cm.get_cmap(cmap_name, 2 * n_quantile_bands + 1) if ribbon_style == "gradient" else None
        unique_x = np.sort(np.unique(x_vals))
        alpha = 1 - ci

        # Setup for quantile ribbons (backward compatibility)
        if ribbon_source == "quantile":
            q_low, q_high = alpha / 2, 1 - alpha / 2
            band_probs = np.linspace(q_low, 0.5, n_quantile_bands, endpoint=False) if ribbon_style == "gradient" else None
        else:
            q_low = q_high = band_probs = None

        # CI calculation functions
        def calculate_ci_t(subset, summary_stat, alpha):
            """Calculate confidence interval using t-distribution."""
            n = subset.size
            if n <= 1:
                return np.nan, np.nan

            if summary_stat == "mean":
                m = subset.mean()
                se = subset.std(ddof=1) / np.sqrt(n)
                t_crit = scipy.stats.t.ppf(1 - alpha/2, df=n-1)
                return m - t_crit * se, m + t_crit * se
            else:
                # Median t-CI is not well-defined, warn and return NaN
                import warnings
                warnings.warn("t-distribution CI for median is not well-defined. Use bootstrap method instead.", UserWarning)
                return np.nan, np.nan

        def calculate_ci_bootstrap(subset, summary_stat, alpha, n_bootstrap):
            """Calculate confidence interval using bootstrap."""
            n = subset.size
            if n <= 1:
                return np.nan, np.nan

            stat_func = np.mean if summary_stat == "mean" else np.median
            try:
                res = scipy.stats.bootstrap(
                    (subset,),
                    statistic=stat_func,
                    confidence_level=ci,
                    n_resamples=n_bootstrap,
                    method="basic",
                    vectorized=False,
                    batch=None,
                )
                return res.confidence_interval.low, res.confidence_interval.high
            except Exception:
                # Fallback to NaN if bootstrap fails
                return np.nan, np.nan

        # ===========================================================
        # plotting loop
        # ===========================================================
        for ax, gi, gene in zip(axes, range(n_genes), target_genes, strict=False):
            y = expr[:, gi]
            central, low, high = [], [], []
            if ribbon_source == "quantile" and ribbon_style == "gradient":
                lower_grid = np.empty((n_quantile_bands, unique_x.size))
                upper_grid = np.empty_like(lower_grid)

            for j, xv in enumerate(unique_x):
                subset = y[x_vals == xv]
                if subset.size:
                    cen = np.median(subset) if summary_stat == "median" else np.mean(subset)

                    # Calculate ribbon bounds based on ribbon_source
                    if ribbon_source == "ci":
                        if ci_method == "t":
                            lo, hi = calculate_ci_t(subset, summary_stat, alpha)
                        else:  # bootstrap
                            lo, hi = calculate_ci_bootstrap(subset, summary_stat, alpha, n_bootstrap)
                    else:  # quantile
                        lo, hi = np.quantile(subset, [q_low, q_high])
                        if ribbon_style == "gradient":
                            for b, p in enumerate(band_probs):
                                lower_grid[b, j], upper_grid[b, j] = np.quantile(subset, [p, 1 - p])
                else:
                    cen = lo = hi = np.nan
                    if ribbon_source == "quantile" and ribbon_style == "gradient":
                        lower_grid[:, j] = upper_grid[:, j] = np.nan
                central.append(cen)
                low.append(lo)
                high.append(hi)

            central_raw = np.asarray(central, float)

            # ---------- smoothing or model extrapolation ------------
            if extrapolate_grid is not None:
                grid = np.asarray(extrapolate_grid, float)

                y_grid = []  # list[(draws,)]
                for a in grid:
                    px = self.sample_px(
                        predict_age=float(a),
                        n_draw=n_draws,
                        mean=False,
                        device=device,
                    )[:, :, gi]  # (draws, cells)
                    px = px.mean(1)  # ★ セル平均 → (draws,)
                    if stabilize_log1p:
                        px = np.log1p(px)
                    y_grid.append(px)

                y_grid = np.stack(y_grid, axis=1)  # (draws, len(grid))
                y_mean = y_grid.mean(0)  # (len(grid),)

                # Calculate confidence bounds for extrapolation
                if ribbon_source == "ci":
                    y_lo, y_hi = np.quantile(y_grid, [alpha/2, 1 - alpha/2], axis=0)
                else:  # quantile
                    y_lo, y_hi = np.quantile(y_grid, [q_low, q_high], axis=0)

                ax.fill_between(grid, y_lo, y_hi, color=line_color, alpha=0.15, zorder=2)
                ax.plot(grid, y_mean, lw=line_width, color=line_color, zorder=3, label="model extrapolation")
                se_sm = None

            else:
                central_sm, se_sm = TrainedContinuousVI.apply_smoothing(central_raw, x=unique_x, method=smoothing, **smoothing_kwargs)
                if outline:
                    ax.plot(unique_x, central_sm, lw=outline_width, color=outline_color, zorder=4)
                ax.plot(unique_x, central_sm, lw=line_width, color=line_color, zorder=5)

            # ---------- variability ribbons from raw data -----------
            if ribbon_style == "uniform":
                ax.fill_between(unique_x, low, high, alpha=0.30, color="grey", zorder=1)
            elif ribbon_style == "gradient" and ribbon_source == "quantile":
                for b in range(n_quantile_bands - 1, -1, -1):
                    ax.fill_between(unique_x, lower_grid[b], upper_grid[b], color=cmap(b + n_quantile_bands + 1), alpha=0.70, zorder=1 + b)

            # ---------- ±1 SE ribbon for GLM ------------------------
            if se_sm is not None:
                ax.fill_between(unique_x, central_sm - se_sm, central_sm + se_sm, color=line_color, alpha=0.15, zorder=3)

            # ---------- raw markers --------------------------------
            ax.scatter(unique_x, central_raw, s=marker_size, color=line_color, zorder=6, edgecolors="none")

            ax.set_title(gene)
            ax.set_xlabel(continuous_key)
            ax.set_ylabel(y_label)

        for ax in axes[n_genes:]:
            ax.axis("off")
        fig.tight_layout()


    def regression(
        self,
        transform_batch: int = 0,
        stabilize_log1p: bool = True,
        mode: Literal["ols", "poly2", "spline"] = "ols",
        n_samples: int = 25,
        batch_size: int = 512,
        spline_df: int = 5,
        spline_degree: int = 3,
        use_mcmc: bool = True,
        use_raw: bool = False,
        mcmc_warmup: int = 500,
        mcmc_num_samples: int = 1000,
        mcmc_num_chains: int | None = None,
        mcmc_max_threads: int | None = None,
        library_size: int = 1e4,
    ) -> pd.DataFrame:
        """
        Gene‑wise regression on a continuous covariate *with an improved full‑MCMC option*.

        Differences from the original version
        -------------------------------------
        * 全ドローを plate 化して MCMC に投入
        * 連続共変量を Z‑score 標準化
        * より情報的な階層事前 (Normal/HalfNormal, weak‑to‑moderate)
        * チェーン数・サンプル数を十分に確保 (収束診断しやすい)
        * gene plate はチャンク分割しつつ μ, τ を全遺伝子で共有
        * target_accept_prob=0.9 で発散を抑制
        """
        # ------------------------------------------------------------------------------
        # 0. checks & aliases
        # ------------------------------------------------------------------------------
        if self.continuous_key is None:
            raise ValueError("continuous_key must be set in the model.")
        if mode not in {"ols", "poly2", "spline"}:
            raise ValueError("mode must be 'ols', 'poly2', or 'spline'.")

        adata = self.adata
        n_cells, n_genes = adata.n_obs, adata.n_vars
        gene_names = adata.var_names.to_numpy()

        x_raw = adata.obs[self.continuous_key].astype(float).to_numpy()
        x_mean, x_std = x_raw.mean(), x_raw.std(ddof=0)
        x_c = (x_raw - x_mean) / (x_std + 1e-8)           # ---- ★ Z‑score 標準化

        # ------------------------------------------------------------------------------
        # 1. expression tensor: shape (draws, cells, genes)
        # ------------------------------------------------------------------------------
        if use_raw:
            mat = adata.X.toarray() if sp.issparse(adata.X) else adata.X
            expr = mat.astype(float)[None, ...]            # (1, cells, genes)
            n_draws = 1
            use_mcmc = False                               # raw ⇒ 強制 OLS
        else:
            px_stack = self.sample_px(
                transform_batch=transform_batch,
                n_draw=n_samples,
                batch_size=batch_size,
                mean=False,
                library_size=library_size,
            )
            expr = px_stack.cpu().numpy()                  # (draws, cells, genes)
            n_draws = n_samples

        if stabilize_log1p:
            expr = np.log1p(expr)

        # ------------------------------------------------------------------------------
        # 2. design matrix  (cells × P)
        # ------------------------------------------------------------------------------
        if mode == "ols":
            X_design = sm.add_constant(x_c)
            design_cols = ["Intercept", "Slope_std"]       # slope は標準化スケール
        elif mode == "poly2":
            X_design = np.vstack([x_c**2, x_c, np.ones_like(x_c)]).T
            design_cols = ["Coef_x2", "Coef_x1_std", "Intercept"]
        else:  # spline
            dm = patsy.dmatrix(
                f"bs(x, df={spline_df}, degree={spline_degree}, include_intercept=True)",
                {"x": x_c},
                return_type="dataframe",
            )
            X_design = dm.to_numpy()
            design_cols = dm.columns.tolist()

        # helper for summarising draws
        def _summarise(mat2d: np.ndarray) -> dict[str, np.ndarray]:
            return {
                "mean": mat2d.mean(0),
                "std":  mat2d.std(0, ddof=0),
                "2.5pct":  np.percentile(mat2d, 2.5, 0),
                "97.5pct": np.percentile(mat2d, 97.5, 0),
                "prob_positive": (mat2d > 0).mean(0),
            }

        # =========================================================================================
        # 3‑A. Frequentist branch  (unchanged except for x standardisation)
        # =========================================================================================
        if not use_mcmc:
            n_p = X_design.shape[1]
            coeff = np.zeros((n_draws, n_genes, n_p), dtype=np.float32)
            r2    = np.zeros((n_draws, n_genes),      dtype=np.float32)

            def _fit(args):
                d, g, y_vec = args
                res = sm.OLS(y_vec, X_design).fit()
                return d, g, res.params, res.rsquared

            jobs = [(d, g, expr[d, :, g]) for d in range(n_draws) for g in range(n_genes)]
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as ex:
                for fut in as_completed([ex.submit(_fit, j) for j in jobs]):
                    d_idx, g_idx, p_vec, rval = fut.result()
                    coeff[d_idx, g_idx] = p_vec
                    r2[d_idx, g_idx]    = rval

            summary = {"gene": gene_names}
            for j, col in enumerate(design_cols):
                s = _summarise(coeff[:, :, j])
                summary.update({f"{col}_{k}": v for k, v in s.items()})
            s_r2 = _summarise(r2)
            summary.update({f"r2_{k}": v for k, v in s_r2.items()})

            df = pd.DataFrame(summary)

            # sort helper
            sort_key = None
            if mode == "ols":
                sort_key = "Slope_std_mean"
            elif mode == "poly2":
                sort_key = "Coef_x1_std_mean"
            if sort_key in df.columns:
                df = df.sort_values(sort_key, ascending=False, ignore_index=True)

            # ---- ★ slope を元スケールへ戻す (mean, pct なども同率変換)
            if mode in {"ols", "poly2"}:
                scale_cols = [c for c in df.columns if c.startswith(("Slope_std", "Coef_x1_std"))]
                for col in scale_cols:
                    df[col] = df[col] / (x_std + 1e-8)

            return df

        # =========================================================================================
        # 3‑B. Full MCMC branch  (hierarchical Bayesian linear regression)
        # =========================================================================================
        pyro.set_rng_seed(0)
        pyro.enable_validation(False)
        torch.set_default_tensor_type(torch.FloatTensor)

        # --- prepare design & response tensors ------------------------------------
        # flatten draws × cells  →  N = n_draws * n_cells
        N = n_draws * n_cells
        X_big = np.repeat(X_design, n_draws, axis=0)          # (N, P)
        Y_big = expr.reshape(N, n_genes)                      # (N, G)

        x_t  = torch.tensor(X_big, dtype=torch.float32)       # (N, P)
        n_p  = x_t.shape[1]

        # --- threading & chunking --------------------------------------------------
        max_threads = mcmc_max_threads or max(1, (os.cpu_count() or 2) - 1)
        mcmc_num_chains = mcmc_num_chains or min(4, max_threads)

        chunk_size = int(math.ceil(n_genes / max_threads))
        chunks = [(i, min(i + chunk_size, n_genes)) for i in range(0, n_genes, chunk_size)]

        # --- hierarchical model ----------------------------------------------------
        def _model(x_mtx, y_mtx):
            """
            x_mtx : (N, P)  --- shared across genes
            y_mtx : (N, G_chunk)
            """
            N_loc, G_loc = y_mtx.shape

            # hyper‑priors
            with pyro.plate("params", n_p):
                mu   = pyro.sample("mu",   dist.Normal(0.0, 1.0))
                tau  = pyro.sample("tau",  dist.HalfNormal(1.0))

            with pyro.plate("gene", G_loc):
                beta  = pyro.sample("beta",  dist.Normal(mu, tau).to_event(1))      # (G_loc, P)
                sigma = pyro.sample("sigma", dist.HalfNormal(1.0))

            # linear predictor
            mu_y = x_mtx @ beta.T                            # (N, G_loc)

            with pyro.plate("data", N_loc):
                pyro.sample("obs", dist.Normal(mu_y, sigma), obs=y_mtx)

        # --- per‑chunk MCMC --------------------------------------------------------
        def _run_mcmc(start, end):
            y_chunk = torch.tensor(Y_big[:, start:end], dtype=torch.float32)  # (N, G')
            kernel = NUTS(
                _model,
                target_accept_prob=0.90,
                max_tree_depth=10,
                adapt_step_size=True,
            )
            mcmc = MCMC(
                kernel,
                num_samples=mcmc_num_samples,
                warmup_steps=mcmc_warmup,
                num_chains=mcmc_num_chains,
                progress_bar=False,
            )
            mcmc.run(x_t, y_chunk)

            post   = mcmc.get_samples()          # dict(β: (S, G', P), σ: (S, G'))
            beta_a = post["beta"].cpu().numpy()  # (S, G', P)
            sigma_a= post["sigma"].cpu().numpy() # (S, G')

            # R² (posterior draws × gene) ------------------------------------------
            y_np   = y_chunk.cpu().numpy()       # (N, G')
            S, G_  = beta_a.shape[:2]
            r2_a   = np.zeros((S, G_), dtype=np.float32)

            x_np = X_big                         # (N, P)
            for s in range(S):
                pred = x_np @ beta_a[s].T        # (N, G')
                ss_res = ((y_np - pred) ** 2).sum(0)
                ss_tot = ((y_np - y_np.mean(0)) ** 2).sum(0) + 1e-12
                r2_a[s] = 1.0 - ss_res / ss_tot

            # summarise -------------------------------------------------------------
            res = {"gene": gene_names[start:end]}
            for j, col in enumerate(design_cols):
                stat = _summarise(beta_a[:, :, j])
                res.update({f"{col}_{k}": v for k, v in stat.items()})
            stat_sigma = _summarise(sigma_a)
            res.update({f"sigma_{k}": v for k, v in stat_sigma.items()})
            stat_r2 = _summarise(r2_a)
            res.update({f"r2_{k}": v for k, v in stat_r2.items()})

            return pd.DataFrame(res)

        # --- run chunks in parallel ------------------------------------------------
        with ThreadPoolExecutor(max_workers=len(chunks)) as ex:
            dfs = list(as_completed([ex.submit(_run_mcmc, s, e) for s, e in chunks]))
            df_final = pd.concat([f.result() for f in dfs], axis=0, ignore_index=True)

        # --- sort & back‑transform slope ------------------------------------------
        if mode == "ols":
            key = "Slope_std_mean"
        elif mode == "poly2":
            key = "Coef_x1_std_mean"
        else:
            key = None
        if key and key in df_final.columns:
            df_final = df_final.sort_values(key, ascending=False, ignore_index=True)

        # slope → 元スケールへ
        if mode in {"ols", "poly2"}:
            scale_cols = [c for c in df_final.columns if c.startswith(("Slope_std", "Coef_x1_std"))]
            for col in scale_cols:
                df_final[col] = df_final[col] / (x_std + 1e-8)

        return df_final

    class Embeddings:
        """Embeddings class for handling dimensional reductions and plotting.

        An instance of this class is created after calling `calc_embeddings()`
        on the parent `TrainedContinuousVI` object. Provides convenience methods
        for plotting UMAP or other embeddings with gene or metadata coloring.
        """

        def __init__(self, trained_vi: TrainedContinuousVI) -> None:
            """Construct an Embeddings object.

            Parameters
            ----------
            trained_vi : TrainedContinuousVI
                The parent TrainedContinuousVI instance containing the AnnData
                and trained models.

            """
            self.trained_vi = trained_vi

        def umap(
            self,
            color_by: list[str] | None = None,
            n_draw: int = 25,
            transform_batch: int | str | None = None,
            n_use_model: int = 0,
        ) -> TrainedContinuousVI.Embeddings:
            """Plot a UMAP embedding colored by genes or metadata.

            If `color_by` contains gene names that exist in `adata.var_names`,
            expression levels are sampled from the scVI models. If `color_by`
            contains column names that exist in `adata.obs`, those columns are used
            for coloring. The resulting AnnData (with X_umap, X_latent, etc.)
            is then plotted via `scanpy.pl.umap`.

            Parameters
            ----------
            color_by : list of str, optional
                A list of gene names (in `adata.var_names`) or column names (in `adata.obs`)
                by which to color the UMAP plot.
            n_draw : int, default=25
                Number of forward passes (draws) to estimate gene expression with scVI
                for coloring genes. Ignored for categorical obs coloring.
            transform_batch : int, str, or None, default=None
                The batch to condition on when estimating normalized gene expression.
                If None, no specific batch transformation is applied.
            n_use_model : int, default=0
                The index of the trained model to use when obtaining latent coordinates
                (if needed).

            Returns
            -------
            TrainedContinuousVI.Embeddings
                The Embeddings instance (self) for potential chaining.

            """
            unique_color_by: list[str] | None = list(dict.fromkeys(color_by)) if color_by is not None else None
            _target_vars: list[str] = []
            _target_obs: list[str] = []

            if unique_color_by is not None:
                for c in unique_color_by:
                    if c in self.trained_vi.adata.var_names:
                        _target_vars.append(c)
                    elif c in self.trained_vi.adata.obs.columns:
                        _target_obs.append(c)

                expression: np.ndarray | None = None
                if len(_target_vars) > 0:
                    expression = np.mean(
                        [
                            model.get_normalized_expression(
                                self.trained_vi.adata,
                                gene_list=_target_vars,
                                n_samples=n_draw,
                                transform_batch=transform_batch,
                            )
                            for model in self.trained_vi.trained_models
                        ],
                        axis=0,
                    )

                obs_df: pd.DataFrame = self.trained_vi.adata.obs[_target_obs] if len(_target_obs) > 0 else pd.DataFrame(index=self.trained_vi.adata.obs.index)
                vars_df: pd.DataFrame | None = None
                if len(_target_vars) > 0:
                    vars_df = self.trained_vi.adata.var[self.trained_vi.adata.var.index.isin(_target_vars)]

                _adata = sc.AnnData(
                    X=expression,
                    obs=obs_df,
                    var=vars_df,
                    obsm={
                        "X_latent": self.trained_vi.latent_coord(n_use_model),
                        "X_umap": self.trained_vi.adata.obsm["X_umap"],
                    },
                )
            if color_by is not None:
                sc.pl.umap(_adata, color=color_by, show=False)
            else:
                sc.pl.umap(_adata, show=False)

            return self
