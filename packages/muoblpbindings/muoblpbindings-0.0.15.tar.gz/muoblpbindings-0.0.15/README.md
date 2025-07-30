# muoblpbindings

## Adding new algorithm 
1. Assuming algorithm is named `x`
2. Create `x.cpp` and `x.hpp` files with implementation
3. Bind method in `binder.cpp`
4. Define import and method signature in `__init__.py` and `__init__.pyi`
5. Add and link x.cpp as library in `CMakeLists.txt`
6. Bump project version in `pyproject.toml`
