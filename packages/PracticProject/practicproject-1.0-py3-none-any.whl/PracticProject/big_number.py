def comparison(x, y):
    x = str(x)
    y = str(y)
    if len(x) != 0 and len(y)!= 0:
        if len(x) == len(y):
            for i in range(0, len(x)):
                if x[i] > y[i]:
                    return(x)
                    break
                elif x[i] < y[i]:
                    return(y)
                    break
                elif i == len(x)-1:
                    return(x,y)
        else:
            if len(x) > len(y):
                return(x)
            else:
                return(y)

def summ(x, y):
    x = str(x)
    y = str(y)
    n = min(len(x), len(y))
    ost = 0
    c = ''
    for i in range(1,n+1):
        i = 0 - i
        d = str(int(x[i])+ int(y[i])+ int(ost))
        c = d[-1] + c
        ost = 0
        if len(d) == 2:
            ost = d[0]
    if len(x) == len(y):
        if ost!=0:
            c = '1' + c
    elif len(x) > len(y):
        c = str(int(x[:(i)])+int(ost)) + c
    else:
        c = str(int(y[:(i)])+int(ost)) + c
    return(c)
def subtraction(x, y):
    x = str(x)
    y = str(y)
    n = min(len(x), len(y))
    ost = 0
    c = ''
    if x>y:
        for i in range(1,n+1):
            i = 0 - i
            d = str(int(x[i])- int(y[i])- int(ost))
            c = d[-1] + c
            ost = 0
            if len(d) == 2:
                ost = d[0]
        c = str(int(x[:(i)])-int(ost)) + c
    if x<y:
        for i in range(1,n+1):
            i = 0 - i
            d = str(int(y[i])- int(x[i])- int(ost))
            c = d[-1] + c
            ost = 0
            if len(d) == 2:
                ost = d[0]
        c = '-' + str(int(y[:(i)])-int(ost)) + c
    if c == '': c = 0
    return(c)
