def prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
def f(n):
    i = 1
    ans = float('inf')
    while i * i <= n:
        if n % i == 0:
            d = n // i
            val1 = int(str(i) + str(d))
            val2 = int(str(d) + str(i))
            if ans > val1:
                ans = val1
            if ans > val2:
                ans = val2  
        i += 1
    return ans
n = int(input())
if n > 10 and prime(n):
    print(-1)
elif n < 10:
    print(n)
else:
    print(f(n))