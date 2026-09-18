with open('d:/housing/backend/static/css/jazzmin_custom.css', 'r', encoding='utf-8') as f: content=f.read()
content=content.replace('@import url("cairo.css");\n', '')
content=content.replace('@import url("source_sans_pro.css");\n', '')
content='@import url("cairo.css");\n@import url("source_sans_pro.css");\n' + content
open('d:/housing/backend/static/css/jazzmin_custom.css', 'w', encoding='utf-8').write(content)
