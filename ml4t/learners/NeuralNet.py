import numpy as np
import json, os, sys


def clear():
        if os.name == 'nt':
                os.system('cls')
        else:
                os.system('clear')

# Activation functions
class Linear(object):
        @staticmethod
        def fn(x):
                """Return the linear activation unit."""
                return x

        @staticmethod
        def prime(x):
                """Return the derivative of the linear activation unit."""
                return 1.

class Sigmoid(object):
	@staticmethod
	def fn(x):
		"""Return the sigmoid activation unit."""
		expone = np.nan_to_num(np.exp(-x))
		return np.array( 1./(1.-expone) )
	
	@staticmethod
	def prime(x):
		"""Return the derivative of the sigmoid activation unit."""
		return Sigmoid.fn(x)*(1.-Sigmoid.fn(x))
	
class Tanh(object):
        @staticmethod
        def fn(x):
		"""Return the hyperbolic tangent activation unit."""
		pos = np.nan_to_num( np.exp(x) )
                neg = np.nan_to_num( np.exp(-x) )
                return (pos-neg)/(pos+neg)
	
	@staticmethod
	def prime(x):
		"""Return the derivative of the hyperbolic tangent activation unit."""
		return (1-Tanh.fn(x)**2)
	
class ReLU(object):
	@staticmethod
	def fn(x):
		"""Return the rectified linear activation unit."""
		return np.maximum(x,0.01)
	
	@staticmethod
	def prime(x):
		"""Return the derivative of the sigmoid activation unit."""
		return np.maximum(0.01, x>0)

class Softmax(object):
	@staticmethod
	def fn(x):
		"""Return the softmax activation unit."""
		return np.nan_to_num(np.exp(x))/np.sum(np.exp(x), axis=0)
	
	@staticmethod
	def prime(x):
		"""Return the derivative of the sigmoid activation unit."""
		return np.multiply( -Softmax.fn(x),Softmax.fn(x) )

# Cost functions
class QuadraticCost(object):
	@staticmethod
	def fn(a, y):
		""" """
		return 0.5*np.linalg.norm(a-y)**2
	
	@staticmethod
	def delta(z, a, y, activation=Linear):
		""" """
		return (a-y)*activation.prime(z)

class CrossEntropyCost(object):
    """Cross-Entropy Cost function and delta for output layer."""
    @staticmethod
    def fn(a, y):
        return np.sum( np.nan_to_num( -y*np.log(a)-(1-y)*np.log(1-a) ) )

    @staticmethod
    def delta(z, a, y, activation=Linear):
        return (a-y)

class Network(object):
	def __init__(self, sizes, cost=QuadraticCost, activations=None):
		self.cost = cost
		self.sizes = sizes
		self.num_layers= len(sizes)
		self.initialize_weights()
		if activations==None:
			self.activations = [ReLU for i in sizes[1:]]
		elif not len(activations) == len(sizes[1:]):
			print "You need {} activations.".format( len(sizes[1:]) )
			exit()
		else:
                        self.activations = activations

	def initialize_weights(self):
                self.biases = [np.random.randn(1, y) for y in self.sizes[1:]]
		self.weights = [np.random.randn(x, y)/np.sqrt(x)
                                for x,y in zip(self.sizes[:-1], self.sizes[1:])]
		
	def forward(self, a):
		for act, w, b  in zip(self.activations, self.weights, self.biases):
                        z = np.dot(a, w) + b
			a = act.fn( z )
		return a
		
	def backprop(self, x, y):
		n_w = [np.zeros(w.shape) for w in self.weights]
		n_b = [np.zeros(b.shape) for b in self.biases]
		
		# Feed-Forward Pass
		z_s = []
		a_s = [x]
		a = x
		for w, b, act in zip(self.weights, self.biases, self.activations):
			z = np.dot(a, w) + b
			z_s.append(z)
			a = act.fn(z)
			a_s.append(a)
		
		# Feed-Backward Pass
		delta = (self.cost).delta(z_s[-1], a_s[-1], y, self.activations[-1])
		n_b[-1] = delta.mean(axis=0)
		n_b[-1] = n_b[-1].reshape(1, delta.shape[1])
                n_w[-1] = np.dot(a_s[-2].transpose(), delta)
                for l in xrange(2,self.num_layers):
                        z = z_s[-l]
                        sp = self.activations[-l].prime(z)
                        delta = np.dot(delta, self.weights[-l+1].transpose())
                        delta *= sp
                        n_b[-l] = delta.mean(axis=0)
                        n_b[-l] = n_b[-l].reshape(1, delta.shape[1])
                        a = np.array(a_s[-l-1])
                        n_w[-l] = np.dot(a.transpose(), delta)
		return (n_b, n_w)
	
	def sgd(self, trainX, trainY, iterations=10000, lmbda=0.0, mu=0.9):
                eta = 0.00001
                # for adjusting learning rate (eta)
                old_costs = []
                # for stopping criteria
                running_cost = []
                # for reset criteria
                init_cost = QuadraticCost.fn(self.forward(trainX), trainY)
                something_wrong = 0 
                # Nesterov Momentum 1: Initiate previous weight and bias derivatives
                v_weights = [np.zeros(w.shape) for w in self.weights]
                v_biases = [np.zeros(b.shape) for b in self.biases]
                # Preparing for stochasticity
                n_smpl = float(trainX.shape[0])
                # Adagrad Initiation
                cache = [np.zeros(w.shape) for w in self.weights]
                eps = 1e-6
                decay_rate = 0.99
                for _ in range(iterations):
                        # Nesterov Momentum 2: Make copies of the original weights
                        orig_weights = [w for w in self.weights]
                        orig_biases = [b for b in self.biases]
                        # Nesterov Momentum 3: Add contributions from past derivatives to weights

                        # Retrieve derivatives for current weights and biases
                        nabla_b, nabla_w = self.backprop(trainX, trainY)
                        # Adagrad
                        cache = [decay_rate*cac + (1-decay_rate)*nw**2 for cac, nw in zip(cache, nabla_w)]
                        # Nesterov Momentum: Store previous values of velocity update
                        v_prev_weights = [vw for vw in v_weights]
                        v_prev_biases = [vb for vb in v_biases]
                        # Nesterov Momentum: Retrieve velocity update
                        v_weights = [mu*vw - eta*nw/(np.sqrt(cac) + eps) for vw, nw, cac in zip(v_weights, nabla_w, cache)]
                        v_biases = [mu*vb - eta*nb for vb, nb in zip(v_biases, nabla_b)]
                        # Nesterov Momentum: Store the lookahead value as the weights and biases
                        self.weights = [w - mu*vpw + (1+mu)*vw for w, vpw, vw in zip(self.weights, v_prev_weights, v_weights)]
                        self.weights = [w - lmbda*w for w in self.weights]
                        self.biases = [b - mu*vpb + (1+mu)*vb for b, vpb, vb in zip(self.biases, v_prev_biases, v_biases)]

                        new_cost = QuadraticCost.fn(self.forward(trainX), trainY)
                        # adjust learning rate (eta)
                        eta = self.adjust_eta(eta, old_costs, new_cost)
                        old_costs.append(new_cost)
                        # Assess learning
                        if _%(iterations/10)==0:
                                print "Cost at iter {}: {}".format(_,new_cost)
