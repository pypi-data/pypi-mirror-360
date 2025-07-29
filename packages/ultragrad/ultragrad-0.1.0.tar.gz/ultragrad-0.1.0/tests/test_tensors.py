import pytest
import numpy as np
from ultragrad import Tensor
from ultragrad.tensors import Tensor_Error

# init test
def test_tensor_creation():
    # From list
    t1 = Tensor([1, 2, 3])
    assert isinstance(t1.data, np.ndarray)
    assert t1.data.shape == (3,)

    # From numpy array
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    t2 = Tensor(a)
    assert np.array_equal(t2.data, a)
    
    # From scalar
    t3 = Tensor(5)
    assert t3.data.shape == ()
    assert t3.data == 5.0

def test_tensor_dtype_conversion():
    # Integers should be converted to float64
    t1 = Tensor([1, 2, 3])
    assert t1.data.dtype == np.float64

    # Floats should be upcasted to float64
    t2 = Tensor(np.array([1.0, 2.0], dtype=np.float32))
    assert t2.data.dtype == np.float64

def test_tensor_grad_initialization():
    data = np.random.randn(3, 4)
    t = Tensor(data)
    assert isinstance(t.grad, np.ndarray)
    assert t.grad.shape == data.shape
    assert np.all(t.grad == 0)
    assert t.grad.dtype == data.dtype

def test_tensor_properties():
    t = Tensor([1, 2], _label='t', requires_grad=False)
    assert t.requires_grad is False
    assert t._label == 't'
    assert repr(t) == f"Tensor(data={t.data},shape={t.data.shape})"

def test_tensor_creation_error():
    with pytest.raises(Tensor_Error):
        Tensor("not-a-number")
    with pytest.raises(Tensor_Error):
        Tensor([1, [2, 3]], requires_grad=True)

# math operation tests
def test_add_op():
    a = Tensor([1, 2, 3], requires_grad=True)
    b = Tensor([4, 5, 6], requires_grad=True)
    c = a + b
    assert np.allclose(c.data, [5, 7, 9])
    
    c.backward(gradient=np.array([1.0, 2.0, 3.0]))
    assert np.allclose(a.grad, [1.0, 2.0, 3.0])
    assert np.allclose(b.grad, [1.0, 2.0, 3.0])

def test_mul_op():
    a = Tensor([1, 2, 3], requires_grad=True)
    b = Tensor([4, 5, 6], requires_grad=True)
    c = a * b
    assert np.allclose(c.data, [4, 10, 18])
    
    c.backward(gradient=np.array([1.0, 2.0, 3.0]))
    assert np.allclose(a.grad, [4.0, 10.0, 18.0])
    assert np.allclose(b.grad, [1.0, 4.0, 9.0])
    
def test_sub_op():
    a = Tensor([10, 20], requires_grad=True)
    b = Tensor([4, 5], requires_grad=True)
    c = a - b
    assert np.allclose(c.data, [6, 15])
    
    c.backward(gradient=np.array([1.0, 2.0]))
    assert np.allclose(a.grad, [1.0, 2.0])
    assert np.allclose(b.grad, [-1.0, -2.0])

def test_div_op():
    a = Tensor([10, 20], requires_grad=True)
    b = Tensor([2, 5], requires_grad=True)
    c = a / b
    assert np.allclose(c.data, [5, 4])
    
    c.backward(gradient=np.array([1.0, 2.0]))
    assert np.allclose(a.grad, [0.5, 0.4])
    assert np.allclose(b.grad, [-2.5, -1.6])

def test_pow_op():
    a = Tensor([2, 3], requires_grad=True)
    c = a ** 3
    assert np.allclose(c.data, [8, 27])
    
    c.backward(gradient=np.array([1.0, 2.0]))
    assert np.allclose(a.grad, [12.0, 54.0])

def test_neg_op():
    a = Tensor([1, -2, 3], requires_grad=True)
    b = -a
    assert np.allclose(b.data, [-1, 2, -3])
    
    b.backward(gradient=np.array([1.0, 2.0, 3.0]))
    assert np.allclose(a.grad, [-1.0, -2.0, -3.0])

