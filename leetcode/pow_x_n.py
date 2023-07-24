# https://leetcode.com/problems/powx-n/

class Solution:
    def myPow(self, x: float, n: int) -> float:
        if n == 0:
            return 1.0

        if n < 0:
            x = 1 / x
            n = -n

        def power(x, n):
            if n == 0:
                return 1.0
            half_power = power(x, n // 2)
            return half_power * half_power if n % 2 == 0 else half_power * half_power * x

        return power(x, n)
