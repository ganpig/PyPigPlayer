from chardet import detect


def cul_btn(n, mt, mb, x, y=10000):
    if y <= mb:
        k = y / mb
        mt *= k
        mb *= k
    ms = (mb - mt) / 2
    if x >= n * (mt + ms) + ms:
        return mt, mb, (x - n * mt) / (n + 1)
    a = mt / ms
    s = x / ((a + 1) * n + 1)
    t = a * s
    return t, mb * t / mt, s


def time_to_ms(time):
    m, s = time.split(':')
    return int(int(m) * 60000 + float(s) * 1000)


def sec_to_time(sec):
    return '{:0>2d}:{:0>2d}'.format(*divmod(max(int(sec), 0), 60))


def parse_lrc(lrc):
    ret = {-1: ''}
    for line in lrc:
        for i in range(len(tmp := line[1:].replace('][', ']').split(']')) - 1):
            ret[time_to_ms(tmp[i])] = tmp[-1].replace('\n', '').strip()
    return ret


def auto_decode(data):
    return data.decode(detect(data)['encoding']).split('\n')


def upper_bound(array, num):
    l = 0
    r = len(array) - 1
    while l < r:
        mid = (l + r) // 2
        if array[mid] <= num:
            l = mid + 1
        else:
            r = mid
    return l if array[l] >= num else len(array)
