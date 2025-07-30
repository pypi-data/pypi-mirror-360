import inspect
import textwrap

class Solution:
    def __init__(self, author, number, difficulty):
        self.author = author
        self.number = number
        self.difficulty = difficulty

    def __str__(self):
        return f'KZLeet Solution \'({type(self)})\' for LeetCode problem {self.number} by {self.author}. Problem difficulty: {self.difficulty}.\n{textwrap.dedent(inspect.getsource(self.main))}'

    def main(self, *args):
        '''
        Main method of the solution class.
        Override this method in subclasses to implement the solution logic.
        Define def solution_func(...): -> and set main = solution.
        This is to keep the original function name the same and still have a unified method.
        '''

        raise NotImplementedError('Subclasses should implement this method; set it equal to the solution.')