from typing import List
from scipy.optimize import minimize


def stupid_minimal(func, init_params: List, steps, *args, n=2, **kws):

    best_params = init_params.copy()
    for epoch in range(n):
        for index in range(len(init_params)):
            now_result = func(best_params, *args, **kws)
            while True:
                now_params_1 = best_params.copy()
                now_params_2 = best_params.copy()
                now_params_1[index] += steps[index]
                now_params_2[index] -= steps[index]

                res1 = func(now_params_1, *args, **kws)
                res2 = func(now_params_2, *args, **kws)

                if res1 < now_result:
                    best_params = now_params_1
                    now_result = res1
                    continue

                if res2 < now_result:
                    now_result = res2
                    best_params = now_params_2
                    continue

                break

        print(f"epoch: {epoch} now {now_result}")
    return best_params


def super_minimize(func, x0, arg=(), *args, **kw):
    """如果这个不行，就是scipy.optimize import minimize不行了"""

    methods = [
        "Nelder-Mead",
        "Powell",
        "CG",
        "BFGS",
        "L-BFGS-B",
        "TNC",
        "COBYLA",
        "COBYQA",
        "SLSQP",
        "trust-constr",
    ]

    if "method" in kw:
        methods = kw["method"]
        return minimize(func, x0, arg, *args, **kw)

    # 首轮最小值
    method_results = {}
    for m in methods:
        result = minimize(func, x0, arg, method=m, *args, **kw)
        method_results[m] = result
        print(m, result.fun)

    min_method = min(method_results, key=lambda m: method_results[m].fun)
    new_x0 = method_results[min_method].x

    print({k: v.fun for k, v in method_results.items()})

    method_results = {}
    for m in methods:
        result = minimize(func, new_x0, arg, method=m, *args, **kw)
        method_results[m] = result
        print(m, result.fun)

    print({k: v.fun for k, v in method_results.items()})
    min_method = min(method_results, key=lambda m: method_results[m].fun)
    # new_x0 = method_results[min_method].x
    return method_results[min_method]


