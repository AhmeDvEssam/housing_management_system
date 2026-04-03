@echo off
echo ====================================================
echo    تشغيل الخادم المحلي لمشروع الإسكان
echo ====================================================
echo.

IF NOT EXIST ".venv" (
    echo خطأ: لم يتم العثور على بيئة بايثون!
    echo يرجى تشغيل ملف setup_windows.bat أولاً لتجهيز النظام.
    pause
    exit /b
)

echo جاري تفعيل البيئة...
call .venv\Scripts\activate.bat

echo جاري تشغيل الخادم على الشبكة المحلية...
cd backend
echo يمكنك الآن فتح الموقع عبر المتصفح على أي جهاز في الشبكة عبر رقم الأي بي الخاص بهذا الجهاز.
echo مثال: http://192.168.1.50:8000
echo.

waitress-serve --listen=0.0.0.0:8000 housing.wsgi:application
pause
