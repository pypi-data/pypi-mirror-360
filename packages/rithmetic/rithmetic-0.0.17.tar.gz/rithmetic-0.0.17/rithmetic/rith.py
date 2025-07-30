def welcome():
    print('\n')
    print('Welcome to __\'rithmetic__')
    print('\n')


def ver():
    print('\n')
    print('rithmetic-0.0.17')
    print('\n')


def decphandle(num):
    val = []
    c = 0
    snum = None
    num = str(num)
    for n in num:
        val.append(n)
    for n in val:
        if n == '.':
            c = c + 1
            val.remove(n)
        else:
            continue
    if c > 1:
        return 'Invalid number'
    else:
        for n in val:
            if snum is None:
                snum = n
            else:
                snum = snum + n
        return snum


def signhandle(sinum):
    sinum = str(sinum)
    if sinum[0] == '-' or sinum[0] == '+':
        val = []
        ans = None
        for i in sinum:
            val.append(i)
        val.remove(val[0])
        for i in val:
            if ans is None:
                ans = i
            else:
                ans = ans + i
        for i in ans:
            if i == '-' or i == '+':
                return 'Invalid number'
            else:
                continue
        return ans
    else:
        for i in sinum:
            if i == '-' or i == '+':
                return 'Invalid number'
            else:
                continue
        return sinum


def fracbtodec(num, frac, base):
    num = str(num)
    frac = str(frac)
    pow = 1
    b = 0
    for n in frac:
        b = b + (int(n) * (1/(int(base) ** pow)))
        pow = pow + 1
    diff = int(base) - 10
    N = int(int(num) / 10)
    val = (N * diff)
    p = 1
    while N != 0:
        N = int(N / 10)
        val = val + (N * diff * (int(base) ** p))
        p = p + 1
    a = int(num) + val
    a = str(a)
    b = str(b)
    b1, b2 = b.split('.')
    b2 = '.' + b2
    ans = a + b2
    ans = float(ans)
    return ans


def frac11todec(num, frac):
    num = str(num)
    frac = str(frac)
    flist = []
    for n in frac:
        if n == 'A' or n == 'a':
            n = '10'
            flist.append(n)
        else:
            flist.append(n)
    pow = 1
    b = 0
    for n in flist:
        b = b + (int(n) * (1/(11 ** pow)))
        pow = pow + 1
    val = []
    c = 0
    for n in num:
        val.append(num[c])
        c = c + 1
    c = 0
    for p in val:
        if val[c] == 'A' or val[c] == 'a':
            val[c] = 10
            c = c + 1
        else:
            val[c] = int(val[c])
            c = c + 1
    c = 0
    l = len(val)
    a = 0
    for r in val:
        a = a + (val[c] * (11 ** (l - 1)))
        c = c + 1
        l = l - 1
    a = str(a)
    b = str(b)
    b1, b2 = b.split('.')
    b2 = '.' + b2
    ans = a + b2
    ans = float(ans)
    return ans


def frac12todec(num, frac):
    num = str(num)
    frac = str(frac)
    flist = []
    for n in frac:
        if n == 'A' or n == 'a':
            n = '10'
            flist.append(n)
        elif n == 'B' or n == 'b':
            n = '11'
            flist.append(n)
        else:
            flist.append(n)
    pow = 1
    b = 0
    for n in flist:
        b = b + (int(n) * (1/(12 ** pow)))
        pow = pow + 1
    val = []
    c = 0
    for n in num:
        val.append(num[c])
        c = c + 1
    c = 0
    for p in val:
        if val[c] == 'A' or val[c] == 'a':
            val[c] = 10
            c = c + 1
        elif val[c] == 'B' or val[c] == 'b':
            val[c] = 11
            c = c + 1
        else:
            val[c] = int(val[c])
            c = c + 1
    c = 0
    l = len(val)
    a = 0
    for r in val:
        a = a + (val[c] * (12 ** (l - 1)))
        c = c + 1
        l = l - 1
    a = str(a)
    b = str(b)
    b1, b2 = b.split('.')
    b2 = '.' + b2
    ans = a + b2
    ans = float(ans)
    return ans


def frac13todec(num, frac):
    num = str(num)
    frac = str(frac)
    flist = []
    for n in frac:
        if n == 'A' or n == 'a':
            n = '10'
            flist.append(n)
        elif n == 'B' or n == 'b':
            n = '11'
            flist.append(n)
        elif n == 'C' or n == 'c':
            n = '12'
            flist.append(n)
        else:
            flist.append(n)
    pow = 1
    b = 0
    for n in flist:
        b = b + (int(n) * (1/(13 ** pow)))
        pow = pow + 1
    val = []
    c = 0
    for n in num:
        val.append(num[c])
        c = c + 1
    c = 0
    for p in val:
        if val[c] == 'A' or val[c] == 'a':
            val[c] = 10
            c = c + 1
        elif val[c] == 'B' or val[c] == 'b':
            val[c] = 11
            c = c + 1
        elif val[c] == 'C' or val[c] == 'c':
            val[c] = 12
            c = c + 1
        else:
            val[c] = int(val[c])
            c = c + 1
    c = 0
    l = len(val)
    a = 0
    for r in val:
        a = a + (val[c] * (13 ** (l - 1)))
        c = c + 1
        l = l - 1
    a = str(a)
    b = str(b)
    b1, b2 = b.split('.')
    b2 = '.' + b2
    ans = a + b2
    ans = float(ans)
    return ans


def frac14todec(num, frac):
    num = str(num)
    frac = str(frac)
    flist = []
    for n in frac:
        if n == 'A' or n == 'a':
            n = '10'
            flist.append(n)
        elif n == 'B' or n == 'b':
            n = '11'
            flist.append(n)
        elif n == 'C' or n == 'c':
            n = '12'
            flist.append(n)
        elif n == 'D' or n == 'd':
            n = '13'
            flist.append(n)
        else:
            flist.append(n)
    pow = 1
    b = 0
    for n in flist:
        b = b + (int(n) * (1/(14 ** pow)))
        pow = pow + 1
    val = []
    c = 0
    for n in num:
        val.append(num[c])
        c = c + 1
    c = 0
    for p in val:
        if val[c] == 'A' or val[c] == 'a':
            val[c] = 10
            c = c + 1
        elif val[c] == 'B' or val[c] == 'b':
            val[c] = 11
            c = c + 1
        elif val[c] == 'C' or val[c] == 'c':
            val[c] = 12
            c = c + 1
        elif val[c] == 'D' or val[c] == 'd':
            val[c] = 13
            c = c + 1
        else:
            val[c] = int(val[c])
            c = c + 1
    c = 0
    l = len(val)
    a = 0
    for r in val:
        a = a + (val[c] * (14 ** (l - 1)))
        c = c + 1
        l = l - 1
    a = str(a)
    b = str(b)
    b1, b2 = b.split('.')
    b2 = '.' + b2
    ans = a + b2
    ans = float(ans)
    return ans


def frac15todec(num, frac):
    num = str(num)
    frac = str(frac)
    flist = []
    for n in frac:
        if n == 'A' or n == 'a':
            n = '10'
            flist.append(n)
        elif n == 'B' or n == 'b':
            n = '11'
            flist.append(n)
        elif n == 'C' or n == 'c':
            n = '12'
            flist.append(n)
        elif n == 'D' or n == 'd':
            n = '13'
            flist.append(n)
        elif n == 'E' or n == 'e':
            n = '14'
            flist.append(n)
        else:
            flist.append(n)
    pow = 1
    b = 0
    for n in flist:
        b = b + (int(n) * (1/(15 ** pow)))
        pow = pow + 1
    val = []
    c = 0
    for n in num:
        val.append(num[c])
        c = c + 1
    c = 0
    for p in val:
        if val[c] == 'A' or val[c] == 'a':
            val[c] = 10
            c = c + 1
        elif val[c] == 'B' or val[c] == 'b':
            val[c] = 11
            c = c + 1
        elif val[c] == 'C' or val[c] == 'c':
            val[c] = 12
            c = c + 1
        elif val[c] == 'D' or val[c] == 'd':
            val[c] = 13
            c = c + 1
        elif val[c] == 'E' or val[c] == 'e':
            val[c] = 14
            c = c + 1
        else:
            val[c] = int(val[c])
            c = c + 1
    c = 0
    l = len(val)
    a = 0
    for r in val:
        a = a + (val[c] * (15 ** (l - 1)))
        c = c + 1
        l = l - 1
    a = str(a)
    b = str(b)
    b1, b2 = b.split('.')
    b2 = '.' + b2
    ans = a + b2
    ans = float(ans)
    return ans


