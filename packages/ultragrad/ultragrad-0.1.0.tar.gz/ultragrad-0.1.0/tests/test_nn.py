import pytest
import numpy as np
import os

from ultragrad import Tensor
from ultragrad.nn import Module,Linear,Sequential,ReLU,Sigmoid,Tanh,save,load

class SimpleNet(Module):
    '''
    A simple network
    '''
    def __init__(self):
        super().__init__()
        self.layers = Sequential(
            Linear(10, 20),
            ReLU(),
            Linear(20, 5)
        )

    def forward(self, x):
        return self.layers(x)

@pytest.fixture
def simple_model():
    '''
    Provides a fresh instance of SimpleNet for each test
    '''
    return SimpleNet()

@pytest.fixture
def sample_input():
    '''
    Provides a sample input Tensor
    '''
    return Tensor(np.random.randn(4, 10))

def test_module_parameter_registration():
    '''
    Tests that Tensors and sub-Modules are registered correctly
    '''
    class TestModule(Module):
        def __init__(self):
            super().__init__()
            self.a_param = Tensor([1, 2, 3])
            self.another_param = Tensor([4, 5, 6], requires_grad=False)
            self.a_layer = Linear(5, 5)
            self.not_a_param = [1, 2, 3]

    m = TestModule()
    
    assert 'a_param' in m._parameters
    assert 'another_param' in m._parameters
    assert 'a_layer' in m._modules
    assert 'not_a_param' not in m._parameters
    
    params = m.parameters()
    assert len(params) == 3

def test_linear_layer_forward_shape():
    '''
    Tests the forward pass of the Linear layer for correct output shape
    '''
    in_features, out_features, batch_size = 10, 5, 4
    layer = Linear(in_features, out_features)
    x = Tensor(np.random.randn(batch_size, in_features))
    
    output = layer(x)
    
    assert isinstance(output, Tensor)
    assert output.data.shape == (batch_size, out_features)

def test_linear_layer_backward_pass():
    '''
    Tests that gradients are computed for the Linear layer's parameters
    '''
    layer = Linear(3, 2)
    x = Tensor([[1, 2, 3]])
    
    output = layer(x)
    loss = output.sum()
    loss.backward()
    
    assert layer.weight.grad is not None
    assert layer.bias.grad is not None # type: ignore
    assert not np.all(layer.weight.grad == 0)
    assert not np.all(layer.bias.grad == 0) # type: ignore

def test_sequential_container(simple_model, sample_input):
    '''
    Tests the forward pass of the Sequential container
    '''
    output = simple_model(sample_input)
    
    assert isinstance(output, Tensor)
    assert output.data.shape == (4, 5)

def test_zero_grad(simple_model, sample_input):
    '''
    Tests if zero_grad() correctly resets all parameter gradients to zero
    '''
    output = simple_model(sample_input)
    loss = output.mean()
    loss.backward()
    
    params = simple_model.parameters()
    assert any(np.any(p.grad != 0) for p in params)
    
    simple_model.zero_grad()
    
    for p in params:
        assert np.all(p.grad == 0)

@pytest.mark.parametrize("activation_class, func", [
    (ReLU, np.maximum),
    (Sigmoid, lambda x: 1 / (1 + np.exp(-x))),
    (Tanh, np.tanh),
])
def test_activation_layers(activation_class, func):
    '''
    Tests activation layers (ReLU, Sigmoid, Tanh) forward and backward
    '''
    layer = activation_class()
    input_data = np.array([-1.0, 0.0, 2.0])
    x = Tensor(input_data)
    
    output = layer(x)
    expected_output = func(0, input_data) if activation_class is ReLU else func(input_data)
    assert np.allclose(output.data, expected_output)
    
    loss = output.sum()
    loss.backward()
    assert x.grad is not None
    assert not np.all(x.grad == 0)

def test_state_dict(simple_model):
    '''
    Tests the creation of a state_dict
    '''
    state_dict = simple_model.state_dict()
    
    expected_keys = [
        'layers.0.weight', 
        'layers.0.bias', 
        'layers.2.weight', 
        'layers.2.bias'
    ]
    
    assert sorted(state_dict.keys()) == sorted(expected_keys)
    
    assert isinstance(state_dict['layers.0.weight'], np.ndarray)
    
    assert state_dict['layers.0.weight'].shape == (20, 10)
    assert state_dict['layers.2.bias'].shape == (5,)

def test_save_load_cycle(simple_model, tmp_path):
    '''
    Tests the full save and load cycle, ensuring weights are identical
    '''
    model_path = os.path.join(tmp_path, "model.safetensors")
    

    save(simple_model, model_path)
    assert os.path.exists(model_path)
    
    new_model = SimpleNet()
    
    orig_weight = simple_model.layers._modules['0'].weight.data
    new_weight_before = new_model.layers._modules['0'].weight.data
    assert not np.allclose(orig_weight, new_weight_before)
    
    load(new_model, model_path)
    
    new_weight_after = new_model.layers._modules['0'].weight.data
    assert np.allclose(orig_weight, new_weight_after)
    
    for p_orig, p_new in zip(simple_model.parameters(), new_model.parameters()):
        assert np.allclose(p_orig.data, p_new.data)

def test_load_state_dict_shape_mismatch():
    '''
    Tests that loading a state_dict with incorrect shapes raises ValueError
    '''
    model = Linear(5, 3)
    bad_state_dict = {
        'weight': np.random.randn(4, 6),
        'bias': np.random.randn(3)
    }
    
    with pytest.raises(ValueError, match="Shape mismatch for 'weight'"):
        model.load_state_dict(bad_state_dict)

def test_load_nonexistent_file():
    '''
    Tests that loading from a non-existent path raises FileNotFoundError
    '''
    model = Linear(5, 3)
    with pytest.raises(FileNotFoundError):
        load(model, "nonexistent/file/path.safetensors")