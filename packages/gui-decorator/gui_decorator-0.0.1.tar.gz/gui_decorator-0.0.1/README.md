```python
from gui_decorator import gui

@gui(title="The Title", width=500, height=300, input_filter=[("Excel files", ".xlsx")], output_filter=[("Excel files", ".xlsx"))])
def foo(input_path, output_path):
  # use `yield` to send logs to the GUI
  yield f"Got input_path: {input_path}"
  yield f"Got output_path: {output_path}"
```
