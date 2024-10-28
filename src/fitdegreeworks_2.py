# file '..\inputs_new\degreeworks.pdf' to html file

import fitz
doc = fitz.open("..\inputs_new\degreeworks.pdf")
for page in doc:
    text = page.get_text("text")
    print(text)
