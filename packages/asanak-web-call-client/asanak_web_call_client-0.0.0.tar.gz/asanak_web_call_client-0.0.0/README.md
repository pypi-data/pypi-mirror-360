# 📦 Asanak Web Call Client (Python)

یک کلاینت پایتونی برای مدیریت تماس ها از طریق API Asanak

## 📌 ویژگی‌ها

- آپلود فایل صوتی به لیست فایل ها
- ایجاد تماس از طریق فایل صوتی (تک یا چند مقصده)
- ایجاد تماس برای کد های احراز هویت (OTP)
- دریافت گزارش وضعیت تماس ها
- دریافت اعتبار باقی مانده

## 📄 منابع و مستندات

- 🌐 [صفحه اصلی سرویس تماس آسا‌نک](https://callapi.asanak.com/)
- 🧾 [مستندات آنلاین کامل](https://callapi.asanak.com/docs/v1)
- 🚀 [مستندات آنلاین Postman](https://documenter.getpostman.com/view/45759202/2sB34Zq3mN)
- ⬇️ [دانلود فایل کالکشن Postman](https://callapi.asanak.com/docs/v1/Asanak_Call_API_Service.postman_collection.json)

## 🚀 نصب پکیج

### از PyPI:
```bash
pip install asanak-web-call-client
```

### از GitHub:
```bash
pip install git+https://github.com/Asanak-Team/python-web-call-client.git
```

## 📚 استفاده از کلاینت

```python
from web_call_client import AsanakWebCallClient

client = AsanakWebCallClient("username", "password")

```

1- افزودن فایل صوتی جدید
```python

try:
    data = client.upload_new_voice("/path/file/voice.mp3")
    print(data)
except Exception as e:
    print(e)
```

2- تماس از طریق فایل صوتی
```python

try:
    data = client.call_by_voice("VOICE_ID", "0912000000")
    print(data)
except Exception as e:
    print(e)
```

3-  تماس OTP
```python

try:
    data = client.call_by_otp(1234, "0912000000")
    print(data)
except Exception as e:
    print(e)
```

4-  استعلام وضعیت تماس ها
```python

try:
    data = client.call_status(['CALL_ID_1', 'CALL_ID_2'])
    print(data)
except Exception as e:
    print(e)
```

5-  استعلام اعتبار باقی مانده
```python

try:
    data = client.credit()
    print(data)
except Exception as e:
    print(e)
```


## 📝 پارامتر‌های ورودی

- `username`: نام کاربری از API Asanak
- `password`: رمز عبور از API Asanak
- `base_url`: آدرس سرور API Asanak (پیش‌فرض: `https://callapi.asanak.com`)

## 📝 پارامتر‌های خروجی
```json
{
    "success": boolean,
    "error": null|str,
}
```