def frac16todec(num, frac):
    num = str(num)
    frac = str(frac)
    flist = []
    for n in frac:
        if n == 'A' or n == 'a':
            n = '10'
            flist.append(n)
        elif n == 'B' or n == 'b':
            n = '11'
            flist.append(n)
        elif n == 'C' or n == 'c':
            n = '12'
            flist.append(n)
        elif n == 'D' or n == 'd':
            n = '13'
            flist.append(n)
        elif n == 'E' or n == 'e':
            n = '14'
            flist.append(n)
        elif n == 'F' or n == 'f':
            n = '15'
            flist.append(n)
        else:
            flist.append(n)
    pow = 1
    b = 0
    for n in flist:
        b = b + (int(n) * (1/(16 ** pow)))
        pow = pow + 1
    val = []
    c = 0
    for n in num:
        val.append(num[c])
        c = c + 1
    c = 0
    for p in val:
        if val[c] == 'A' or val[c] == 'a':
            val[c] = 10
            c = c + 1
        elif val[c] == 'B' or val[c] == 'b':
            val[c] = 11
            c = c + 1
        elif val[c] == 'C' or val[c] == 'c':
            val[c] = 12
            c = c + 1
        elif val[c] == 'D' or val[c] == 'd':
            val[c] = 13
            c = c + 1
        elif val[c] == 'E' or val[c] == 'e':
            val[c] = 14
            c = c + 1
        elif val[c] == 'F' or val[c] == 'f':
            val[c] = 15
            c = c + 1
        else:
            val[c] = int(val[c])
            c = c + 1
    c = 0
    l = len(val)
    a = 0
    for r in val:
        a = a + (val[c] * (16 ** (l - 1)))
        c = c + 1
        l = l - 1
    a = str(a)
    b = str(b)
    b1, b2 = b.split('.')
    b2 = '.' + b2
    ans = a + b2
    ans = float(ans)
    return ans


def fracdectob(num, frac, base):
    num = str(num)
    frac = '0.' + str(frac)
    check = frac
    val = []
    count = 0
    b = 0
    stage = None
    while b != float(check):
        pow = 1
        b = 0
        frac = float(frac) * int(base)
        frac = str(frac)
        try:
            frac1, frac2 = frac.split('.')
        except:
            break
        val.append(frac1)
        frac = '0.' + frac2
        for n in val:
            b = b + (int(n) * (1 / (int(base) ** pow)))
            pow = pow + 1
        count = count + 1
        if count == 100:
            break
        else:
            continue
    for n in val:
        if stage is None:
            stage = n
        else:
            stage = stage + n
    diff = 10 - int(base)
    N = int(int(num) / int(base))
    val = (N * diff)
    p = 1
    while N != 0:
        N = int(N / int(base))
        val = val + (N * diff * (10 ** p))
        p = p + 1
    ans = int(num) + val
    ans = str(ans)
    stage = '.' + stage
    result = ans + stage
    return result


def fracdectob11(num, frac):
    num = str(num)
    frac = '0.' + str(frac)
    check = frac
    val = []
    count = 0
    b = 0
    stage = None
    while b != float(check):
        pow = 1
        b = 0
        frac = float(frac) * 11
        frac = str(frac)
        try:
            frac1, frac2 = frac.split('.')
        except:
            break
        val.append(frac1)
        frac = '0.' + frac2
        for n in val:
            b = b + (int(n) * (1 / (11 ** pow)))
            pow = pow + 1
        count = count + 1
        if count == 100:
            break
        else:
            continue
    for n in val:
        if n == '10':
            n = 'A'
        if stage is None:
            stage = n
        else:
            stage = stage + n
    val1 = []
    Q = int(int(num) / 11)
    M = int(num) % 11
    val1.append(M)
    while Q > 0:
        M = Q % 11
        val1.append(M)
        Q = int(Q / 11)
    val1.reverse()
    t = 0
    for i in val1:
        val1[t] = str(val1[t])
        if val1[t] == '10':
            val1[t] = 'A'
        t = t + 1
    n = 0
    ans = None
    for i in val1:
        if ans is None:
            ans = val1[n]
        else:
            ans = ans + val1[n]
        n = n + 1
    ans = str(ans)
    stage = '.' + stage
    result = ans + stage
    return result


def fracdectob12(num, frac):
    num = str(num)
    frac = '0.' + str(frac)
    check = frac
    val = []
    count = 0
    b = 0
    stage = None
    while b != float(check):
        pow = 1
        b = 0
        frac = float(frac) * 12
        frac = str(frac)
        try:
            frac1, frac2 = frac.split('.')
        except:
            break
        val.append(frac1)
        frac = '0.' + frac2
        for n in val:
            b = b + (int(n) * (1 / (12 ** pow)))
            pow = pow + 1
        count = count + 1
        if count == 100:
            break
        else:
            continue
    for n in val:
        if n == '10':
            n = 'A'
        elif n == '11':
            n = 'B'
        if stage is None:
            stage = n
        else:
            stage = stage + n
    val1 = []
    Q = int(int(num) / 12)
    M = int(num) % 12
    val1.append(M)
    while Q > 0:
        M = Q % 12
        val1.append(M)
        Q = int(Q / 12)
    val1.reverse()
    t = 0
    for i in val1:
        val1[t] = str(val1[t])
        if val1[t] == '10':
            val1[t] = 'A'
        elif val1[t] == '11':
            val1[t] = 'B'
        t = t + 1
    n = 0
    ans = None
    for i in val1:
        if ans is None:
            ans = val1[n]
        else:
            ans = ans + val1[n]
        n = n + 1
    ans = str(ans)
    stage = '.' + stage
    result = ans + stage
    return result


def fracdectob13(num, frac):
    num = str(num)
    frac = '0.' + str(frac)
    check = frac
    val = []
    count = 0
    b = 0
    stage = None
    while b != float(check):
        pow = 1
        b = 0
        frac = float(frac) * 13
        frac = str(frac)
        try:
            frac1, frac2 = frac.split('.')
        except:
            break
        val.append(frac1)
        frac = '0.' + frac2
        for n in val:
            b = b + (int(n) * (1 / (13 ** pow)))
            pow = pow + 1
        count = count + 1
        if count == 100:
            break
        else:
            continue
    for n in val:
        if n == '10':
            n = 'A'
        elif n == '11':
            n = 'B'
        elif n == '12':
            n = 'C'
        if stage is None:
            stage = n
        else:
            stage = stage + n
    val1 = []
    Q = int(int(num) / 13)
    M = int(num) % 13
    val1.append(M)
    while Q > 0:
        M = Q % 13
        val1.append(M)
        Q = int(Q / 13)
    val1.reverse()
    t = 0
    for i in val1:
        val1[t] = str(val1[t])
        if val1[t] == '10':
            val1[t] = 'A'
        elif val1[t] == '11':
            val1[t] = 'B'
        elif val1[t] == '12':
            val1[t] = 'C'
        t = t + 1
    n = 0
    ans = None
    for i in val1:
        if ans is None:
            ans = val1[n]
        else:
            ans = ans + val1[n]
        n = n + 1
    ans = str(ans)
    stage = '.' + stage
    result = ans + stage
    return result


