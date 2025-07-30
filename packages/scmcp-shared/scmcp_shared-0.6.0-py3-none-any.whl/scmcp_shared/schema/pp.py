from pydantic import Field, field_validator, BaseModel

from typing import Optional, Union, List, Dict, Any
from typing import Literal
import numpy as np


class FilterCellsParam(BaseModel):
    """Input schema for the filter_cells preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    min_counts: Optional[int] = Field(
        default=None,
        description="Minimum number of counts required for a cell to pass filtering.",
    )

    min_genes: Optional[int] = Field(
        default=None,
        description="Minimum number of genes expressed required for a cell to pass filtering.",
    )

    max_counts: Optional[int] = Field(
        default=None,
        description="Maximum number of counts required for a cell to pass filtering.",
    )

    max_genes: Optional[int] = Field(
        default=None,
        description="Maximum number of genes expressed required for a cell to pass filtering.",
    )

    @field_validator("min_counts", "min_genes", "max_counts", "max_genes")
    def validate_positive_integers(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("must be positive_integers")
        return v


class FilterGenesParam(BaseModel):
    """Input schema for the filter_genes preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    min_counts: Optional[int] = Field(
        default=None,
        description="Minimum number of counts required for a gene to pass filtering.",
    )

    min_cells: Optional[int] = Field(
        default=None,
        description="Minimum number of cells expressed required for a gene to pass filtering.",
    )

    max_counts: Optional[int] = Field(
        default=None,
        description="Maximum number of counts required for a gene to pass filtering.",
    )

    max_cells: Optional[int] = Field(
        default=None,
        description="Maximum number of cells expressed required for a gene to pass filtering.",
    )

    @field_validator("min_counts", "min_cells", "max_counts", "max_cells")
    def validate_positive_integers(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("must be positive_integers")
        return v


class SubsetCellParam(BaseModel):
    """Input schema for subsetting AnnData objects based on various criteria."""

    adata: str = Field(..., description="The AnnData object variable name.")
    obs_key: Optional[str] = Field(
        default=None,
        description="Key in adata.obs to use for subsetting observations/cells.",
    )
    obs_min: Optional[float] = Field(
        default=None,
        description="Minimum value for the obs_key to include in the subset.",
    )
    obs_max: Optional[float] = Field(
        default=None,
        description="Maximum value for the obs_key to include in the subset.",
    )
    obs_value: Optional[Any] = Field(
        default=None,
        description="Exact value for the obs_key to include in the subset (adata.obs[obs_key] == obs_value).",
    )
    min_counts: Optional[int] = Field(
        default=None,
        description="Minimum number of counts required for a cell to pass filtering.",
    )
    min_genes: Optional[int] = Field(
        default=None,
        description="Minimum number of genes expressed required for a cell to pass filtering.",
    )
    max_counts: Optional[int] = Field(
        default=None,
        description="Maximum number of counts required for a cell to pass filtering.",
    )
    max_genes: Optional[int] = Field(
        default=None,
        description="Maximum number of genes expressed required for a cell to pass filtering.",
    )


class SubsetGeneParam(BaseModel):
    """Input schema for subsetting AnnData objects based on various criteria."""

    adata: str = Field(..., description="The AnnData object variable name.")
    min_counts: Optional[int] = Field(
        default=None,
        description="Minimum number of counts required for a gene to pass filtering.",
    )
    min_cells: Optional[int] = Field(
        default=None,
        description="Minimum number of cells expressed required for a gene to pass filtering.",
    )
    max_counts: Optional[int] = Field(
        default=None,
        description="Maximum number of counts required for a gene to pass filtering.",
    )
    max_cells: Optional[int] = Field(
        default=None,
        description="Maximum number of cells expressed required for a gene to pass filtering.",
    )
    var_key: Optional[str] = Field(
        default=None,
        description="Key in adata.var to use for subsetting variables/genes.",
    )
    var_min: Optional[float] = Field(
        default=None,
        description="Minimum value for the var_key to include in the subset.",
    )
    var_max: Optional[float] = Field(
        default=None,
        description="Maximum value for the var_key to include in the subset.",
    )
    highly_variable: Optional[bool] = Field(
        default=False,
        description="If True, subset to highly variable genes. Requires 'highly_variable' column in adata.var.",
    )


class CalculateQCMetrics(BaseModel):
    """Input schema for the calculate_qc_metrics preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")

    expr_type: str = Field(default="counts", description="Name of kind of values in X.")

    var_type: str = Field(
        default="genes", description="The kind of thing the variables are."
    )

    qc_vars: Optional[Union[List[str], str]] = Field(
        default=[],
        description=(
            "Keys for boolean columns of .var which identify variables you could want to control for "
            "mark_var tool should be called frist when you want to calculate mt, ribo, hb, and check tool output for var columns"
        ),
    )

    percent_top: Optional[List[int]] = Field(
        default=[50, 100, 200, 500],
        description="List of ranks (where genes are ranked by expression) at which the cumulative proportion of expression will be reported as a percentage.",
    )

    layer: Optional[str] = Field(
        default=None,
        description="If provided, use adata.layers[layer] for expression values instead of adata.X",
    )

    use_raw: bool = Field(
        default=False,
        description="If True, use adata.raw.X for expression values instead of adata.X",
    )
    log1p: bool = Field(
        default=True,
        description="Set to False to skip computing log1p transformed annotations.",
    )

    @field_validator("percent_top")
    def validate_percent_top(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """验证 percent_top 中的值为正整数"""
        if v is not None:
            for rank in v:
                if not isinstance(rank, int) or rank <= 0:
                    raise ValueError("percent_top 中的所有值必须是正整数")
        return v


class Log1PParam(BaseModel):
    """Input schema for the log1p preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    base: Optional[Union[int, float]] = Field(
        default=None,
        description="Base of the logarithm. Natural logarithm is used by default.",
    )

    chunked: Optional[bool] = Field(
        default=None,
        description="Process the data matrix in chunks, which will save memory.",
    )

    chunk_size: Optional[int] = Field(
        default=None,
        description="Number of observations in the chunks to process the data in.",
    )

    layer: Optional[str] = Field(
        default=None, description="Entry of layers to transform."
    )

    obsm: Optional[str] = Field(default=None, description="Entry of obsm to transform.")

    @field_validator("chunk_size")
    def validate_chunk_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate chunk_size is positive integer"""
        if v is not None and v <= 0:
            raise ValueError("chunk_size must be a positive integer")
        return v


class HighlyVariableGenesParam(BaseModel):
    """Input schema for the highly_variable_genes preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    layer: Optional[str] = Field(
        default=None,
        description="If provided, use adata.layers[layer] for expression values.",
    )

    n_top_genes: Optional[int] = Field(
        default=None,
        description="Number of highly-variable genes to keep. Mandatory if `flavor='seurat_v3'",
    )

    min_disp: Optional[float] = Field(
        default=0.5, description="Minimum dispersion cutoff for gene selection."
    )

    max_disp: Optional[float] = Field(
        default=np.inf, description="Maximum dispersion cutoff for gene selection."
    )
    min_mean: Optional[float] = Field(
        default=0.0125, description="Minimum mean expression cutoff for gene selection."
    )
    max_mean: Optional[float] = Field(
        default=3, description="Maximum mean expression cutoff for gene selection."
    )
    span: Optional[float] = Field(
        default=0.3,
        description="Fraction of data used for loess model fit in seurat_v3.",
        gt=0,
        lt=1,
    )
    n_bins: Optional[int] = Field(
        default=20, description="Number of bins for mean expression binning.", gt=0
    )
    flavor: Optional[
        Literal["seurat", "cell_ranger", "seurat_v3", "seurat_v3_paper"]
    ] = Field(
        default="seurat", description="Method for identifying highly variable genes."
    )
    subset: Optional[bool] = Field(
        default=False, description="Inplace subset to highly-variable genes if True."
    )
    batch_key: Optional[str] = Field(
        default=None, description="Key in adata.obs for batch information."
    )

    check_values: Optional[bool] = Field(
        default=True, description="Check if counts are integers for seurat_v3 flavor."
    )

    @field_validator("n_top_genes", "n_bins")
    def validate_positive_integers(cls, v: Optional[int]) -> Optional[int]:
        """Validate positive integers"""
        if v is not None and v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("span")
    def validate_span(cls, v: float) -> float:
        """Validate span is between 0 and 1"""
        if v <= 0 or v >= 1:
            raise ValueError("span must be between 0 and 1")
        return v


class RegressOutParam(BaseModel):
    """Input schema for the regress_out preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    keys: Union[str, List[str]] = Field(
        description="Keys for observation annotation on which to regress on."
    )
    layer: Optional[str] = Field(
        default=None, description="If provided, which element of layers to regress on."
    )
    n_jobs: Optional[int] = Field(
        default=None, description="Number of jobs for parallel computation.", gt=0
    )

    @field_validator("n_jobs")
    def validate_n_jobs(cls, v: Optional[int]) -> Optional[int]:
        """Validate n_jobs is positive integer"""
        if v is not None and v <= 0:
            raise ValueError("n_jobs must be a positive integer")
        return v

    @field_validator("keys")
    def validate_keys(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """Ensure keys is either a string or list of strings"""
        if isinstance(v, str):
            return v
        elif isinstance(v, list) and all(isinstance(item, str) for item in v):
            return v
        raise ValueError("keys must be a string or list of strings")


class ScaleParam(BaseModel):
    """Input schema for the scale preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    zero_center: bool = Field(
        default=True,
        description="If False, omit zero-centering variables to handle sparse input efficiently.",
    )

    max_value: Optional[float] = Field(
        default=None,
        description="Clip (truncate) to this value after scaling. If None, do not clip.",
    )

    layer: Optional[str] = Field(
        default=None, description="If provided, which element of layers to scale."
    )

    obsm: Optional[str] = Field(
        default=None, description="If provided, which element of obsm to scale."
    )

    mask_obs: Optional[Union[str, bool]] = Field(
        default=None,
        description="Boolean mask or string referring to obs column for subsetting observations.",
    )

    @field_validator("max_value")
    def validate_max_value(cls, v: Optional[float]) -> Optional[float]:
        """Validate max_value is positive if provided"""
        if v is not None and v <= 0:
            raise ValueError("max_value must be positive if provided")
        return v


class CombatParam(BaseModel):
    """Input schema for the combat batch effect correction tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    key: str = Field(
        default="batch",
        description="Key to a categorical annotation from adata.obs that will be used for batch effect removal.",
    )

    covariates: Optional[List[str]] = Field(
        default=None,
        description="Additional covariates besides the batch variable such as adjustment variables or biological condition.",
    )

    @field_validator("key")
    def validate_key(cls, v: str) -> str:
        """Validate key is not empty"""
        if not v.strip():
            raise ValueError("key cannot be empty")
        return v

    @field_validator("covariates")
    def validate_covariates(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate covariates are non-empty strings if provided"""
        if v is not None:
            if not all(isinstance(item, str) and item.strip() for item in v):
                raise ValueError("covariates must be non-empty strings")
        return v


class ScrubletParam(BaseModel):
    """Input schema for the scrublet doublet prediction tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    adata_sim: Optional[str] = Field(
        default=None,
        description="Optional path to AnnData object with simulated doublets.",
    )

    batch_key: Optional[str] = Field(
        default=None, description="Key in adata.obs for batch information."
    )

    sim_doublet_ratio: float = Field(
        default=2.0,
        description="Number of doublets to simulate relative to observed transcriptomes.",
        gt=0,
    )

    expected_doublet_rate: float = Field(
        default=0.05,
        description="Estimated doublet rate for the experiment.",
        ge=0,
        le=1,
    )

    stdev_doublet_rate: float = Field(
        default=0.02,
        description="Uncertainty in the expected doublet rate.",
        ge=0,
        le=1,
    )

    synthetic_doublet_umi_subsampling: float = Field(
        default=1.0,
        description="Rate for sampling UMIs when creating synthetic doublets.",
        gt=0,
        le=1,
    )

    knn_dist_metric: str = Field(
        default="euclidean",
        description="Distance metric used when finding nearest neighbors.",
    )

    normalize_variance: bool = Field(
        default=True,
        description="Normalize data such that each gene has variance of 1.",
    )

    log_transform: bool = Field(
        default=False, description="Whether to log-transform the data prior to PCA."
    )

    mean_center: bool = Field(
        default=True, description="Center data such that each gene has mean of 0."
    )

    n_prin_comps: int = Field(
        default=30,
        description="Number of principal components used for embedding.",
        gt=0,
    )

    use_approx_neighbors: Optional[bool] = Field(
        default=None, description="Use approximate nearest neighbor method (annoy)."
    )

    get_doublet_neighbor_parents: bool = Field(
        default=False,
        description="Return parent transcriptomes that generated doublet neighbors.",
    )

    n_neighbors: Optional[int] = Field(
        default=None,
        description="Number of neighbors used to construct KNN graph.",
        gt=0,
    )

    threshold: Optional[float] = Field(
        default=None,
        description="Doublet score threshold for calling a transcriptome a doublet.",
        ge=0,
        le=1,
    )

    @field_validator(
        "sim_doublet_ratio",
        "expected_doublet_rate",
        "stdev_doublet_rate",
        "synthetic_doublet_umi_subsampling",
        "n_prin_comps",
        "n_neighbors",
    )
    def validate_positive_numbers(
        cls, v: Optional[Union[int, float]]
    ) -> Optional[Union[int, float]]:
        """Validate positive numbers where applicable"""
        if v is not None and v <= 0:
            raise ValueError("must be a positive number")
        return v

    @field_validator("knn_dist_metric")
    def validate_knn_dist_metric(cls, v: str) -> str:
        """Validate distance metric is supported"""
        valid_metrics = ["euclidean", "manhattan", "cosine", "correlation"]
        if v.lower() not in valid_metrics:
            raise ValueError(f"knn_dist_metric must be one of {valid_metrics}")
        return v.lower()


class NeighborsParam(BaseModel):
    """Input schema for the neighbors graph construction tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    n_neighbors: int = Field(
        default=15,
        description="Size of local neighborhood used for manifold approximation.",
        gt=1,
        le=100,
    )

    n_pcs: Optional[int] = Field(
        default=None,
        description="Number of PCs to use. If None, automatically determined.",
        ge=0,
    )

    use_rep: Optional[str] = Field(
        default=None, description="Key for .obsm to use as representation."
    )

    knn: bool = Field(
        default=True,
        description="Whether to use hard threshold for neighbor restriction.",
    )

    method: Literal["umap", "gauss"] = Field(
        default="umap",
        description="Method for computing connectivities ('umap' or 'gauss').",
    )

    transformer: Optional[str] = Field(
        default=None,
        description="Approximate kNN search implementation ('pynndescent' or 'rapids').",
    )

    metric: str = Field(default="euclidean", description="Distance metric to use.")

    metric_kwds: Dict[str, Any] = Field(
        default_factory=dict, description="Options for the distance metric."
    )

    random_state: int = Field(default=0, description="Random seed for reproducibility.")

    key_added: Optional[str] = Field(
        default=None, description="Key prefix for storing neighbor results."
    )

    @field_validator("n_neighbors", "n_pcs")
    def validate_positive_integers(cls, v: Optional[int]) -> Optional[int]:
        """Validate positive integers where applicable"""
        if v is not None and v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("method")
    def validate_method(cls, v: str) -> str:
        """Validate method is supported"""
        if v not in ["umap", "gauss"]:
            raise ValueError("method must be either 'umap' or 'gauss'")
        return v

    @field_validator("transformer")
    def validate_transformer(cls, v: Optional[str]) -> Optional[str]:
        """Validate transformer option is supported"""
        if v is not None and v not in ["pynndescent", "rapids"]:
            raise ValueError("transformer must be either 'pynndescent' or 'rapids'")
        return v


class NormalizeTotalParam(BaseModel):
    """Input schema for the normalize_total preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    target_sum: Optional[float] = Field(
        default=None,
        description="If None, after normalization, each cell has a total count equal to the median of total counts before normalization. If a number is provided, each cell will have this total count after normalization.",
    )

    exclude_highly_expressed: bool = Field(
        default=False,
        description="Exclude highly expressed genes for the computation of the normalization factor for each cell.",
    )

    max_fraction: float = Field(
        default=0.05,
        description="If exclude_highly_expressed=True, consider cells as highly expressed that have more counts than max_fraction of the original total counts in at least one cell.",
        gt=0,
        le=1,
    )

    key_added: Optional[str] = Field(
        default=None,
        description="Name of the field in adata.obs where the normalization factor is stored.",
    )

    layer: Optional[str] = Field(
        default=None,
        description="Layer to normalize instead of X. If None, X is normalized.",
    )

    layers: Optional[Union[Literal["all"], List[str]]] = Field(
        default=None,
        description="List of layers to normalize. If 'all', normalize all layers.",
    )

    layer_norm: Optional[str] = Field(
        default=None, description="Specifies how to normalize layers."
    )

    inplace: bool = Field(
        default=True,
        description="Whether to update adata or return dictionary with normalized copies.",
    )

    @field_validator("target_sum")
    def validate_target_sum(cls, v: Optional[float]) -> Optional[float]:
        """Validate target_sum is positive if provided"""
        if v is not None and v <= 0:
            raise ValueError("target_sum must be positive")
        return v

    @field_validator("max_fraction")
    def validate_max_fraction(cls, v: float) -> float:
        """Validate max_fraction is between 0 and 1"""
        if v <= 0 or v > 1:
            raise ValueError("max_fraction must be between 0 and 1")
        return v


class BBKNNParam(BaseModel):
    """Input schema for the bbknn (batch balanced kNN) preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")

    batch_key: str = Field(
        default="batch",
        description="adata.obs column name discriminating between your batches.",
    )

    use_rep: str = Field(
        default="X_pca",
        description="The dimensionality reduction in .obsm to use for neighbour detection. Defaults to PCA.",
    )

    approx: bool = Field(
        default=True,
        description="If True, use approximate neighbour finding - annoy or PyNNDescent. This results in a quicker run time for large datasets while also potentially increasing the degree of batch correction.",
    )

    use_annoy: bool = Field(
        default=True,
        description="Only used when approx=True. If True, will use annoy for neighbour finding. If False, will use pyNNDescent instead.",
    )

    metric: str = Field(
        default="euclidean",
        description="What distance metric to use. The options depend on the choice of neighbour algorithm.",
    )

    neighbors_within_batch: int = Field(
        default=3,
        description="How many top neighbours to report for each batch; total number of neighbours in the initial k-nearest-neighbours computation will be this number times the number of batches.",
        gt=0,
    )

    n_pcs: int = Field(
        default=50,
        description="How many dimensions (in case of PCA, principal components) to use in the analysis.",
        gt=0,
    )

    trim: Optional[int] = Field(
        default=None,
        description="Trim the neighbours of each cell to these many top connectivities. May help with population independence and improve the tidiness of clustering. If None, sets the parameter value automatically to 10 times neighbors_within_batch times the number of batches. Set to 0 to skip.",
        ge=0,
    )

    annoy_n_trees: int = Field(
        default=10,
        description="Only used with annoy neighbour identification. The number of trees to construct in the annoy forest. More trees give higher precision when querying, at the cost of increased run time and resource intensity.",
        gt=0,
    )

    pynndescent_n_neighbors: int = Field(
        default=30,
        description="Only used with pyNNDescent neighbour identification. The number of neighbours to include in the approximate neighbour graph. More neighbours give higher precision when querying, at the cost of increased run time and resource intensity.",
        gt=0,
    )

    pynndescent_random_state: int = Field(
        default=0,
        description="Only used with pyNNDescent neighbour identification. The RNG seed to use when creating the graph.",
    )

    use_faiss: bool = Field(
        default=True,
        description="If approx=False and the metric is 'euclidean', use the faiss package to compute nearest neighbours if installed. This improves performance at a minor cost to numerical precision as faiss operates on float32.",
    )

    set_op_mix_ratio: float = Field(
        default=1.0,
        description="UMAP connectivity computation parameter, float between 0 and 1, controlling the blend between a connectivity matrix formed exclusively from mutual nearest neighbour pairs (0) and a union of all observed neighbour relationships with the mutual pairs emphasised (1).",
        ge=0.0,
        le=1.0,
    )

    local_connectivity: int = Field(
        default=1,
        description="UMAP connectivity computation parameter, how many nearest neighbors of each cell are assumed to be fully connected (and given a connectivity value of 1).",
        gt=0,
    )

    @field_validator(
        "neighbors_within_batch",
        "n_pcs",
        "annoy_n_trees",
        "pynndescent_n_neighbors",
        "local_connectivity",
    )
    def validate_positive_integers(cls, v: int) -> int:
        """Validate positive integers"""
        if v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("trim")
    def validate_trim(cls, v: Optional[int]) -> Optional[int]:
        """Validate trim is non-negative if provided"""
        if v is not None and v < 0:
            raise ValueError("trim must be non-negative")
        return v

    @field_validator("set_op_mix_ratio")
    def validate_set_op_mix_ratio(cls, v: float) -> float:
        """Validate set_op_mix_ratio is between 0 and 1"""
        if v < 0 or v > 1:
            raise ValueError("set_op_mix_ratio must be between 0 and 1")
        return v

    @field_validator("metric")
    def validate_metric(cls, v: str) -> str:
        """Validate metric is supported"""
        valid_metrics = [
            "euclidean",
            "l2",
            "sqeuclidean",
            "manhattan",
            "taxicab",
            "l1",
            "chebyshev",
            "linfinity",
            "linfty",
            "linf",
            "minkowski",
            "seuclidean",
            "standardised_euclidean",
            "wminkowski",
            "angular",
            "hamming",
        ]
        if v.lower() not in valid_metrics:
            raise ValueError(f"metric must be one of {valid_metrics}")
        return v.lower()


class HarmonyIntegrateParam(BaseModel):
    """Input schema for the harmony_integrate preprocessing tool."""

    adata: str = Field(..., description="The AnnData object variable name.")

    key: Union[str, List[str]] = Field(
        description="The name of the column in adata.obs that differentiates among experiments/batches. To integrate over two or more covariates, you can pass multiple column names as a list."
    )

    basis: str = Field(
        default="X_pca",
        description="The name of the field in adata.obsm where the PCA table is stored. Defaults to 'X_pca', which is the default for sc.pp.pca().",
    )

    adjusted_basis: str = Field(
        default="X_pca_harmony",
        description="The name of the field in adata.obsm where the adjusted PCA table will be stored after running this function. Defaults to X_pca_harmony.",
    )

    theta: float = Field(
        default=2.0,
        description="Diversity clustering penalty parameter. Theta = 0 does not encourage any diversity. Larger values of theta result in more diverse clusters.",
        gt=0,
    )

    lambda_: float = Field(
        default=1.0,
        description="Ridge regression penalty parameter. Lambda = 0 gives no regularization. Larger values of lambda result in more regularization.",
        ge=0,
    )

    sigma: float = Field(
        default=0.1,
        description="Width of soft kmeans clusters. Sigma scales the distance from a cell to cluster centroids. Larger values of sigma result in cells assigned to more clusters. Each cell is assigned to clusters with probability proportional to exp(-distance^2 / sigma^2).",
        gt=0,
    )

    nclust: Optional[int] = Field(
        default=None,
        description="Number of clusters in Harmony. If None, estimated automatically. If provided, this overrides the theta parameter.",
        gt=0,
    )

    tau: float = Field(
        default=0.0,
        description="Protection against overclustering small datasets with rare cell types. tau is the expected number of cells per cluster.",
        ge=0,
    )

    block_size: float = Field(
        default=0.05,
        description="What proportion of cells to update during clustering. Between 0 to 1, e.g. 0.05 updates 5% of cells per iteration.",
        gt=0,
        le=1,
    )

    max_iter_harmony: int = Field(
        default=10,
        description="Maximum number of rounds to run Harmony. One round of Harmony involves one clustering and one correction step.",
        gt=0,
    )

    max_iter_kmeans: int = Field(
        default=20,
        description="Maximum number of rounds to run clustering at each round of Harmony. If at least k < nclust clusters contain 1 or fewer cells, then stop early.",
        gt=0,
    )

    epsilon_cluster: float = Field(
        default=1e-5,
        description="Convergence tolerance for clustering round of Harmony. Set to -Inf to never stop early.",
        gt=0,
    )

    epsilon_harmony: float = Field(
        default=1e-4,
        description="Convergence tolerance for Harmony. Set to -Inf to never stop early.",
        gt=0,
    )

    random_state: int = Field(default=0, description="Random seed for reproducibility.")

    verbose: bool = Field(
        default=True, description="Whether to print progress messages."
    )

    @field_validator("key")
    def validate_key(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """Ensure key is either a string or list of strings"""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("key cannot be empty")
            return v
        elif isinstance(v, list) and all(
            isinstance(item, str) and item.strip() for item in v
        ):
            return v
        raise ValueError("key must be a non-empty string or list of non-empty strings")

    @field_validator("basis", "adjusted_basis")
    def validate_basis_names(cls, v: str) -> str:
        """Validate basis names are not empty"""
        if not v.strip():
            raise ValueError("basis and adjusted_basis cannot be empty")
        return v

    @field_validator(
        "theta",
        "lambda_",
        "sigma",
        "tau",
        "block_size",
        "epsilon_cluster",
        "epsilon_harmony",
    )
    def validate_positive_floats(cls, v: float) -> float:
        """Validate positive floats"""
        if v < 0:
            raise ValueError("must be non-negative")
        return v

    @field_validator("max_iter_harmony", "max_iter_kmeans")
    def validate_positive_integers(cls, v: int) -> int:
        """Validate positive integers"""
        if v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("nclust")
    def validate_nclust(cls, v: Optional[int]) -> Optional[int]:
        """Validate nclust is positive if provided"""
        if v is not None and v <= 0:
            raise ValueError("nclust must be positive if provided")
        return v
