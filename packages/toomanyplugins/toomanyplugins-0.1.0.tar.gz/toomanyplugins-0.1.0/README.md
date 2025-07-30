# toomanyplugins

**Python utilities for excruciating logging, dynamic plugins & stub generation.**

- **`excruciating_logger`** / **`@annoying_class`**  
  Trace and log every line of your methods (sync or async) when `self.verbose` is `True`.  
- **`plugin(...)` decorator**  
  Inject functions into existing classes at runtime, with optional overrides and nested decorators.  
- **`auto_stub`**  
  Auto-generate and update PEP-compliant `.pyi` stubs next to your classes.  
- **`TypeConverter`**  
  Async helper for converting objects ↔ types, absorbing attributes, merging annotations, and introspection.