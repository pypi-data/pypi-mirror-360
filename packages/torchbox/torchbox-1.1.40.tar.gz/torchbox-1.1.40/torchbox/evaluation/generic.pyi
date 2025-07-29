def geval(P, G, tol, eps=1e-6):
    r"""generic evaluation function

    Parameters
    ----------
    P : list
        The predicted results, e.g. [(attribute1, attribute2, ...), (attribute1, attribute2, ...), ...]
    G : list
        The groundtruth results, e.g. [(attribute1, attribute2, ...), (attribute1, attribute2, ...), ...]
    tol : list or float
        The error tolerance for each attribute
    eps : float
        The precision, epsilon

        
    Examples
    --------

    ::

        import torchbox as tb

        P = [(1, 2.0), (3, 4.0), (5, 6.9)]
        G = [(1, 2.1), (3, 4.3)]

        print(P)
        print(G)
        print(tb.geval(P, G, tol=(0.5, 0.5)))

        P = [('cat', 1, 2.0), ('dog', 3, 4.0), ('bird', 5, 6.9)]
        G = [('cat', 1, 2.0), ('cat', 3, 4.3)]

        print(P)
        print(G)
        print(tb.geval(P, G, tol=(0, 0.5, 0.5)))


    """    

def eprint(rslt, fmt='%.4f'):
    r"""print evaluation result

    Parameters
    ----------
    rslt : dict
        evaluation result dict
    fmt : str, optional
        print formation of metric value, by default ``'%.4f'``

    """

def eplot(rslt, mode='vbar', xlabel=None, ylabel=None, title='Average performance of %d experiments', **kwargs):
    r"""plots evaluation results.

    plots evaluation results. If the results contain many experiments, it will be averaged.

    Parameters
    ----------
    rslt : dict
        The result dict of evaluation, {'Method1': {'Metric1': [...], 'Metric2': [...], ...}, 'Method2': {'Metric1': [...], 'Metric2': [...], ...}}
    mode : str, optional
        ``'mat'``, ``'barh'`` or ``'hbar'``, ``'barv'`` or ``'vbar'`` (default).
    xlabel : str, optional
        The label string of axis-x, by default :obj:`None` (if :attr:`mode` is ``'mat'``, ``'barv'`` or ``'vbar'``, :attr:`xlabel` is empty;
        if :attr:`mode` is ``'barh'`` or ``'hbar'``, :attr:`xlabel` is ``'Score'``.)
    ylabel : str, optional
        The label string of axis-y, by default :obj:`None` (if :attr:`mode` is ``'mat'``, ``'barh'`` or ``'hbar'``, :attr:`ylabel` is empty;
        if :attr:`mode` is ``'barv'`` or ``'vbar'``, :attr:`ylabel` is ``'Score'``.)
    title : str, optional
        The title string, by default ``'Average performance of %d experiments'``
    kwargs :
        cmap: str or None
            The colormap, by default :obj:`None`, which means our default configuration (green-coral)
            see :func:`~torchbox.utils.colors.rgb2gray` for available colormap str.
        colors: list or None
            the color for different method, only work when mode is bar, by default `None`
        grid: bool
            plot grid?, by default :obj:`False`
        bwidth: float
            The width of bar, by default ``0.5``
        bheight: float
            The height of bar, by default ``0.5``
        bspacing: float
            The spacing between bars, by default ``0.1``
        strftd : dict
            The font dict of label, title, method or metric names, by default ::

                dict(fontsize=12, color='black', 
                     family='Times New Roman', 
                     weight='light', style='normal')
        mvftd : dict
            The font dict of metric value, by default ::
            
                dict(fontsize=12, color='black', 
                     family='Times New Roman', 
                     weight='light', style='normal')
        mvfmt : str or None
            the format of metric value, such as ``'%.xf'`` means formating with two decimal places, by default ``'%.2f'``
            If :obj:`None`, no label.
        mvnorm: bool
            normalize the maximum metric value to 1? by default :obj:`False`

    Returns
    -------
    pyplot
        pyplot handle

        
    Examples
    --------

    ::

        import torchbox as tb

        result = {'Method1': {'Metric1': [1, 1.1, 1.2], 'Metric2': [2.1, 2.2, 2.3]}, 'Method2': {'Metric1': [11, 11.1, 11.2], 'Metric2': [21.1, 21.2, 21.3]}}
        tb.eprint(result)

        plt = tb.eplot(result, mode='mat')
        plt.show()
        plt = tb.eplot(result, mode='mat', mvnorm=True)
        plt.show()

        plt = tb.eplot(result, mode='mat', cmap='summer')
        plt.show()
        plt = tb.eplot(result, mode='mat', cmap='summer', mvnorm=True)
        plt.show()

        plt = tb.eplot(result, mode='vbar', bheight=0.5)
        plt.show()
        plt = tb.eplot(result, mode='vbar', bheight=0.5, mvnorm=True)
        plt.show()

        plt = tb.eplot(result, mode='hbar', bwidth=0.5)
        plt.show()
        plt = tb.eplot(result, mode='hbar', bwidth=0.5, mvnorm=True)
        plt.show()


    """    


