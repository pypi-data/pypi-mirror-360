def fib(n):
    x,y=0,1
    print(x, y, end=" ")
    for i in range(n):
        print(x+y, end=" ")
        temp = x
        x = y
        y = temp + y

def fibeth(n):
    x,y=0,1
    o=0
    for i in range(n):
        o=x+y
        temp = x
        x = y
        y = temp + y
    return o

def fact(n):
    prod=1
    for i in range(1,n+1):
        prod = prod*i
    return(prod)

def summer(n):
    summerifier=0
    for i in range(0,n+1):
        summerifier = summerifier+i
    return(summerifier)
