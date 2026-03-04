---
title: Rabin-Karp 算法
date: '2020-06-21'
tags:
- 算法
---

Rabin-Karp算法，是由M.O.Rabin和R.A.Karp发明的一种基于哈希函数的字符串查找算法。

近期在leetcode遇到的一道hard题 ，了解到了Rabin-Karp算法。原题如下：

> 给出一个字符串 S，考虑其所有重复子串（S 的连续子串，出现两次或多次，可能会有重叠）。返回任何具有最长可能长度的重复子串。（如果 S 不含重复子串，那么答案为 “”。）

一个很自然的想法是假设一个长度为L的子串，然后查找这个长度的子串是否是重复的。由于如果L长度子串有重复的，则L-1也必定满足拥有重复的字串。我们可以使用二分查找来寻找最大的长度。这样，问题就变成了寻找一个长度为L的子串在S中是否有相同的子串。

如果不使用Rabin-Karp算法，遍历字符串需要 $O(n)$的时间，而每一次的比较又需要$O(n)$的时间，这样一来一次验证需要$O(n^2)$的时间。Rabin-Karp算法的思想很简单：不去直接比较字符串是否相等，而是去比较字符串的哈希值，相等则认为是一致的。（其实因为哈希是不可逆的，在实际情况数据很大的时候有时会不一致，这时需要再比较下字符串验证。）

Rabin-Karp使用的哈希方法如下：

字母$a-z$分别对应数字$1-26$，这样我们就可以把字符串转换成26进制的数字了。例如abc可以转换成：  
$$  
abc = 1 \times 26^2 + 2 \times 26^1 + 3 \times 26^0  
$$  
更广泛的说一个长度为$L$ 字符串的哈希函数为：  
$$  
H\_i = S[i] \times 26^{L-1} + S[i+1] \times 26^{L-2} + …+ S[i+L-1] \times 26^{0}  
$$

如果是直接比较哈希值的话则没有意义（因为计算这个公式的哈希值就和直接比较字符串复杂度一样了）但是如果考虑到$H\_{i+1}$ 和 $H\_i$ 有方程关系，我们不需要每次去重新计算子串哈希值，只要再原来基础上加上右边新加入的字符哈希值，减去左边的字符哈希值就可以去比较了。这样一来计算哈希值的时间复杂度就是$O(1)$。这个思想有点类似slide-window。

```
def RabinKarp(self, L, S):
    '''
    input:
    L: pattern length
    S: target string
    output:
    tuple: (bool, aim string)
    '''
    a = 26
    n = len(S)
    h = 0
    nums = [ord(S[i]) - ord('a') for i in range(n)]
    for i in range(L):
        h = (h * a + nums[i]) % (2**32 - 1)
    
    aL = pow(a, L, 2**32)
    seen = {h}
    for start in range(1, n - L + 1):
        # compute rolling hash in O(1) time
        h = (h * a - nums[start - 1] * aL + nums[start + L - 1]) % (2**32 - 1)
        if h in seen:
            return (True, S[start: start+L])
        else:
            seen.add(h)
    return (False, '')
```

### 注意事项

由于代码里有指数运算，数字会变得很大，所以在进行哈希值求解后要进行取模运算。
