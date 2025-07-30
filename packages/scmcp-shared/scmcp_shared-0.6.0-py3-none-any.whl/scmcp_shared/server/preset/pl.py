import scanpy as sc
from fastmcp.tools.tool import Tool
from fastmcp.exceptions import ToolError
from scmcp_shared.schema.preset.pl import *
from scmcp_shared.schema.preset import AdataInfo
from scmcp_shared.util import forward_request, sc_like_plot, get_ads
from scmcp_shared.mcp_base import BaseMCP


class ScanpyPlottingMCP(BaseMCP):
    def __init__(
        self,
        include_tools: list = None,
        exclude_tools: list = None,
        AdataInfo: AdataInfo = AdataInfo,
    ):
        """
        Initialize ScanpyPreprocessingMCP with optional tool filtering.

        Args:
            include_tools (list, optional): List of tool names to include. If None, all tools are included.
            exclude_tools (list, optional): List of tool names to exclude. If None, no tools are excluded.
            AdataInfo: The AdataInfo class to use for type annotations.
        """
        super().__init__("ScanpyMCP-PL-Server", include_tools, exclude_tools, AdataInfo)

    def _tool_pca(self):
        def _pca(request: PCAParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """Scatter plot in PCA coordinates. default figure for PCA plot"""
            try:
                if (res := forward_request("pl_pca", request, adinfo)) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.pca, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_pca, name="pca", enabled=True)

    def _tool_diffmap(self):
        def _diffmap(
            request: DiffusionMapParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Plot diffusion map embedding of cells."""
            try:
                if (res := forward_request("pl_diffmap", request, adinfo)) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.diffmap, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_diffmap, name="diffmap", enabled=True)

    def _tool_violin(self):
        def _violin(request: ViolinParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """Plot violin plot of one or more variables."""
            try:
                if (res := forward_request("pl_violin", request, adinfo)) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.violin, adata, request, adinfo)
                return {"figpath": fig_path}
            except KeyError as e:
                raise ToolError(
                    f"doest found {e} in current sampleid with adtype {adinfo.adtype}"
                )
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_violin, name="violin", enabled=True)

    def _tool_stacked_violin(self):
        def _stacked_violin(
            request: StackedViolinParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Plot stacked violin plots. Makes a compact image composed of individual violin plots stacked on top of each other."""
            try:
                if (
                    res := forward_request("pl_stacked_violin", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.stacked_violin, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_stacked_violin, name="stacked_violin", enabled=True)

    def _tool_heatmap(self):
        async def _heatmap(
            request: HeatmapParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Heatmap of the expression values of genes."""
            try:
                if (res := forward_request("pl_heatmap", request, adinfo)) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.heatmap, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_heatmap, name="heatmap", enabled=True)

    def _tool_dotplot(self):
        def _dotplot(request: DotplotParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """Plot dot plot of expression values per gene for each group."""
            try:
                if (res := forward_request("pl_dotplot", request, adinfo)) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.dotplot, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_dotplot, name="dotplot", enabled=True)

    def _tool_matrixplot(self):
        def _matrixplot(
            request: MatrixplotParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """matrixplot, Create a heatmap of the mean expression values per group of each var_names."""
            try:
                if (
                    res := forward_request("pl_matrixplot", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.matrixplot, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_matrixplot, name="matrixplot", enabled=True)

    def _tool_tracksplot(self):
        def _tracksplot(
            request: TracksplotParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """tracksplot, compact plot of expression of a list of genes."""
            try:
                if (
                    res := forward_request("pl_tracksplot", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.tracksplot, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_tracksplot, name="tracksplot")

    def _tool_scatter(self):
        def _scatter(
            request: EnhancedScatterParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Plot a scatter plot of two variables, Scatter plot along observations or variables axes."""
            try:
                if (res := forward_request("pl_scatter", request, adinfo)) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.scatter, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_scatter, name="scatter", enabled=True)

    def _tool_embedding(self):
        def _embedding(
            request: EmbeddingParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Scatter plot for user specified embedding basis (e.g. umap, tsne, etc)."""
            try:
                if (
                    res := forward_request("pl_embedding", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.embedding, adata, request, adinfo)
                return {"figpath": fig_path}
            except KeyError as e:
                raise ToolError(
                    f"doest found {e} in current sampleid with adtype {adinfo.adtype}"
                )
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_embedding, name="embedding", enabled=True)

    def _tool_embedding_density(self):
        def _embedding_density(
            request: EmbeddingDensityParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Plot the density of cells in an embedding."""
            try:
                if (
                    res := forward_request("pl_embedding_density", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.embedding_density, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _embedding_density, name="embedding_density", enabled=True
        )

    def _tool_rank_genes_groups(self):
        def _rank_genes_groups(
            request: RankGenesGroupsParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Plot ranking of genes based on differential expression."""
            try:
                if (
                    res := forward_request("pl_rank_genes_groups", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.rank_genes_groups, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _rank_genes_groups, name="rank_genes_groups", enabled=True
        )

    def _tool_rank_genes_groups_dotplot(self):
        def _rank_genes_groups_dotplot(
            request: RankGenesGroupsDotplotParam,
            adinfo: self.AdataInfo = self.AdataInfo(),
        ):
            """Plot ranking of genes(DEGs) using dotplot visualization. Defualt plot DEGs for rank_genes_groups tool"""
            try:
                if (
                    res := forward_request(
                        "pl_rank_genes_groups_dotplot", request, adinfo
                    )
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(
                    sc.pl.rank_genes_groups_dotplot, adata, request, adinfo
                )
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _rank_genes_groups_dotplot, name="rank_genes_groups_dotplot", enabled=True
        )

    def _tool_clustermap(self):
        def _clustermap(
            request: ClusterMapParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Plot hierarchical clustering of cells and genes."""
            try:
                if (
                    res := forward_request("pl_clustermap", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(sc.pl.clustermap, adata, request, adinfo)
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_clustermap, name="clustermap", enabled=True)

    def _tool_highly_variable_genes(self):
        def _highly_variable_genes(
            request: HighlyVariableGenesParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """plot highly variable genes; Plot dispersions or normalized variance versus means for genes."""
            try:
                if (
                    res := forward_request("pl_highly_variable_genes", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(
                    sc.pl.highly_variable_genes, adata, request, adinfo
                )
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _highly_variable_genes, name="highly_variable_genes", enabled=True
        )

    def _tool_pca_variance_ratio(self):
        def _pca_variance_ratio(
            request: PCAVarianceRatioParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Plot the PCA variance ratio to visualize explained variance."""
            try:
                if (
                    res := forward_request("pl_pca_variance_ratio", request, adinfo)
                ) is not None:
                    return res
                adata = get_ads().get_adata(adinfo=adinfo)
                fig_path = sc_like_plot(
                    sc.pl.pca_variance_ratio, adata, request, adinfo
                )
                return {"figpath": fig_path}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _pca_variance_ratio, name="pca_variance_ratio", enabled=True
        )