def test_reverse_ops():
    a = Tensor([1, 2, 3], requires_grad=True)
    
    # __radd__
    b = 10 + a
    b.backward(gradient=np.ones_like(a.data))
    assert np.allclose(b.data, [11, 12, 13])
    assert np.allclose(a.grad, [1.0, 1.0, 1.0])
    
    # __rmul__
    a.zero_grad()
    c = 10 * a
    c.backward(gradient=np.ones_like(a.data))
    assert np.allclose(c.data, [10, 20, 30])
    assert np.allclose(a.grad, [10.0, 10.0, 10.0])

    # __rsub__
    a.zero_grad()
    d = 10 - a
    d.backward(gradient=np.ones_like(a.data))
    assert np.allclose(d.data, [9, 8, 7])
    assert np.allclose(a.grad, [-1.0, -1.0, -1.0])

    # __rtrudiv__
    a.zero_grad()
    e = 10 / a
    e.backward(gradient=np.ones_like(a.data))
    assert np.allclose(e.data, [10.0, 5.0, 10.0/3.0])
    assert np.allclose(a.grad, [-10.0, -2.5, -10.0/9.0])
    

# Broadcasting test
def test_broadcast_add():
    a_data = np.arange(6).reshape(2, 3)
    b_data = np.array([10, 20, 30])
    a = Tensor(a_data, requires_grad=True)
    b = Tensor(b_data, requires_grad=True)
    
    c = a + b
    assert np.allclose(c.data, [[10, 21, 32], [13, 24, 35]])
    
    grad_c = np.ones((2, 3))
    c.backward(gradient=grad_c)
    
    assert np.allclose(a.grad, grad_c)
    assert np.allclose(b.grad, [2.0, 2.0, 2.0])

def test_broadcast_mul():
    a_data = np.arange(4).reshape(4, 1)
    b_data = np.array([10, 20])
    a = Tensor(a_data, requires_grad=True)
    b = Tensor(b_data, requires_grad=True)
    
    c = a * b
    expected_c_data = np.array([[0, 0], [10, 20], [20, 40], [30, 60]])
    assert np.allclose(c.data, expected_c_data)
    
    grad_c = np.ones((4, 2))
    c.backward(gradient=grad_c)
    
    expected_a_grad = np.array([[30], [30], [30], [30]]) 
    assert np.allclose(a.grad, expected_a_grad)
    
    expected_b_grad = np.array([6, 6])
    assert np.allclose(b.grad, expected_b_grad)
    
def test_broadcast_ndim_diff():
    a_data = np.random.randn(2, 3, 4)
    b_data = np.random.randn(3, 4)
    a = Tensor(a_data, requires_grad=True)
    b = Tensor(b_data, requires_grad=True)

    c = a + b
    assert np.allclose(c.data, a_data + b_data)
    
    grad_c = np.ones_like(c.data)
    c.backward(gradient=grad_c)
    
    assert np.allclose(a.grad, np.ones_like(a.data))
    assert np.allclose(b.grad, np.full_like(b.data, 2.0))

# Reduction operations Test
def test_sum_op():
    a = Tensor(np.arange(6).reshape(2, 3), requires_grad=True)
    
    # Full sum
    s = a.sum()
    assert np.allclose(s.data, 15)
    s.backward()
    assert np.allclose(a.grad, np.ones((2, 3)))
    
    # Sum along axis
    a.zero_grad()
    s_axis = a.sum(axis=0)
    assert np.allclose(s_axis.data, [3, 5, 7])
    s_axis.backward(gradient=np.array([1, 10, 100]))
    assert np.allclose(a.grad, [[1, 10, 100], [1, 10, 100]])
    
    # Sum with keepdims
    a.zero_grad()
    s_axis_keep = a.sum(axis=1, keepdims=True)
    assert s_axis_keep.data.shape == (2, 1)
    assert np.allclose(s_axis_keep.data, [[3], [12]])
    s_axis_keep.backward(gradient=np.array([[10], [20]]))
    assert np.allclose(a.grad, [[10, 10, 10], [20, 20, 20]])

def test_mean_op():
    a = Tensor([1, 2, 3, 4], requires_grad=True)
    m = a.mean()
    assert np.allclose(m.data, 2.5)
    
    m.backward()
    assert np.allclose(a.grad, [0.25, 0.25, 0.25, 0.25])
    
