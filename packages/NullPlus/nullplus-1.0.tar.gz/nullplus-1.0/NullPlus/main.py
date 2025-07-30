class Null:
    def __init__(self, *data): self.data = data[0] if len(data) == 1 else data
    def __getattribute__(self, item): return super().__getattribute__(item) if item in ('__class__', '__dict__', '__weakref__', '__doc__', '__module__', 'data', '__repr__') or (item.startswith('__') and item.endswith('__')) else self
    def __getattr__(self, item): return self
    def __setattr__(self, key, value): return super().__setattr__(key, value) if key == 'data' else self
    def __delattr__(self, item): return self
    def __dir__(self): return []
    def __getitem__(self, key): return self
    def __setitem__(self, key, value): return self
    def __delitem__(self, key): return self
    def __getslice__(self, i, j): return self
    def __call__(self, *args, **kwargs): return self
    def __get__(self, instance, owner): return self
    def __set__(self, instance, value): return self
    def __delete__(self, instance): return self
    def __bool__(self): return False
    def __len__(self): return 0
    def __int__(self): return -1
    def __float__(self): return float('nan')
    def __complex__(self): return complex(float('nan'))
    def __index__(self): return 0
    def __round__(self, ndigits=None): return self
    def __abs__(self): return self
    def __repr__(self): return f"<Null: {repr(self.data)}>" if hasattr(self, 'data') else "<Null>"
    def __str__(self): return self.__repr__()
    def __format__(self, format_spec): return ""
    def __iter__(self): return iter(())
    def __reversed__(self): return iter(())
    def __contains__(self, item): return False
    def __eq__(self, other): return isinstance(other, Null)
    def __ne__(self, other): return not isinstance(other, Null)
    def __lt__(self, other): return self
    def __le__(self, other): return self
    def __gt__(self, other): return self
    def __ge__(self, other): return self
    def __add__(self, other): return self
    def __sub__(self, other): return self
    def __mul__(self, other): return self
    def __truediv__(self, other): return self
    def __floordiv__(self, other): return self
    def __mod__(self, other): return self
    def __pow__(self, other): return self
    def __divmod__(self, other): return (self, self)
    def __radd__(self, other): return self
    def __rsub__(self, other): return self
    def __rmul__(self, other): return self
    def __rtruediv__(self, other): return self
    def __rfloordiv__(self, other): return self
    def __rmod__(self, other): return self
    def __rpow__(self, other): return self
    def __rdivmod__(self, other): return (self, self)
    def __iadd__(self, other): return self
    def __isub__(self, other): return self
    def __imul__(self, other): return self
    def __itruediv__(self, other): return self
    def __ifloordiv__(self, other): return self
    def __imod__(self, other): return self
    def __ipow__(self, other): return self
    def __and__(self, other): return self
    def __or__(self, other): return self
    def __xor__(self, other): return self
    def __invert__(self): return self
    def __rand__(self, other): return self
    def __ror__(self, other): return self
    def __rxor__(self, other): return self
    def __iand__(self, other): return self
    def __ior__(self, other): return self
    def __ixor__(self, other): return self
    def __lshift__(self, other): return self
    def __rshift__(self, other): return self
    def __rlshift__(self, other): return self
    def __rrshift__(self, other): return self
    def __ilshift__(self, other): return self
    def __irshift__(self, other): return self
    def __matmul__(self, other): return self
    def __rmatmul__(self, other): return self
    def __imatmul__(self, other): return self
    def __neg__(self): return self
    def __pos__(self): return self
    def __enter__(self): return self
    def __exit__(self, *exc): return True
    async def __aenter__(self): return self
    async def __aexit__(self, *exc): return False
    def __await__(self): yield; return self
    def __aiter__(self): return self
    async def __anext__(self): raise StopAsyncIteration
    def __hash__(self): return 0
    @classmethod
    def __class_getitem__(cls, item): return cls()
    def __copy__(self): return self
    def __deepcopy__(self, memo): return self
    # "Ah, a visitor!"
    # - Minos prime, ultrakill
    
    # "You only have the oneshot"
    # - The World Machine, oneshot
    
    # "You can do this."
    # - Madeline, Celeste
    
    # "THE POINTY-HEADED WILL SAY 'TOOTHPASTE,' AND THEN 'BOY.'"
    # - The Prophecy, Deltarune
    
class Unset:
    def __repr__(self): return "<Unset>"
    def __bool__(self): return False
    def __str__(self): return self.__repr__
    def __eq__(self, other): return isinstance(other, Unset)
    def __ne__(self, other): return not isinstance(other, Unset)
