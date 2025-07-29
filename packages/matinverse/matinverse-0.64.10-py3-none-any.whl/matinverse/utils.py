from jax import numpy as jnp
from jax import custom_vjp,custom_jvp
from typing import Generic, TypeVar,Callable
from dataclasses import dataclass,field
import jax
from functools import wraps


def constraint(needs_filtered: bool = False, epsilon: Callable[[int], float] = lambda x: 0.0):
    """Utilities for constraint"""

    def decorator(func):

        @wraps(func)
        def wrapper(x):

            return func(x)

        wrapper.epsilon = epsilon
        wrapper.needs_filtered = needs_filtered
        return wrapper
    
    return decorator


def compose_bwd(func):
    """It adds a custom vjp to func"""
    #fdiff = custom_vjp(cachable(func))
    fdiff = custom_vjp(func)

    def f_fwd(pt,*args):
     output = fdiff(pt,*args)

     return output[0],output[1]

    #@jax.jit
    def f_bwd(jac, v):
       
     output = jnp.zeros(jac[list(v[0].keys())[0]].shape[-1])
     for k,(key,v1) in enumerate(v[0].items()):
           output  += jnp.einsum('...,...i->i',v1,jac[key])

     return (output,None)  

    fdiff.defvjp(f_fwd, f_bwd)

    return fdiff

def apply_g_to_f(f, g):
         """Helper function"""
         def new_func(a,b):
          return f(g(a),b)
         return new_func
    
#https://github.com/google/jax/issues/7603
#_T = TypeVar('_T')
#class RefHolder(Generic[_T]):
#    def __init__(self, value: _T):
#        self.value = value

#    def __call__(self,value):
#        return self.value(value)

#def _refholder_flatten(self):
#        return (), self.value

#def _refholder_unflatten(value, _):
#        return RefHolder(value)

#jax.tree_util.register_pytree_node(RefHolder, _refholder_flatten, _refholder_unflatten)
#---------------------
