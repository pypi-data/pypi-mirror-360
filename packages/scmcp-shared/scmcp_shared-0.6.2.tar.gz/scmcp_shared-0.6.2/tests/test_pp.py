import pytest
from fastmcp import Client
from pathlib import Path
import nest_asyncio

# Apply nest_asyncio at module level
nest_asyncio.apply()


@pytest.mark.asyncio
async def test_complete_workflow(mcp):
    test_dir = Path(__file__).parent / "data/hg19"
    async with Client(mcp) as client:
        # Load the data
        result = await client.call_tool("io_read", {"request": {"filename": test_dir}})
        assert "AnnData" in result.content[0].text

        # Filter cells and genes
        result = await client.call_tool(
            "pp_subset_cells", {"request": {"min_genes": 200}}
        )
        assert "AnnData" in result.content[0].text
        result = await client.call_tool(
            "pp_subset_genes", {"request": {"min_cells": 3}}
        )
        assert "AnnData" in result.content[0].text

        # Add mitochondrial genes and calculate QC metrics
        result = await client.call_tool(
            "ul_mark_var",
            {
                "request": {
                    "var_name": "mt",
                    "pattern_type": "startswith",
                    "patterns": "MT-",
                }
            },
        )
        assert "mt" in result.content[0].text
        result = await client.call_tool(
            "pp_calculate_qc_metrics",
            {"request": {"qc_vars": ["mt"], "percent_top": None, "log1p": False}},
        )
        assert "total_counts" in result.content[0].text

        # Filter based on QC metrics
        result = await client.call_tool(
            "pp_subset_cells", {"request": {"max_genes": 2500, "max_mt_percent": 5}}
        )
        assert "AnnData" in result.content[0].text

        # Normalize and transform
        result = await client.call_tool(
            "pp_normalize_total", {"request": {"target_sum": 1e4}}
        )
        assert "AnnData" in result.content[0].text
        result = await client.call_tool("pp_log1p", {"request": {}})
        assert "log1p" in result.content[0].text

        # Find highly variable genes
        result = await client.call_tool(
            "pp_highly_variable_genes",
            {"request": {"min_mean": 0.0125, "max_mean": 3, "min_disp": 0.5}},
        )
        assert "highly_variable" in result.content[0].text

        # Subset to highly variable genes
        result = await client.call_tool(
            "pp_subset_genes", {"request": {"highly_variable": True}}
        )
        assert "AnnData" in result.content[0].text

        # Regress out effects
        result = await client.call_tool(
            "pp_regress_out", {"request": {"keys": ["total_counts", "pct_counts_mt"]}}
        )
        assert "AnnData" in result.content[0].text

        # Scale the data
        result = await client.call_tool("pp_scale", {"request": {"max_value": 10}})
        assert "AnnData" in result.content[0].text

        # PCA
        result = await client.call_tool(
            "tl_pca", {"request": {"n_comps": 50, "svd_solver": "arpack"}}
        )
        assert "X_pca" in result.content[0].text

        # Compute neighborhood graph
        result = await client.call_tool(
            "pp_neighbors", {"request": {"n_neighbors": 10, "n_pcs": 40}}
        )
        assert "neighbors" in result.content[0].text

        # Leiden clustering
        result = await client.call_tool("tl_leiden", {"request": {}})
        assert "leiden" in result.content[0].text

        # UMAP
        result = await client.call_tool("tl_umap", {"request": {}})
        assert "X_umap" in result.content[0].text

        # Plot UMAP
        result = await client.call_tool(
            "pl_embedding",
            {"request": {"basis": "umap", "color": ["leiden", "NKG7", "PPBP"]}},
        )
        assert "figure" in result.content[0].text
