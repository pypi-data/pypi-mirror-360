
e = 2.718281828459045235360287471352662498
pi = 3.141592653589793238462643383279502884
tau = 2 * pi  
inf = float('inf')
nan = float('nan')


def abs(x):
    if x >= 0:
        return x
    else:
        return -x

def fabs(x):
    return float(abs(x))

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def sqrt(x):
    if x < 0:
        raise ValueError
    if x == 0:
        return 0.0
    
    guess = x / 2.0
    
    for _ in range(50):  
        new_guess = 0.5 * (guess + x / guess)
        if abs(new_guess - guess) < 1e-15:
            break
        guess = new_guess
    
    return guess

def pow(x, y):
    if y == 0:
        return 1.0
    if y == 1:
        return x
    if y == -1:
        return 1.0 / x
    
    if isinstance(y, int) and y > 0:
        result = 1.0
        base = x
        exp = y
        while exp > 0:
            if exp % 2 == 1:
                result *= base
            base *= base
            exp //= 2
        return result
    
    if x <= 0:
        
        if x == 0:
            if y > 0:
                return 0.0
            else:
                raise ValueError
        else:
            raise ValueError
    
    return exp(y * log(x))

def exp(x):
    if x == 0:
        return 1.0
    
    if x > 700:
        return inf
    if x < -700:
        return 0.0
    
    n = int(x)
    x = x - n
    
    result = 1.0
    term = 1.0
    
    for i in range(1, 50):
        term *= x / i
        result += term
        if abs(term) < 1e-15:
            break
    
    for _ in range(abs(n)):
        if n > 0:
            result *= e
        else:
            result /= e
    
    return result

def log(x):
    if x <= 0:
        raise ValueError
    if x == 1:
        return 0.0
    
    n = 0
    while x >= 2:
        x /= 2
        n += 1
    while x < 1:
        x *= 2
        n -= 1
    
    u = x - 1
    result = 0.0
    term = u
    
    for i in range(1, 50):
        result += term / i if i % 2 == 1 else -term / i
        term *= u
        if abs(term) < 1e-15:
            break
    
    return result + n * 0.6931471805599453  

def log10(x):
    return log(x) / 2.302585092994046  

def log2(x):
    return log(x) / 0.6931471805599453 

def strong_log(x):

    if x <= 0:
        raise ValueError
    
    if x == 1.0:
        return 0.0
    
    if x == 2.71828182845904523536:  
        return 1.0
    
    if x < 1e-10:
        return -23.025850929940456 
    
    if x > 1e10:
        k = 0
        temp_x = x
        e_approx = 2.71828182845904523536
        while temp_x > e_approx:
            temp_x /= e_approx
            k += 1
        return strong_log(temp_x) + k
    
    k = 0
    while x < 0.5:
        x *= 2
        k -= 1
    while x > 2.0:
        x /= 2
        k += 1
    
    ln2 = 0.6931471805599453094172321214581766
    
    sqrt2 = 1.4142135623730950488016887242097
    if x > sqrt2:
        x /= 2
        k += 1
    
    z = (x - 1) / (x + 1)
    z_squared = z * z

    series_sum = z
    z_power = z
    
    for n in range(3, 41, 2):  
        z_power *= z_squared
        term = z_power / n
        series_sum += term

        if abs(term) < 1e-15:
            break
    
    result = 2 * series_sum + k * ln2
    
    return result


def strong_log10(x):

    if x <= 0:
        raise ValueError
    
    ln10 = 2.3025850929940456840179914546844
    return strong_log(x) / ln10


def strong_log2(x):

    if x <= 0:
        raise ValueError
    
    ln2 = 0.6931471805599453094172321214581766
    return strong_log(x) / ln2


def sin(x):
    x = x % (2 * pi)
    if x > pi:
        x -= 2 * pi
    
    result = 0.0
    term = x
    
    for n in range(1, 50, 2):
        result += term
        term *= -x * x / ((n + 1) * (n + 2))
        if abs(term) < 1e-15:
            break
    
    return result

