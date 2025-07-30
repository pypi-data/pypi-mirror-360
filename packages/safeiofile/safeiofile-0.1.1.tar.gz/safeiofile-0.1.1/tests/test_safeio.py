import os
from safeiofile import File

def test_write_and_read():
    f = File("test.txt")
    f.write("Hello")
    assert f.read() == "Hello"
    os.remove("test.txt")
