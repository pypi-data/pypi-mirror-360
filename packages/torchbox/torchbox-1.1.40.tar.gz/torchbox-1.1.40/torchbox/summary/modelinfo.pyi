def profile(model, inputs=None, device='cpu', backend='torch'):
    """profile model

    Parameters
    ----------
    model : torch module
        the model to be profiled
    inputs : list, tuple, optional
         the input of network, by default None
    device : str, optional
         device string, by default 'cpu'
    backend : str, optional
        the backend tool for profiling, ``'torch'`` or ``'torchinfo'``, by default 'torch'
    """


