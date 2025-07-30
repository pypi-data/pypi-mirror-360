import inspect
import os
import importlib

# Define the list of sub-modules


class ReadmeGenerator:
    def __init__(self,module_path:str,sub_modules:list[str],readme_path='README.md'):
        self.module_path = module_path
        self.sub_modules = sub_modules
        self.readme_path = readme_path


    # Function to get function details from a module
    def get_function_details(self,module_name):
        try:
            module = importlib.import_module(f"{self.module_path}.{module_name}")
            functions = [func for func in dir(module) if callable(getattr(module, func))]

            function_details = []
            for func in functions:
                function_obj = getattr(module, func)
                if inspect.isfunction(function_obj):
                    docstring = inspect.getdoc(function_obj) or "No description available"
                    function_details.append({
                        "name": func,
                        "docstring": docstring
                    })
            
            return function_details
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")
            return []

    def add_standard_readme_content(self):
        

        self.readme_content = """
# lb_tech_handler
<p align="center">
<a href="" rel="noopener">
<img width=400px height=200px src="logo.png" alt="Company logo"></a>
</p>

<h3 align="center">LB Tech Handler</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/lb_tech_handler/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/lb_tech_handler/The-Documentation-Compendium/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Few lines describing your project.
    <br> 
</p>
"""
        self.readme_content = """

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [TODO](../TODO.md)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)
## 🧐 About <a name = "about"></a>

Write about 1-2 paragraphs describing the purpose of your project.

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Setting Up the Module

Set the Envirornment Varibles

Create a file called `.env` in the root directory

```
LB_DB_HOST_NAME_OR_IP = 192.168.1.1
LB_DB_USER_NAME = USER1
LB_DB_PASSWORD = ABCDEF
LB_DB_PORT = 5432
LB_DB_DATABASE_NAME = DBNAME
```

Install the Module

```
pip install lb_tech_handler
```

if already installed then upgrade

```
pip install --upgrade lb_tech_handler
```

End with an example of getting some data out of the system or using it for a little demo.


"""

    def generate_readme(self):

        self.add_standard_readme_content()

        self.readme_content += "## Overall Functions In each Modules\n\n"

        for sub_module in self.sub_modules:
            self.readme_content += f"### {sub_module.replace('_', ' ').title()}\n"
            
            self.readme_content += f"The `{sub_module}` sub-module handles various operations.\n\n"
            
            function_details = self.get_function_details(sub_module)

            if function_details:
                for func in function_details:
                    self.readme_content += f"[- **`{func['name']}`**](#{func['name']})\n\n"
                    # readme_content += f"- **`{func['name']}`**: \n\n"
            else:
                self.readme_content += "No functions available.\n\n"
        
        self.readme_content += "## Function Defination\n\n"

        for sub_module in self.sub_modules:
            self.readme_content += f"### {sub_module.replace('_', ' ').title()}\n"

            self.readme_content += f"The `{sub_module}` sub-module handles various operations.\n\n"
            
            function_details = self.get_function_details(sub_module)
            

            if function_details:
                for func in function_details:
                    self.readme_content += f"- ### **`{func['name']}`**: \n\n"
                    
                    # Process docstring line by line to add an additional tab
                    if func['docstring']:
                        doc_lines = func['docstring'].split('\n')
                        for line in doc_lines:
                            line:str
                            self.readme_content += f"        {line.rstrip()}\n"  # Add one tab to all lines
                    else:
                        self.readme_content += "        No description available.\n\n"  # Indent 'No description' as well
            else:
                self.readme_content += "No functions available.\n\n"
            


        self.readme_content += "## License\n\n"
        self.readme_content += "This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.\n"

        self.readme_content+= """
Add notes about how to use the system.

## 🚀 Deployment <a name = "deployment"></a>

Add additional notes about how to deploy this on a live system.

## ⛏️ Built Using <a name = "built_using"></a>

- [MongoDB](https://www.mongodb.com/) - Database
- [Express](https://expressjs.com/) - Server Framework
- [VueJs](https://vuejs.org/) - Web Framework
- [NodeJs](https://nodejs.org/en/) - Server Environment

## ✍️ Authors <a name = "authors"></a>

- [@kylelobo](https://github.com/kylelobo) - Idea & Initial work

See also the list of [contributors](https://github.com/kylelobo/The-Documentation-Compendium/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Hat tip to anyone whose code was used
- Inspiration
- References
"""
        return self.readme_content

    # Save the generated README content to a file
    def save_readme(self,content):
        with open(self.readme_path, "w",encoding="utf-8") as readme_file:
            readme_file.write(content)

if __name__ == "__main__":

    module_path = 'lb_tech_handler'
    
    sub_modules = ['db_handler', 'api_handler', 'file_handler', 'os_handler','common_methods','documentation_handler','notification_handler']
    
    readme_obj = ReadmeGenerator(module_path=module_path,sub_modules=sub_modules,readme_path='README.md')

    readme_content = readme_obj.generate_readme()

    readme_obj.save_readme(readme_content)

    print("README.md has been generated successfully.")
