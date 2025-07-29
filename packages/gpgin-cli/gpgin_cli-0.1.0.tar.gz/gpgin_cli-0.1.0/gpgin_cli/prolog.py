import torch
from torch import nn
from tqdm.auto import tqdm
from rdkit import Chem, RDLogger
from typing import List, Optional
from torch_geometric.data import Data, InMemoryDataset
import os
cuda=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# Suppress RDKit warnings
RDLogger.DisableLog('rdApp.*')
from pathlib import Path

def get_cliapp_root_dir(mkdir=False) -> Path:
    path = Path.home() / ".gpgin"
    if mkdir:
        path.mkdir(parents=True, exist_ok=True)
    return path

    
class MolData(Data):
    def __inc__(self, key, value, *args, **kwargs):
        if 'index' in key:
            return self.num_nodes
        elif key=='dest' or key=='inbound':
            return self.num_edges
        else:
            return 0
    
    def __cat_dim__(self, key, value, *args, **kwargs):
        if 'index' in key:
            return 1
        else:
            return 0

import numpy as np
import hashlib

def file_checksum(*files):
    h = hashlib.new('sha256')
    for filepath in files:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
    return h.hexdigest()


class UserDataset(InMemoryDataset):

    def __init__(
        self,
        x_file: str,
        y_file: Optional[str],
        transform = None,
        pre_transform = None,
        pre_filter = None,
        force_reload = False,
    ) -> None:
        root=get_cliapp_root_dir(mkdir=True)
        self.x_file=x_file
        self.y_file=y_file
        files = (x_file, y_file) if y_file else (x_file,)
        self.checksum=file_checksum(*files)
        super().__init__(root, transform, pre_transform, pre_filter,
                         force_reload=force_reload)
        self._load_with_metadata(self.processed_paths[0])
    
    def _load_with_metadata(self, path):
        obj = torch.load(path)
        self.data, self.slices = obj['data'], obj['slices']
        self.y_mean = obj['y_mean']
        self.y_std = obj['y_std']

    @property
    def raw_file_names(self) -> List[str]:
        return []

    @property
    def processed_file_names(self) -> str:
        return [f'{self.checksum}.pt']

    def download(self) -> None:
        pass
    
    def process(self) -> None:
        suppl = Chem.SDMolSupplier(self.x_file)
        Y = (None for _ in range(len(suppl)))
        if self.y_file:
            Y = np.loadtxt(self.y_file, dtype=float)
            self.y_mean = float(np.mean(Y))
            self.y_std = float(np.std(Y))
        
        data_list = []
        for mol, y in zip(tqdm(suppl), Y):
            if isinstance(mol, Chem.Mol):
                d = Data(mol=mol)
                data_list.append(process_molecule_sparse(d, y))
        
        data, slices = self.collate(data_list)
        if self.y_file:
            torch.save({
                'data': data,
                'slices': slices,
                'y_mean': self.y_mean,
                'y_std': self.y_std,
            }, self.processed_paths[0])
        else:
            torch.save({
                'data': data,
                'slices': slices,
                'y_mean': float('nan'),
                'y_std': float('nan'),
            }, self.processed_paths[0])



ATOMIC_SYMBOL = {
    'H':0, 'He': 1, 'Li': 2, 'Be': 3, 'B': 4, 'C': 5, 'N': 6, 'O': 7, 'F': 8, 'Ne': 9, 
    'Na': 10, 'Mg': 11, 'Al': 12, 'Si': 13, 'P': 14, 'S': 15, 'Cl': 16, 'Ar': 17, 
    'K': 18, 'Ca': 19, 'Sc': 20, 'Ti': 21, 'V': 22, 'Cr': 23, 'Mn': 24, 'Fe': 25, 
    'Co': 26, 'Ni': 27, 'Cu': 28, 'Zn': 29, 'Ga': 30, 'Ge': 31, 'As': 32, 'Se': 33, 
    'Br': 34, 'Kr': 35, 'Rb': 36, 'Sr': 37, 'Y': 38, 'Zr': 39, 'Nb': 40, 'Mo': 41, 
    'Tc': 42, 'Ru': 43, 'Rh': 44, 'Pd': 45, 'Ag': 46, 'Cd': 47, 'In': 48, 'Sn': 49, 
    'Sb': 50, 'Te': 51, 'I': 52, 'Xe': 53, 'Cs': 54, 'Ba': 55, 'La': 56, 'Ce': 57, 
    'Pr': 58, 'Nd': 59, 'Pm': 60, 'Sm': 61, 'Eu': 62, 'Gd': 63, 'Tb': 64, 'Dy': 65, 
    'Ho': 66, 'Er': 67, 'Tm': 68, 'Yb': 69, 'Lu': 70, 'Hf': 71, 'Ta': 72, 'W ': 73, 
    'Re': 74, 'Os': 75, 'Ir': 76, 'Pt': 77, 'Au': 78, 'Hg': 79, 'Tl': 80, 'Pb': 81, 
    'Bi': 82, 'Po': 83, 'At': 84, 'Rn': 85, 'Fr': 86, 'Ra': 87, 'Ac': 88, 'Th': 89, 
    'Pa': 90, 'U': 91, 'Np': 92, 'Pu': 93, 'Am': 94, 'Cm': 95, 'Bk': 96, 'Cf': 97, 
    'Es': 98, 'Fm': 99, 'Md': 100, 'No': 101, 'Lr': 102, 'Rf': 103, 'Db': 104, 'Sg': 105, 
    'Bh': 106, 'Hs': 107, 'Mt': 108, 'Ds': 109, 'Rg': 110, 'Cn': 111, 'Nh': 112, 'Fl': 113, 
    'Mc': 114, 'Lv': 115, 'Ts': 116, 'Og': 117
}

