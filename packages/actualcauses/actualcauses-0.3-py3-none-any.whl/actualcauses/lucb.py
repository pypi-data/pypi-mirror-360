import numpy as np, time
from tqdm import tqdm

from .base_algorithm import beam_search, get_rules, show_rules, get_sets

# This file is inspired by https://github.com/marcotcr/anchor

def kl_bernoulli(p, q):
    p = min(0.9999999999999999, max(0.0000001, p))
    q = min(0.9999999999999999, max(0.0000001, q))
    return (p * np.log(float(p) / q) + (1 - p) *
            np.log(float(1 - p) / (1 - q)))

def dup_bernoulli(p, level):
    lm = p
    um = min(min(1, p + np.sqrt(level / 2.)), 1)
    qm = (um + lm) / 2.
    if kl_bernoulli(p, qm) > level:
        um = qm
    else:
        lm = qm
    return um

def dlow_bernoulli(p, level):
    um = p
    lm = max(min(1, p - np.sqrt(level / 2.)), 0)
    qm = (um + lm) / 2.
    if kl_bernoulli(p, qm) > level:
        lm = qm
    else:
        um = qm
    return lm

def compute_beta(n_features, t):
    delta = .1
    alpha = 1.1
    k = 405.5
    temp = np.log(k * n_features * (t ** alpha) / delta)
    return temp + np.log(temp)


def lucb(simulation, rules, beam_size, a=.05, beam_eps=.1, cause_eps=.01, non_cause_esp=.01, 
         max_iter=200, verbose=1, batch_size=10, lucb_infos=None):
        
    n_arms = len(rules) # Doing armed bandits with the rules to evaluate
    # For each arm we keep track of the number of samples, the number of success, the upper bound and the lower bound
    positives, scores, lb, means, mean_scores = np.zeros((5, n_arms))
    ub = np.ones(n_arms)
    n_samples = np.zeros(n_arms, dtype=int)
    beta = 0
    
    # Utils function
    def action_arm(arm):
        for _ in range(batch_size):
            _, label, score = simulation(rules[arm])
            positives[arm] += label
            scores[arm] += score
        n_samples[arm] += batch_size
        means[arm] = positives[arm] / n_samples[arm]
        mean_scores[arm] = scores[arm] / n_samples[arm]

    def update_bounds_beam(t):
        bs = beam_size + (means < a).sum()
        sorted_rule_ids = sorted(range(n_arms), key = lambda i: (means[i],mean_scores[i]))
        
        beam_ids = sorted_rule_ids[:bs]
        non_beam_ids = sorted_rule_ids[bs:]
        # print(f"{beam_ids=} / {non_beam_ids=}")
        if not beam_ids or not non_beam_ids: return 0
        for i in beam_ids:
            ub[i] = dup_bernoulli(means[i], beta / n_samples[i])
        for i in non_beam_ids:
            lb[i] = dlow_bernoulli(means[i], beta / n_samples[i])
            
        ut = beam_ids[np.argmax(ub[beam_ids])]
        lt = non_beam_ids[np.argmin(lb[non_beam_ids])]
        B = ub[ut] - lb[lt]
        if B >= beam_eps:
            action_arm(ut)
            action_arm(lt)
        return B

    def update_bounds_non_cause(t):
        ids = np.argwhere(means >= a).flatten()
        # print(f"non cause: {ids=}")
        for i in ids:
            lb[i] = dlow_bernoulli(means[i], beta / n_samples[i])
        if not ids.size: return 0
        lt = ids[np.argmin(lb[ids])]
        B = a - lb[lt]
        if B >= non_cause_esp:
            action_arm(lt)
        return B

    def update_bounds_cause(t):
        ids = np.argwhere(means < a).flatten()
        # print(f"cause: {ids=}")
        for i in ids:
            ub[i] = dup_bernoulli(means[i], beta / n_samples[i])
        if not ids.size: return 0
        ut = ids[np.argmax(ub[ids])]
        B = ub[ut] - a
        if B >= cause_eps:
            action_arm(ut)
        return B
    
    # Initialization
    beam_bound = 1
    cause_bound = 1
    non_cause_bound = 1
    for arm in tqdm(range(n_arms), disable=not verbose):
        action_arm(arm)
    it = 1
    # Loop
    with tqdm(total=n_arms * max_iter, disable=not verbose) as pbar:
        while n_samples.sum() < n_arms * max_iter:
            # Stop condition
            if beam_bound <= beam_eps and cause_bound <= cause_eps and non_cause_bound <= non_cause_esp: 
                if verbose > 1: 
                    print(f"Success: {beam_bound=:.4f} / {cause_bound=:.4f} / {non_cause_bound=:.4f})")
                break
            if cause_bound <= cause_eps and non_cause_bound <= non_cause_esp and beam_size + (means < a).sum() >= n_arms:
                if verbose > 1:
                    print(f"All rules pass on to next state: {cause_bound=:.4f}, {non_cause_bound=:.4f}")
                break
                
            # Update bounds
            beta = compute_beta(n_arms, it)
            beam_bound = update_bounds_beam(it)
            cause_bound = update_bounds_cause(it)
            non_cause_bound = update_bounds_non_cause(it)
            pbar.n = n_samples.sum()
            pbar.refresh()
            it += 1
        else:
            # Render how much we fail if we fail to reach the bound
            if verbose > 1: 
                print(f"Fail: {beam_bound=:.4f} / {cause_bound=:.4f} / {non_cause_bound=:.4f}")
            
    if verbose > 2:
        print(f"ub={ub.round(4)}")
        print(f"lb={lb.round(4)}")
        print(f"preds={means.round(2)}")
        print(f"n_samples={n_samples}")
    if lucb_infos is not None:
        lucb_infos.append({
            "n_calls": int(n_samples.sum())
        })
    outputs = [((n_sample, ub_i, lb_i), mean, mean_score) for \
                   n_sample, ub_i, lb_i, mean, mean_score in \
                    zip(
                        n_samples.tolist(),
                        ub.tolist(), 
                        lb.tolist(), 
                        means.tolist(), 
                        mean_scores.tolist()
                    )]
    return outputs