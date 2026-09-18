import os

def search_text(path, text):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(('.py', '.html', '.js')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if text in f.read():
                            print(f"Found in: {file_path}")
                except Exception:
                    pass

search_text(r'D:\housing\backend', 'للمشغول')
search_text(r'D:\housing\backend', 'اضافة للحجز')
