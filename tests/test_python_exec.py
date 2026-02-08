from micromorph import *

async def fn(a):
    await asyncio.sleep(0.001)
    print("some output")
    return a * 2

async def test_python_exec():
    res = await py_exec("fn(3)")
    print(res)
    assert "6" in res
    assert "some output" in res