def fracdectob14(num, frac):
    num = str(num)
    frac = '0.' + str(frac)
    check = frac
    val = []
    count = 0
    b = 0
    stage = None
    while b != float(check):
        pow = 1
        b = 0
        frac = float(frac) * 14
        frac = str(frac)
        try:
            frac1, frac2 = frac.split('.')
        except:
            break
        val.append(frac1)
        frac = '0.' + frac2
        for n in val:
            b = b + (int(n) * (1 / (14 ** pow)))
            pow = pow + 1
        count = count + 1
        if count == 100:
            break
        else:
            continue
    for n in val:
        if n == '10':
            n = 'A'
        elif n == '11':
            n = 'B'
        elif n == '12':
            n = 'C'
        elif n == '13':
            n = 'D'
        if stage is None:
            stage = n
        else:
            stage = stage + n
    val1 = []
    Q = int(int(num) / 14)
    M = int(num) % 14
    val1.append(M)
    while Q > 0:
        M = Q % 14
        val1.append(M)
        Q = int(Q / 14)
    val1.reverse()
    t = 0
    for i in val1:
        val1[t] = str(val1[t])
        if val1[t] == '10':
            val1[t] = 'A'
        elif val1[t] == '11':
            val1[t] = 'B'
        elif val1[t] == '12':
            val1[t] = 'C'
        elif val1[t] == '13':
            val1[t] = 'D'
        t = t + 1
    n = 0
    ans = None
    for i in val1:
        if ans is None:
            ans = val1[n]
        else:
            ans = ans + val1[n]
        n = n + 1
    ans = str(ans)
    stage = '.' + stage
    result = ans + stage
    return result


def fracdectob15(num, frac):
    num = str(num)
    frac = '0.' + str(frac)
    check = frac
    val = []
    count = 0
    b = 0
    stage = None
    while b != float(check):
        pow = 1
        b = 0
        frac = float(frac) * 15
        frac = str(frac)
        try:
            frac1, frac2 = frac.split('.')
        except:
            break
        val.append(frac1)
        frac = '0.' + frac2
        for n in val:
            b = b + (int(n) * (1 / (15 ** pow)))
            pow = pow + 1
        count = count + 1
        if count == 100:
            break
        else:
            continue
    for n in val:
        if n == '10':
            n = 'A'
        elif n == '11':
            n = 'B'
        elif n == '12':
            n = 'C'
        elif n == '13':
            n = 'D'
        elif n == '14':
            n = 'E'
        if stage is None:
            stage = n
        else:
            stage = stage + n
    val1 = []
    Q = int(int(num) / 15)
    M = int(num) % 15
    val1.append(M)
    while Q > 0:
        M = Q % 15
        val1.append(M)
        Q = int(Q / 15)
    val1.reverse()
    t = 0
    for i in val1:
        val1[t] = str(val1[t])
        if val1[t] == '10':
            val1[t] = 'A'
        elif val1[t] == '11':
            val1[t] = 'B'
        elif val1[t] == '12':
            val1[t] = 'C'
        elif val1[t] == '13':
            val1[t] = 'D'
        elif val1[t] == '14':
            val1[t] = 'E'
        t = t + 1
    n = 0
    ans = None
    for i in val1:
        if ans is None:
            ans = val1[n]
        else:
            ans = ans + val1[n]
        n = n + 1
    ans = str(ans)
    stage = '.' + stage
    result = ans + stage
    return result


def fracdectob16(num, frac):
    num = str(num)
    frac = '0.' + str(frac)
    check = frac
    val = []
    count = 0
    b = 0
    stage = None
    while b != float(check):
        pow = 1
        b = 0
        frac = float(frac) * 16
        frac = str(frac)
        try:
            frac1, frac2 = frac.split('.')
        except:
            break
        val.append(frac1)
        frac = '0.' + frac2
        for n in val:
            b = b + (int(n) * (1 / (16 ** pow)))
            pow = pow + 1
        count = count + 1
        if count == 100:
            break
    for n in val:
        if n == '10':
            n = 'A'
        elif n == '11':
            n = 'B'
        elif n == '12':
            n = 'C'
        elif n == '13':
            n = 'D'
        elif n == '14':
            n = 'E'
        elif n == '15':
            n = 'F'
        if stage is None:
            stage = n
        else:
            stage = stage + n
    val1 = []
    Q = int(int(num) / 16)
    M = int(num) % 16
    val1.append(M)
    while Q > 0:
        M = Q % 16
        val1.append(M)
        Q = int(Q / 16)
    val1.reverse()
    t = 0
    for i in val1:
        val1[t] = str(val1[t])
        if val1[t] == '10':
            val1[t] = 'A'
        elif val1[t] == '11':
            val1[t] = 'B'
        elif val1[t] == '12':
            val1[t] = 'C'
        elif val1[t] == '13':
            val1[t] = 'D'
        elif val1[t] == '14':
            val1[t] = 'E'
        elif val1[t] == '15':
            val1[t] = 'F'
        t = t + 1
    n = 0
    ans = None
    for i in val1:
        if ans is None:
            ans = val1[n]
        else:
            ans = ans + val1[n]
        n = n + 1
    ans = str(ans)
    stage = '.' + stage
    result = ans + stage
    return result


