"""ContinuousTrajectory module for lineage-based pseudotime analysis in scRNA-seq data.

This module builds on the ContinuousVI/TrainedContinuousVI framework to define
and analyze multiple lineages in single-cell data. It provides methods to:

- Train scVI models (via ContinuousVI) on the data.
- Define lineages based on cell-cluster annotations.
- Calculate pseudotime within each lineage.
- Perform regression of gene expression on pseudotime.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import scanpy as sc
from tqdm import tqdm

from . import ContinuousVI, TrainedContinuousVI


class ContinuousTrajectory:
    """ContinuousTrajectory class for multi-lineage pseudotime analyses.

    This class manages:
    - An AnnData object with scRNA-seq data.
    - A trained scVI model(s) (via `TrainedContinuousVI`) for batch correction
      and latent-space analysis.
    - Defined lineages, each with a list of clusters that constitute that lineage.
    - Pseudotime calculations for each defined lineage.
    """

    def __init__(self, adata: sc.AnnData) -> None:
        """Initialize a ContinuousTrajectory object.

        Parameters
        ----------
        adata : sc.AnnData
            The annotated data matrix of shape (n_cells, n_genes). Rows correspond
            to cells and columns to genes.

        """
        self.adata: sc.AnnData = adata
        self.trainedVI: TrainedContinuousVI | None = None
        self.defined_lineages: dict[str, list[int]] | None = None
        self.pseudotimes: dict[str, pd.DataFrame] | None = None

    @staticmethod
    def _calc_iroot_idx(
        adata: sc.AnnData,
        key: str,
        value: list[str],
        latent_coord: np.ndarray,
    ) -> int:
        """Calculate an index for a root cell given cluster assignment(s) in `adata.obs`.

        This is typically used to define a "root" cell for pseudotime calculation.
        The function finds cells whose `adata.obs[key]` is in `value`, computes the
        centroid of those cells in `latent_coord`, and returns the index of the
        cell closest to that centroid.

        Parameters
        ----------
        adata : sc.AnnData
            The AnnData object containing the cells of interest.
        key : str
            The column name in `adata.obs` used to identify the root cluster(s).
        value : list of str
            The cluster identifier(s) to define as root (e.g. ["0"]).
        latent_coord : numpy.ndarray
            A 2D array of shape (n_cells, n_dimensions), typically the
            latent or PCA coordinates of cells.

        Returns
        -------
        int
            The index (row) in `adata` corresponding to the root cell.

        """
        # Identify the indices of cells belonging to the specified cluster(s)
        nsc_idxs = np.where(adata.obs[key].isin(value))[0]
        X_root_cluster = latent_coord[nsc_idxs]
        # Calculate the centroid of these cells
        centroid = X_root_cluster.mean(axis=0)
        # Compute distances from each cell to the centroid and choose the closest
        dists = np.linalg.norm(X_root_cluster - centroid, axis=1)
        return nsc_idxs[dists.argmin()]

    def train(
        self,
        batch_key: str,
        label_key: str | None,
        continuous_key: str | None,
        n_train: int,
        adata: sc.AnnData | None = None,
        n_latent: int = 30,
        max_epochs: int = 800,
        early_stopping: bool = True,
    ) -> ContinuousTrajectory:
        """Train scVI models on the provided or internal AnnData object for trajectory analysis.

        This method initializes a `ContinuousVI` instance using the given keys,
        trains `n_train` scVI models, and stores the resulting `TrainedContinuousVI`
        in `self.trainedVI`. If `adata` is not provided, the default `self.adata`
        is used.

        Parameters
        ----------
        batch_key : str
            The column name in `.obs` denoting batch assignments.
        label_key : str or None
            The column name in `.obs` for cell type or other labels. If None, no
            label covariate is used.
        continuous_key : str or None
            A column name in `.obs` for a continuous variable (e.g., pseudotime).
            If None, no continuous covariate is used during model training.
        n_train : int
            Number of times to train scVI with the same hyperparameters but
            different random initializations.
        adata : sc.AnnData or None, default=None
            If provided, use this AnnData object instead of `self.adata` for training.
        n_latent : int, default=30
            Dimensionality of the latent space for scVI.
        max_epochs : int, default=800
            The maximum number of training epochs for each training run.
        early_stopping : bool, default=True
            Whether to use early stopping.

        Returns
        -------
        ContinuousTrajectory
            The same ContinuousTrajectory object (self) with a trained
            `TrainedContinuousVI` stored in `self.trainedVI`.

        """
        _adata = adata if adata is not None else self.adata
        self.trainedVI: TrainedContinuousVI = ContinuousVI(
            _adata,
            batch_key,
            label_key,
            continuous_key,
        ).train(
            n_train=n_train,
            n_latent=n_latent,
            max_epochs=max_epochs,
            early_stopping=early_stopping,
        )
        return self

    def define_lineages(
        self,
        lineages: dict[str, list[int]],
        cluster_key: str = "clusters",
    ) -> ContinuousTrajectory:
        """Define multiple lineages based on cluster memberships in `self.adata.obs`.

        Each lineage is defined by a list of cluster IDs. Clusters can appear in
        multiple lineages. This method checks that all defined clusters exist in
        `adata.obs[cluster_key]` and that each lineage has at least two clusters.

        Parameters
        ----------
        lineages : dict of str to list of int
            A dictionary mapping a lineage name to a list of integer cluster IDs.
            Example:
            {
                "EX_neuron": [1, 6, 5],
                "Oligo": [1, 20]
            }
        cluster_key : str, default="clusters"
            The column in `adata.obs` that stores cluster assignments.

        Returns
        -------
        ContinuousTrajectory
            The same ContinuousTrajectory object (self) with the new attribute
            `self.defined_lineages` storing the provided lineages.

        Raises
        ------
        ValueError
            If any specified cluster ID in `lineages` is not found in
            `adata.obs[cluster_key]`, or if any lineage list contains fewer
            than two clusters, or if `cluster_key` does not exist in `adata.obs`.

        """
        LOW_LIN = 2
        lineage_clusters = {x for v in lineages.values() for x in v}
        adata_clusters = set(self.adata.obs[cluster_key].astype(int).unique())

        if not lineage_clusters.issubset(adata_clusters):
            missing = lineage_clusters - adata_clusters
            raise ValueError(
                f"Defined clusters in path are out of range in adata.obs[{cluster_key}]. Missing clusters: {missing}",
            )

        if cluster_key not in self.adata.obs.columns:
            raise ValueError(
                f"{cluster_key} not found in `adata.obs`. Please execute `<ContinuousTrajectoryObject>.train()` function first if needed.",
            )
        for lin in lineages.values():
            if len(lin) < LOW_LIN:
                raise ValueError("Lineage should have at least 2 clusters.")

        self.defined_lineages = lineages
        return self

    def _get_adata_lineage(
        self,
        target_lineage: str,
        cluster_key: str = "clusters",
    ) -> sc.AnnData:
        """Subset the main AnnData to only cells belonging to the specified lineage.

        This method uses the lineage name to retrieve its constituent cluster IDs
        from `self.defined_lineages`, then filters `self.adata` by those clusters.

        Parameters
        ----------
        target_lineage : str
            The lineage name defined in `self.defined_lineages`.
        cluster_key : str, default="clusters"
            The column in `adata.obs` used to filter clusters.

        Returns
        -------
        sc.AnnData
            A new AnnData object containing only the cells in the specified lineage.

        Raises
        ------
        ValueError
            If `self.defined_lineages` is not defined.

        """
        if self.defined_lineages is None:
            raise ValueError(
                "Please define lineages using <ContinuousTrajectoryObject>.define_lineages() first.",
            )
        lineage_str = [str(lin) for lin in self.defined_lineages[target_lineage]]
        _adata_sub = self.adata.copy()
        return _adata_sub[_adata_sub.obs[cluster_key].isin(lineage_str)]

    def calculate_pseudotime(
        self,
        cluster_key: str = "clusters",
    ) -> ContinuousTrajectory:
        """Calculate pseudotime for each defined lineage and store results in `self.pseudotimes`.

        For each lineage, the first cluster in the lineage definition is used as
        the root. The root cell is found by `self._calc_iroot_idx()`, and pseudotime
        is computed with `scanpy.tl.dpt`. The pseudotime values are saved in a
        pandas DataFrame and stored in `self.pseudotimes[lineage_name]`.

        Parameters
        ----------
        cluster_key : str, default="clusters"
            The column in `adata.obs` that stores cluster assignments.

        Returns
        -------
        ContinuousTrajectory
            The same ContinuousTrajectory object (self) with pseudotime information
            stored in `self.pseudotimes`.

        Raises
        ------
        ValueError
            If no lineages have been defined yet (`self.defined_lineages` is None).

        """
        if self.defined_lineages is None:
            raise ValueError(
                "Please define lineages using <ContinuousTrajectoryObject>.define_lineages() first.",
            )
        self.pseudotimes = {}
        for name, lineage in tqdm(
            self.defined_lineages.items(),
            desc="Calculating the pseudotime.",
            leave=True,
        ):
            root_cluster = str(lineage[0])
            _adata_sub = self._get_adata_lineage(name, cluster_key=cluster_key)
            _adata_sub.uns["iroot"] = ContinuousTrajectory._calc_iroot_idx(
                _adata_sub,
                cluster_key,
                [root_cluster],
                _adata_sub.obsm["X_latent"],
            )
            sc.tl.dpt(_adata_sub)
            self.pseudotimes[name] = pd.DataFrame(
                index=_adata_sub.obs.index,
                data={"pseudotime": _adata_sub.obs["dpt_pseudotime"].to_list()},
            )
            del _adata_sub
        return self

    def regression_lineage(
        self,
        batch_key: str,
        label_key: str | None,
        n_train: int,
        cluster_key: str = "clusters",
        n_latent: int = 30,
        max_epochs: int = 800,
        early_stopping: bool = True,
        transform_batch: int = 0,
        stabilize_log1p: bool = True,
        n_draws: int = 25,
    ) -> dict[str, pd.DataFrame]:
        """Perform regression of gene expression on pseudotime for each defined lineage.

        For each lineage:
        1. Subset the data to that lineage's cells.
        2. Store the pseudotime in `obs["pseudotime"]`.
        3. Retrain scVI on the subset data (with pseudotime as the continuous covariate),
           storing the trained model in `self.trainedVI`.
        4. Call `self.trainedVI.regression()` to get slope, intercept, and R² for each gene.

        Note
        ----
        - Some arguments (`resolution`, `n_neighbors`, `n_use_model`) are passed to
          `train()` in the code, but the current implementation of `train()` does not
          explicitly use them. They are included for potential future integration
          (e.g., for performing neighbor graph construction or selecting a specific
          model index). For now, they have no effect in training.

        Parameters
        ----------
        batch_key : str
            The column name in `.obs` denoting batch assignments.
        label_key : str or None
            The column name in `.obs` for cell type or other labels. If None, no
            label covariate is used.
        n_train : int
            Number of times to train scVI on the subset data.
        cluster_key : str, default="clusters"
            The column in `adata.obs` used to filter clusters.
        n_latent : int, default=30
            The dimensionality of the latent space for scVI.
        max_epochs : int, default=800
            The maximum number of training epochs for each scVI model.
        early_stopping : bool, default=True
            Whether to use early stopping in scVI training.
        resolution : float, default=0.5
            (Currently unused) A potential resolution parameter for clustering
            or other tasks.
        n_neighbors : int, default=10
            (Currently unused) A potential neighbor number for graph-based analyses.
        n_use_model : int, default=0
            (Currently unused) An index specifying which trained model to use for
            certain downstream calculations.
        transform_batch : int, default=0
            The batch index to condition on when sampling px for regression.
        stabilize_log1p : bool, default=True
            Whether to apply `log1p` to the sampled expression values before regression.
        n_draws : int, default=25
            Number of forward passes (draws) to compute the mean expression (`px`)
            for each gene during regression.

        Returns
        -------
        dict of str to pd.DataFrame
            A dictionary mapping each lineage name to a DataFrame containing the
            columns "gene", "slope", "intercept", and "r2", sorted by slope in
            descending order.

        Raises
        ------
        ValueError
            If no scVI model is trained (`self.trainedVI is None`),
            if no lineages are defined (`self.defined_lineages is None`),
            or if pseudotime has not been calculated yet (`self.pseudotimes is None`).

        """
        if self.trainedVI is None:
            raise ValueError(
                "Not yet trained. Please execute `<ContinuousTrajectoryObject>.train()` first.",
            )
        if self.defined_lineages is None:
            raise ValueError(
                "Please define lineages using `<ContinuousTrajectoryObject>.define_lineages()` first.",
            )
        if self.pseudotimes is None:
            raise ValueError(
                "Not yet defining pseudotime. Please execute `<ContinuousTrajectoryObject>.define_lineages().calculate_pseudotime()` first.",
            )

        regression_result: dict[str, pd.DataFrame] = {}
        for name, _ in tqdm(
            self.defined_lineages.items(),
            desc="Calculating the regression.",
            leave=True,
        ):
            # Subset data to one lineage
            _adata_sub = self._get_adata_lineage(name, cluster_key=cluster_key)
            # Store the pseudotime in obs
            _adata_sub.obs["pseudotime"] = self.pseudotimes[name]["pseudotime"]
            # Retrain scVI with pseudotime as the continuous covariate
            regression_result[name] = self.train(
                batch_key,
                label_key,
                continuous_key="pseudotime",
                n_train=n_train,
                adata=_adata_sub,
                n_latent=n_latent,
                max_epochs=max_epochs,
                early_stopping=early_stopping,
            ).trainedVI.regression(
                transform_batch=transform_batch,
                stabilize_log1p=stabilize_log1p,
                n_draws=n_draws,
            )
        return regression_result
