from .Solution import Solution

class Solution_135(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 135, 'Hard')

    main = None

    def candy(self, ratings):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/candy/?envType=daily-question&envId=2025-06-02

        :type ratings: List[int]
        :rtype: int
        '''

        n = len(ratings)
        candy = [1] * n

        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                if candy[i] <= candy[i - 1]:
                    candy[i] = candy[i - 1] + 1 # in cases like 1, 2, 3 where they are in a row

        for i in reversed(range(n - 1)):
            if ratings[i] > ratings[i + 1]:
                if candy[i] <= candy[i + 1]:
                    candy[i] = max(candy[i], candy[i + 1]) + 1 # if this one is equal to the other or the other is greater than this

        return sum(candy)

    main = candy

class Solution_440(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 440, 'Hard')

    main = None

    def findKthNumber(self, n, k):
        '''
        Plan: if the we can go from 1 - 2, 11 - 12, do it. If we cannot, then go from 1 - 10, 11 - 110.
        Either next lexicographical sibling or child.
        '''

        '''
        Author: Kevin zhu
        Link: https://leetcode.com/problems/k-th-smallest-in-lexicographical-order/?envType=daily-question&envId=2025-06-09

        :type k: int
        :rtype: int
        '''

        def count_between(n, f):
            steps = 0
            l = f # first, last

            while f <= n:
                steps += min(l, n) - f + 1 # inclusive + 1
                f *= 10
                l *= 10; l += 9
                # if a was 10 (so steps between 10 and 11) and n was ..., + 1 [10, 10], then [100, 109], then [1000, 1099].

            return steps

        k -= 1
        c = 1

        while k > 0:
            steps = count_between(n, c)

            if k < steps: # rooted inside --> ex: the answer is 101, and I am at 10. It is inside this tree.
                k -= 1
                c *= 10

            else: # not inside --> ex: the answer is 201, and I am at 1, so it must be inside the '2' tree
                  # ex2: the answer is 123. I am at 120. If n is a very big number, then between 120 and 121 there is an entire tree ... until I get to 123.
                k -= steps
                c += 1

        return c

    main = findKthNumber

class Solution_1298(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1298, 'Hard')

    main = None

    def maxCandies(self, status, candies, keys, containedBoxes, initialBoxes):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximum-candies-you-can-get-from-boxes/?envType=daily-question&envId=2025-06-03

        :type status: List[int]
        :type candies: List[int]
        :type keys: List[List[int]]
        :type containedBoxes: List[List[int]]
        :type initialBoxes: List[int]
        :rtype: int
        '''

        queue = initialBoxes
        available = []
        candy = 0
        while queue:
            b = queue.pop(0)

            if status[b] == 1:
                candy += candies[b]
            else:
                available.append(b)
                continue

            available.extend(containedBoxes[b])
            for key in keys[b]:
                status[key] = 1

            for j in available[:]:
                if status[j] == 1:
                    if j not in queue:
                        queue.append(j)
                    available.remove(j)

        return candy

    main = maxCandies

