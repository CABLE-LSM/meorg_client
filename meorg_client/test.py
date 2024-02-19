import jinja2 as j2


template = j2.Environment(loader=j2.BaseLoader).from_string(open("test.j2", "r").read())

paths = dict(login=dict(method="POST", args=[["email", "str", "None"]]))

rendered = template.render(file_doc="TEST", paths=paths)

print(rendered)