#                                 print "learning rate: {}\t".format(eta)
                        # Assess stopping criteria
                        if len(running_cost)>=100:
                                if np.std(running_cost)<1e-6 and np.mean(running_cost)>new_cost: break
                                running_cost.pop(0)
                        running_cost.append(new_cost)
                        # Assess reset criteria
                        if new_cost > 2*init_cost or eta>1e2:
                                self.initialize_weights()
                                eta = 1e-5
                        if len(old_costs)>2 and new_cost==np.mean(old_costs[-3:]):
                                something_wrong+=1
                                if something_wrong>2:
                                        self.initialize_weights()
                                        something_wrong=0
                        

        def adjust_eta(self, eta, old_costs, new_cost):
                len_reached = len(old_costs)>=1000
                if len(old_costs)<1:
                        return eta
                elif np.mean(old_costs)<=new_cost:
                        if len_reached:
                                old_costs.pop(0)
                        return eta*0.5 + 1e-9
                else:
                        if len_reached:
                                old_costs.pop(0)
                        return eta*1.001

	def save(self, filename):
                """Save the neural network to the file ``filename``."""
                data = {"sizes": self.sizes,
                        "weights": [w.tolist() for w in self.weights],
                        "biases": [b.tolist() for b in self.biases],
                        "cost": str(self.cost.__name__),
                        "activations": [str(act.__name__) for act in self.activations]}
                f = open(filename, "w")
                json.dump(data, f)
                f.close()

#     def draw(self, cost):
#         clear()
#         print "The current error is {}".format(cost[0])
#         
#     def display_error(self):
#         '''#Inform the user of the current error as iterations increase.'''
#         #self.draw(self.costs[len(self.costs)-1])
#         sys.stdout.write(
#             "ERROR LEVEL: {0:.5g}\r".format(
#                 self.costs[len(self.costs)-1]
#                                              )
#             )
#         sys.stdout.flush()
#         self.hidden_history.append(self.a2)

#### Loading a Network
def load(filename):
        """Load a neural network from the file ``filename``.  Returns an
        instance of Network.
        """
        f = open(filename, "r")
        data = json.load(f)
        f.close()
        activations = [getattr(sys.modules[__name__], act) for act in data["activations"]]
        cost = getattr(sys.modules[__name__], data["cost"])
        net = Network(data["sizes"], cost=cost, activations=activations)
        net.weights = [np.array(w) for w in data["weights"]]
        net.biases = [np.array(b) for b in data["biases"]]
        return net

 
# trainX=np.array(
#  [[0.],
#   [1.],
#   [2.],
#   [3.],
#   [4.]]
#  )
# 
# trainY=np.array(
#  [[0., 0., 0.],
#   [1., 2., 3.],
#   [4., 4., 6.],
#   [9., 6., 9.],
#   [16., 8., 12.]]
#  )
# 
# trainY=np.array(
#  [[1., 0., 0.],
#   [0., 1., 0.],
#   [1., 0., 0.],
#   [0., 1., 0.],
#   [1., 0., 0.]]
#  )
# acts = [ReLU,ReLU]
# 
# feature_size = trainX.shape[1]
# output_size = trainY.shape[1]
# net = Network([feature_size,
#         100,
#         output_size],cost=CrossEntropyCost,
#        activations=acts)
# print net.forward(trainX)
# bs, ws = net.backprop(trainX, trainY)
# net.sgd(trainX, trainY, iterations=100000, lmbda=1.0)
# print np.round(net.forward(trainX))