class Solution_1857(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1857, 'Hard')

    main = None

    def largestPathValue(self, colors, edges):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/largest-color-value-in-a-directed-graph/?envType=daily-question&envId=2025-05-26

        :type colors: str
        :type edges: List[List[int]]
        :rtype: int
        '''

        n = len(colors)

        # Build graph as adjacency list and indegree array
        graph = [[] for _ in range(n)]
        indegree = [0] * n
        for u, v in edges:
            graph[u].append(v)
            indegree[v] += 1

        # Initialize DP table: dp[node][color] = max count of color at node
        dp = [[0] * 26 for _ in range(n)]
        for i in range(n):
            dp[i][ord(colors[i]) - ord('a')] = 1

        # Initialize queue with nodes having indegree zero
        queue = []
        for i in range(n):
            if indegree[i] == 0:
                queue.append(i)

        visited = 0
        max_value = 0

        # BFS traversal (topological sort)
        while queue:
            node = queue.pop(0)  # pop front (acts as deque.popleft())
            visited += 1
            for neighbor in graph[node]:
                for c in range(26):
                    add = 1 if c == ord(colors[neighbor]) - ord('a') else 0
                    if dp[neighbor][c] < dp[node][c] + add:
                        dp[neighbor][c] = dp[node][c] + add
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
            max_value = max(max_value, max(dp[node]))

        return max_value if visited == n else -1

    main = largestPathValue

class Solution_2014(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2014, 'Hard')

    main = None

    def longestSubsequenceRepeatedK(self, s, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-subsequence-repeated-k-times/?envType=daily-question&envId=2025-06-27

        :type s: str
        :type k: int
        :rtype: str
        '''

        n = len(s)

        # precompute next position of the character
        next_position = [[-1] * 26 for _ in range(n + 1)]
        for i in reversed(range(n)):
            for c in range(26):
                next_position[i][c] = next_position[i + 1][c]

            next_position[i][ord(s[i]) - ord('a')] = i

        def is_valid(pattern, start_index, repetitions_needed):
            if not pattern:
                return True

            l = len(pattern)
            _i = start_index
            found = 0

            while found < repetitions_needed:
                pattern_index = 0
                temp_index = _i

                while pattern_index < l:
                    char_index = ord(pattern[pattern_index]) - ord('a')
                    next_idx = next_position[temp_index][char_index] # continue down the array for the next index of the pattern

                    if next_idx == -1:
                        return False

                    temp_index = next_idx + 1
                    pattern_index += 1

                found += 1
                _i = temp_index

            return True

        result = ''
        queue = ['']
        MAX_LENGTH = len(s) // k # abcabcab --> 3 cannot work since only 8 chars so use floor

        freq = [0] * 26
        for ch in s:
            freq[ord(ch) - ord('a')] += 1

        usable_chars = [chr(i + ord('a')) for i in range(26) if freq[i] >= k]

        while queue:
            current = queue.pop(0)

            if len(current) > len(result) or (len(current) == len(result) and current > result):
                result = current

            if len(current) >= MAX_LENGTH:
                continue

            for c in reversed(usable_chars):
                candidate = current + c

                if is_valid(candidate, 0, k):
                    queue.append(candidate)

        return result

    main = longestSubsequenceRepeatedK

class Solution_2040(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2040, 'Hard')

    main = None

    def kthSmallestProduct(self, nums1, nums2, k):
        import bisect

        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/kth-smallest-product-of-two-sorted-arrays/?envType=daily-question&envId=2025-06-25

        :type nums1: List[int]
        :type nums2: List[int]
        :type k: int
        :rtype: int
        '''

        def leq(x):
            count = 0
            for i in nums1: # apply to each one: nums1[i] * nums2[...]
                if i > 0:
                    count += bisect.bisect_right(nums2, x // i)

                elif i < 0:
                    count += len(nums2) - bisect.bisect_left(nums2, -(-x // i))

                else:  # a == 0 --> 0 * array = [0] * len(array)
                    if x >= 0:
                        count += len(nums2)

            return count

        if len(nums1) > len(nums2): # nums1 is on the outside
            nums1, nums2 = nums2, nums1

        left, right = -10 ** 10, 10 ** 10 # max value

        while left < right: # binary search until left == right --> no more range of answers
            mid = (left + right) // 2

            if leq(mid) >= k:
                right = mid

            else:
                left = mid + 1

        return left

    main = kthSmallestProduct

class Solution_2081(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2081, 'Hard')

    main = None

    def kMirror(self, k, n):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/sum-of-k-mirror-numbers/?envType=daily-question&envId=2025-06-23

        :type k: int
        :type n: int
        :rtype: int
        '''

        def mirror(n, base, odd):
            result = n
            if odd:
                n //= base # remove last digit

            while n:
                result = result * base + n % base
                n //= base

            return result

        def generate(base): # generate palindrome, not a set amount --> yield
            prefix_num, total = [1] * 2, [base] * 2
            odd = 1

            while True:
                x = mirror(prefix_num[odd], base, odd)
                prefix_num[odd] += 1

                if prefix_num[odd] == total[odd]:
                    total[odd] *= base
                    odd = (odd + 1) % 2 # switch odd

                yield x

        def find_k_mirror_number(gen_base_k_palindromes):
            while True:
                candidate_num = next(gen_base_k_palindromes) # this number is already a palindrome in base k, and it is a base 10 integer

                s_candidate = str(candidate_num)

                if s_candidate == s_candidate[::-1]:
                    return candidate_num

        base1 = k

        gen_k_palindromes = generate(base1)
        return sum(find_k_mirror_number(gen_k_palindromes) for _ in range(n))

    main = kMirror

