from .base_algorithm import beam_search
from .iterative_subinstance_algorithm import iterative_identification

def find_causes(
    instance, domains, simulation, variables, # SCM
    dag=None, init_var_ids=None, # inputs for the iterative algo
    max_steps=5, beam_size=10, epsilon=.05, early_stop=True, max_time=None, # Parameters
    var_mapping=None, ref_w=tuple(), Cs=None, # Additional parameters when running for sub-instance
    verbose=0
):
    if dag is None or init_var_ids is None:
        return beam_search(
            instance, domains, simulation, variables, 
            max_steps, beam_size, epsilon, early_stop, max_time, 
            var_mapping, ref_w, Cs, verbose
        )
    else:
        return iterative_identification(
            instance, domains, simulation, variables, dag, init_var_ids,
            max_steps=max_steps, beam_size=beam_size, epsilon=epsilon, early_stop=early_stop, max_time=max_time, 
            var_mapping=var_mapping, ref_w=ref_w, Cs=Cs, verbose=verbose
        )
