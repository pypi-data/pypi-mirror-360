from gpgin_cli.prolog import *
from gpgin_cli.gpgin import GPGIN
import torch
import numpy as np
from torch_geometric.loader import DataLoader
def run_inference(args):
    X=args.X
    out=args.out
    dataset=UserDataset(X, None, force_reload=args.force_reload_data).to(cuda)
    model=TrainingContext.load(args.name, GPGIN)
    y_mean=model.y_mean
    y_std=model.y_std
    model=model.inner.to(cuda).eval()
    bl=DataLoader(dataset, batch_size=args.batch_size)
    result=torch.zeros(len(dataset)).to(cuda)
    i=0
    with torch.no_grad():
        for batch in tqdm(bl, total=len(bl)):
            next_idx=i+batch.ptr.size(0)-1
            result[i:next_idx]=model.forward(batch)*y_std+y_mean
            i=next_idx
    np.savetxt(out, result.cpu().numpy(), fmt='%f')
