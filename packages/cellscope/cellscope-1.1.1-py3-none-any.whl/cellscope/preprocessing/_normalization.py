from typing import Tuple, Union, Optional,List
import pathlib
import scanpy as sc
import atopos

def normalise(adata:sc.AnnData,
    batch_key:str = "Sample",
    outdir:Union[pathlib.PosixPath,str] = pathlib.Path().absolute(),
    n_jobs:int = 1,
    n_top_genes:int = 3000,
    target_sum:int = 1e4,
    scale:bool = True,
    regress_out:Optional[List[str]] = ['pct_counts_Mito','total_counts'],
    dpi:int = 300,
    formats:tuple = ('pdf','png'),
    inplace:bool = False,
    ) -> Optional[sc.AnnData]:
    """
    normalise
    """
    # inplace=False;target_sum=1e4;n_top_genes=3000;batch_key='Sample'
    atopos.tl.mkdir(outdir)
    _saveimg = atopos.tl.saveimg(formats=formats,outdir=outdir,dpi=dpi)
    _adata = adata if inplace else adata.copy()
    _adata.layers["counts"] = _adata.X.copy()
    sc.pp.normalize_total(_adata, target_sum=target_sum, inplace=True)
    sc.pp.log1p(_adata,base=None)
    _adata.layers["data"] = _adata.X.copy()
    sc.pp.highly_variable_genes(_adata,n_top_genes=n_top_genes,flavor="seurat", batch_key=batch_key, subset=False,inplace=True)
    sc.pl.highly_variable_genes(_adata,show=False, log=True)
    _saveimg("highly_variable_genes_" + batch_key)
    if regress_out:
        sc.pp.regress_out(_adata, keys=regress_out, n_jobs=n_jobs)
    if scale:
        scaled = sc.pp.scale(_adata[:,_adata.var.highly_variable],copy=True)
        _adata.layers['scaledata']=scaled.X
    return None if inplace else _adata

