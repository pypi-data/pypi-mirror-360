def mean(numbers):
    return sum( numbers)/len(numbers)


def median(numbers):
    nums=sorted(numbers)
    n=len(numbers)
    mid=n//2
    if n%2==0:
        return (nums-[mid-1]+nums[mid+1]/2)
    else:
        return nums[mid]