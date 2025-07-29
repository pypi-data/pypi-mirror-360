from gpgin_cli.prolog import *
from gpgin_cli.gpgin import GPGIN
import torch
from torch_geometric.loader import DataLoader
def run_training(args):
    X=args.X
    y=args.y
    N_EPOCHS=args.n_epochs
    if not args.force_retrain:
        path=get_cliapp_root_dir()/'models'/(args.name+'.pth')
        if os.path.exists(path):
            print("model with the same name already exists, but --force_retrain is not present")
            return
    dataset=UserDataset(X, y, force_reload=args.force_reload_data)
    test_size = min(int(0.2*len(dataset)), 1024)
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [len(dataset)-test_size, test_size])
    ctx=TrainingContext(GPGIN,
        node_dimses=[
            [120, 150, 120],
            [120, 150, 120],
            [120, 150, 120],
            [120, 150, 120],
            [120, 150, 120],
            [120, 150, 1 ],
        ],
        edge_dimses=[
            [50, 220, 120],
            [50, 220, 120],
            [50, 220, 120],
            [50, 220, 120],
            [50, 220, 120],
            [50, 220, 120],
        ],
        activation=nn.SiLU,
        dropout_rate=0
        )
    ctx.second_init(
        name=args.name,
        batch_size=args.batch_size,
        target_name=args.target_name,
        dataset_name=args.dataset_name,
        y_mean=dataset.y_mean,
        y_std=dataset.y_std,
    )
    models = [ctx]
    BATCH_SIZE=ctx.batch_size
    N_mols=len(train_dataset)
    long_bar=tqdm(range(N_EPOCHS*N_mols//BATCH_SIZE),smoothing=0)
    e_bar=tqdm(range(N_mols//BATCH_SIZE),smoothing=0)
    Q=10000
    for model in models:
        model.inner=model.inner.train()
        model.stopped=False
    
    for epoch in range(N_EPOCHS):
        e_bar.refresh()
        e_bar.reset(N_mols//BATCH_SIZE)
        train_bl=DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
        for i, batch in zip(range(N_mols//BATCH_SIZE), train_bl):
            long_bar.update(1)
            e_bar.update(1)
            
            try:
                batch=(batch.to(cuda))
                
                for model in models:
                    if model.stopped or not model.training: continue
                    model.inner=model.inner.train()
                    out = model.inner(batch)
                    extra_loss=0
                    if isinstance(out, tuple):
                        out, extra_loss=out
                    loss = ((out*model.y_std+model.y_mean-batch.y)**2).mean()+extra_loss
                    model.inner.zero_grad(set_to_none=True)
                    
                    if model.total_iters<5:
                        model.running_loss = model.running_loss*.3+loss.item()*.7
                    else:
                        model.running_loss = model.running_loss*(1-1/100)+loss.item()/100
                        
                    if model.total_iters+.2>1.1**len(model.train_loss_record):
                        model.train_loss_record[model.total_iters]=model.running_loss
                    loss.backward()
                    model.optim.step()
                    model.total_iters+=1
                    if model.total_iters%100_000==0:
                        model.sched.step()
                        
    
                ### evaluation
                if i%64==0:
                    for model in models:
                        if model.stopped or not model.training: continue
                        model.inner=model.inner.eval()
                        L=len(test_dataset)
                        test_bl=DataLoader(test_dataset, batch_size=L)
                        all_eval_y=list()
                        model.test_loss_record[model.total_iters]=0
                        for batch in test_bl:
                            batch=(batch.to(cuda))
                            all_eval_y+=batch.y.view(-1).tolist()
                            with torch.no_grad():
                                out = model.inner(batch)
                                if isinstance(out, tuple):
                                    out, _=out
                            model.results=out.view(-1).tolist()
                            loss = ((out*model.y_std+model.y_mean-batch.y).abs()).sum().detach().item()
                            model.test_loss_record[model.total_iters]+=loss/L
                        
                        if model.test_loss_record[model.total_iters]<model.best_eval_loss:
                            model.best_eval_loss=model.test_loss_record[model.total_iters]
                            model.save()

                ###logging
                logstr=''
                for model in models:
                    if model.stopped:
                        logstr+=f'{model.name}(stopped) => running MSE: {int(Q*model.running_loss)/Q}(best eval MAE: {int(Q*model.best_eval_loss)/Q}). '
                    else:
                        logstr+=f'{model.name} => running MSE: {int(Q*model.running_loss)/Q} (best eval MAE: {int(Q*model.best_eval_loss)/Q}). '
                e_bar.set_description(logstr)
            except Exception as e:
                raise e
