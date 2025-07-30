from pathlib import Path
import scanpy as sc
from fastmcp.tools.tool import Tool
from fastmcp.exceptions import ToolError
from scmcp_shared.schema.preset import AdataInfo
from scmcp_shared.schema.preset.io import *
from scmcp_shared.util import filter_args, forward_request, get_ads
from scmcp_shared.mcp_base import BaseMCP


class ScanpyIOMCP(BaseMCP):
    def __init__(
        self,
        include_tools: list = None,
        exclude_tools: list = None,
        AdataInfo=AdataInfo,
    ):
        """Initialize ScanpyIOMCP with optional tool filtering."""
        super().__init__("SCMCP-IO-Server", include_tools, exclude_tools, AdataInfo)

    def _tool_read(self):
        def _read(request: ReadParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """
            Read data from 10X directory or various file formats (h5ad, 10x, text files, etc.).
            """
            try:
                res = forward_request("io_read", request, adinfo)
                if res is not None:
                    return res
                kwargs = request.model_dump()
                file = Path(kwargs.get("filename", None))
                if file.is_dir():
                    kwargs["path"] = kwargs["filename"]
                    func_kwargs = filter_args(request, sc.read_10x_mtx)
                    adata = sc.read_10x_mtx(kwargs["path"], **func_kwargs)
                elif file.is_file():
                    func_kwargs = filter_args(request, sc.read)
                    adata = sc.read(**func_kwargs)
                    if kwargs.get("transpose", False):
                        adata = adata.T
                else:
                    raise FileNotFoundError(f"{kwargs['filename']} does not exist")

                ads = get_ads()
                if adinfo.sampleid is not None:
                    ads.active_id = adinfo.sampleid
                else:
                    ads.active_id = f"adata{len(ads.adata_dic[adinfo.adtype])}"

                adata.layers["counts"] = adata.X
                adata.var_names_make_unique()
                adata.obs_names_make_unique()
                adata.obs["scmcp_sampleid"] = adinfo.sampleid or ads.active_id
                ads.set_adata(adata, adinfo=adinfo)
                return [
                    {
                        "sampleid": adinfo.sampleid or ads.active_id,
                        "adtype": adinfo.adtype,
                        "adata": adata,
                        "adata.obs_names[:10]": adata.obs_names[:10],
                        "adata.var_names[:10]": adata.var_names[:10],
                        "notice": "check obs_names and var_names. transpose the data if needed",
                    }
                ]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_read, name="read", enabled=True)

    def _tool_write(self):
        def _write(request: WriteParam, adinfo: self.AdataInfo = self.AdataInfo()):
            """save adata into a file."""
            try:
                res = forward_request("io_write", request, adinfo)
                if res is not None:
                    return res
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                kwargs = request.model_dump()
                sc.write(kwargs["filename"], adata)
                return {"filename": kwargs["filename"], "msg": "success to save file"}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, "__context__") and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)

        return Tool.from_function(_write, name="write", enabled=True)


# Create an instance of the class
io_mcp = ScanpyIOMCP().mcp