class Solution_3307(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3307, 'Hard')

    main = None

    def kthCharacter(self, k, operations):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-the-k-th-character-in-string-game-i/?envType=daily-question&envId=2025-07-03

        :type k: int
        :rtype: str
        '''

        '''
        See 'easy' problem 3304, this one just adds an extra condition for when operation[i] == 1.
        '''

        x = bin(k - 1) # how many shifts have happened, represent in binary

        count = 0

        for i, c in enumerate(reversed(x[2:])):
            if c == '1' and operations[i] == 1: # only if the operation is 1
                count += 1

        return chr(count % 26 + ord('a')) # mod isn't needed since the length constraint

    main = kthCharacter

class Solution_3333(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3333, 'Hard')

    main = None

    def possibleStringCount(self, word, k):
        '''
        Author: Kevin Zhu (used AI for dp hints)
        Link: https://leetcode.com/problems/find-the-original-typed-string-ii/?envType=daily-question&envId=2025-07-02

        :type word: str
        :type k: int
        :rtype: int
        '''

        MOD = 10 ** 9 + 7

        # count lengths of runs
        lengths = []
        prev_char = None

        for char in word:
            if char == prev_char:
                lengths[-1] += 1  # current run

            else:
                lengths.append(1)  # new run
                prev_char = char

        num_runs = len(lengths)

        total_combinations = 1
        for length in lengths:
            total_combinations = (total_combinations * length) % MOD

        if num_runs >= k: # no extra repetitions needed
            return total_combinations

        necessary = k - num_runs

        dp = [0] * necessary
        dp[0] = 1

        # use dynamic programming to find invalid solutions: ones that don't meet the length requirement
        for length in lengths:
            # prefix sums
            prefix_sums = [0] * (necessary + 1)
            for j in range(necessary):
                prefix_sums[j + 1] = (prefix_sums[j] + dp[j]) % MOD

            for j in range(necessary):
                lower_bound = j - (length - 1)
                if lower_bound <= 0:
                    dp[j] = prefix_sums[j + 1]

                else:
                    dp[j] = (prefix_sums[j + 1] - prefix_sums[lower_bound]) % MOD

        invalid_combinations = sum(dp) % MOD

        return (total_combinations - invalid_combinations) % MOD

    main = possibleStringCount

class Solution_3373(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3373, 'Hard')

    main = None

    def maxTargetNodes(self, edges1, edges2):
        '''
        Explanation for the solution:

        First, a graph is built from the edges provided for both trees.
        The graph is represented as an adjacency list (similar to 28th).
        Then, we make the parities of each tree. It determines if it is on the odd or even level.
        We use the current parity and then send the opposite parity to the next level in the DFS.
        Finally, we calculate the maximum number of target nodes based on the parity of each node.
        The amount of 'even' parity nodes is the same as the amount of nodes in Tree 1 with the same parity.
        Then, it is added to the best possible solution from Tree 2, since we can determine the node connection.
        '''

        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-ii/?envType=daily-question&envId=2025-05-29

        :type edges1: List[List[int]]
        :type edges2: List[List[int]]
        :rtype: List[int]
        '''

        def build_graph(edges, n):
            graph = [[] for _ in range(n)]
            for u, v in edges:
                graph[u].append(v)
                graph[v].append(u)

            return graph

        def dfs(graph, node, parent, parity, is_even):
            count = 1 if is_even else 0
            parity[node] = is_even

            for neighbor in graph[node]:
                if neighbor != parent:
                    count += dfs(graph, neighbor, node, parity, not is_even)

            return count

        n1 = len(edges1) + 1
        n2 = len(edges2) + 1

        graph1 = build_graph(edges1, n1)
        graph2 = build_graph(edges2, n2)

        parity1 = [False] * n1
        parity2 = [False] * n2

        even_count1 = dfs(graph1, 0, -1, parity1, True)
        even_count2 = dfs(graph2, 0, -1, parity2, True)

        odd_count1 = n1 - even_count1
        odd_count2 = n2 - even_count2

        result = []
        best = max(even_count2, odd_count2)

        for i in range(n1):
            if parity1[i]:
                result.append(even_count1 + best)

            else:
                result.append(odd_count1 + best)

        return result

    main = maxTargetNodes

