import numpy as np
from typing import Tuple
from ..err import MException


def add(x, y):
    return x**2 + x**3 + y**2


class PSO:
    def __init__(self):
        self.pn = 20
        self.dim = 2
        self.max_iter = 150
        self.w = 0.729844
        self.c1 = 1.49618
        self.c2 = 1.49618
        self.s_scope = [[-10, 10], [-5, 10]]
        self.v_scope = [[-10, 10], [-5, 10]]
        self.func = add
        self.dim_scope = True

    def create_pn_v_matrix(self):
        pn_matrix = np.column_stack(
            [
                np.random.uniform(low=low, high=high, size=self.pn)
                for low, high in self.s_scope
            ]
        )
        v_matrix = np.column_stack(
            [
                np.random.uniform(low=low, high=high, size=self.pn)
                for low, high in self.v_scope
            ]
        )
        return pn_matrix, v_matrix

    def run(self) -> Tuple[bool, MException]:
        if not self.func:
            return None, MException("FuncISNone", "优化函数为空")
        func_params = self.func.__code__.co_argcount
        if func_params != self.dim:
            return None, MException(
                "FuncParamsError",
                f"优化函数参数个数不匹配，需要{self.dim}个，实际是{func_params}",
            )
        if self.dim_scope:
            pn_matrix, v_matrix = self.create_pn_v_matrix()
        else:
            pn_matrix = np.random.randint(*self.s_scope, size=(self.pn, self.dim))
            v_matrix = np.random.randint(*self.v_scope, size=(self.pn, self.dim))
        p_best = np.empty_like(pn_matrix)
        p_best_value = np.full(self.pn, np.inf)
        pn_best = None
        pn_best_value = np.inf
        for batch in range(self.max_iter):
            for dim in range(len(pn_matrix)):
                if p_best_value is None:
                    p_best[dim] = pn_matrix[dim]
                    p_best_value[dim] = self.func(*pn_matrix[dim])
                elif self.func(*pn_matrix[dim]) < p_best_value[dim]:
                    p_best[dim] = pn_matrix[dim]
                    p_best_value[dim] = self.func(*pn_matrix[dim])
            min_index = np.argmin(p_best_value)
            if pn_best_value is None:
                pn_best = pn_matrix[min_index]
                pn_best_value = p_best_value[min_index]
            elif p_best_value[min_index] < pn_best_value:
                pn_best = pn_matrix[min_index]
                pn_best_value = p_best_value[min_index]
            r1, r2 = np.random.rand(2)
            v_matrix = (
                self.w * v_matrix
                + self.c1 * r1 * (p_best - pn_matrix)
                + self.c2 * r2 * (pn_best - pn_matrix)
            )
            pn_matrix = np.clip(v_matrix, *self.s_scope)
            v_matrix = np.clip(v_matrix, *self.v_scope)
            print(f"第{batch + 1}次迭代结果：{p_best_value}")
        print(f"最优解：{pn_best}, 最小值：{pn_best_value}")
        return True, None

    @staticmethod
    def test():
        pso = PSO()
        status, err = pso.run()
        if not status:
            print(err.dump())
