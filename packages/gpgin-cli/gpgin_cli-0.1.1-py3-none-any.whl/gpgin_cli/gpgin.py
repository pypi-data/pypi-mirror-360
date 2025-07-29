import torch
from torch import nn, Tensor
from torch_scatter import scatter
from torch_geometric.nn import MessagePassing, radius_graph, GraphNorm
from torch_geometric.utils import add_self_loops
from torch_geometric.typing import Adj
from typing import List


def constant(value, fill_value: float):
    if isinstance(value, Tensor):
        value.data.fill_(fill_value)
    else:
        for v in value.parameters() if hasattr(value, 'parameters') else []:
            constant(v, fill_value)
        for v in value.buffers() if hasattr(value, 'buffers') else []:
            constant(v, fill_value)


class GaussianSmearing(torch.nn.Module):
    def __init__(
        self,
        start: float = 0.0,
        stop: float = 5.0,
        num_gaussians: int = 50,
    ):
        super().__init__()
        offset = torch.linspace(start, stop, num_gaussians)
        self.coeff = -0.5 / (offset[1] - offset[0]).item()**2
        self.register_buffer('offset', offset)

    def forward(self, dist: Tensor) -> Tensor:
        dist = dist.view(-1, 1) - self.offset.view(1, -1)
        return torch.exp(self.coeff * torch.pow(dist, 2))
    
class MLP(nn.Module):
    def __init__(self, 
                input_dim, 
                hidden_dims, 
                output_dim, 
                norm=nn.LayerNorm, 
                final_norm=nn.Identity, 
                activation=nn.SiLU, 
                final_activation=nn.Identity, 
                dropout_rate=0.1, 
                final_dropout_rate=0.0,
                ):
        super().__init__()
        dims=[input_dim]+hidden_dims+[output_dim]
        self.lins=nn.ModuleList()
        self.norms=nn.ModuleList()
        self.acts=nn.ModuleList()
        self.dropouts=nn.ModuleList()
        for i in range(len(dims)-1):
            self.lins.append(nn.Linear(dims[i], dims[i+1]))
            if i+1<len(dims)-1:
                self.norms.append(norm(dims[i+1]))
                self.acts.append(activation())
                self.dropouts.append(nn.Dropout(dropout_rate))
            else:
                self.norms.append(final_norm(dims[i+1]))
                self.acts.append(final_activation())
                self.dropouts.append(nn.Dropout(final_dropout_rate))
        self.reset_parameters()
    def reset_parameters(self):
        for layer in self.lins:
            torch.nn.init.xavier_uniform_(layer.weight)
            layer.bias.data.fill_(0)
    def forward(self, x):
        for lin, norm, act, do in zip(self.lins, self.norms, self.acts, self.dropouts):
            x=lin(x)
            x=norm(x)
            x=act(x)
            x=do(x)
        return x

class RadiusInteractionGraph(torch.nn.Module):
    def __init__(self, cutoff: float = 10.0, max_num_neighbors: int = 32, with_self_loops=True):
        super().__init__()
        self.cutoff = cutoff
        self.max_num_neighbors = max_num_neighbors
        self.with_self_loops=with_self_loops

    def forward(self, pos: Tensor, batch: Tensor):
        edge_index = radius_graph(pos, r=self.cutoff, batch=batch,
                                  max_num_neighbors=self.max_num_neighbors)
        if self.with_self_loops:
            edge_index, _ = add_self_loops(edge_index)
        row, col = edge_index
        edge_weight = (pos[row] - pos[col]).norm(dim=-1)
        return edge_index, edge_weight

class ConvLayer(MessagePassing):
    cached_state_dict=None
    cutoff=10
    @classmethod
    def set_cached_state_dict(cls, x):
        cls.cached_state_dict=x
    @classmethod
    def get_cached_state_dict(cls):
        return cls.cached_state_dict
    def __init__(
        self,
        mlp_dims_node: List[int],
        mlp_dims_edge: List[int],
        
        aggr: str = 'sum',
        
        node_norm=nn.LayerNorm, 
        final_node_norm=nn.Identity, 
        
        edge_norm=nn.LayerNorm,
        final_edge_norm=nn.Identity, 
        
        activation=nn.SiLU, 
        final_activation=nn.Identity, 
        
        dropout_rate=0.1, 
        final_dropout_rate=0.0,
    ):
        super().__init__(node_dim=0,aggr=aggr)
        self.node_mlp=(MLP(
            mlp_dims_node[0], 
            mlp_dims_node[1:-1], 
            mlp_dims_node[-1],
            norm=node_norm, 
            final_norm=final_node_norm, 
            activation=activation, 
            final_activation=final_activation, 
            dropout_rate=dropout_rate, 
            final_dropout_rate=final_dropout_rate,
        ))
        #self.projector=(nn.Linear(mlp_dims_node[0], mlp_dims_node[0]+mlp_dims_edge[-1]))
        self.alpha=nn.Parameter(torch.empty(mlp_dims_edge[-1]))
        self.edge_mlp = MLP(
            mlp_dims_edge[0], 
            mlp_dims_edge[1:-1], 
            mlp_dims_edge[-1], 
            norm=edge_norm, 
            final_norm=nn.Identity,
            activation=activation, 
            final_activation=nn.Identity, 
            dropout_rate=dropout_rate, 
            final_dropout_rate=0,
        )
        
        self.reset_parameters()
        
    def reset_parameters(self):
        #torch.nn.init.xavier_uniform_(self.projector.weight)
        self.node_mlp.reset_parameters()
        self.edge_mlp.reset_parameters()
        constant(self.alpha,0.8)
        
    @classmethod
    def from_config(cls, config):
        return cls(**config)
        
    def get_config(self):
        return self.hparams
    
    def forward(self, 
                x: Tensor,
                edge_index: Adj, 
                edge_attr: Tensor):
        size = (x.size(0), x.size(0))
        edge_attr = self.edge_mlp(edge_attr)
        h0 = self.propagate(
            edge_index, 
            edge_attr=edge_attr, 
            x=x, 
            w=torch.tensor(1.0,device=x.device),
            size=size,
        )
        out=self.node_mlp(self.alpha.view(1,-1)*h0+x)
        return out
        
    def message(self, x_j: Tensor, edge_attr) -> Tensor:
        return x_j*edge_attr