MOD = 10 ** 9 + 7
MAX_N = 10 ** 5

fact = [1] * MAX_N
inv_fact = [1] * MAX_N
_precomputed = False

def _power(base, exp):
    res = 1
    base %= MOD
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % MOD
        base = (base * base) % MOD
        exp //= 2
    return res

def _nCr_mod_p(n_val, r_val):
    global _precomputed
    if not _precomputed:
        for i in range(1, MAX_N):
            fact[i] = (fact[i-1] * i) % MOD

        inv_fact[MAX_N - 1] = _power(fact[MAX_N - 1], MOD - 2)

        for i in range(MAX_N - 2, -1, -1):
            inv_fact[i] = (inv_fact[i+1] * (i+1)) % MOD

        _precomputed = True

    if r_val < 0 or r_val > n_val:
        return 0
    if r_val == 0 or r_val == n_val:
        return 1

    numerator = fact[n_val]
    denominator = (inv_fact[r_val] * inv_fact[n_val - r_val]) % MOD
    return (numerator * denominator) % MOD

class Solution_3405:
    def __init__(self):
        super().__init__('Google Gemini / Kevin Zhu', 3405, 'Hard')

    main = None

    def countGoodArrays(self, n, m, k):
        '''
        Extra Functions

        MOD = 10 ** 9 + 7
        MAX_N = 10 ** 5

        fact = [1] * MAX_N
        inv_fact = [1] * MAX_N
        _precomputed = False

        def _power(base, exp):
            res = 1
            base %= MOD
            while exp > 0:
                if exp % 2 == 1:
                    res = (res * base) % MOD
                base = (base * base) % MOD
                exp //= 2
            return res

        def _nCr_mod_p(n_val, r_val):
            global _precomputed
            if not _precomputed:
                for i in range(1, MAX_N):
                    fact[i] = (fact[i-1] * i) % MOD

                inv_fact[MAX_N - 1] = _power(fact[MAX_N - 1], MOD - 2)

                for i in range(MAX_N - 2, -1, -1):
                    inv_fact[i] = (inv_fact[i+1] * (i+1)) % MOD

                _precomputed = True

            if r_val < 0 or r_val > n_val:
                return 0
            if r_val == 0 or r_val == n_val:
                return 1

            numerator = fact[n_val]
            denominator = (inv_fact[r_val] * inv_fact[n_val - r_val]) % MOD
            return (numerator * denominator) % MOD
        '''

        '''
        Author: Kevin Zhu, used Google Gemini
        Link: https://leetcode.com/problems/count-the-number-of-arrays-with-k-matching-adjacent-elements/?envType=daily-question&envId=2025-06-17

        :type n: int
        :type m: int
        :type k: int
        :rtype: int
        '''

        if m == 1:
            return 1 if k == n - 1 else 0

        combinations = _nCr_mod_p(n - 1, k)
        first_element_choices = m
        non_matching_count = (n - 1) - k
        non_matching_choices = _power(m - 1, non_matching_count)

        ans = (combinations * first_element_choices) % MOD
        ans = (ans * non_matching_choices) % MOD

        return ans

    main = countGoodArrays

