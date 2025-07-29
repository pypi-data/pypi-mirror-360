class LossLog():
    ...

    def __init__(self, plotdir=None, xlabel='Epoch', ylabel='Loss', title=None, filename=None, logdict=None, lom='min'):
        ...

    def assign(self, key, value):
        ...

    def add(self, key, value):
        ...

    def get(self, key=None):
        ...

    def updir(self, plotdir=None):
        ...

    def plot(self, x=None, offset=0):
        ...

    def judge(self, key, n1=50, n2=10):
        r"""judge how to save weights

        |____n1____|__n2__||
                       current epoch

        If the average loss of the last n2 epochs is better than the average of the previous n1 epochs 
        and the loss value of the current epoch is the best among the n2 epochs, 
        then save the weights of current epoch with ``'Average'`` flag. 
        If the loss of current epoch is the best of all previous epochs, then save the weights of 
        current epoch with ``'Single'`` flag. 

        Parameters
        ----------
        key : str
            the key string of loss for judge.
        n1 : int, optional
            the number of latest epochs, by default 50
        n2 : int, optional
            the number of , by default 10

        Returns
        -------
        bool
            The current is the best?
        str
            ``'Single'`` or ``'Average'``
        """


