from collections.abc import Iterable
from abcoder.backend import NotebookManager

__all__ = ["AdataManager", "NotebookManager"]


class AdataManager:
    def __init__(self, add_adtypes=None):
        self.adata_dic = {"exp": {}, "activity": {}, "cnv": {}, "splicing": {}}
        if isinstance(add_adtypes, str):
            self.adata_dic[add_adtypes] = {}
        elif isinstance(add_adtypes, Iterable):
            self.adata_dic.update({adtype: {} for adtype in add_adtypes})
        self.active_id = None
        self.metadatWa = {}
        self.cr_kernel = {}
        self.cr_estimator = {}

    def get_adata(self, sampleid=None, adtype="exp", adinfo=None):
        if adinfo is not None:
            kwargs = adinfo.model_dump()
            sampleid = kwargs.get("sampleid", None)
            adtype = kwargs.get("adtype", "exp")
        try:
            if self.active_id is None:
                return None
            sampleid = sampleid or self.active_id
            return self.adata_dic[adtype][sampleid]
        except KeyError as e:
            raise KeyError(
                f"Key {e} not found in adata_dic[{adtype}].Please check the sampleid or adtype."
            )
        except Exception as e:
            raise Exception(f"fuck {e} {type(e)}")

    def set_adata(self, adata, sampleid=None, sdtype="exp", adinfo=None):
        if adinfo is not None:
            kwargs = adinfo.model_dump()
            sampleid = kwargs.get("sampleid", None)
            sdtype = kwargs.get("adtype", "exp")
        sampleid = sampleid or self.active_id
        if sdtype not in self.adata_dic:
            self.adata_dic[sdtype] = {}
        self.adata_dic[sdtype][sampleid] = adata