class Solution_3445(Solution):
    def __init__(self):
        super().__init__('Google Gemini', 3445, 'Hard')

    main = None

    def maxDifference(self, s, k):
        '''
        Author: Google Gemini --> this one was just too hard!!
        Link: https://leetcode.com/problems/maximum-difference-between-even-and-odd-frequency-ii/?envType=daily-question&envId=2025-06-11

        :type s: str
        :type k: int
        :rtype: int

        Gemini Explanation:
        Core Idea: Sliding Window with Prefix Sums and State-Based Dynamic Programming
        The problem involves substrings and their properties, which immediately suggests a sliding window approach.
        Since we need to calculate frequencies efficiently within these windows, prefix sums are ideal.
        The tricky part is the parity (odd/even) and minimum value (>= 1) constraints on frequencies, which require a clever way to keep track of previous window start states.
        This leads to a form of dynamic programming or state compression where we store minimum values for specific 'left-side' states.

        gl understanding this one
        '''

        n = len(s)
        digits = [str(i) for i in range(5)]

        max_overall_diff = -float('inf')

        for char_a in digits:
            for char_b in digits:
                if char_a == char_b:
                    continue

                prefix_a = [0] * (n + 1)
                prefix_b = [0] * (n + 1) # for the i + 1

                for i in range(n):
                    prefix_a[i + 1] = prefix_a[i] + (1 if s[i] == char_a else 0)
                    prefix_b[i + 1] = prefix_b[i] + (1 if s[i] == char_b else 0)

                min_state_values = [[[ (float('inf'), 0) ] * 3 for _ in range(2)] for _ in range(2)] # it's literally a 3D array in this sort of problem ........

                min_state_values[0][0][0] = (0, 0)

                current_pair_max_diff = -float('inf')

                for right in range(n):
                    # 1. Update `min_state_values` with the new 'L' candidate that becomes valid
                    # The new `L` candidate is `right - k + 1`. This `L` represents `s[L]` as the start of a window.
                    # This update must happen *before* we try to use this `L` for the current `right` pointer.
                    # It becomes valid for forming windows of length >= k.

                    l_candidate_idx = right - k + 1
                    if l_candidate_idx >= 0: # Ensure L is a valid index for prefix sums
                        current_pa_L = prefix_a[l_candidate_idx]
                        current_pb_L = prefix_b[l_candidate_idx]

                        pa_L_parity = current_pa_L % 2
                        pb_L_parity = current_pb_L % 2

                        pb_L_cat = 0
                        if current_pb_L == 1:
                            pb_L_cat = 1
                        elif current_pb_L >= 2:
                            pb_L_cat = 2

                        val_to_store = (current_pa_L - current_pb_L, current_pb_L)

                        # Update if this `val_to_store` has a smaller (P_A[L] - P_B[L])
                        # The tuple comparison `min((a,b), (c,d))` in Python compares `a` vs `c` first, then `b` vs `d`.
                        # This works correctly for minimizing the first element.
                        min_state_values[pa_L_parity][pb_L_parity][pb_L_cat] = \
                            min(min_state_values[pa_L_parity][pb_L_parity][pb_L_cat], val_to_store)

                    # 2. Process the current window ending at `right`
                    # We only consider windows of length at least `k`.
                    if right + 1 < k:
                        continue

                    current_pa_R = prefix_a[right+1]
                    current_pb_R = prefix_b[right+1]

                    # Determine the required parities for `P_A[L]` and `P_B[L]`
                    # so that freq(a) is odd and freq(b) is even in the substring.
                    req_pa_L_parity = (current_pa_R % 2) ^ 1 # If P_A[R+1] is odd, P_A[L] must be even. If even, P_A[L] must be odd.
                    req_pb_L_parity = current_pb_R % 2      # If P_B[R+1] is odd, P_B[L] must be odd. If even, P_B[L] must be even.

                    # Iterate through all 3 possible `pb_L_value_category` states (0, 1, or >=2)
                    # to find the `L` that minimizes (P_A[L] - P_B[L]) and satisfies conditions.
                    for pb_L_cat in range(3):

                        min_tuple = min_state_values[req_pa_L_parity][req_pb_L_parity][pb_L_cat]
                        min_diff_val_L = min_tuple[0]
                        corresponding_pb_L = min_tuple[1]

                        if min_diff_val_L == float('inf'):
                            continue # No valid `L` found yet for this specific state.

                        # Reconstruct freq(a) and freq(b) for the substring s[L...right]
                        # P_A[L] = (P_A[L] - P_B[L]) + P_B[L] = min_diff_val_L + corresponding_pb_L
                        freq_a_substring = current_pa_R - (min_diff_val_L + corresponding_pb_L)
                        freq_b_substring = current_pb_R - corresponding_pb_L

                        # Final check: `freq(b)` must be at least 2.
                        # Parity checks are implicitly handled by selecting `req_pa_L_parity` and `req_pb_L_parity`.
                        if freq_b_substring >= 2:
                            # This is a valid substring. Update the max difference for the current (a, b) pair.
                            current_pair_max_diff = max(current_pair_max_diff, freq_a_substring - freq_b_substring)

                # After iterating through all 'right' for the current (a, b) pair, update the overall max.
                max_overall_diff = max(max_overall_diff, current_pair_max_diff)

        # According to the problem statement, a valid substring always exists.
        # So `max_overall_diff` should not remain -inf.
        return max_overall_diff

    main = maxDifference