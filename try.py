def read_number(s):
    try:
        num = int(s)
    except ValueError:
        print("无法转化成数字")
        return None
    else:
        return num
