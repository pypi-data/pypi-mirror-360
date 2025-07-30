from pydantic import Field, field_validator, model_validator, BaseModel
from typing import Optional, Literal


class ReadParam(BaseModel):
    """Input schema for the read tool."""

    adata: str = Field(
        ..., description="The AnnData object variable name will be stored in."
    )
    filename: str = Field(
        ...,
        description="Path to the file to read. If the filename has no file extension, it is interpreted as a key for generating a filename via sc.settings.writedir / (filename + sc.settings.file_format_data).",
    )

    backed: Optional[Literal["r", "r+"]] = Field(
        default=None,
        description="If 'r', load AnnData in backed mode instead of fully loading it into memory (memory mode). If you want to modify backed attributes of the AnnData object, you need to choose 'r+'.",
    )

    sheet: Optional[str] = Field(
        default=None, description="Name of sheet/table in hdf5 or Excel file."
    )

    ext: Optional[str] = Field(
        default=None,
        description="Extension that indicates the file type. If None, uses extension of filename.",
    )

    delimiter: Optional[str] = Field(
        default=None,
        description="Delimiter that separates data within text file. If None, will split at arbitrary number of white spaces, which is different from enforcing splitting at any single white space ' '.",
    )

    first_column_names: bool = Field(
        default=False,
        description="Assume the first column stores row names. This is only necessary if these are not strings: strings in the first column are automatically assumed to be row names.",
    )

    backup_url: Optional[str] = Field(
        default=None,
        description="Retrieve the file from an URL if not present on disk.",
    )

    cache: bool = Field(
        default=False,
        description="If False, read from source, if True, read from fast 'h5ad' cache.",
    )

    cache_compression: Optional[Literal["gzip", "lzf"]] = Field(
        default=None,
        description="See the h5py Filter pipeline. (Default: settings.cache_compression)",
    )

    @field_validator("backed")
    def validate_backed(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["r", "r+"]:
            raise ValueError("If backed is provided, it must be either 'r' or 'r+'")
        return v

    @field_validator("cache_compression")
    def validate_cache_compression(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["gzip", "lzf"]:
            raise ValueError("cache_compression must be either 'gzip', 'lzf', or None")
        return v


class Read10xMtxParam(BaseModel):
    """Input schema for the read_10x_mtx tool."""

    path: str = Field(
        ...,
        description="Path to directory for .mtx and .tsv files, e.g. './filtered_gene_bc_matrices/hg19/'.",
    )

    var_names: Literal["gene_symbols", "gene_ids"] = Field(
        default="gene_symbols", description="The variables index."
    )

    make_unique: bool = Field(
        default=True,
        description="Whether to make the variables index unique by appending '-1', '-2' etc. or not.",
    )

    cache: bool = Field(
        default=False,
        description="If False, read from source, if True, read from fast 'h5ad' cache.",
    )

    cache_compression: Optional[Literal["gzip", "lzf"]] = Field(
        default=None,
        description="See the h5py Filter pipeline. (Default: settings.cache_compression)",
    )

    gex_only: bool = Field(
        default=True,
        description="Only keep 'Gene Expression' data and ignore other feature types, e.g. 'Antibody Capture', 'CRISPR Guide Capture', or 'Custom'",
    )

    prefix: Optional[str] = Field(
        default=None,
        description="Any prefix before matrix.mtx, genes.tsv and barcodes.tsv. For instance, if the files are named patientA_matrix.mtx, patientA_genes.tsv and patientA_barcodes.tsv the prefix is patientA_. (Default: no prefix)",
    )

    @field_validator("path")
    def validate_path(cls, v: str) -> str:
        """Validate path is not empty"""
        if not v.strip():
            raise ValueError("path cannot be empty")
        return v

    @field_validator("var_names")
    def validate_var_names(cls, v: str) -> str:
        """Validate var_names is supported"""
        if v not in ["gene_symbols", "gene_ids"]:
            raise ValueError("var_names must be either 'gene_symbols' or 'gene_ids'")
        return v

    @field_validator("cache_compression")
    def validate_cache_compression(cls, v: Optional[str]) -> Optional[str]:
        """Validate cache_compression is supported if provided"""
        if v is not None and v not in ["gzip", "lzf"]:
            raise ValueError("cache_compression must be either 'gzip', 'lzf', or None")
        return v


class WriteParam(BaseModel):
    """Input schema for the write tool."""

    adata: str = Field(..., description="The AnnData object variable name.")
    filename: str = Field(
        description="Path to save the file. If no extension is provided, the default format will be used."
    )
    ext: Literal["h5", "csv", "txt", "npz"] = Field(
        default=None,
        description="File extension to infer file format. If None, defaults to scanpy's settings.file_format_data.",
    )
    compression: Literal["gzip", "lzf"] = Field(
        default="gzip", description="Compression format for h5 files."
    )
    compression_opts: int = Field(
        default=None, description="Compression options for h5 files."
    )

    @field_validator("filename")
    def validate_filename(cls, v: str) -> str:
        # Allow any filename since the extension is optional and can be inferred
        return v

    @model_validator(mode="after")
    def validate_extension_compression(self) -> "WriteParam":
        # If ext is provided and not h5, compression should be None
        if self.ext is not None and self.ext != "h5" and self.compression is not None:
            raise ValueError("Compression can only be used with h5 files")
        return self
