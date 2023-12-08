from util.logger import Logger, logMe

@logMe(Logger.Level.DEBUG, "333333", "444444")
def stringJoin(A, B, C, D, *args):
    st = ''
    for i in args:
        st += str(i)

    Logger.getLogger().debug(f"{Logger.functionName()}|st={st}")
    return st


@logMe(Logger.Level.DEBUG)
def test2(A: str, B: str, C: str, D: str):
    return str('-'.join((A, B, C, D)))


@logMe(Logger.Level.DEBUG, "333|||||||||||||||333", "{|x}")
def raiseException(*args):
    x = 20 / 0
    return None


@logMe()
def test(*args):
    x = 20 / 1
    return None


def jim2(x: int):
    z = 1

    def jim3(y: int):
        global z
        z = z + 1
        return x * y

    return jim3


def main():
    test()
    test2(C='qqqq', D='424544', A='23r@fergtre.com', B='IUYU I')
    stringJoin("aaaa", 'ccccc', 'fgdfgd', 'gdfte56546', 45435, 34535, 354353)
    raiseException()
    # t = jim2(2)
    # print(t(3))
    # print(t(4))
    print(Logger.FILE())
    print(Logger.LINE())


if __name__ == "__main__":
    main()
