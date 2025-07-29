def train_epoch(model, dl, nin, criterions, criterionws=None, gclip=None, optimizer=None, scheduler=None, epoch=None, logf='stdout', device='cuda:0', **kwargs):
    r"""train one epoch

    Parameters
    ----------
    model : Module
        an instance of torch.nn.Module
    dl : DataLoader
        the dataloader for training
    nin : int
        the number of input tensors
    criterions : list, tuple or function
        loss function or list/tuple of loss function, e.g. lossfn, [[output_target_pair1_lossf1, output_target_pair1_lossf2], [output_target_pair2_lossf1, output_target_pair2_lossf2], ...]
    criterionws : list, tuple, float or None
        float loss weight or list/tuple of float loss weight, e.g. w, [[w11, w12], [w21, w22]]
    gclip : function
        gradient clip function, default is :obj:`None`.
    optimizer : Optimizer or None
        an instance of torch.optim.Optimizer, default is :obj:`None`, 
        which means ``th.optim.Adam(model.parameters(), lr=0.001)``
    scheduler : LrScheduler or None
        an instance of torch.optim.LrScheduler, default is :obj:`None`, 
        which means using fixed learning rate
    epoch : int
        epoch index
    logf : str or object, optional
        IO for print log, file object or ``'stdout'`` (default)
    device : str, optional
        device for training, by default ``'cuda:0'``
    kwargs :
        (navg) ``'nb'`` average loss with the number of batchs, ``'ns'`` average loss with the number of samples.
        (...) other forward args

    see also :func:`~torchbox.optim.solver.valid_epoch`, :func:`~torchbox.optim.solver.test_epoch`, :func:`~torchbox.optim.save_load.save_model`, :func:`~torchbox.optim.save_load.load_model`.
    
    Examples
    ----------
    
    ::

        import torch as th
        import torchbox as tb

        device = 'cuda:0'
        th.manual_seed(2020)
        Ns, k, b = 200, 1.5, 3.0
        x = th.linspace(0, 10, Ns)
        t = x * k + b
        t = tb.awgn(t, snrv=30)

        deg = (0, 1)

        model = tb.PolyFit(deg=deg).to(device)

        dstrain = th.utils.data.TensorDataset(x, t)
        dltrain = th.utils.data.DataLoader(dstrain, batch_size=50, shuffle=True)
        dsvalid = th.utils.data.TensorDataset(x, t)
        dlvalid = th.utils.data.DataLoader(dsvalid, batch_size=20, shuffle=False)

        criterions = [[tb.SSELoss(reduction='sum'), tb.SSELoss(reduction='sum')]]
        criterionws = [[1., 0.5]]
        optimizer = th.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-2)
        scheduler = th.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.98)

        for n in range(1000):
            losstrain = tb.train_epoch(model, dltrain, 1, criterions, criterionws=criterionws, optimizer=optimizer, scheduler=None, epoch=n, logf='stdout', device=device)
            lossvalid = tb.valid_epoch(model, dlvalid, 1, criterions, criterionws=criterionws, epoch=n, logf='stdout', device=device)
            scheduler.step()
            print(model.w[0].item(), model.w[1].item(), scheduler.get_lr())
        y = tb.demo_epoch(model, x, 10, logf='stdout', device=device)

        print(y.shape)
        plt = tb.plot([[y.cpu(), t]], Xs=[[x, x]], legends=[['Pred', 'GT']])
        plt.show()

        
        # output
        --->Train epoch 996, loss: 0.2361, time: 0.01
        --->Valid epoch 996, loss: 0.2360, time: 0.01
        2.645081043243408 1.5538312196731567 [0.0013532607744362547]
        --->Train epoch 997, loss: 0.2360, time: 0.01
        --->Valid epoch 997, loss: 0.2359, time: 0.01
        2.6454339027404785 1.553778886795044 [0.0013532607744362547]
        --->Train epoch 998, loss: 0.2359, time: 0.01
        --->Valid epoch 998, loss: 0.2358, time: 0.01
        2.6457810401916504 1.553715705871582 [0.0013532607744362547]
        --->Train epoch 999, loss: 0.2358, time: 0.01
        --->Valid epoch 999, loss: 0.2357, time: 0.01
        2.6461341381073 1.5536682605743408 [0.001299671647768579]
        --->Demo, time: 0.00
        torch.Size([200])

    """

