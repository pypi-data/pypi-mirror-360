
class PureRandom:

    def __init__(self, seed=None):

        self.a = 1103515245  
        self.c = 12345       
        self.m = 2**31       
        
        if seed is None:
            seed = abs(hash(str(id(self))) + id(self)) % self.m
        
        self.seed_value = seed % self.m
        self._state = self.seed_value
    
    def seed(self, seed_value):

        if seed_value is None:
            seed_value = abs(hash(str(id(self))) + id(self)) % self.m
        
        self.seed_value = seed_value % self.m
        self._state = self.seed_value
    
    def _next(self):

        self._state = (self.a * self._state + self.c) % self.m
        return self._state
    
    def random(self):

        return self._next() / self.m
    
    def randint(self, min_val, max_val):

        if min_val > max_val:
            
            raise ValueError
        
        range_size = max_val - min_val + 1
        return min_val + (self._next() % range_size)
    
    def choice(self, sequence):

        if not sequence:
            raise IndexError
        
        index = self.randint(0, len(sequence) - 1)
        return sequence[index]
    
    def shuffle(self, sequence):

        if not sequence:
            return
        
        for i in range(len(sequence) - 1, 0, -1):
            j = self.randint(0, i)
            sequence[i], sequence[j] = sequence[j], sequence[i]
    
    def sample(self, population, k):

        if k > len(population):
            raise ValueError
        
        if k < 0:
            raise ValueError
        
        indices = list(range(len(population)))
        result = []
        
        for _ in range(k):
            if not indices:
                break
            
            idx = self.randint(0, len(indices) - 1)
            selected_idx = indices.pop(idx)
            result.append(population[selected_idx])
        
        return result
    
    def uniform(self, min_val, max_val):
        
        return min_val + (max_val - min_val) * self.random()

_global_random = PureRandom()


def seed(seed_value=None):
    _global_random.seed(seed_value)


def random():
    return _global_random.random()


def randint(min_val, max_val):
    return _global_random.randint(min_val, max_val)


def choice(sequence):
    return _global_random.choice(sequence)


def weighted_choice(sequence, weights=None, size=1, replace=True):

    if isinstance(sequence, int):
        sequence = list(range(sequence))
    elif not isinstance(sequence, (list, tuple)):
        sequence = list(sequence)
    
    if not sequence:
        raise ValueError
    
    if weights is None:
        weights = [1.0] * len(sequence)
    else:
        if hasattr(weights, 'data'):
            weights = weights.data if isinstance(weights.data, list) else list(weights.data)
        elif hasattr(weights, '__iter__'):
            weights = list(weights)
        else:
            weights = [weights]
    
    if len(weights) != len(sequence):
        raise ValueError
    
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError
    
    normalized_weights = [w / total_weight for w in weights]
    
    cumulative_weights = []
    cumsum = 0.0
    for w in normalized_weights:
        cumsum += w
        cumulative_weights.append(cumsum)
    
    cumulative_weights[-1] = 1.0
    
    def select_one():
        rand_val = _global_random.random()
        for i, cum_weight in enumerate(cumulative_weights):
            if rand_val <= cum_weight:
                return sequence[i]
        return sequence[-1]
    
    if size == 1:
        return select_one()
    
    results = []
    available_indices = list(range(len(sequence)))
    available_weights = normalized_weights[:]
    
    for _ in range(size):
        if not available_indices:
            break
        
        if replace or len(available_indices) == len(sequence):
            selected = select_one()
            results.append(selected)
        else:
            if not available_indices:
                break
            
            total_available_weight = sum(available_weights)
            if total_available_weight <= 0:
                break
            
            normalized_available = [w / total_available_weight for w in available_weights]
            cumulative_available = []
            cumsum = 0.0
            for w in normalized_available:
                cumsum += w
                cumulative_available.append(cumsum)
            cumulative_available[-1] = 1.0
            
            rand_val = _global_random.random()
            selected_idx = None
            for i, cum_weight in enumerate(cumulative_available):
                if rand_val <= cum_weight:
                    selected_idx = i
                    break
            
            if selected_idx is None:
                selected_idx = len(cumulative_available) - 1

            actual_idx = available_indices[selected_idx]
            selected = sequence[actual_idx]
            results.append(selected)
            
            available_indices.pop(selected_idx)
            available_weights.pop(selected_idx)
    
    return results


def shuffle(sequence):
    _global_random.shuffle(sequence)


def sample(population, k):
    return _global_random.sample(population, k)


def uniform(min_val, max_val):
    return _global_random.uniform(min_val, max_val)


def normal(mean=0.0, std=1.0):

    return _global_random.normal(mean, std)


def normal_batch(size, mean=0.0, std=1.0):

    result = [0.0] * size
    from . import A20_math as math1
    from .A20_math import strong_log
    
    two_pi = 2.0 * math1.pi
    
    i = 0
    random_func = _global_random.random 
    sqrt_func = math1.sqrt
    cos_func = math1.cos
    sin_func = math1.sin
    log_func = strong_log
    
    while i < size:
        u1 = random_func()
        u2 = random_func()
        
        if u1 <= 1e-10: 
            continue
        
        sqrt_term = sqrt_func(-2.0 * log_func(u1))
        angle = two_pi * u2
        
        z0 = sqrt_term * cos_func(angle)
        result[i] = mean + std * z0
        i += 1
        
        if i < size:
            z1 = sqrt_term * sin_func(angle)
            result[i] = mean + std * z1
            i += 1
    
    return result


def uniform_batch(size, low=0.0, high=1.0):

    from . import A2_arrays as arrays
    total_size = size if isinstance(size, int) else int(arrays.prod(arrays.Array(size)))
    result = [0.0] * total_size
    range_val = high - low
    
    for i in range(total_size):
        result[i] = low + range_val * _global_random.random()
    
    return result