def chknum(num):
    guide =['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'a', 'b', 'c', 'd', 'e', 'f']
    num = str(num)
    num = signhandle(num)
    if num == 'Invalid number':
        return num
    else:
        num = decphandle(num)
        if num == 'Invalid number':
            return num
        else:
            for i in num:
                if i in guide:
                    continue
                else:
                    return 'Invalid number'
            return num


def chk2(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 2:
                return False
            else:
                i = i + 1
        return True


def chk3(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 3:
                return False
            else:
                i = i + 1
        return True


def chk4(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 4:
                return False
            else:
                i = i + 1
        return True


def chk5(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 5:
                return False
            else:
                i = i + 1
        return True


def chk6(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 6:
                return False
            else:
                i = i + 1
        return True


def chk7(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 7:
                return False
            else:
                i = i + 1
        return True


def chk8(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 8:
                return False
            else:
                i = i + 1
        return True


def chk9(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 9:
                return False
            else:
                i = i + 1
        return True


def chk10(num):
    i = 0
    num = str(num)
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for n in num:
            try:
                int(n)
            except:
                return False
            if int(num[i]) >= 10:
                return False
            else:
                i = i + 1
        return True


def chksub(num, base):
    i = 0
    snum = str(num)
    snum = chknum(snum)
    if snum == 'Invalid number':
        return snum
    else:
        try:
            base = int(base)
        except:
            return 'Invalid base value'
        if base < 2 or base > 10:
            return 'Invalid base value'
        else:
            for n in snum:
                try:
                    int(n)
                except:
                    return False
                if int(snum[i]) >= base:
                    return False
                else:
                    i = i + 1
            return True


def chk11(num):
    num = str(num)
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a']
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for i in num:
            if i in guide:
                continue
            else:
                return False
        return True


def chk12(num):
    num = str(num)
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a', 'B', 'b']
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for i in num:
            if i in guide:
                continue
            else:
                return False
        return True


def chk13(num):
    num = str(num)
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a', 'B', 'b', 'C', 'c']
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for i in num:
            if i in guide:
                continue
            else:
                return False
        return True


def chk14(num):
    num = str(num)
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd']
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for i in num:
            if i in guide:
                continue
            else:
                return False
        return True


def chk15(num):
    num = str(num)
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e']
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for i in num:
            if i in guide:
                continue
            else:
                return False
        return True


def chk16(num):
    num = str(num)
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f']
    num = chknum(num)
    if num == 'Invalid number':
        return num
    else:
        for i in num:
            if i in guide:
                continue
            else:
                return False
        return True


def chkbase(num, base):
    try:
        base = int(base)
    except:
        return 'Invalid base value'
    if base < 2 or base > 16:
        return 'Invalid base value'
    else:
        Bguide = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        num = str(num)
        if base in Bguide:
            result = chksub(num,base)
            return result
        elif base == 11:
            result = chk11(num)
            return result
        elif base == 12:
            result = chk12(num)
            return result
        elif base == 13:
            result = chk13(num)
            return result
        elif base == 14:
            result = chk14(num)
            return result
        elif base == 15:
            result = chk15(num)
            return result
        elif base == 16:
            result = chk16(num)
            return result


def b2todec(num):
    num = str(num)
    chk = chk2(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1,numd,2)
            return ans
        else:
            diff = 2 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (2 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def b3todec(num):
    num = str(num)
    chk = chk3(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1, numd, 3)
            return ans
        else:
            diff = 3 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (3 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def b4todec(num):
    num = str(num)
    chk = chk4(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1, numd, 4)
            return ans
        else:
            diff = 4 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (4 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def b5todec(num):
    num = str(num)
    chk = chk5(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1, numd, 5)
            return ans
        else:
            diff = 5 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (5 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def b6todec(num):
    num = str(num)
    chk = chk6(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1, numd, 6)
            return ans
        else:
            diff = 6 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (6 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def b7todec(num):
    num = str(num)
    chk = chk7(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1, numd, 7)
            return ans
        else:
            diff = 7 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (7 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def b8todec(num):
    num = str(num)
    chk = chk8(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1, numd, 8)
            return ans
        else:
            diff = 8 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (8 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def b9todec(num):
    num = str(num)
    chk = chk9(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracbtodec(num1, numd, 9)
            return ans
        else:
            diff = 9 - 10
            N = int(int(num) / 10)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 10)
                val = val + (N * diff * (9 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def subtodec(num, fromB):
    num = str(num)
    try:
        fromB = int(fromB)
    except:
        return 'Invalid base value'
    if fromB < 2 or fromB > 10:
        return 'Invalid base value'
    else:
        chk = chksub(num, fromB)
        if chk is False:
            return 'Invalid number'
        elif chk == 'Invalid base value':
            return chk
        elif chk == 'Invalid number':
            return chk
        else:
            for i in num:
                if i == '.':
                    c = True
                    break
                else:
                    c = False
            if c is True:
                num1, numd = num.split('.')
                ans = fracbtodec(num1, numd, fromB)
                return ans
            else:
                diff = fromB - 10
                N = int(int(num) / 10)
                val = (N * diff)
                p = 1
                while N != 0:
                    N = int(N / 10)
                    val = val + (N * diff * (fromB ** p))
                    p = p + 1
                ans = int(num) + val
                return ans


def b11todec(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk11(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = frac11todec(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return float(ans)
        else:
            val = []
            c = 0
            for n in num:
                val.append(num[c])
                c = c + 1
            c = 0
            for p in val:
                if val[c] == 'A' or val[c] == 'a':
                    val[c] = 10
                    c = c + 1
                else:
                    val[c] = int(val[c])
                    c = c + 1
            c = 0
            l = len(val)
            ans = 0
            for r in val:
                ans = ans + (val[c] * (11 ** (l - 1)))
                c = c + 1
                l = l - 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return int(ans)


def b12todec(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk12(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = frac12todec(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return float(ans)
        else:
            val = []
            c = 0
            for n in num:
                val.append(num[c])
                c = c + 1
            c = 0
            for p in val:
                if val[c] == 'A' or val[c] == 'a':
                    val[c] = 10
                    c = c + 1
                elif val[c] == 'B' or val[c] == 'b':
                    val[c] = 11
                    c = c + 1
                else:
                    val[c] = int(val[c])
                    c = c + 1
            c = 0
            l = len(val)
            ans = 0
            for r in val:
                ans = ans + (val[c] * (12 ** (l - 1)))
                c = c + 1
                l = l - 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return int(ans)


def b13todec(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk13(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = frac13todec(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return float(ans)
        else:
            val = []
            c = 0
            for n in num:
                val.append(num[c])
                c = c + 1
            c = 0
            for p in val:
                if val[c] == 'A' or val[c] == 'a':
                    val[c] = 10
                    c = c + 1
                elif val[c] == 'B' or val[c] == 'b':
                    val[c] = 11
                    c = c + 1
                elif val[c] == 'C' or val[c] == 'c':
                    val[c] = 12
                    c = c + 1
                else:
                    val[c] = int(val[c])
                    c = c + 1
            c = 0
            l = len(val)
            ans = 0
            for r in val:
                ans = ans + (val[c] * (13 ** (l - 1)))
                c = c + 1
                l = l - 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return int(ans)


def b14todec(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk14(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = frac14todec(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return float(ans)
        else:
            val = []
            c = 0
            for n in num:
                val.append(num[c])
                c = c + 1
            c = 0
            for p in val:
                if val[c] == 'A' or val[c] == 'a':
                    val[c] = 10
                    c = c + 1
                elif val[c] == 'B' or val[c] == 'b':
                    val[c] = 11
                    c = c + 1
                elif val[c] == 'C' or val[c] == 'c':
                    val[c] = 12
                    c = c + 1
                elif val[c] == 'D' or val[c] == 'd':
                    val[c] = 13
                    c = c + 1
                else:
                    val[c] = int(val[c])
                    c = c + 1
            c = 0
            l = len(val)
            ans = 0
            for r in val:
                ans = ans + (val[c] * (14 ** (l - 1)))
                c = c + 1
                l = l - 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return int(ans)


def b15todec(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk15(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = frac15todec(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return float(ans)
        else:
            val = []
            c = 0
            for n in num:
                val.append(num[c])
                c = c + 1
            c = 0
            for p in val:
                if val[c] == 'A' or val[c] == 'a':
                    val[c] = 10
                    c = c + 1
                elif val[c] == 'B' or val[c] == 'b':
                    val[c] = 11
                    c = c + 1
                elif val[c] == 'C' or val[c] == 'c':
                    val[c] = 12
                    c = c + 1
                elif val[c] == 'D' or val[c] == 'd':
                    val[c] = 13
                    c = c + 1
                elif val[c] == 'E' or val[c] == 'e':
                    val[c] = 14
                    c = c + 1
                else:
                    val[c] = int(val[c])
                    c = c + 1
            c = 0
            l = len(val)
            ans = 0
            for r in val:
                ans = ans + (val[c] * (15 ** (l - 1)))
                c = c + 1
                l = l - 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return int(ans)


def b16todec(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk16(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = frac16todec(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return float(ans)
        else:
            val = []
            c = 0
            for n in num:
                val.append(num[c])
                c = c + 1
            c = 0
            for p in val:
                if val[c] == 'A' or val[c] == 'a':
                    val[c] = 10
                    c = c + 1
                elif val[c] == 'B' or val[c] == 'b':
                    val[c] = 11
                    c = c + 1
                elif val[c] == 'C' or val[c] == 'c':
                    val[c] = 12
                    c = c + 1
                elif val[c] == 'D' or val[c] == 'd':
                    val[c] = 13
                    c = c + 1
                elif val[c] == 'E' or val[c] == 'e':
                    val[c] = 14
                    c = c + 1
                elif val[c] == 'F' or val[c] == 'f':
                    val[c] = 15
                    c = c + 1
                else:
                    val[c] = int(val[c])
                    c = c + 1
            c = 0
            l = len(val)
            ans = 0
            for r in val:
                ans = ans + (val[c] * (16 ** (l - 1)))
                c = c + 1
                l = l - 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return int(ans)


def dectob2(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 2)
            return ans
        else:
            diff = 10 - 2
            N = int(int(num) / 2)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 2)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectob3(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 3)
            return ans
        else:
            diff = 10 - 3
            N = int(int(num) / 3)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 3)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectob4(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 4)
            return ans
        else:
            diff = 10 - 4
            N = int(int(num) / 4)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 4)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectob5(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 5)
            return ans
        else:
            diff = 10 - 5
            N = int(int(num) / 5)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 5)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectob6(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 6)
            return ans
        else:
            diff = 10 - 6
            N = int(int(num) / 6)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 6)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectob7(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 7)
            return ans
        else:
            diff = 10 - 7
            N = int(int(num) / 7)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 7)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectob8(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 8)
            return ans
        else:
            diff = 10 - 8
            N = int(int(num) / 8)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 8)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectob9(num):
    num = str(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob(num1, numd, 9)
            return ans
        else:
            diff = 10 - 9
            N = int(int(num) / 9)
            val = (N * diff)
            p = 1
            while N != 0:
                N = int(N / 9)
                val = val + (N * diff * (10 ** p))
                p = p + 1
            ans = int(num) + val
            return ans


def dectosub(num, toB):
    try:
        toB = int(toB)
    except:
        return 'Invalid base value'
    if toB > 10 or toB < 2:
        return 'Invalid base value'
    else:
        num = str(num)
        chk = chk10(num)
        if chk is False:
            return 'Invalid number'
        elif chk == 'Invalid number':
            return chk
        else:
            for i in num:
                if i == '.':
                    c = True
                    break
                else:
                    c = False
            if c is True:
                num1, numd = num.split('.')
                ans = fracdectob(num1, numd, toB)
                return ans
            else:
                diff = 10 - toB
                N = int(int(num) / toB)
                val = (N * diff)
                p = 1
                while N != 0:
                    N = int(N / toB)
                    val = val + (N * diff * (10 ** p))
                    p = p + 1
                ans = int(num) + val
                return ans


def dectob11(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob11(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return ans
        else:
            val = []
            Q = int(int(num) / 11)
            M = int(num) % 11
            val.append(M)
            while Q > 0:
                M = Q % 11
                val.append(M)
                Q = int(Q / 11)
            val.reverse()
            t = 0
            for i in val:
                val[t] = str(val[t])
                if val[t] == '10':
                    val[t] = 'A'
                t = t + 1
            n = 0
            ans = None
            for i in val:
                if ans is None:
                    ans = val[n]
                else:
                    ans = ans + val[n]
                n = n + 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                return temp + ans


def dectob12(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob12(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return ans
        else:
            val = []
            Q = int(int(num) / 12)
            M = int(num) % 12
            val.append(M)
            while Q > 0:
                M = Q % 12
                val.append(M)
                Q = int(Q / 12)
            val.reverse()
            t = 0
            for i in val:
                val[t] = str(val[t])
                if val[t] == '10':
                    val[t] = 'A'
                elif val[t] == '11':
                    val[t] = 'B'
                t = t + 1
            n = 0
            ans = None
            for i in val:
                if ans is None:
                    ans = val[n]
                else:
                    ans = ans + val[n]
                n = n + 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                return temp + ans


def dectob13(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob13(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return ans
        else:
            val = []
            Q = int(int(num) / 13)
            M = int(num) % 13
            val.append(M)
            while Q > 0:
                M = Q % 13
                val.append(M)
                Q = int(Q / 13)
            val.reverse()
            t = 0
            for i in val:
                val[t] = str(val[t])
                if val[t] == '10':
                    val[t] = 'A'
                elif val[t] == '11':
                    val[t] = 'B'
                elif val[t] == '12':
                    val[t] = 'C'
                t = t + 1
            n = 0
            ans = None
            for i in val:
                if ans is None:
                    ans = val[n]
                else:
                    ans = ans + val[n]
                n = n + 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                return temp + ans


def dectob14(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob14(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return ans
        else:
            val = []
            Q = int(int(num) / 14)
            M = int(num) % 14
            val.append(M)
            while Q > 0:
                M = Q % 14
                val.append(M)
                Q = int(Q / 14)
            val.reverse()
            t = 0
            for i in val:
                val[t] = str(val[t])
                if val[t] == '10':
                    val[t] = 'A'
                elif val[t] == '11':
                    val[t] = 'B'
                elif val[t] == '12':
                    val[t] = 'C'
                elif val[t] == '13':
                    val[t] = 'D'
                t = t + 1
            n = 0
            ans = None
            for i in val:
                if ans is None:
                    ans = val[n]
                else:
                    ans = ans + val[n]
                n = n + 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                return temp + ans


def dectob15(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob15(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return ans
        else:
            val = []
            Q = int(int(num) / 15)
            M = int(num) % 15
            val.append(M)
            while Q > 0:
                M = Q % 15
                val.append(M)
                Q = int(Q / 15)
            val.reverse()
            t = 0
            for i in val:
                val[t] = str(val[t])
                if val[t] == '10':
                    val[t] = 'A'
                elif val[t] == '11':
                    val[t] = 'B'
                elif val[t] == '12':
                    val[t] = 'C'
                elif val[t] == '13':
                    val[t] = 'D'
                elif val[t] == '14':
                    val[t] = 'E'
                t = t + 1
            n = 0
            ans = None
            for i in val:
                if ans is None:
                    ans = val[n]
                else:
                    ans = ans + val[n]
                n = n + 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                return temp + ans


def dectob16(num):
    temp = None
    num = str(num)
    if num[0] == '-' or num[0] == '+':
        temp = num[0]
        num = signhandle(num)
    chk = chk10(num)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    else:
        for i in num:
            if i == '.':
                c = True
                break
            else:
                c = False
        if c is True:
            num1, numd = num.split('.')
            ans = fracdectob16(num1,numd)
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                ans = temp + ans
                return ans
        else:
            val = []
            Q = int(int(num) / 16)
            M = int(num) % 16
            val.append(M)
            while Q > 0:
                M = Q % 16
                val.append(M)
                Q = int(Q / 16)
            val.reverse()
            t = 0
            for i in val:
                val[t] = str(val[t])
                if val[t] == '10':
                    val[t] = 'A'
                elif val[t] == '11':
                    val[t] = 'B'
                elif val[t] == '12':
                    val[t] = 'C'
                elif val[t] == '13':
                    val[t] = 'D'
                elif val[t] == '14':
                    val[t] = 'E'
                elif val[t] == '15':
                    val[t] = 'F'
                t = t + 1
            n = 0
            ans = None
            for i in val:
                if ans is None:
                    ans = val[n]
                else:
                    ans = ans + val[n]
                n = n + 1
            if temp == '+' or temp is None:
                return ans
            elif temp == '-':
                ans = str(ans)
                return temp + ans


def base(num, fromB, toB):
    Bguide = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    Bguide1 = [2, 3, 4, 5, 6, 7, 8, 9]
    try:
        B1 = int(fromB)
        B2 = int(toB)
    except:
        return "Invalid base value"
    X = str(num)
    if B1 in Bguide and B2 in Bguide:
        if B1 == 10 and B2 in Bguide1:
            result = dectosub(X, B2)
            return result
        elif B1 in Bguide1 and B2 == 10:
            result = subtodec(X, B1)
            return result
        elif B1 == B2:
            chk = chkbase(X, B1)
            if chk is False:
                return 'Invalid number'
            elif chk == 'Invalid number':
                return chk
            elif chk == 'Invalid base value':
                return chk
            else:
                return num
        elif B1 == 11 and B2 == 10:
            result = b11todec(X)
            return result
        elif B1 == 10 and B2 == 11:
            result = dectob11(X)
            return result
        elif B1 == 10 and B2 == 12:
            result = dectob12(X)
            return result
        elif B1 == 12 and B2 == 10:
            result = b12todec(X)
            return result
        elif B1 == 10 and B2 == 13:
            result = dectob13(X)
            return result
        elif B1 == 13 and B2 == 10:
            result = b13todec(X)
            return result
        elif B1 == 10 and B2 == 14:
            result = dectob14(X)
            return result
        elif B1 == 14 and B2 == 10:
            result = b14todec(X)
            return result
        elif B1 == 10 and B2 == 15:
            result = dectob15(X)
            return result
        elif B1 == 15 and B2 == 10:
            result = b15todec(X)
            return result
        elif B1 == 10 and B2 == 16:
            result = dectob16(X)
            return result
        elif B1 == 16 and B2 == 10:
            result = b16todec(X)
            return result
        elif B1 in Bguide1 and B2 in Bguide1:
            stage = subtodec(X, B1)
            if stage == 'Invalid number':
                return stage
            elif stage == 'Invalid base value':
                return stage
            else:
                result = dectosub(stage, B2)
                return result
        elif B1 in Bguide1 and B2 == 11:
            stage = subtodec(X, B1)
            if stage == 'Invalid number':
                return stage
            elif stage == 'Invalid base value':
                return stage
            else:
                result = dectob11(stage)
                return result
        elif B1 == 11 and B2 in Bguide1:
            stage = b11todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectosub(stage, B2)
                return result
        elif B1 in Bguide1 and B2 == 12:
            stage = subtodec(X, B1)
            if stage == 'Invalid number':
                return stage
            elif stage == 'Invalid base value':
                return stage
            else:
                result = dectob12(stage)
                return result
        elif B1 == 12 and B2 in Bguide1:
            stage = b12todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectosub(stage, B2)
                return result
        elif B1 in Bguide1 and B2 == 13:
            stage = subtodec(X, B1)
            if stage == 'Invalid number':
                return stage
            elif stage == 'Invalid base value':
                return stage
            else:
                result = dectob13(stage)
                return result
        elif B1 == 13 and B2 in Bguide1:
            stage = b13todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectosub(stage, B2)
                return result
        elif B1 in Bguide1 and B2 == 14:
            stage = subtodec(X, B1)
            if stage == 'Invalid number':
                return stage
            elif stage == 'Invalid base value':
                return stage
            else:
                result = dectob14(stage)
                return result
        elif B1 == 14 and B2 in Bguide1:
            stage = b14todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectosub(stage, B2)
                return result
        elif B1 in Bguide1 and B2 == 15:
            stage = subtodec(X, B1)
            if stage == 'Invalid number':
                return stage
            elif stage == 'Invalid base value':
                return stage
            else:
                result = dectob15(stage)
                return result
        elif B1 == 15 and B2 in Bguide1:
            stage = b15todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectosub(stage, B2)
                return result
        elif B1 in Bguide1 and B2 == 16:
            stage = subtodec(X, B1)
            if stage == 'Invalid number':
                return stage
            elif stage == 'Invalid base value':
                return stage
            else:
                result = dectob16(stage)
                return result
        elif B1 == 16 and B2 in Bguide1:
            stage = b16todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectosub(stage, B2)
                return result
        elif B1 == 11 and B2 == 12:
            stage = b11todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob12(stage)
                return result
        elif B1 == 11 and B2 == 13:
            stage = b11todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob13(stage)
                return result
        elif B1 == 11 and B2 == 14:
            stage = b11todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob14(stage)
                return result
        elif B1 == 11 and B2 == 15:
            stage = b11todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob15(stage)
                return result
        elif B1 == 11 and B2 == 16:
            stage = b11todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob16(stage)
                return result
        elif B1 == 12 and B2 == 11:
            stage = b12todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob11(stage)
                return result
        elif B1 == 12 and B2 == 13:
            stage = b12todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob13(stage)
                return result
        elif B1 == 12 and B2 == 14:
            stage = b12todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob14(stage)
                return result
        elif B1 == 12 and B2 == 15:
            stage = b12todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob15(stage)
                return result
        elif B1 == 12 and B2 == 16:
            stage = b12todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob16(stage)
                return result
        elif B1 == 13 and B2 == 11:
            stage = b13todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob11(stage)
                return result
        elif B1 == 13 and B2 == 12:
            stage = b13todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob12(stage)
                return result
        elif B1 == 13 and B2 == 14:
            stage = b13todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob14(stage)
                return result
        elif B1 == 13 and B2 == 15:
            stage = b13todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob15(stage)
                return result
        elif B1 == 13 and B2 == 16:
            stage = b13todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob16(stage)
                return result
        elif B1 == 14 and B2 == 11:
            stage = b14todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob11(stage)
                return result
        elif B1 == 14 and B2 == 12:
            stage = b14todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob12(stage)
                return result
        elif B1 == 14 and B2 == 13:
            stage = b14todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob13(stage)
                return result
        elif B1 == 14 and B2 == 15:
            stage = b14todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob15(stage)
                return result
        elif B1 == 14 and B2 == 16:
            stage = b14todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob16(stage)
                return result
        elif B1 == 15 and B2 == 11:
            stage = b15todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob11(stage)
                return result
        elif B1 == 15 and B2 == 12:
            stage = b15todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob12(stage)
                return result
        elif B1 == 15 and B2 == 13:
            stage = b15todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob13(stage)
                return result
        elif B1 == 15 and B2 == 14:
            stage = b15todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob14(stage)
                return result
        elif B1 == 15 and B2 == 16:
            stage = b15todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob16(stage)
                return result
        elif B1 == 16 and B2 == 11:
            stage = b16todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob11(stage)
                return result
        elif B1 == 16 and B2 == 12:
            stage = b16todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob12(stage)
                return result
        elif B1 == 16 and B2 == 13:
            stage = b16todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob13(stage)
                return result
        elif B1 == 16 and B2 == 14:
            stage = b16todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob14(stage)
                return result
        elif B1 == 16 and B2 == 15:
            stage = b16todec(X)
            if stage == 'Invalid number':
                return stage
            else:
                result = dectob15(stage)
                return result
    else:
        return "Invalid base value"


def add(num1, num2, Base):
    num1 = str(num1)
    num2 = str(num2)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    else:
        N1 = base(num1, Base, '10')
        N2 = base(num2, Base, '10')
        if N1 == 'Invalid number' or N2 == 'Invalid number':
            return 'Invalid number'
        else:
            N1 = float(N1)
            N2 = float(N2)
            stage = N1 + N2
            test = str(stage)
            T1, T2 = test.split('.')
            T2 = int(T2)
            if T2 == 0:
                stage = int(stage)
            result = base(str(stage), '10', Base)
            return result


def sub(num1, num2, Base):
    num1 = str(num1)
    num2 = str(num2)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    else:
        N1 = base(num1, Base, '10')
        N2 = base(num2, Base, '10')
        if N1 == 'Invalid number' or N2 == 'Invalid number':
            return 'Invalid number'
        else:
            N1 = float(N1)
            N2 = float(N2)
            stage = N1 - N2
            test = str(stage)
            T1, T2 = test.split('.')
            T2 = int(T2)
            if T2 == 0:
                stage = int(stage)
            result = base(str(stage), '10', Base)
            return result


def mul(num1, num2, Base):
    num1 = str(num1)
    num2 = str(num2)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    else:
        N1 = base(num1, Base, '10')
        N2 = base(num2, Base, '10')
        if N1 == 'Invalid number' or N2 == 'Invalid number':
            return 'Invalid number'
        else:
            N1 = float(N1)
            N2 = float(N2)
            stage = N1 * N2
            test = str(stage)
            T1, T2 = test.split('.')
            T2 = int(T2)
            if T2 == 0:
                stage = int(stage)
            result = base(str(stage), '10', Base)
            return result


def div(num1, num2, Base):
    num1 = str(num1)
    num2 = str(num2)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    else:
        N1 = base(num1, Base, '10')
        N2 = base(num2, Base, '10')
        if N1 == 'Invalid number' or N2 == 'Invalid number':
            return 'Invalid number'
        else:
            N1 = float(N1)
            N2 = float(N2)
            if N2 == 0.0:
                return 'Cannot divide by zero'
            stage = N1 / N2
            test = str(stage)
            T1, T2 = test.split('.')
            T2 = int(T2)
            if T2 == 0:
                stage = int(stage)
            result = base(str(stage), '10', Base)
            return result


def addmany(*nums, Base):
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    else:
        val = []
        res = []
        ans = 0.00
        for n in nums:
            val.append(n)
        for n in val:
            n = str(n)
            stage = base(n, Base, 10)
            if stage == 'Invalid number':
                return stage
            else:
                res.append(float(stage))
        for n in res:
            ans = ans + n
        test = str(ans)
        T1, T2 = test.split('.')
        T2 = int(T2)
        if T2 == 0:
            ans = int(ans)
        result = base(str(ans), '10', Base)
        return result


def mulmany(*nums, Base):
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    else:
        val = []
        res = []
        ans = 1.00
        for n in nums:
            val.append(n)
        for n in val:
            n = str(n)
            stage = base(n, Base, 10)
            if stage == 'Invalid number':
                return stage
            else:
                res.append(float(stage))
        for n in res:
            ans = ans * n
        test = str(ans)
        T1, T2 = test.split('.')
        T2 = int(T2)
        if T2 == 0:
            ans = int(ans)
        result = base(str(ans), '10', Base)
        return result


def power(num1, num2, Base):
    num1 = str(num1)
    num2 = str(num2)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    chk = chkbase(num1, Base)
    if chk is False:
        return 'Invalid number'
    elif chk == 'Invalid number':
        return chk
    elif chk == 'Invalid base value':
        return chk
    else:
        chk = chkbase(num2, Base)
        if chk is False:
            return 'Invalid number'
        elif chk == 'Invalid number':
            return chk
        elif chk == 'Invalid base value':
            return chk
        else:
            if float(num1) == 0.0 and float(num2) == 0.0:
                return 'Undefined'
            num1 = base(num1, Base, 10)
            num2 = base(num2, Base, 10)
            res = float(num1) ** float(num2)
            test = str(res)
            T1, T2 = test.split('.')
            T2 = int(T2)
            if T2 == 0:
                ans = int(res)
                result = base(str(ans), '10', Base)
            else:
                result = base(test, '10', Base)
    return str(result)


def extractnum(exp1, exp2):
    exp1 = str(exp1)
    exp2 = str(exp2)
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e',
             'F', 'f']
    oguide = ['+', '-', '*', '/', '^']
    num1stage = None
    num2stage = None
    num1 = None
    num2 = None
    for n in exp1:
        if n in guide:
            if num1stage is None:
                num1stage = n
            else:
                num1stage = num1stage + n
        else:
            break
    num1stage = num1stage + '00'
    if len(num1stage) > len(exp1):
        num1 = exp1
    else:
        num1 = exp1[:len(num1stage)]
        if num1[len(num1) - 1] in oguide:
            if num1[len(num1) - 2] == '-' or num1[len(num1) - 2] == '+':
                num1 = num1[:len(num1) - 1]
            else:
                num1 = None
        else:
            num1 = num1stage[:len(num1stage) - 2]
    num1 = ''.join(reversed(num1))
    if exp2[0] == '-' or exp2[0] == '+':
        exp2stage = exp2[1:]
        for n in exp2stage:
            if n in guide:
                if num2stage is None:
                    num2stage = n
                else:
                    num2stage = num2stage + n
            else:
                break
        num2 = exp2[0] + num2stage
    else:
        for n in exp2:
            if n in guide:
                if num2 is None:
                    num2 = n
                else:
                    num2 = num2 + n
            else:
                break
    return num1, num2


def insertnum(opt, pos, res, num1, num2, exp):
    opt = str(opt)
    pos = int(pos)
    res = str(res)
    num1 = str(num1)
    num2 = str(num2)
    exp = str(exp)
    if opt == '**':
        exp1 = exp[:pos]
        exp1 = ''.join(reversed(exp1))
        exp2 = exp[pos + 2:]
    else:
        exp1 = exp[:pos]
        exp1 = ''.join(reversed(exp1))
        exp2 = exp[pos + 1:]
    exp1 = exp1[len(num1):]
    exp1 = ''.join(reversed(exp1))
    exp2 = exp2[len(num2):]
    nexp = exp1 + res + exp2
    return nexp


def express(exp, Base):
    exp = str(exp)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    l1 = 0
    while l1 <= len(exp):
        pos = exp.find('**', l1)
        if pos == -1:
            l1 = l1 + 1
        else:
            exp1 = exp[:pos]
            exp1 = ''.join(reversed(exp1))
            exp2 = exp[pos + 2:]
            num1, num2 = extractnum(exp1, exp2)
            if float(num1) == 0.0 and float(num2) == 0.0:
                return 'Undefined power operation'
            powres = power(num1, num2, Base)
            nexp = insertnum('**', pos, powres, num1, num2, exp)
            exp = nexp
    l1 = 0
    while l1 <= len(exp):
        pos = exp.find('^', l1)
        if pos == -1:
            l1 = l1 + 1
        else:
            exp1 = exp[:pos]
            exp1 = ''.join(reversed(exp1))
            exp2 = exp[pos + 1:]
            num1, num2 = extractnum(exp1, exp2)
            if float(num1) == 0.0 and float(num2) == 0.0:
                return 'Undefined power operation'
            powres = power(num1, num2, Base)
            nexp = insertnum('^', pos, powres, num1, num2, exp)
            exp = nexp
    while True:
        pos1 = exp.find('*')
        pos2 = exp.find('/')
        if pos1 == -1:
            if pos2 == -1:
                break
            else:
                exp1 = exp[:pos2]
                exp1 = ''.join(reversed(exp1))
                exp2 = exp[pos2 + 1:]
                num1, num2 = extractnum(exp1, exp2)
                if float(num2) == 0.0:
                    return 'Cannot divide by zero'
                divres = div(num1, num2, Base)
                nexp = insertnum('/', pos2, divres, num1, num2, exp)
                exp = nexp
        else:
            if pos2 == -1:
                exp1 = exp[:pos1]
                exp1 = ''.join(reversed(exp1))
                exp2 = exp[pos1 + 1:]
                num1, num2 = extractnum(exp1, exp2)
                mulres = mul(num1, num2, Base)
                nexp = insertnum('*', pos1, mulres, num1, num2, exp)
                exp = nexp
            else:
                if pos1 < pos2:
                    exp1 = exp[:pos1]
                    exp1 = ''.join(reversed(exp1))
                    exp2 = exp[pos1 + 1:]
                    num1, num2 = extractnum(exp1, exp2)
                    mulres = mul(num1, num2, Base)
                    nexp = insertnum('*', pos1, mulres, num1, num2, exp)
                    exp = nexp
                else:
                    exp1 = exp[:pos2]
                    exp1 = ''.join(reversed(exp1))
                    exp2 = exp[pos2 + 1:]
                    num1, num2 = extractnum(exp1, exp2)
                    if float(num2) == 0.0:
                        return 'Cannot divide by zero'
                    divres = div(num1, num2, Base)
                    nexp = insertnum('/', pos2, divres, num1, num2, exp)
                    exp = nexp
    while True:
        pos1 = exp.find('+')
        pos2 = exp.find('-')
        if pos1 == -1:
            if pos2 == -1:
                break
            else:
                if pos2 == 0:
                    pos2 = exp.find('-', 1)
                    if pos2 == -1:
                        break
                exp1 = exp[:pos2]
                exp1 = ''.join(reversed(exp1))
                exp2 = exp[pos2 + 1:]
                num1, num2 = extractnum(exp1, exp2)
                subres = sub(num1, num2, Base)
                nexp = insertnum('-', pos2, subres, num1, num2, exp)
                exp = nexp
                try:
                    if float(exp) < 0.0:
                        break
                except:
                    continue
        else:
            if pos2 == -1:
                if pos1 == 0:
                    pos1 = exp.find('+', 1)
                    if pos1 == -1:
                        break
                exp1 = exp[:pos1]
                exp1 = ''.join(reversed(exp1))
                exp2 = exp[pos1 + 1:]
                num1, num2 = extractnum(exp1, exp2)
                addres = add(num1, num2, Base)
                nexp = insertnum('+', pos1, addres, num1, num2, exp)
                exp = nexp
                try:
                    if float(exp) < 0.0:
                        break
                except:
                    continue
            else:
                if pos1 < pos2:
                    if pos1 == 0:
                        pos1 = exp.find('+', 1)
                        if pos1 > pos2:
                            exp1 = exp[:pos2]
                            exp1 = ''.join(reversed(exp1))
                            exp2 = exp[pos2 + 1:]
                            num1, num2 = extractnum(exp1, exp2)
                            subres = sub(num1, num2, Base)
                            nexp = insertnum('-', pos2, subres, num1, num2, exp)
                            exp = nexp
                            try:
                                if float(exp) < 0.0:
                                    break
                            except:
                                continue
                        elif pos1 == -1:
                            pos1 = exp.find('-')
                            exp1 = exp[:pos1]
                            exp1 = ''.join(reversed(exp1))
                            exp2 = exp[pos1 + 1:]
                            num1, num2 = extractnum(exp1, exp2)
                            subres = sub(num1, num2, Base)
                            nexp = insertnum('-', pos1, subres, num1, num2, exp)
                            exp = nexp
                            try:
                                if float(exp) < 0.0:
                                    break
                            except:
                                continue
                    exp1 = exp[:pos1]
                    exp1 = ''.join(reversed(exp1))
                    exp2 = exp[pos1 + 1:]
                    num1, num2 = extractnum(exp1, exp2)
                    addres = add(num1, num2, Base)
                    nexp = insertnum('+', pos1, addres, num1, num2, exp)
                    exp = nexp
                    try:
                        if float(exp) < 0.0:
                            break
                    except:
                        continue
                else:
                    if pos2 == 0:
                        pos2 = exp.find('-', 1)
                        if pos2 > pos1:
                            exp1 = exp[:pos1]
                            exp1 = ''.join(reversed(exp1))
                            exp2 = exp[pos1 + 1:]
                            num1, num2 = extractnum(exp1, exp2)
                            addres = add(num1, num2, Base)
                            nexp = insertnum('+', pos1, addres, num1, num2, exp)
                            exp = nexp
                            try:
                                if float(exp) < 0.0:
                                    break
                            except:
                                continue
                        elif pos2 == -1:
                            pos2 = exp.find('+')
                            exp1 = exp[:pos2]
                            exp1 = ''.join(reversed(exp1))
                            exp2 = exp[pos2 + 1:]
                            num1, num2 = extractnum(exp1, exp2)
                            addres = add(num1, num2, Base)
                            nexp = insertnum('+', pos2, addres, num1, num2, exp)
                            exp = nexp
                            try:
                                if float(exp) < 0.0:
                                    break
                            except:
                                continue
                    exp1 = exp[:pos2]
                    exp1 = ''.join(reversed(exp1))
                    exp2 = exp[pos2 + 1:]
                    num1, num2 = extractnum(exp1, exp2)
                    subres = sub(num1, num2, Base)
                    nexp = insertnum('-', pos2, subres, num1, num2, exp)
                    exp = nexp
                    try:
                        if float(exp) < 0.0:
                            break
                    except:
                        continue
    return exp


def unpack(exp):
    exp = str(exp)
    exp = ''.join(exp.split())
    op = []
    cl = []
    for i, j in enumerate(exp):
        if j == '(' or j == '{' or j == '[':
            op.append(i)
        elif j == ')' or j == '}' or j == ']':
            cl.append(i)
    if len(op) != len(cl):
        return (0, 0), 'Invalid brackets'
    if len(op) == 0 and len(cl) == 0:
        return (0, 0), exp
    itr = 0
    res = []
    for i in op:
        if i < cl[itr]:
            res.append(i)
    m = (max(res), cl[itr])
    if exp[m[0]] == '(':
        if exp[m[1]] == '}' or exp[m[1]] == ']':
            return (0, 0), 'Invalid brackets'
    if exp[m[0]] == '{':
        if exp[m[1]] == ')' or exp[m[1]] == ']':
            return (0, 0), 'Invalid brackets'
    if exp[m[0]] == '[':
        if exp[m[1]] == '}' or exp[m[1]] == ')':
            return (0, 0), 'Invalid brackets'
    val = []
    for n in range(m[0] + 1, m[1]):
        val.append(exp[n])
    st = None
    for n in val:
        if st is None:
            st = n
        else:
            st = st + n
    return m, st


def insertbracket(exp, pos, num):
    exp = str(exp)
    num = str(num)
    guide = ['+', '-', '*', '/', '^', '(', '{', '[', ')', '}', ']']
    if pos[0] == 0 and pos[1] == 0:
        return exp
    if num == 'chkexp':
        exp = ''.join(exp.split())
        exp1 = exp[:pos[0]]
        if exp1 is None or exp1 == '':
            exp1 = exp1
        else:
            if exp1[len(exp1) - 1] not in guide:
                exp1 = exp1 + '*'
        exp2 = exp[pos[1] + 1:]
        if exp2 is None or exp2 == '':
            exp2 = exp2
        else:
            if exp2[0] not in guide:
                exp2 = '*' + exp2
        nexp = exp1 + '0' + exp2
        return nexp
    else:
        exp = ''.join(exp.split())
        exp1 = exp[:pos[0]]
        if exp1 is None or exp1 == '':
            exp1 = exp1
        else:
            if exp1[len(exp1) - 1] not in guide:
                exp1 = exp1 + '*'
        exp2 = exp[pos[1] + 1:]
        if exp2 is None or exp2 == '':
            exp2 = exp2
        else:
            if exp2[0] not in guide:
                exp2 = '*' + exp2
        nexp = exp1 + num + exp2
        return nexp


def chkexp(exp, Base):
    exp = str(exp)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    exp = ''.join(exp.split())
    guide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e',
             'F', 'f']
    nguide = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e',
             'F', 'f', '.']
    oguide = ['+', '-', '*', '/', '^']
    bguide = ['(', ')', '{', '}', '[', ']']
    texp = exp
    if texp[len(texp) - 1] in oguide:
        return 'Operator missing operand'
    if texp[len(texp) - 1] == '.':
        return 'Invalid number'
    if texp[0] == '*' or texp[0] == '/' or texp[0] == '^':
        return 'Operator missing operand'
    if texp[0] == '.':
        return 'Invalid number'
    opos = texp.find('--')
    if opos == 0:
        return 'Invalid operators'
    opos = texp.find('++')
    if opos == 0:
        return 'Invalid operators'
    iop = ['-*', '+*', '_/', '+/', '-**', '+**', '-^', '+^', '---', '+++', '***', '//', '^^']
    for i in iop:
        opos = texp.find(i)
        if opos == -1:
            continue
        else:
            return 'Invalid operators'
    nums = []
    num = None
    for i, j in enumerate(texp):
        if j in nguide:
            if num is None:
                num = j
                if i == len(texp)-1:
                    nums.append(num)
            else:
                num = num + j
                if i == len(texp)-1:
                    nums.append(num)
        else:
            if j in oguide or j in bguide:
                nums.append(num)
                num = None
            else:
                return 'Invalid number'
    for num in nums:
        if num is None:
            continue
        else:
            chk = chkbase(num, Base)
            if chk is False:
                return 'Invalid number'
            elif chk == 'Invalid number':
                return chk
            elif chk == 'Invalid base value':
                return chk
    while True:
        pos, st = unpack(texp)
        if st == texp:
            break
        if st == 'Invalid brackets':
            return st
        opos = st.find('--')
        if opos == 0:
            return 'Invalid operators'
        opos = texp.find('++')
        if opos == 0:
            return 'Invalid operators'
        chk = False
        if st is None or st == '':
            return 'Empty brackets'
        for i in st:
            if i in guide:
                chk = True
        if chk is False:
            return 'Brackets without any number'
        if st[len(st)-1] in oguide:
            return 'Operator missing operand'
        if st[len(st) - 1] == '.':
            return 'Invalid number'
        if st[0] == '*' or st[0] == '/' or st[0] == '^':
            return 'Operator missing operand'
        if st[0] == '.':
            return 'Invalid number'
        nexp = insertbracket(texp, pos, 'chkexp')
        texp = nexp
    return 'Valid'


def exp(expression, Base):
    exp = str(expression)
    try:
        Base = int(Base)
    except:
        return 'Invalid base value'
    if Base < 2 or Base > 16:
        return 'Invalid base value'
    exp = ''.join(exp.split())
    chk = chkexp(exp, Base)
    if chk != 'Valid':
        return chk
    else:
        while True:
            pos, st = unpack(exp)
            if st == exp:
                break
            if st == 'Invalid brackets':
                return st
            num = express(st, Base)
            if num == 'Invalid base value':
                return num
            if num == 'Undefined power operation':
                return num
            if num == 'Cannot divide by zero':
                return num
            nexp = insertbracket(exp, pos, num)
            exp = nexp
        ans = express(exp, Base)
        return ans


def exp10(expression):
    Base = 10
    exp = str(expression)
    exp = ''.join(exp.split())
    chk = chkexp(exp, Base)
    if chk != 'Valid':
        return chk
    else:
        while True:
            pos, st = unpack(exp)
            if st == exp:
                break
            if st == 'Invalid brackets':
                return st
            num = express(st, Base)
            if num == 'Invalid base value':
                return num
            if num == 'Undefined power operation':
                return num
            if num == 'Cannot divide by zero':
                return num
            nexp = insertbracket(exp, pos, num)
            exp = nexp
        ans = express(exp, Base)
        return ans
