import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import seaborn as sns
from scipy.stats import ttest_ind
from tqdm import tqdm

# ロガーの設定（必要に応じてファイル出力などを追加してください）
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)


def _age_effect(age: float, effect_size: float, mode: str) -> float:
    """年齢(age)に応じたUp/Downの効果量を計算するためのヘルパー関数。

    Parameters
    ----------
    age : float
        対象の年齢。
    effect_size : float
        ベースとなる効果量。
    mode : str
        "linear" または "poly"。
        - "linear"：単純に effect_size × age
        - "poly"：例として age^2 に比例させた簡単な二次式にする
                  （実際の利用用途に合わせて実装を拡張してください）

    Returns
    -------
    float
        年齢に応じた加算すべき（または減算すべき）ログスケールの値。

    """
    if mode == "linear":
        return effect_size * age
    if mode == "poly":
        # ここでは簡単に age^2 / 500.0 をスケールに使う例
        return effect_size * (age**2 / 500.0)
    raise ValueError(f"Unknown mode: {mode}. Please use 'linear' or 'poly'.")


class BatchSimulation:
    """A simulator for scRNA-seq data with batch effects and age-dependent gene expression.

    Main Features:
    --------------
    1) Assign Up/Down-regulated genes for each cell type (with respect to age).
    2) Introduce batch effects by sampling library size factors from a log-normal distribution,
       per project (batch). Also apply batch-specific dropout rates.
    3) Assign discrete ages to cells and apply log-scale Up/Down effects (linear or polynomial)
       to the expression.
    4) Generate counts using a negative binomial distribution plus dropout, stored in an AnnData object.
    5) Provide convenient functions for:
       - Visualizing raw or log1p-transformed expression across ages and batches.
       - Verifying Up/Down trends via statistical tests.
    """

    def __init__(
        self,
        n_genes: int = 1000,
        cell_types: list[str] = None,
        projects: list[str] = None,
        cells_per_combination: int = 100,
        n_up_genes_per_ct: int = 50,
        n_down_genes_per_ct: int = 50,
        effect_size_up: float = 0.03,
        effect_size_down: float = 0.03,
        base_expr_mean: float = 3.0,
        base_expr_sd: float = 0.8,
        library_size_logmean: dict[str, float] = None,
        library_size_sigma: float = 0.3,
        dropout_rates: dict[str, float] = None,
        dispersion: float = 0.5,
        possible_ages: list[int] = None,
        random_seed: int = 42,
        age_mode: str = "linear",
    ) -> None:
        """Parameters
        ----------
        n_genes : int
            Total number of genes to simulate.
        cell_types : list[str]
            List of cell type names (e.g., ["Tcell", "Bcell", "Macrophage"]).
        projects : list[str]
            List of project/batch IDs (e.g., ["A", "B"]).
        cells_per_combination : int
            Number of cells per (cell_type × project).
        n_up_genes_per_ct : int
            Number of Up-regulated genes per cell type (w.r.t. age).
        n_down_genes_per_ct : int
            Number of Down-regulated genes per cell type (w.r.t. age).
        effect_size_up : float
            Base log-scale effect size for Up genes (per unit age, if linear).
        effect_size_down : float
            Base log-scale effect size for Down genes (per unit age, if linear).
        base_expr_mean : float
            Mean of the base log-expression for all genes.
        base_expr_sd : float
            Std of the base log-expression for all genes.
        library_size_logmean : dict[str, float]
            Mean (in log space) of the log-normal distribution for library size factors (per project).
        library_size_sigma : float
            Sigma (std in log space) of the log-normal distribution for library size factors.
        dropout_rates : dict[str, float]
            Dropout rate for each project. Example: {"A": 0.05, "B": 0.1}.
        dispersion : float
            Dispersion parameter for the negative binomial distribution (1/r in NB notation).
        possible_ages : list[int]
            Possible discrete ages to assign (e.g., [10, 30, 50, 70, 90]).
        random_seed : int
            Seed for reproducibility.
        age_mode : str
            "linear" or "poly". Determines how age affects Up/Down (linear or polynomial).

        """
        if cell_types is None:
            cell_types = ["Tcell", "Bcell", "Macrophage"]
        if projects is None:
            projects = ["A", "B"]
        if library_size_logmean is None:
            # Project A は平均が大きめ、B は小さめ
            library_size_logmean = {"A": 0.3, "B": -0.3}
        if dropout_rates is None:
            dropout_rates = {"A": 0.05, "B": 0.1}
        if possible_ages is None:
            possible_ages = [10, 30, 50, 70, 90]

        np.random.seed(random_seed)

        self.n_genes = n_genes
        self.cell_types = cell_types
        self.projects = projects
        self.cells_per_combination = cells_per_combination

        self.n_up_genes_per_ct = n_up_genes_per_ct
        self.n_down_genes_per_ct = n_down_genes_per_ct
        self.effect_size_up = effect_size_up
        self.effect_size_down = effect_size_down
        self.base_expr_mean = base_expr_mean
        self.base_expr_sd = base_expr_sd

        self.library_size_logmean = library_size_logmean
        self.library_size_sigma = library_size_sigma
        self.dropout_rates = dropout_rates
        self.dispersion = dispersion
        self.possible_ages = possible_ages
        self.age_mode = age_mode

        # ロガー出力
        logger.info("Initializing BatchSimulation with parameters:")
        logger.info(f"  cell_types={self.cell_types}, projects={self.projects}")
        logger.info(f"  library_size_logmean={self.library_size_logmean}, dropout_rates={self.dropout_rates}")
        logger.info(f"  age_mode={self.age_mode}")

        # 1) Gene names
        var_names = [f"Gene{i}" for i in range(self.n_genes)]
        np.random.shuffle(var_names)
        self.var_names = var_names  # for AnnData usage

        # 2) Assign Up/Down genes (use list[str], not set)
        self.ct_up_genes = {}
        self.ct_down_genes = {}

        idx_pos = 0
        for ct in self.cell_types:
            up_genes = var_names[idx_pos : idx_pos + n_up_genes_per_ct]
            idx_pos += n_up_genes_per_ct
            down_genes = var_names[idx_pos : idx_pos + n_down_genes_per_ct]
            idx_pos += n_down_genes_per_ct

            # dict[str, list[str]] の形で保持
            self.ct_up_genes[ct] = list(up_genes)
            self.ct_down_genes[ct] = list(down_genes)

        self.neutral_genes = list(var_names[idx_pos:])
        logger.info("=== Genes Count Summary ===")
        for ct in self.cell_types:
            logger.info(f"  {ct}: Up={len(self.ct_up_genes[ct])}, Down={len(self.ct_down_genes[ct])}")
        logger.info(f"  Neutral={len(self.neutral_genes)}")

        # 3) Base log expression
        base_expr_vals = np.random.normal(loc=self.base_expr_mean, scale=self.base_expr_sd, size=self.n_genes)
        self.base_expr_dict = dict(zip(var_names, base_expr_vals, strict=False))

        # NB generator function
        def nb_generator(log_expr_array: np.ndarray, lib_factors: np.ndarray, dropout_rate: float) -> np.ndarray:
            """Generate count data using a negative binomial distribution, then apply dropout."""
            n_cells = log_expr_array.shape[0]
            mu = np.exp(log_expr_array) * lib_factors[:, None]
            r = 1.0 / self.dispersion  # NB 'r' parameter
            p = r / (r + mu)  # NB 'p' parameter
            mat = np.random.negative_binomial(r, p)

            # dropout
            drop_mask = np.random.rand(*mat.shape) < dropout_rate
            mat[drop_mask] = 0
            return mat

        name_to_idx = {g: i for i, g in enumerate(var_names)}

        # 4) Generate cells per (project × cell_type)
        all_mats = []
        all_obs = []

        for proj in tqdm(self.projects, desc="Project loop"):
            drop_rate = self.dropout_rates[proj]

            for ct in tqdm(self.cell_types, desc="CellType loop", leave=False):
                n_cells = self.cells_per_combination

                # log-normal sampling for library size factors
                lib_factors = np.random.lognormal(mean=self.library_size_logmean[proj], sigma=self.library_size_sigma, size=n_cells)

                # Assign ages
                ages = np.random.choice(self.possible_ages, size=n_cells)

                # Base log expression
                base_vec = np.array([self.base_expr_dict[g] for g in var_names], dtype=float)

                # shape = (n_cells, n_genes)
                log_expr_array = np.tile(base_vec, (n_cells, 1))

                # Up/Down effect
                up_list = self.ct_up_genes[ct]
                down_list = self.ct_down_genes[ct]

                for i in range(n_cells):
                    age_i = ages[i]
                    # Up genes
                    for g_up in up_list:
                        idx_g = name_to_idx[g_up]
                        # modeに応じて効果を計算
                        up_val = _age_effect(age_i, self.effect_size_up, self.age_mode)
                        log_expr_array[i, idx_g] += up_val
                    # Down genes
                    for g_down in down_list:
                        idx_g = name_to_idx[g_down]
                        down_val = _age_effect(age_i, self.effect_size_down, self.age_mode)
                        # Downなのでマイナス
                        log_expr_array[i, idx_g] -= down_val

                # Negative binomial + dropout
                mat = nb_generator(log_expr_array, lib_factors, drop_rate)

                # obs chunk
                obs_chunk = pd.DataFrame({"project_id": [proj] * n_cells, "cell_type": [ct] * n_cells, "age": ages})

                all_mats.append(mat)
                all_obs.append(obs_chunk)

        # Combine
        X = np.vstack(all_mats)
        obs = pd.concat(all_obs, ignore_index=True)
        var = pd.DataFrame(index=var_names)

        self.adata = sc.AnnData(X=X, obs=obs, var=var)
        logger.info("=== Final AnnData ===")
        logger.info(self.adata)

        # 不要になった up_gene_to_ct / down_gene_to_ct は廃止
        # （必要ならここでct_up_genes, ct_down_genesを見れば良い）

    def plot_genes_by_age(self, genes: list[str], with_regline: bool = True, use_log: bool = False) -> None:
        """Plot the specified genes' expression against discrete ages and across batches.
        No min-max scaling is applied, so absolute differences are visible.

        Parameters
        ----------
        genes : list[str]
            List of gene names to plot.
        with_regline : bool
            Whether to include a regression line (lowess) in the plot.
        use_log : bool
            Whether to use log1p(count) for expression to_numpy().

        """
        sub_adata = self.adata[:, genes].copy()
        df_expr = sub_adata.to_df()

        if use_log:
            df_expr = np.log1p(df_expr)

        df_expr["age"] = sub_adata.obs["age"].to_numpy()
        df_expr["project_id"] = sub_adata.obs["project_id"].to_numpy()
        df_expr["cell_type"] = sub_adata.obs["cell_type"].to_numpy()

        df_melt = df_expr.melt(id_vars=["age", "project_id", "cell_type"], var_name="gene", value_name="expr")

        if with_regline:
            g = sns.lmplot(
                data=df_melt,
                x="age",
                y="expr",
                col="project_id",
                row="cell_type",
                scatter=True,
                fit_reg=True,
                lowess=True,
                hue="cell_type",
                scatter_kws=dict(s=20, alpha=0.5),
                height=3,
                aspect=1.3,
            )
            g.set_titles(row_template="{row_name}", col_template="Project {col_name}")
            y_label = "log1p(Expression)" if use_log else "Expression (raw)"
            g.set_axis_labels("Age", y_label)
            plt.tight_layout()
            # plt.show()
        else:
            g = sns.relplot(
                data=df_melt,
                x="age",
                y="expr",
                col="project_id",
                row="cell_type",
                hue="cell_type",
                kind="scatter",
                height=3,
                aspect=1.3,
            )
            g.set_titles(row_template="{row_name}", col_template="Project {col_name}")
            y_label = "log1p(Expression)" if use_log else "Expression (raw)"
            g.set_axis_labels("Age", y_label)
            plt.tight_layout()
            # plt.show()

    def plot_boxplot_by_batch(self, genes: list[str], use_log: bool = False) -> None:
        """Show a boxplot for each gene, separated by project_id (batch), allowing
        direct visualization of batch effects (library size differences, etc.).

        Parameters
        ----------
        genes : list[str]
            List of genes to plot.
        use_log : bool
            Whether to use log1p for expression to_numpy().

        """
        sub_adata = self.adata[:, genes].copy()
        df_expr = sub_adata.to_df()

        if use_log:
            df_expr = np.log1p(df_expr)

        df_expr["project_id"] = sub_adata.obs["project_id"].to_numpy()
        df_expr["cell_type"] = sub_adata.obs["cell_type"].to_numpy()

        df_melt = df_expr.melt(id_vars=["project_id", "cell_type"], var_name="gene", value_name="expr")

        plt.figure(figsize=(8, 5))
        sns.boxplot(data=df_melt, x="project_id", y="expr", hue="gene", showfliers=False)
        y_label = "log1p(Expression)" if use_log else "Expression (raw)"
        plt.ylabel(y_label)
        plt.title("Batch-wise Boxplot")
        plt.tight_layout()
        # plt.show()

    def verify_simulation(self, alpha=0.05) -> None:
        """Verify the simulation by comparing expression at min_age vs. max_age
        for each Up/Down gene using a t-test.

        - Up genes: Check if the expression at max_age is significantly higher than at min_age.
        - Down genes: Check if the expression at max_age is significantly lower than at min_age.

        Parameters
        ----------
        alpha : float
            Significance level for the t-test.

        """
        adata = self.adata
        all_ages = sorted(adata.obs["age"].unique())
        min_age, max_age = all_ages[0], all_ages[-1]

        X = adata.X.A if hasattr(adata.X, "A") else adata.X

        up_correct = 0
        up_total = 0
        for ct in self.cell_types:
            up_genes = self.ct_up_genes[ct]
            for g in up_genes:
                if g not in adata.var_names:
                    continue
                g_idx = adata.var_names.get_loc(g)

                ct_mask = (adata.obs["cell_type"] == ct).to_numpy()
                expr_ct = X[ct_mask, g_idx]

                min_mask = (adata.obs.loc[ct_mask, "age"] == min_age).to_numpy()
                expr_min = expr_ct[min_mask]

                max_mask = (adata.obs.loc[ct_mask, "age"] == max_age).to_numpy()
                expr_max = expr_ct[max_mask]

                if len(expr_min) > 1 and len(expr_max) > 1:
                    up_total += 1
                    stat, pval = ttest_ind(expr_max, expr_min, equal_var=False)
                    mean_diff = expr_max.mean() - expr_min.mean()
                    if (pval < alpha) and (mean_diff > 0):
                        up_correct += 1

        down_correct = 0
        down_total = 0
        for ct in self.cell_types:
            down_genes = self.ct_down_genes[ct]
            for g in down_genes:
                if g not in adata.var_names:
                    continue
                g_idx = adata.var_names.get_loc(g)

                ct_mask = (adata.obs["cell_type"] == ct).to_numpy()
                expr_ct = X[ct_mask, g_idx]

                min_mask = (adata.obs.loc[ct_mask, "age"] == min_age).to_numpy()
                expr_min = expr_ct[min_mask]

                max_mask = (adata.obs.loc[ct_mask, "age"] == max_age).to_numpy()
                expr_max = expr_ct[max_mask]

                if len(expr_min) > 1 and len(expr_max) > 1:
                    down_total += 1
                    stat, pval = ttest_ind(expr_min, expr_max, equal_var=False)
                    mean_diff = expr_min.mean() - expr_max.mean()
                    if (pval < alpha) and (mean_diff > 0):
                        down_correct += 1

        logger.info(f"[Verification: Up genes] {up_correct}/{up_total} genes showed a significant increase at age {max_age} vs. {min_age} (p<{alpha}).")
        logger.info(f"[Verification: Down genes] {down_correct}/{down_total} genes showed a significant decrease at age {max_age} vs. {min_age} (p<{alpha}).")
