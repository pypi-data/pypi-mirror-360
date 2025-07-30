def f():
    try:
        raise ValueError
    except ValueError:
        print("ValueError")
        return 0
    finally:
        print("finally")
        return 1


print(f())