DEFAULT_TYPE=torch.tensor([]).dtype
def process_molecule_sparse(data: Data, y: Optional[float]):
    m = data.mol
    conf: Chem.Conformer=m.GetConformer()
    atoms: List[Chem.Atom]=m.GetAtoms()
    Nv=len(atoms)
    atom_type=torch.empty(Nv).long()
    P=torch.empty(Nv, 3, dtype=DEFAULT_TYPE)
    for idx,atom in enumerate(atoms):
        atom_type[idx]=ATOMIC_SYMBOL[atom.GetSymbol()]
        p=conf.GetAtomPosition(idx)
        P[idx]=torch.tensor([p.x,p.y,p.z])
    if y is not None:
        return Data(atom_type=atom_type,pos=P,y=torch.tensor(y))
    return Data(atom_type=atom_type,pos=P)

def load_model(name,cls,prefix='saves'):
    checkpoint=torch.load(os.path.join(prefix,name,'checkpoint.pth'))
    instance:nn.Module = cls.from_config(checkpoint['config'])
    instance.load_state_dict(checkpoint['model_state_dict'])
    return instance

def save_model(
    name, 
    model, 
    optimizer=None, 
    scheduler=None, 
    arch=None, 
    epoch=None,
    loss_record=None, 
    loss_metric=None,
    total_training_iters=None,
    target_name=None, 
    batch_size=None,
    dataset_name=None,
    tag_uuid=True,
    or_tag_date=True,
    allow_overwrite=False,
    y_mean=None,
    y_std=None,
    prefix='saves',
):
    import inspect
    if tag_uuid:
        import uuid
        name=name+'-'+uuid.uuid4().hex[:6]
    elif or_tag_date:
        import datetime
        suffix=datetime.datetime.now().strftime("%y%m%d")
        name=name+'-'+suffix
    checkpoint = {
        'epoch': epoch,
        'loss_record': loss_record if loss_record is not None else dict(),  
        'loss_metric': loss_metric, 
        'target_name': target_name,  
        'total_training_iters': total_training_iters,
        'arch': arch, 
        'batch_size': batch_size, 
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict() if optimizer is not None else None,
        'scheduler_state_dict': scheduler.state_dict() if scheduler is not None else None,
        'y_mean':y_mean,
        'y_std':y_std,
        'config': model.get_config(), 
        'arch': arch if arch is not None else type(model).__name__,
    }
    
    torch.save(checkpoint, os.path.join(prefix,name+'.pth'))


class TrainingContext:
    def __init__(self, cls, *args, **kwargs):
        self.inner = cls(*args, **kwargs).to(cuda)
        self.name = cls.__name__
        self.optim = torch.optim.AdamW(self.inner.parameters())
        self.sched = torch.optim.lr_scheduler.ExponentialLR(self.optim, gamma=0.96)
        self.num_parameters = sum(map(torch.numel, self.inner.parameters()))
        self.train_loss_record = dict()
        self.test_loss_record = dict()
        self.results = list()
        self.total_iters = 0
        self.running_loss = 0
        self.best_eval_loss = 99e99
        self.stopped = False
        self.batch_size = 32
        self.train_loss_metric='MSE'
        self.eval_loss_metric='MAE'
        self.target_name='undefined'
        self.dataset_name='undefined'
        self.y_mean = float('nan')
        self.y_std = float('nan')
        self.training=True
    def second_init(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError(f"{k} is not a valid attribute")

    def save(self):
        prefix=get_cliapp_root_dir()/"models"
        prefix.mkdir(parents=True, exist_ok=True)
        save_model(
            self.name,
            self.inner,
            optimizer=self.optim,
            scheduler=self.sched,
            loss_record={
                'train':self.train_loss_record,
                'test':self.test_loss_record,
            },
            total_training_iters=self.total_iters,
            batch_size=self.batch_size,
            loss_metric={
                'train':'MSE',
                'test':'MAE',
            },
            target_name=self.target_name,
            dataset_name=self.dataset_name,
            tag_uuid=False,
            or_tag_date=False,
            allow_overwrite=True,
            y_mean=self.y_mean,
            y_std=self.y_std,
            prefix=prefix
        )
    @classmethod
    def load(cls, name, class_, training=False, override=None):
        prefix=get_cliapp_root_dir()/"models"
        if override is None:
            override=dict()
        checkpoint=torch.load(os.path.join(prefix,name+'.pth'))
        self=cls(class_,**dict(**checkpoint['config'],**override))
        self.inner.load_state_dict(checkpoint['model_state_dict'])
        self.optim.load_state_dict(checkpoint['optimizer_state_dict'])
        self.sched.load_state_dict(checkpoint['scheduler_state_dict'])
        self.total_iters=checkpoint['total_training_iters']
        self.batch_size=checkpoint['batch_size']
        self.train_loss_record=checkpoint['loss_record']['train']
        self.test_loss_record=checkpoint['loss_record']['test']
        self.best_eval_loss=min(self.test_loss_record.values())
        self.y_mean=checkpoint['y_mean']
        self.y_std=checkpoint['y_std']
        self.training=training
        return self
    
