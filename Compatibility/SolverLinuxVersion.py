#   ______   __  __  __ ____      ___           _     _           
#  | __ ) \ / / |  \/  |  _ \    |_ _|_ __  ___(_) __| | ___ _ __ 
#  |  _ \\ V /  | |\/| | |_) |    | || '_ \/ __| |/ _` |/ _ \ '__|
#  | |_) || |   | |  | |  _ < _   | || | | \__ \ | (_| |  __/ |   
#  |____/ |_|   |_|  |_|_| \_(_) |___|_| |_|___/_|\__,_|\___|_|   
#
#  Codigo en español por que es mi idioma nativo.
#
#  Esta primera version se realizo con la ia de vscode, acepto sugerencias.
#
##################################################################

import sys
import multiprocessing


# Función para combinar dos valores con las operaciones permitidas.

import time
def combine_vals(a, ea, b, eb, ops, MAX_RESULT=10**6, MAX_EXP=9):
    out = []
    if 1 in ops:  # suma
        v = a + b
        if abs(v) <= MAX_RESULT:
            out.append((v, f"({ea}+{eb})"))
    if 2 in ops:  # multiplicación
        v = a * b
        if abs(v) <= MAX_RESULT:
            out.append((v, f"({ea}*{eb})"))
    if 3 in ops:  # resta
        v1 = a - b
        if v1 > 0 and v1 <= MAX_RESULT:
            out.append((v1, f"({ea}-{eb})"))
        v2 = b - a
        if v2 > 0 and v2 <= MAX_RESULT:
            out.append((v2, f"({eb}-{ea})"))
    if 4 in ops:  # división exacta
        if b != 0 and a % b == 0:
            v = a // b
            if v > 0:
                out.append((v, f"({ea}/{eb})"))
        if a != 0 and b % a == 0:
            v = b // a
            if v > 0:
                out.append((v, f"({eb}/{ea})"))
    if 5 in ops:  # elevación (potencia)
        if b >= 2 and b <= MAX_EXP:
            try:
                v = a ** b
                if v > 0 and v <= MAX_RESULT:
                    out.append((v, f"({ea}**{eb})"))
            except OverflowError:
                pass
        if a >= 2 and a <= MAX_EXP:
            try:
                v = b ** a
                if v > 0 and v <= MAX_RESULT:
                    out.append((v, f"({eb}**{ea})"))
            except OverflowError:
                pass
    return out

# Función worker para procesamiento paralelo.
def solve_beltmatic_worker(args):
    a_items, b_items, ops = args
    results = []
    for a, ea in a_items:
        for b, eb in b_items:
            results.extend(combine_vals(a, ea, b, eb, ops))
    return results

# Esta es la función principal que resuelve el problema.
def solve_beltmatic(base, objetivo, ops, max_copias=1000, timeout=10):
    return solve_beltmatic_with_timeout(base, objetivo, ops, max_copias, timeout)

def solve_beltmatic_with_timeout(base, objetivo, ops, max_copias=1000, timeout=None):
    start_time = time.time()
    dp = [dict() for _ in range(max_copias + 1)]
    dp[1][base] = str(base)

    cpu_count = max(1, multiprocessing.cpu_count() // 2)
    pool = multiprocessing.Pool(processes=cpu_count)

    for k in range(2, max_copias + 1):
        # Comprobando el tiempo para cerrar el script si se excede el timeout.
        if timeout is not None and (time.time() - start_time) > timeout:
            print(f"Timeout reached ({timeout}s). Stopping script before RAM Crash, BelmaticSolver dont can solver the number :(")
            pool.close()
            pool.terminate()
            return None, None
        seen = dp[k]
        tasks = []
        for i in range(1, k):
            j = k - i
            tasks.append((list(dp[i].items()), list(dp[j].items()), ops))

        results = pool.map(solve_beltmatic_worker, tasks)
        for comb_list in results:
            for val, expr in comb_list:
                if val not in seen:
                    seen[val] = expr
                    if val == objetivo:
                        pool.close()
                        pool.terminate()
                        return expr, k
    pool.close()
    pool.terminate()
    return None, None

# Esto solo muestra el como hacer el calculo, osea es el resultado.
def reconstruct_expression(base, objetivo, ops, max_copias):
    dp_expr = [dict() for _ in range(max_copias + 1)]
    dp_expr[1][base] = str(base)

    for k in range(2, max_copias + 1):
        seen = dp_expr[k]
        for i in range(1, k):
            j = k - i
            for a, ea in dp_expr[i].items():
                for b, eb in dp_expr[j].items():
                    for val, expr in combine_vals(a, ea, b, eb, ops):
                        if val not in seen:
                            seen[val] = expr
                            if val == objetivo:
                                return expr, k
    return None, None


# Esto es lo que se ve en la terminal al ejecutar el script, es interactivo.
BANNER = r"""
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   ______   __  __  __ ____      ___           _     _            │
│  | __ ) \ / / |  \/  |  _ \    |_ _|_ __  ___(_) __| | ___ _ __  │
│  |  _ \  V /  | |\/| | |_) |    | ||  _ \/ __| |/ _` |/ _ \  __| │
│  | |_) || |   | |  | |  _ < _   | || | | \__ \ | (_| |  __/ |    │
│  |____/ |_|   |_|  |_|_| \_(_) |___|_| |_|___/_|\__,_|\___|_|    │
│                                                                  │
│   Project: BeltmaticSolver                                       │
│   Description: A simple calculator built specifically            │
│                for the game Beltmatic.                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
"""
if __name__ == "__main__":
    print(BANNER)
    print("Choose allowed operations (enter numbers separated by spaces, like '1 2 3'):")
    print("1 = addition   2 = multiplication   3 = subtraction   4 = division   5 = exponentiation")
    ops = list(map(int, input("Operations: ").split()))

    base = int(input("Extractor (1–99): "))
    objetivo = int(input("Target Number: "))

    print(f"\nLooking for how to build {objetivo} using only {base} with operations {ops}...\n")

    expr, k = solve_beltmatic(base, objetivo, ops, max_copias=1000, timeout=10)
    if expr:
        print(f"Number to Build: {objetivo}")
        expr_didactico, _ = reconstruct_expression(base, objetivo, ops, k)
        print(f"Final expression: {expr_didactico}")
    else:
        print(f"Could not construct {objetivo} with ≤{1000} copies of {base}")