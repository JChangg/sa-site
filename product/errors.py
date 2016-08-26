class NotEnoughStockException(Exception):
    def __init__(self, stock, sell):

        message = 'Attempted to sell %i > %i (stock) items' %(sell, stock)
        super(NotEnoughStockException, self).__init__(message)