def auto_save_hyperparams(init_fn):
    import inspect
    def wrapper(self, *args, **kwargs):
        # Bind the arguments to the function signature and apply defaults
        sig = inspect.signature(init_fn)
        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()
        # Save all parameters except 'self'
        self.hparams = {
            name: value 
            for name, value in bound_args.arguments.items() 
            if name != "self"
        }
        return init_fn(self, *args, **kwargs)
    return wrapper
    
class GPGIN(nn.Module):
    @auto_save_hyperparams
    def __init__(
                self, 
        
                node_dimses, 
                edge_dimses, 
        
                cutoff=10.0,
                max_neighbors=32,
                with_self_loops=True,
        
                aggr: str = 'sum',
                
                node_norm=nn.LayerNorm, 
                edge_norm=nn.LayerNorm,
                
                activation=nn.SiLU, 
                
                dropout_rate=0.1, 
                final_dropout_rate=0.0,
                ):
        super().__init__()
        assert len(node_dimses)==len(edge_dimses), "number of layers (MLPs) must be same for  nodes and edges"
        for i in range(len(node_dimses)-1):
            assert node_dimses[i][-1]==edge_dimses[i][-1], "mlp last dims must be the same for node and edge because they will be multiplied"
            assert edge_dimses[i][0]==edge_dimses[i+1][0], "edge dim must start the same since edge features are not dynamic"
        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()
        self.n_convs = len(node_dimses)
        self.atom_type_emb = nn.Embedding(200, node_dimses[0][0])
        self.interaction_graph=RadiusInteractionGraph(cutoff,max_neighbors,with_self_loops=with_self_loops)
        self.gaussian_smear = GaussianSmearing(0.0, cutoff, edge_dimses[0][0])
        for i, (mlp_dims_node, mlp_dims_edge) in enumerate(zip(node_dimses, edge_dimses)):
            if i+1<len(node_dimses):
                self.convs.append(ConvLayer(
                    mlp_dims_node, 
                    mlp_dims_edge, 
                    aggr=aggr,
                    node_norm=node_norm,
                    final_node_norm=node_norm,
                    edge_norm=edge_norm,
                    final_edge_norm=edge_norm,
                    activation=activation,
                    final_activation=activation,
                    dropout_rate=dropout_rate,
                    final_dropout_rate=dropout_rate,
                ))
            else:
                self.convs.append(ConvLayer(
                    mlp_dims_node, 
                    mlp_dims_edge, 
                    aggr=aggr,
                    node_norm=node_norm,
                    final_node_norm=nn.Identity,
                    edge_norm=edge_norm,
                    final_edge_norm=nn.Identity,
                    activation=activation,
                    final_activation=nn.Identity,
                    dropout_rate=dropout_rate,
                    final_dropout_rate=0,
                ))
            self.norms.append(GraphNorm(mlp_dims_node[-1]))
        self.alpha=nn.Parameter(torch.empty(self.n_convs))
        self.activation=activation()
        self.reset_parameters()
        
    def reset_parameters(self):
        for conv in self.convs:
            conv.reset_parameters()
        constant(self.alpha,0.8)#it seems from previously trained models that alpha tends to be 0.8 across the layers
            
    @classmethod
    def from_config(cls, config):
        return cls(**config)
        
    def get_config(self):
        return self.hparams

    def forward(self, data):
        return self._forward(data.atom_type, data.pos, data.batch)
        
    def _forward(self, atom_type, pos, batch=None):
        had_batch = batch is not None
        if not had_batch:
            batch=torch.zeros_like(pos[:,0]).long()
        edge_index, edge_length = self.interaction_graph(pos, batch)
        edge_attr = self.gaussian_smear(edge_length)
        h = self.atom_type_emb(atom_type)
        for i,(conv, norm) in enumerate(zip(self.convs, self.norms)):
            h_ = conv(h, edge_index, edge_attr)
            if i+1<len(self.convs):
                h_=norm(h_,batch)
                h_=self.activation(h_)
            h=h+self.alpha[i]*h_
        if had_batch:
            h= scatter(h,batch,dim=0,reduce='mean').mean(-1)
        else:
            h= h.mean((-2,-1))
        return h
