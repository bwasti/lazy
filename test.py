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

@lazy.asynchronous
def Send(t, x):
    for _ in t.spin():
        r = random.randint(0, 200)
        if r < 5:
            break

@lazy.asynchronous
def Recv(t):
    for _ in t.spin():
        r = random.randint(0, 200)
        if r < 5:
            return 1337

a = Square(2)
b = Square(3)
c = Mul(a, b)
d = Add(a, b)

#lazy.parallelize = True
t = time.time()
print(c.get())
print(time.time() - t)

t = time.time()
print(d.get())
print(time.time() - t)


