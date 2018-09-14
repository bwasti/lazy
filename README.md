# lazy
Python Library for Lazy Interfaces

# Usage

Decorate synchronous functions with @lazy.synchronous

````
@lazy.synchronous
def Square(x):
    time.sleep(0.1)
    return x ** 2

@lazy.synchronous
def Mul(x, y):
    time.sleep(0.1)
    return x * y
````

Write your program and access the output of annotated functions with `.get()`

````
a = Square(2)
b = Square(a)
# The code isn't run until you call .get()
print(b.get())
````

Run things in parallel automatically with `lazy.parallelize = True`

````
lazy.parallelize = True

a = Square(2)
b = Square(3)
c = Mul(a, b)

t = time.time()
print(c.get())
print(time.time() - t)
````

