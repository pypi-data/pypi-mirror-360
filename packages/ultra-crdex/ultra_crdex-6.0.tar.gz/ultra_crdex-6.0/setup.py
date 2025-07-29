from setuptools import setup, find_packages
import os

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# تحديد المسار النسبي لملفات .so داخل مجلد الحزمة
# هذا يفترض أن ملفات .so موجودة مباشرة داخل مجلد ULTRA
package_data_files = [
    'ULTRA.cpython-39.so',
    'ULTRA.cpython-311.so',
    'ULTRA.cpython-312.so',
]

setup(
    name='ultra-crdex',
    version='6.0',
    author='CR_dex',
    author_email='aymanambaby507@example.com',  # بريدك الإلكتروني
    description='new compiler to enc files python',  # وصف قصير
    # long_description=long_description,
    long_description_content_type='text/markdown',  # نوع محتوى الوصف الطويل
    packages=find_packages(),  # يبحث تلقائيا عن جميع الحزم الفرعية
    # تضمين ملفات البيانات (مثل ملفات .so)
    package_data={
        'ULTRA': package_data_files,
    },
    include_package_data=True, # تأكد من تضمين ملفات البيانات المحددة في MANIFEST.in (إذا استخدمت)
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',  # اختر الترخيص المناسب
        'Operating System :: POSIX :: Linux',  # بما أن ملفات .so خاصة بـ Linux/Android
        'Operating System :: Android', # لـ Termux
        'Development Status :: 5 - Production/Stable', # حالة تطوير المشروع (Alpha, Beta, Production/Stable)
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.9',  # أدنى إصدار بايثون مطلوب
)
