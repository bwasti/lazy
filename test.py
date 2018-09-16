import lazy
import time
import random
import unittest


@lazy.synchronous
def Square(x):
    time.sleep(0.1)
    return x ** 2


@lazy.synchronous
def Mul(x, y):
    time.sleep(0.1)
    return x * y


@lazy.synchronous
def Add(x, y):
    time.sleep(0.1)
    return x + y


@lazy.asynchronous
def Recv(t, ptr):
    # Around 10 spins before we break
    for _ in t.spin():
        r = random.randint(0,5)
        if r == 2:
            break
    return ptr


class TestSynchronous(unittest.TestCase):
    def test_data(self):
        a = lazy.Data(2)
        self.assertEqual(a.get(), 2)
        b = lazy.Data(lazy.Data(2))
        self.assertEqual(b.get().get(), 2)
        c = lazy.Data([1, 2, 3])
        c.get()[0] = 3
        self.assertEqual(c.get()[0], 3)

    def test_simple(self):
        a = Square(2)
        b = Square(3)
        c = Mul(a, b)
        d = Add(a, b)
        self.assertEqual(c.get(), 36)
        self.assertEqual(d.get(), 13)


class TestAsynchronous(unittest.TestCase):
    def test_simple(self):
        data = lazy.Data(2)
        a = Square(Recv(data))
        self.assertEqual(a.get(), 4)


if __name__ == "__main__":
    unittest.main()