def cos(x):
    x = x % (2 * pi)
    if x > pi:
        x -= 2 * pi
    
    result = 1.0
    term = 1.0
    
    for n in range(2, 50, 2):
        term *= -x * x / (n * (n - 1))
        result += term
        if abs(term) < 1e-15:
            break
    
    return result

def tan(x):
    cos_x = cos(x)
    if abs(cos_x) < 1e-15:
        raise ValueError
    return sin(x) / cos_x

def asin(x):
    if abs(x) > 1:
        raise ValueError
    if x == 1:
        return pi / 2
    if x == -1:
        return -pi / 2
    if x == 0:
        return 0.0
    
    result = x
    term = x
    
    for n in range(1, 30):
        term *= x * x * (2 * n - 1) * (2 * n - 1) / ((2 * n) * (2 * n + 1))
        result += term
        if abs(term) < 1e-15:
            break
    
    return result

def acos(x):
    if abs(x) > 1:
        raise ValueError
    return pi / 2 - asin(x)

def atan(x):
    if abs(x) > 1:
        if x > 0:
            return pi / 2 - atan(1 / x)
        else:
            return -pi / 2 - atan(1 / x)
    
    result = 0.0
    term = x
    
    for n in range(1, 50, 2):
        result += term / n
        term *= -x * x
        if abs(term) < 1e-15:
            break
    
    return result

def atan2(y, x):
    if x > 0:
        return atan(y / x)
    elif x < 0:
        if y >= 0:
            return atan(y / x) + pi
        else:
            return atan(y / x) - pi
    else:  
        if y > 0:
            return pi / 2
        elif y < 0:
            return -pi / 2
        else:
            return 0.0 

def sinh(x):
    return (exp(x) - exp(-x)) / 2

def cosh(x):
    return (exp(x) + exp(-x)) / 2

def tanh(x):
    if x > 700:
        return 1.0
    if x < -700:
        return -1.0
    
    exp_2x = exp(2 * x)
    return (exp_2x - 1) / (exp_2x + 1)

def factorial(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError
    
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def gamma(x):
    if x <= 0:
        raise ValueError
    if x < 1:
        return gamma(x + 1) / x
    
    x -= 1
    if x == 0:
        return 1.0
    
    return sqrt(2 * pi / x) * pow(x / e, x)

def erf(x):
    if x == 0:
        return 0.0
    
    sqrt_pi = sqrt(pi)
    result = 0.0
    term = x
    
    for n in range(50):
        coeff = 1.0
        for i in range(1, n + 1):
            coeff /= i
        
        result += ((-1) ** n) * term * coeff / (2 * n + 1)
        term *= x * x
        
        if abs(term * coeff) < 1e-15:
            break
    
    return 2 / sqrt_pi * result

def floor(x):
    return int(x) if x >= 0 else int(x) - 1

def ceil(x):
    return int(x) + 1 if x > int(x) else int(x)

def trunc(x):
    return int(x)

def fmod(x, y):
    if y == 0:
        raise ValueError
    return x - int(x / y) * y

def modf(x):
    integer_part = trunc(x)
    fractional_part = x - integer_part
    return (fractional_part, integer_part)

def ldexp(x, i):
    return x * pow(2, i)

def frexp(x):
    if x == 0:
        return (0.0, 0)
    
    sign = 1 if x >= 0 else -1
    x = abs(x)
    
    exp = 0
    while x >= 1:
        x /= 2
        exp += 1
    while x < 0.5:
        x *= 2
        exp -= 1
    
    return (sign * x, exp)

def hypot(x, y):
    return sqrt(x * x + y * y)

def degrees(x):
    return x * 180 / pi

def radians(x):
    return x * pi / 180

def isnan(x):
    return x != x

def isinf(x):
    return x == inf or x == -inf

def isfinite(x):
    return not (isnan(x) or isinf(x))

def copysign(x, y):
    if y >= 0:
        return abs(x)
    else:
        return -abs(x)

def fmax(x, y):
    if isnan(x):
        return y
    if isnan(y):
        return x
    return max(x, y)

def fmin(x, y):
    if isnan(x):
        return y
    if isnan(y):
        return x
    return min(x, y)
