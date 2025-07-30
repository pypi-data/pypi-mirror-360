import scanpy as sc
from fastmcp.exceptions import ToolError
from fastmcp.tools.tool import Tool
from scmcp_shared.schema.preset.tl import *
from scmcp_shared.schema.preset import AdataInfo
from scmcp_shared.util import (
    filter_args,
    add_op_log,
    forward_request,
    get_ads,
    generate_msg,
)
from scmcp_shared.mcp_base import BaseMCP


class ScanpyToolsMCP(BaseMCP):
    def __init__(
        self,
        include_tools: list = None,
        exclude_tools: list = None,
        AdataInfo: AdataInfo = AdataInfo,
    ):
        """
        Initialize ScanpyMCP with optional tool filtering.

        Args:
            include_tools (list, optional): List of tool names to include. If None, all tools are included.
            exclude_tools (list, optional): List of tool names to exclude. If None, no tools are excluded.
            AdataInfo: The AdataInfo class to use for type annotations.
        """
        super().__init__("ScanpyMCP-TL-Server", include_tools, exclude_tools, AdataInfo)

    def _tool_tsne(self):
        def _tsne(
            request: TSNEParam = TSNEParam(), adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """t-distributed stochastic neighborhood embedding (t-SNE) for visualization"""
            try:
                result = forward_request("tl_tsne", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.tsne)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.tsne(adata, **func_kwargs)
                add_op_log(adata, sc.tl.tsne, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_tsne, name="tsne", enabled=True)

    def _tool_umap(self):
        def _umap(
            request: UMAPParam = UMAPParam(), adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Uniform Manifold Approximation and Projection (UMAP) for visualization"""
            try:
                result = forward_request("tl_umap", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.umap)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.umap(adata, **func_kwargs)
                add_op_log(adata, sc.tl.umap, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_umap, name="umap", enabled=True)

    def _tool_draw_graph(self):
        def _draw_graph(
            request: DrawGraphParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Force-directed graph drawing"""
            try:
                result = forward_request("tl_draw_graph", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.draw_graph)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.draw_graph(adata, **func_kwargs)
                add_op_log(adata, sc.tl.draw_graph, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_draw_graph, name="draw_graph", enabled=True)

    def _tool_diffmap(self):
        def _diffmap(request: DiffMapParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """Diffusion Maps for dimensionality reduction"""
            try:
                result = forward_request("tl_diffmap", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.diffmap)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.diffmap(adata, **func_kwargs)
                adata.obsm["X_diffmap"] = adata.obsm["X_diffmap"][:, 1:]
                add_op_log(adata, sc.tl.diffmap, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_diffmap, name="diffmap", enabled=True)

    def _tool_embedding_density(self):
        def _embedding_density(
            request: EmbeddingDensityParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Calculate the density of cells in an embedding"""
            try:
                result = forward_request("tl_embedding_density", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.embedding_density)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.embedding_density(adata, **func_kwargs)
                add_op_log(adata, sc.tl.embedding_density, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
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

    def _tool_leiden(self):
        def _leiden(
            request: LeidenParam = LeidenParam(),
            adinfo: self.AdataInfo = self.AdataInfo(),
        ):
            """Leiden clustering algorithm for community detection"""
            try:
                result = forward_request("tl_leiden", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.leiden)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.leiden(adata, **func_kwargs)
                add_op_log(adata, sc.tl.leiden, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_leiden, name="leiden", enabled=True)

    def _tool_louvain(self):
        def _louvain(
            request: LouvainParam = LouvainParam(),
            adinfo: self.AdataInfo = self.AdataInfo(),
        ):
            """Louvain clustering algorithm for community detection"""
            try:
                result = forward_request("tl_louvain", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.louvain)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.louvain(adata, **func_kwargs)
                add_op_log(adata, sc.tl.louvain, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_louvain, name="louvain", enabled=True)

    def _tool_dendrogram(self):
        def _dendrogram(
            request: DendrogramParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Hierarchical clustering dendrogram"""
            try:
                result = forward_request("tl_dendrogram", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.dendrogram)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.dendrogram(adata, **func_kwargs)
                add_op_log(adata, sc.tl.dendrogram, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_dendrogram, name="dendrogram", enabled=True)

    def _tool_dpt(self):
        def _dpt(request: DPTParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """Diffusion Pseudotime (DPT) analysis"""
            try:
                result = forward_request("tl_dpt", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.dpt)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.dpt(adata, **func_kwargs)
                add_op_log(adata, sc.tl.dpt, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_dpt, name="dpt", enabled=True)

    def _tool_paga(self):
        def _paga(request: PAGAParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """Partition-based graph abstraction"""
            try:
                result = forward_request("tl_paga", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.paga)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.paga(adata, **func_kwargs)
                add_op_log(adata, sc.tl.paga, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_paga, name="paga", enabled=True)

    def _tool_ingest(self):
        def _ingest(request: IngestParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """Map labels and embeddings from reference data to new data"""
            try:
                result = forward_request("tl_ingest", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.ingest)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.ingest(adata, **func_kwargs)
                add_op_log(adata, sc.tl.ingest, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_ingest, name="ingest", enabled=True)

    def _tool_rank_genes_groups(self):
        def _rank_genes_groups(
            request: RankGenesGroupsParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Rank genes for characterizing groups, for differentially expressison analysis"""
            try:
                result = forward_request("tl_rank_genes_groups", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.rank_genes_groups)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.rank_genes_groups(adata, **func_kwargs)
                add_op_log(adata, sc.tl.rank_genes_groups, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
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

    def _tool_filter_rank_genes_groups(self):
        def _filter_rank_genes_groups(
            request: FilterRankGenesGroupsParam,
            adinfo: self.AdataInfo = self.AdataInfo(),
        ):
            """Filter out genes based on fold change and fraction of genes"""
            try:
                result = forward_request("tl_filter_rank_genes_groups", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.filter_rank_genes_groups)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.filter_rank_genes_groups(adata, **func_kwargs)
                add_op_log(adata, sc.tl.filter_rank_genes_groups, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _filter_rank_genes_groups, name="filter_rank_genes_groups", enabled=True
        )

    def _tool_marker_gene_overlap(self):
        def _marker_gene_overlap(
            request: MarkerGeneOverlapParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Calculate overlap between data-derived marker genes and reference markers"""
            try:
                result = forward_request("tl_marker_gene_overlap", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.marker_gene_overlap)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.marker_gene_overlap(adata, **func_kwargs)
                add_op_log(adata, sc.tl.marker_gene_overlap, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _marker_gene_overlap, name="marker_gene_overlap", enabled=True
        )

    def _tool_score_genes(self):
        def _score_genes(
            request: ScoreGenesParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Score a set of genes based on their average expression"""
            try:
                result = forward_request("tl_score_genes", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.score_genes)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.score_genes(adata, **func_kwargs)
                add_op_log(adata, sc.tl.score_genes, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_score_genes, name="score_genes", enabled=True)

    def _tool_score_genes_cell_cycle(self):
        def _score_genes_cell_cycle(
            request: ScoreGenesCellCycleParam, adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Score cell cycle genes and assign cell cycle phases"""
            try:
                result = forward_request("tl_score_genes_cell_cycle", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.score_genes_cell_cycle)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.score_genes_cell_cycle(adata, **func_kwargs)
                add_op_log(adata, sc.tl.score_genes_cell_cycle, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(
            _score_genes_cell_cycle, name="score_genes_cell_cycle", enabled=True
        )

    def _tool_pca(self):
        def _pca(
            request: PCAParam = PCAParam(), adinfo: self.AdataInfo = self.AdataInfo()
        ):
            """Compute PCA (Principal Component Analysis)."""
            try:
                result = forward_request("tl_pca", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.pca)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.pca(adata, **func_kwargs)
                add_op_log(adata, sc.tl.pca, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_pca, name="pca", enabled=True)
