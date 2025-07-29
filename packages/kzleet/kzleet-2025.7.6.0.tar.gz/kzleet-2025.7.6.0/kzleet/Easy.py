from .Solution import Solution

class Solution_594(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 594, 'Easy')

    main = None

    def findLHS(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-harmonious-subsequence/?envType=daily-question&envId=2025-06-30

        :type nums: List[int]
        :rtype: int
        '''

        counts = {}

        for i in nums:
            if i in counts: # counts.keys()
                counts[i] += 1

            else:
                counts[i] = 1

        max_length = 0

        for num in counts:
            if num + 1 in counts: # so diff == 1
                max_length = max(max_length, counts[num] + counts[num + 1])

        return max_length

    main = findLHS

class Solution_1394(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1394, 'Easy')

    main = None

    def findLucky(self, arr):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-lucky-integer-in-an-array/?envType=daily-question&envId=2025-07-05
        
        :type arr: List[int]
        :rtype: int
        '''

        counts = {}

        for n in arr:
            if n in counts:
                counts[n] += 1

            else:
                counts[n] = 1

        for n, f in sorted(counts.items(), reverse = True): # efficient and get largest
            if n == f:
                return n

        return -1

    main = findLucky

class Solution_2016_A(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2016, 'Easy')

    main = None

    def maximumDifference(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-difference-between-increasing-elements/?envType=daily-question&envId=2025-06-16

        :type nums: List[int]
        :rtype: int
        '''

        max_diff = -1
        for i in range(1, len(nums)):
            max_diff = max(nums[i] - min(nums[:i]), max_diff)

        return max_diff if max_diff > 0 else -1

    main = maximumDifference

class Solution_2016_B(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2016, 'Easy')

    main = None

    def maximumDifference(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-difference-between-increasing-elements/?envType=daily-question&envId=2025-06-16

        :type nums: List[int]
        :rtype: int
        '''

        max_diff = -1
        min_val = nums[0]

        for i in range(1, len(nums)):
            if nums[i] > min_val:
                max_diff = max(max_diff, nums[i] - min_val)

            else:
                min_val = nums[i]

        return max_diff if max_diff > 0 else -1

    main = maximumDifference

class Solution_2099(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2099, 'Easy')

    main = None

    def maxSubsequence(self, nums, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-subsequence-of-length-k-with-the-largest-sum/?envType=daily-question&envId=2025-06-28

        :type nums: List[int]
        :type k: int
        :rtype: List[int]
        '''

        indexed_nums = [(num, i) for i, num in enumerate(nums)]

        best_nums = sorted(indexed_nums, key = lambda x: -x[0])[:k] # get biggest, using the negative and first is faster

        best_ordered_nums = sorted(best_nums, key = lambda x: x[1]) # get first indices

        return [num for num, i in best_ordered_nums]

    main = maxSubsequence

class Solution_2138(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2138, 'Easy')

    main = None

    def divideString(self, s, k, fill):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/divide-a-string-into-groups-of-size-k/?envType=daily-question&envId=2025-06-22

        :type s: str
        :type k: int
        :type fill: str
        :rtype: List[str]
        '''

        s += fill * ((k - len(s) % k) % k)
        result = []
        for i in range(0, len(s), k):
            result.append(s[i: i + k])

        return result

    main = divideString

class Solution_2200(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2200, 'Easy')

    main = None

    def findKDistantIndices(self, nums, key, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-all-k-distant-indices-in-an-array/?envType=daily-question&envId=2025-06-24

        :type nums: List[int]
        :type key: int
        :type k: int
        :rtype: List[int]
        '''

        keys = set([i for i in range(len(nums)) if nums[i] == key])
        for _k in keys.copy():
            keys |= set(range(max(_k - k, 0), min(_k + k, len(nums) - 1) + 1))

        return sorted(list(keys))

    main = findKDistantIndices

class Solution_2566(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2566, 'Easy')

    main = None

    def minMaxDifference(self, num):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-difference-by-remapping-a-digit/?envType=daily-question&envId=2025-06-14

        :type num: int
        :rtype: int
        '''

        a = str(num)
        b = str(num)

        for c in a:
            if int(c) < 9:
                a = a.replace(c, '9')
                break

        for c in b:
            if int(c) > 0:
                b = b.replace(c, '0')
                break

        return abs(int(a) - int(b))

    main = minMaxDifference

class Solution_2894(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2894, 'Easy')

    main = None

    def differenceOfSums(self, n, m):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/divisible-and-non-divisible-sums-difference/?envType=daily-question&envId=2025-05-27

        :type n: int
        :type m: int
        :rtype: int
        '''
        num = 0
        for i in range(n + 1):
            num += i if i % m != 0 else -i

        return num

    main = differenceOfSums

class Solution_2942(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2942, 'Easy')

    main = None

    def findWordsContaining(self, words, x):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-words-containing-character/?envType=daily-question&envId=2025-05-24

        :type words: List[str]
        :type x: str
        :rtype: List[int]
        '''

        indices = []
        for i in range(len(words)):
            if x in words[i]: indices.append(i)

        return indices

    main = findWordsContaining

class Solution_3304(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3304, 'Easy')

    main = None

    def kthCharacter(self, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-the-k-th-character-in-string-game-i/?envType=daily-question&envId=2025-07-03

        :type k: int
        :rtype: str
        '''

        '''
        The amount of shifts is the amount of ones in the binary representation of k - 1.
        0, 0 1, 01 12, 0112 1223, 01121223 12232334
        Notice that the binary representation accounts for the 'root' that this k-value was from.
        If k were 5, k - 1 = 0b100 shows that there was a shift only at the current one.
        If k were 7, k - 1 = 0b110 shows the shift in the current shift and the shift of this number from all those before.

        Essentially, representing k - 1 in binary shows the path of shifts this number had before.
        '''

        x = bin(k - 1).count('1') # how many shifts have happened, represent in binary

        return chr(x % 26 + ord('a')) # mod isn't needed since the length constraint

    main = kthCharacter

class Solution_3330(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3330, 'Easy')

    main = None

    def possibleStringCount(self, word):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-the-original-typed-string-i/?envType=daily-question&envId=2025-07-01

        :type word: str
        :rtype: int
        '''

        count = 1

        for i in range(1, len(word)):
            if word[i] == word[i - 1]:
                count += 1

        return count

    main = possibleStringCount

class Solution_3423(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3423, 'Easy')

    main = None

    def maxAdjacentDistance(self, nums):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-difference-between-adjacent-elements-in-a-circular-array/?envType=daily-question&envId=2025-06-12

        :type nums: List[int]
        :rtype: int
        '''

        nums.append(nums[0])
        diff = [abs(nums[i + 1] - nums[i]) for i in range(len(nums)) if i < len(nums) - 1]

        return max(diff)

    main = maxAdjacentDistance

class Solution_3442(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3442, 'Easy')

    main = None

    def maxDifference(self, s):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-difference-between-even-and-odd-frequency-i/description/?envType=daily-question&envId=2025-06-10

        :type s: str
        :rtype: int
        '''

        g = [0] * 26

        for c in s: g[ord(c) - ord('a')] += 1

        a1 = 0
        a2 = len(s)

        for i in g:
            if i == 0: continue

            if i % 2 == 1 and i > a1:
                a1 = i

            if i % 2 == 0 and i < a2:
                a2 = i

        return a1 - a2

    main = maxDifference