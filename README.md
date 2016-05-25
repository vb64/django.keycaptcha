# django.keycaptcha
Keycaptcha field for Django forms

Based at this [keycaptcha sample](https://www.keycaptcha.ru/python-captcha-api/).

Register your keycaptcha.com account, then replace values of 'KeyCAPTCHA_PrivateKey' and 'KeyCAPTCHA_UserID' keys in keycaptcha.py with proper values from your keycaptcha.com account.

Then you can use keycaptcha field in your Django forms to protect these forms from spam.

```python

from django import forms
import keycaptcha

class MyForm(forms.Form):
    keycaptcha = keycaptcha.Field()

...

form = MyForm(initial={'keycaptcha': request.META['REMOTE_ADDR']})

...

if request.method == 'POST':
    form = MyForm(request.POST)
    if form.is_valid():

```