# Matrix operation tests
def test_matmul_op():
    a = Tensor(np.arange(1, 7).reshape(2, 3), requires_grad=True)
    b = Tensor(np.arange(1, 7).reshape(3, 2), requires_grad=True)
    c = a @ b
    
    expected_c = np.array([[22, 28], [49, 64]])
    assert np.allclose(c.data, expected_c)
    
    grad_c = np.array([[1, 2], [3, 4]])
    c.backward(gradient=grad_c)
    
    grad_a_expected = grad_c @ b.data.T
    assert np.allclose(a.grad, grad_a_expected)
    
    grad_b_expected = a.data.T @ grad_c
    assert np.allclose(b.grad, grad_b_expected)

def test_reshape_op():
    a = Tensor(np.arange(6), requires_grad=True)
    b = a.reshape(2, 3)
    assert np.allclose(b.data, np.arange(6).reshape(2, 3))
    
    grad_b = np.ones((2, 3))
    b.backward(grad_b)
    assert np.allclose(a.grad, np.ones(6))

def test_transpose_op():
    a = Tensor(np.arange(6).reshape(2, 3), requires_grad=True)
    b = a.transpose()
    assert np.allclose(b.data, a.data.T)
    
    grad_b = np.arange(6).reshape(3, 2)
    b.backward(grad_b)
    assert np.allclose(a.grad, grad_b.T)

# Activation function test
def test_relu():
    a = Tensor([-1, 0, 1, 2], requires_grad=True)
    r = a.relu()
    assert np.allclose(r.data, [0, 0, 1, 2])
    
    r.backward(gradient=np.array([10, 20, 30, 40]))
    assert np.allclose(a.grad, [0, 0, 30, 40])
    
def test_tanh():
    a_data = np.array([-1, 0, 1])
    a = Tensor(a_data, requires_grad=True)
    t = a.tanh()
    assert np.allclose(t.data, np.tanh(a_data))
    
    grad_t = np.array([10, 20, 30])
    t.backward(gradient=grad_t)
    expected_grad_a = grad_t * (1 - t.data**2)
    assert np.allclose(a.grad, expected_grad_a)
    
def test_sigmoid():
    a_data = np.array([-1, 0, 1])
    a = Tensor(a_data, requires_grad=True)
    s = a.sigmoid()
    
    expected_s_data = 1 / (1 + np.exp(-a_data))
    assert np.allclose(s.data, expected_s_data)
    
    grad_s = np.array([10, 20, 30])
    s.backward(gradient=grad_s)
    expected_grad_a = grad_s * (s.data * (1-s.data))
    assert np.allclose(a.grad, expected_grad_a)

def test_softmax():
    a_data = np.array([[1, 2, 3], [4, 1, 2]], dtype=np.float64)
    a = Tensor(a_data, requires_grad=True)
    s = a.softmax(axis=1)

    e_x = np.exp(a_data - np.max(a_data, axis=1, keepdims=True))
    expected_s_data = e_x / e_x.sum(axis=1, keepdims=True)
    assert np.allclose(s.data, expected_s_data)

    grad_s = np.array([[1,1,1],[2,2,2]], dtype=np.float64)
    s.backward(grad_s)
    
    sm = s.data
    g = grad_s
    expected_grad_a = sm * (g - (g*sm).sum(axis=1, keepdims=True))
    assert np.allclose(a.grad, expected_grad_a)
    
# Backpropagation test
def test_complex_graph_and_grad_accumulation():
    a = Tensor(2.0, requires_grad=True)
    b = Tensor(3.0, requires_grad=True)
    c = Tensor(4.0, requires_grad=True)
    
    e = a * b 
    f = e + c

    f.backward()
    assert a.grad == 3.0
    assert b.grad == 2.0
    assert c.grad == 1.0
    
    g = a * c 
    h = g + b
    
    h.backward()
    
    assert a.grad == 3.0 + 4.0 
    assert b.grad == 2.0 + 1.0 
    assert c.grad == 1.0 + 2.0

def test_zero_grad():
    a = Tensor(5.0, requires_grad=True)
    b = a * a
    b.backward()
    assert a.grad == 10.0
    
    a.zero_grad()
    assert a.grad == 0.0

def test_backward_on_scalar():
    a = Tensor(2.0, requires_grad=True)
    b = Tensor(3.0, requires_grad=True)
    c = (a * b).sum()
    c.backward()
    assert a.grad == 3.0
    assert b.grad == 2.0

def test_no_grad_propagation():
    a = Tensor(2.0, requires_grad=True)
    b = Tensor(3.0, requires_grad=False)
    c = a * b
    c.backward()
    
    assert a.grad == 3.0
    assert b.grad == 0.0