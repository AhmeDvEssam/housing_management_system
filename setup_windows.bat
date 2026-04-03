@echo off
echo ====================================================
echo    تجهيز نظام تشغيل مشروع الإسكان على ويندوز
echo ====================================================
echo.

IF NOT EXIST ".venv" (
    echo [1/4] جاري إنشاء بيئة بايثون الافتراضية...
    python -m venv .venv
) ELSE (
    echo [1/4] بيئة بايثون الافتراضية موجودة مسبقاً.
)

echo [2/4] جاري تفعيل البيئة وتثبيت المكتبات المطلوبة...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

echo [3/4] جاري تجهيز قاعدة البيانات وتطبيق التحديثات...
cd backend
python manage.py migrate

echo [4/4] جاري تجميع ملفات التصميم (Static Files)...
python manage.py collectstatic --noinput

echo.
echo ====================================================
echo تم تجهيز النظام بنجاح!
echo لتشغيل النظام في أي وقت، قم بالضغط على ملف: run_windows.bat
echo ====================================================
pause
