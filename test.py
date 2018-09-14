import lazy
import time

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

a = Square(2)
b = Square(3)
c = Mul(a, b)
d = Add(a, b)

lazy.draw()

lazy.parallelize = True
t = time.time()
print(c.get())
print(time.time() - t)

lazy.draw()

t = time.time()
print(d.get())
print(time.time() - t)

lazy.draw()

