import torch
import anndata
import numpy as np
import random
from src.sctfbridge.model import scTFBridge
from src.sctfbridge.model import explain_TF2TG, explain_RE2TG, explain_DisLatent


def set_seed(seed):
    import os
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    # torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.set_float32_matmul_precision('high')


set_seed(3407)

dataset_name = 'human_PBMC'
cell_key = 'cell_type'
batch_key = ''


gex_data = anndata.read_h5ad(f'filter_data/{dataset_name}/RNA_filter.h5ad')
atac_adata = anndata.read_h5ad(f'filter_data/{dataset_name}/ATAC_filter.h5ad')
TF_adata = anndata.read_h5ad(f'filter_data/{dataset_name}/TF_filter.h5ad')

TF_length = TF_adata.var.shape[0]

mask_path = f'filter_data/{dataset_name}/TF_binding/TF_binding.txt'


new_model = scTFBridge.load('sctfbridge_model', device=torch.device('cuda:7'))


output = explain_RE2TG(new_model,
                       [gex_data, atac_adata, TF_adata],
                       'human_PBMC',
                       use_gene_list=gex_data.var.index[:10],
                       cell_type='CD14 Mono',
                       cell_key='cell_type',
                       batch_key='',
                       device=torch.device('cuda:7'),
                       tf_binding_path=f'filter_data/{dataset_name}/TF_binding/')
print(output)