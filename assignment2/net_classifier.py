import numpy as np

def one_in_k_encoding(vec, k):
    """ One-in-k encoding of vector to k classes 
    
    Args:
       vec: numpy array - data to encode
       k: int - number of classes to encode to (0,...,k-1)
    """
    n = vec.shape[0]
    enc = np.zeros((n, k))
    enc[np.arange(n), vec] = 1
    return enc

def softmax(X):
    """ 
    You can take this from handin I
    Compute the softmax of each row of an input matrix (2D numpy array). 
    
    the numpy functions amax, log, exp, sum may come in handy as well as the keepdims=True option and the axis option.
    Remember to handle the numerical problems as discussed in the description.
    You should compute lg softmax first and then exponentiate 
    
    More precisely this is what you must do.
    
    For each row x do:
    compute max of x
    compute the log of the denominator sum for softmax but subtracting out the max i.e (log sum exp x-max) + max
    compute log of the softmax: x - logsum
    exponentiate that
    
    You can do all of it without for loops using numpys vectorized operations.

    Args:
        X: numpy array shape (n, d) each row is a data point
    Returns:
        res: numpy array shape (n, d)  where each row is the softmax transformation of the corresponding row in X i.e res[i, :] = softmax(X[i, :])
    """
    res = np.zeros(X.shape)
    ### YOUR CODE HERE no for loops please
    maxX = np.amax(X, axis=1, keepdims=True)
    withoutMax = X - maxX
    expWithoutMax = np.exp(withoutMax)
    sumExpWithoutMax = np.sum(expWithoutMax, axis=1, keepdims=True)
    lnSumExpWithoutMax = np.log(sumExpWithoutMax)
    clnSumExpWithoutMax = maxX + lnSumExpWithoutMax
    XMinusCLn = X - clnSumExpWithoutMax
    expXMinusCLn = np.exp(XMinusCLn)
    res = expXMinusCLn
    ### END CODE
    return res

def relu(x):
    """ Compute the relu activation function on every element of the input
    
        Args:
            x: np.array
        Returns:
            res: np.array same shape as x
        Beware of np.max and look at np.maximum
    """
    ### YOUR CODE HERE
    res = np.maximum(0, x)
    ### END CODE
    return res

