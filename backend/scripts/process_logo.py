import os
from PIL import Image

logo_path = '../static/img/logo.jpg'
out_path = '../static/img/logo_transparent.png'

try:
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        img = img.convert('RGBA')
        datas = img.getdata()
        newData = []
        for item in datas:
            # replace blackish pixels with transparent
            if item[0] < 50 and item[1] < 50 and item[2] < 50:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        img.save(out_path, 'PNG')
        print("Logo processed successfully!")
    else:
        print("logo.jpg not found!")
except Exception as e:
    import traceback
    print("Error occurred:")
    traceback.print_exc()
