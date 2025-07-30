# mememo 1.1 STABLE
from collections import Counter

def mean(mean_list):
    if len(mean_list) == 1:
        raise Exception('MathError: Must have 2 or more numbers in a list to find mean') # checks if < 1
    
    return sum(mean_list) / len(mean_list) # returns the mean


def median(median_list):
    if len(median_list) == 1:
        raise ValueError('MathError: Must have 2 or more numbers in a list to find median')
    
    median_list.sort()
    
    if len(median_list) % 2 != 0:
        median_list.sort(reverse=True)
        return (median_list[1] / 2) + 1
    else:
        return mean([len(median_list) / 2, (len(median_list) / 2) + 1]) # returns the middle number

def mode(mode_list):
    count = Counter(mode_list)
    max_freq = max(count.values())
    modes = [num for num, freq in count.items() if freq == max_freq]
    return modes