def make_dict(W1, b1, W2, b2):
    """ Trivial helper function """
    return {'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2}


def get_init_params(input_dim, hidden_size, output_size):
    """ Initializer function using he et al Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification

    Args:
      input_dim: int
      hidden_size: int
      output_size: int
    Returns:
       dict of randomly initialized parameter matrices.
    """
    W1 = np.random.normal(0, np.sqrt(2./(input_dim+hidden_size)), size=(input_dim, hidden_size))
    b1 = np.zeros((1, hidden_size))
    W2 = np.random.normal(0, np.sqrt(4./(hidden_size+output_size)), size=(hidden_size, output_size))
    b2 = np.zeros((1, output_size))
    return {'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2}

  
class NetClassifier():
    
    def __init__(self):
        """ Trivial Init """
        self.params = None
        self.hist = None

    def predict(self, X, params=None):
        """ Compute class prediction for all data points in class X
        
        Args:
            X: np.array shape n, d
            params: dict of params to use (if none use stored params)
        Returns:
            np.array shape n, 1
        """
        if params is None:
            params = self.params
        pred = None
        ### YOUR CODE HERE
        A1 = X @ params['W1'] + params['b1']
        reluA1 = relu(A1)
        A2 = reluA1 @ params['W2'] + params['b2']
        pred = np.argmax(A2, axis=1)
        ### END CODE
        return pred
     
    def score(self, X, y, params=None):
        """ Compute accuracy of model on data X with labels y
        
        Args:
            X: np.array shape n, d
            y: np.array shape n, 1
            params: dict of params to use (if none use stored params)

        Returns:
            np.array shape n, 1
        """
        if params is None:
            params = self.params
        acc = None
        ### YOUR CODE HERE
        acc = 0
        pred = self.predict(X, params)
        for i, j in zip(pred, y):
            if (i == j):
                acc = acc + 1
        acc = acc / len(y)
        ### END CODE
        return acc
    
    @staticmethod
    def cost_grad(X, y, params, reg=0.0):
        """ Compute cost and gradient of neural net on data X with labels y using weight decay parameter c
        You should implement a forward pass and store the intermediate results 
        and the implement the backwards pass using the intermediate stored results
        
        Use the derivative for cost as a function for input to softmax as derived above
        
        Args:
            X: np.array shape n, self.input_size
            y: np.array shape n, 1
            params: dict with keys (W1, W2, b1, b2)
            reg: float - weight decay regularization weight
            params: dict of params to use for the computation
        
        Returns 
            cost: scalar - average cross entropy cost
            dict with keys
            d_w1: np.array shape w1.shape, entry d_w1[i, j] = \partial cost/ \partial w1[i, j]
            d_w2: np.array shape w2.shape, entry d_w2[i, j] = \partial cost/ \partial w2[i, j]
            d_b1: np.array shape b1.shape, entry d_b1[1, j] = \partial cost/ \partial b1[1, j]
            d_b2: np.array shape b2.shape, entry d_b2[1, j] = \partial cost/ \partial b2[1, j]
            
        """
        
        W1 = params['W1']
        b1 = params['b1']
        W2 = params['W2']
        b2 = params['b2']
        labels = one_in_k_encoding(y, W2.shape[1]) # shape n x k
                        
        ### YOUR CODE HERE - FORWARD PASS - compute regularized cost and store relevant values for backprop
        A1 = X @ W1 + b1
        reluA1 = relu(A1)
        A2 = reluA1 @ W2 + b2
        
        log_softmax = np.log(softmax(A2))
        entropy = np.sum(log_softmax * labels)
        entropy = -entropy 
        decay = reg * (np.sum(np.square(W1)) + np.sum(np.square(W2)))
        
        cost = entropy + decay
        grad = -labels + softmax(A2)
        d_b2 = grad.sum(axis=0, keepdims=True) 
        d_w2 = 2*reg*W2 + (reluA1.T @ grad) 
        d_RA1 = grad @ W2.T 
        d_A1 = d_RA1 * np.where(A1 > 0, 1, 0)
        d_b1 = d_A1.sum(axis=0, keepdims=True)
        d_w1 = X.T @ d_A1 + 2*reg*W1
        d_x = W1 @ d_A1.T
        ### END CODE
        
        ### YOUR CODE HERE - BACKWARDS PASS - compute derivatives of all (regularized) weights and bias, store them in d_w1, d_w2' d_w2, d_b1, d_b2
        
        ### END CODE
        # the return signature
        return cost, {'d_w1': d_w1, 'd_w2': d_w2, 'd_b1': d_b1, 'd_b2': d_b2}
        
    def fit(self, X_train, y_train, X_val, y_val, init_params, batch_size=32, lr=0.1, reg=1e-4, epochs=30):
        """ Run Mini-Batch Gradient Descent on data X, Y to minimize the in sample error (1/n)Cross Entropy for Neural Net classification
        Printing the performance every epoch is a good idea to see if the algorithm is working
    
        Args:
           X_train: numpy array shape (n, d) - the training data each row is a data point
           y_train: numpy array shape (n,) int - training target labels numbers in {0, 1,..., k-1}
           X_val: numpy array shape (n, d) - the validation data each row is a data point
           y_val: numpy array shape (n,) int - validation target labels numbers in {0, 1,..., k-1}
           init_params: dict - has initial setting of parameters
           lr: scalar - initial learning rate
           batch_size: scalar - size of mini-batch
           epochs: scalar - number of iterations through the data to use

        Sets: 
           params: dict with keys {W1, W2, b1, b2} parameters for neural net
           history: dict:{keys: train_loss, train_acc, val_loss, val_acc} each an np.array of size epochs of the the given cost after every epoch
        """
        
        W1 = init_params['W1']
        b1 = init_params['b1']
        W2 = init_params['W2']
        b2 = init_params['b2']

        ### YOUR CODE HERE
        train_loss_arr = []
        val_loss_arr = []
        train_acc_arr = []
        val_acc_arr = []
        batches = int(len(X_train) / batch_size) + 1
        for i in range(epochs):
            np.random.permutation(X_train)
            np.random.permutation(X_val)
            counter = 0
            for j in range(batches):
                _params = {'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2}
                batchX = X_train[counter:counter + batch_size]
                batchy = y_train[counter:counter + batch_size]
                cost,grad = self.cost_grad(batchX, batchy, _params, reg)
                W1 = W1 - lr * grad['d_w1']                
                W2 = W2 - lr * grad['d_w2']
                b1 = b1 - lr * grad['d_b1']
                b2 = b2 - lr * grad['d_b2']
                counter = counter + batch_size
            
            train_loss, _ = self.cost_grad(X_train, y_train, _params, reg)
            train_loss /= y_train.shape[0]
            val_loss, _ =  self.cost_grad(X_val, y_val, _params, reg)   
            val_loss /= y_val.shape[0]
            train_acc = self.score(X_train, y_train, _params)
            val_acc = self.score(X_val, y_val, _params)
            train_loss_arr.append(train_loss)
            val_loss_arr.append(val_loss)
            train_acc_arr.append(train_acc)
            val_acc_arr.append(val_acc)
        ### END CODE
        # hist dict should look like this with something different than none
        self.history = {
            'train_loss': np.array(train_loss_arr),
            'train_acc': np.array(train_acc_arr),
            'val_loss': np.array(val_loss_arr),
            'val_acc': np.array(val_acc_arr), 
        }
        ## self.params should look like this with something better than none, i.e. the best parameters found.
        self.params = {'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2}
    
        

def numerical_grad_check(f, x, key):
    """ Numerical Gradient Checker """
    eps = 1e-6
    h = 1e-5
    # d = x.shape[0]
    cost, grad = f(x)
    grad = grad[key]
    it = np.nditer(x, flags=['multi_index'])
    while not it.finished:    
        dim = it.multi_index    
        print(dim)
        tmp = x[dim]
        x[dim] = tmp + h
        cplus, _ = f(x)
        x[dim] = tmp - h 
        cminus, _ = f(x)
        x[dim] = tmp
        num_grad = (cplus-cminus)/(2*h)
        # print('cplus cminus', cplus, cminus, cplus-cminus)
        # print('dim, grad, num_grad, grad-num_grad', dim, grad[dim], num_grad, grad[dim]-num_grad)
        assert np.abs(num_grad - grad[dim]) < eps, 'numerical gradient error index {0}, numerical gradient {1}, computed gradient {2}'.format(dim, num_grad, grad[dim])
        it.iternext()

def test_grad():
    stars = '*'*5
    print(stars, 'Testing  Cost and Gradient Together')
    input_dim = 7
    hidden_size = 1
    output_size = 3
    nc = NetClassifier()
    params = get_init_params(input_dim, hidden_size, output_size)

    nc = NetClassifier()
    X = np.random.randn(7, input_dim)
    y = np.array([0, 1, 2, 0, 1, 2, 0])

    f = lambda z: nc.cost_grad(X, y, params, reg=1.0)
    print('\n', stars, 'Test Cost and Gradient of b2', stars)
    numerical_grad_check(f, params['b2'], 'd_b2')
    print(stars, 'Test Success', stars)
    
    print('\n', stars, 'Test Cost and Gradient of w2', stars)
    numerical_grad_check(f, params['W2'], 'd_w2')
    print('Test Success')
    
    print('\n', stars, 'Test Cost and Gradient of b1', stars)
    numerical_grad_check(f, params['b1'], 'd_b1')
    print('Test Success')
    
    print('\n', stars, 'Test Cost and Gradient of w1', stars)
    numerical_grad_check(f, params['W1'], 'd_w1')
    print('Test Success')

if __name__ == '__main__':
    input_dim = 3
    hidden_size = 5
    output_size = 4
    batch_size = 7
    nc = NetClassifier()
    params = get_init_params(input_dim, hidden_size, output_size)
    X = np.random.randn(batch_size, input_dim)
    Y = np.array([0, 1, 2, 0, 1, 2, 0])
    nc.cost_grad(X, Y, params, reg=0)
    test_grad()