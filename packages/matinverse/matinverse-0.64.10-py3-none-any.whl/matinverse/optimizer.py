import numpy as np
import nlopt
import jax
from jax import value_and_grad as value_and_grad
import jax.numpy as jnp
import matplotlib as mpl
import sys
from jax.lax import conv
import jax.scipy as jsp
from dataclasses import dataclass, field
from typing import List
import pickle
import gc
from functools import partial
import msgpack
import msgpack_numpy as m


#mpl.interactive(True)

@dataclass
class State:
    objective_function: List = field(default_factory=lambda: [])
    save_evolution: bool = True
    save_all_aux: bool = True
    save_constraint_aux: bool = True
    evolution: List = field(default_factory=list)
    aux: List = field(default_factory=list)
    constraint: List = field(default_factory=list)
    constraint_aux: List[List] = field(default_factory=lambda: [[]])

    def _convert_jax_to_numpy(self, obj):
        """Recursively convert JAX arrays to NumPy before saving."""
        if isinstance(obj, jax.Array):
            return jax.device_get(obj)
        elif isinstance(obj, list):
            return [self._convert_jax_to_numpy(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_jax_to_numpy(v) for k, v in obj.items()}
        return obj  # Keep other types unchanged

    def save(self, filename: str):
        """Save the current state to a msgpack file."""
        data = self._convert_jax_to_numpy(self.__dict__)  # Convert all JAX arrays
        with open(filename, "wb") as f:
            f.write(msgpack.packb(data, default=m.encode))

    @classmethod
    def load(cls, filename: str):
        """Load a State object from a msgpack file."""
        with open(filename, "rb") as f:
            data = msgpack.unpackb(f.read(), object_hook=m.decode)
        return cls(**data)  # Restore the object


   
def colored(text,color,start,end):

 if color == 'green':
    return start+'\033[32m' + text + '\033[39m' + end
 elif color =='red':  
    return start+'\033[31m' + text + '\033[39m' + end
 elif color =='blue':  
    return start+'\033[34m' + text + '\033[39m' + end
 elif color =='white':  
    return start+'\033[39m' + text + '\033[39m' + end
 else:   
      raise "No color recognized"


def get_logger():

    def func(x,color = 'white',end='\n',start=''):

        print(colored(x,color,start,end),end='')  

    return func

logger       = get_logger()


#https://github.com/google/jax/pull/762#issuecomment-1002267121
def value_and_jacrev(f, x):
  y, pullback,aux = jax.vjp(f, x,has_aux=True)
  basis = jnp.eye(y.size, dtype=y.dtype)
  jac = jax.vmap(pullback)(basis)
  return (y,aux), jac





def enhance_inequality_constraint(func_original, state, index,is_last=False, adapt=False):
   

    if not adapt:
        func = func_original
    else:
        def func(x):
            output, *args = func_original(x)
            return jnp.array([output]), *args

    def constraint(results, x, grad):
        # Compute function value and gradient
        (results[...], (to_print, aux)), (grad[...],) = value_and_jacrev(func, x)

        # Print results
        for key, value in to_print.items():
            print(key + ': ', end=' ')
            if jnp.isscalar(value):
                value = [value]
            for v in value:
                print(f"{v:12.3E} ", end=' ')

        if is_last:
            print()

        #Expand list to match number of constraints
        if index > len(state.constraint_aux)-1:
               state.constraint_aux.append([])

        # Save auxiliary data only if needed
        if state.save_constraint_aux:            
            state.constraint_aux[index].append(aux)
        else:
           #SAve only last one [WARNING: this does not necessarily corresponds to the best solution]
           state.constraint_aux[index] = [aux]
     
            #del aux  # Explicitly delete aux if not saved
            #gc.collect()  # Force garbage collection

        # Save results
        if index > len(state.constraint)-1:
               state.constraint.append([])
        state.constraint[index].append(results.tolist())
        


        #state.constraint.append(results.tolist())

        # Block until computation is ready to free memory
        jax.block_until_ready(results)

        return None

    return constraint





def enhance_objective_function(func,state,has_inequality):
    """Make func compatible with NlOpt"""
 
    
    def objective_optimizer(x,grad):

          n_iter = len(state.objective_function)

        #   if n_iter == 1:
        #      carry = initial_carry
        #   else:
        #      carry = state.aux[-1]   
        
       
          #(output,(to_print,aux)),grad[:]    = jax.value_and_grad(func,has_aux=True)(x,**carry)
          (output,(to_print,aux)),grad[:]    = jax.value_and_grad(func,has_aux=True)(x)
    
         
          print(f"Iter: {n_iter:4d} ",end='')
          for key, value in to_print.items():
           
             print(key + ': ',end='')
             if jnp.isscalar(value): value = [value]
             
             for v in value:
               print(f"{v:12.3E}", end='')
             print(' ',end='')  
          
          
          if not has_inequality:    
           print() 
          else:
           print('  ',end=' ') 
          
          output = float(output)
          

          if state.save_evolution:
            state.evolution.append(x)

          if state.save_all_aux:
            state.aux.append(aux)
          else:
            if  len(state.objective_function) == 0:
               state.aux = [aux]  
            else:   
             if output < state.objective_function[-1]:
               #Save only for the best g
               state.aux = [aux]   

          state.objective_function.append(output)     

  

          return output
    
  
    return objective_optimizer  




def MMA(objective,**kwargs):

    #Parse options---
    nDOFs      = int(kwargs['nDOFs'])

    #This works only if 2D and square grid
    #nDOFs,unfolds = get_symmetry(N_full,kwargs.setdefault('symmetry',None))

    bounds  = kwargs.setdefault('bounds',[])
    if len(bounds) == 0:
       upper_bounds =  np.ones(nDOFs)
       lower_bounds =  np.ones(nDOFs)*1e-18
    elif bounds.ndim == 1:  

       #bounds = np.array(bounds).repeat((1,nDOFs),axis=0).T
       bounds = np.tile(bounds, (nDOFs, 1))
       lower_bounds = bounds[:,0]  
       upper_bounds = bounds[:,1]  
    else:    
       lower_bounds = bounds[:,0]  
       upper_bounds = bounds[:,1]  
    #--------------------------------------   
    
    constraints = kwargs.setdefault('constraints',[])
    #First guess---------------------------
    carry = kwargs.setdefault('carry',{})
    x  = kwargs.setdefault('x0',[])
    if len(x) == 0:
        x = lower_bounds +  np.random.rand(nDOFs)*(upper_bounds-lower_bounds)
        

    shape_in                   = jax.ShapeDtypeStruct((nDOFs,), jnp.float64)

    max_iter     = kwargs.setdefault('maxiter',40)
    tol          = kwargs.setdefault('tol',1e-4)

    #Init 
    transform = kwargs.setdefault('transform',lambda x:x)

    opt = nlopt.opt(nlopt.LD_CCSAQ,nDOFs)
    #opt = nlopt.opt(nlopt.LD_LBFGS,nDOFs)
    

    
    opt.set_lower_bounds(lower_bounds)
    opt.set_upper_bounds(upper_bounds)
   

    all_none = all(x is None for x in constraints)

    opt.set_min_objective(enhance_objective_function(objective,kwargs['state'],not all_none))

 
    #Add inequality constraints
    for k,constraint in enumerate(constraints):
        
        if constraint is None:
           continue
        
        adapt=False
        #constraint(jnp.ones(nDOFs))
        #quit()
        #print(jax.eval_shape(constraint, shape_in))
        #quit()
        if len(jax.eval_shape(constraint, shape_in)[0].shape) == 0:
         N_constraints = 1
         adapt = True
        else:
         N_constraints = jax.eval_shape(constraint, shape_in)[0].shape[0]

        opt.add_inequality_mconstraint(enhance_inequality_constraint(constraint,kwargs['state'],k,k==len(constraints)-1,adapt=adapt),N_constraints*[tol])


    opt.set_maxeval(max_iter)
    opt.set_ftol_rel(tol)
     #opt.set_xtol_rel(1e-6)
    #opt.set_stopval(tol)
  

    x = opt.optimize(x)

    
    return x
  





