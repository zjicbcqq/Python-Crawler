import re

class A:
    def __init__(self):
        print("class A init")

    __a = 1



class B(A):
    def __init__(self):
        A.__init__(self)
        print("class B init")

    def test_b(self):
        print("b:", self._A__a)


class C(B):
    def __init__(self):
        B.__init__(self)
        print("class C init")

    def test_c(self, *args):
        print("c:", self._A__a)
        print(len(args))
        print(args[0])
        print(args[1])
        print(args[2])


b = B()
b.test_b()

c = C()
c.test_b()
c.test_c(1, 2, 3)