def valid_epoch(model, dl, nin, criterions, criterionws=None, epoch=None, logf='stdout', device='cuda:0', **kwargs):
    r"""valid one epoch

    Parameters
    ----------
    model : function handle
        an instance of torch.nn.Module
    dl : dataloder
        the validation dataloader
    nin : int
        the number of input tensors
    criterions : list, tuple or function
        loss function or list/tuple of loss function, e.g. lossfn, [[output_target_pair1_lossf1, output_target_pair1_lossf2], [output_target_pair2_lossf1, output_target_pair2_lossf2], ...]
    criterionws : list, tuple, float or None
        float loss weight or list/tuple of float loss weight, e.g. w, [[w11, w12], [w21, w22]]
    epoch : int
        epoch index,  default is None
    logf : str or object, optional
        IO for print log, file object or ``'stdout'`` (default)
    device : str, optional
        device for validation, by default ``'cuda:0'``
    kwargs :
        (navg) ``'nb'`` average loss with the number of batchs, ``'ns'`` average loss with the number of samples.
        (...) other forward args

    see also :func:`~torchbox.optim.solver.train_epoch`, :func:`~torchbox.optim.solver.test_epoch`, :func:`~torchbox.optim.save_load.save_model`, :func:`~torchbox.optim.save_load.load_model`.

    """

def test_epoch(model, dl, nin, criterions, criterionws=None, epoch=None, logf='stdout', device='cuda:0', **kwargs):
    """Test one epoch

    Parameters
    ----------
    model : function handle
        an instance of torch.nn.Module
    dl : dataloder
        the testing dataloader
    nin : int
        the number of input tensors
    criterions : list, tuple or function
        loss function or list/tuple of loss function, e.g. lossfn, [[output_target_pair1_lossf1, output_target_pair1_lossf2], [output_target_pair2_lossf1, output_target_pair2_lossf2], ...]
    criterionws : list, tuple, float or None
        float loss weight or list/tuple of float loss weight, e.g. w, [[w11, w12], [w21, w22]]
    epoch : int or None
        epoch index,  default is None
    logf : str or object, optional
        IO for print log, file object or ``'stdout'`` (default)
    device : str, optional
        device for testing, by default ``'cuda:0'``
    kwargs :
        (navg) ``'nb'`` average loss with the number of batchs, ``'ns'`` average loss with the number of samples.
        (...) other forward args

    see also :func:`~torchbox.optim.solver.train_epoch`, :func:`~torchbox.optim.solver.valid_epoch`, :func:`~torchbox.optim.save_load.save_model`, :func:`~torchbox.optim.save_load.load_model`.

    """

def demo_epoch(model, data, bs, logf='stdout', device='cuda:0', odevice='cpu', **kwargs):
    """Test one epoch

    Parameters
    ----------
    model : function handle
        an instance of torch.nn.Module
    data : tensor or list of tensors
        the data of network inputs
    bs : int
        batch size
    logf : str or object, optional
        IO for print log, file object or ``'stdout'`` (default)
    device : str, optional
        device for testing, by default ``'cuda:0'``
    odevice : str, optional
        device of output, by default ``'cpu'``
    kwargs :
        other forward args

    see also :func:`~torchbox.optim.solver.train_epoch`, :func:`~torchbox.optim.solver.valid_epoch`, :func:`~torchbox.optim.save_load.save_model`, :func:`~torchbox.optim.save_load.load_model`.

    """


