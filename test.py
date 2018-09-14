import lazy
import time
import random


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
    for _ in t.spin():
        r = random.randint(0,200)
        if r < 2:
            break
    return ptr

data = lazy.Data(2)
a = Square(Recv(data))
b = Square(3)
c = Mul(a, b)
d = Add(a, b)

#lazy.draw()

lazy.parallelize = True
for i in range(10):
    data.set(i)
    t = time.time()
    print(c.get())
    print(time.time() - t)

#lazy.draw()

t = time.time()
print(d.get())
print(time.time() - t)

#lazy.draw()
