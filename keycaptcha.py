"""
Support keycaptcha (www.keycaptcha.com) in Django
(C) 2014 by Vitaly Bogomolov mail@vitaly-bogomolov.ru
Based at code: https://www.keycaptcha.ru/python-captcha-api/

Usage:

>>> from django import forms
>>> import keycaptcha
>>>
>>> class MyForm(forms.Form):
>>>     keycaptcha = keycaptcha.Field()
>>>
>>> ...
>>>
>>> form = MyForm(initial={'keycaptcha': request.META['REMOTE_ADDR']})
>>>
>>> ...
>>>
>>> if request.method == 'POST':
>>>     form = MyForm(request.POST)
>>>     if form.is_valid():
>>> ...

Template:

<form action="" method="POST">
  {% csrf_token %}
  {{myform.as_p}}
  <input type="submit" id="postbut" value="Test" />
</form>

"""

from random import randint
from hashlib import md5
from urllib import urlopen

from django import forms
from django.utils.safestring import mark_safe

# Replace PUT_YOUR_PRIVATE_KEY_HERE and PUT_YOUR_KEYCAPTCHA_USER_ID_HERE
# with proper values from your keycaptcha.com account
KeyCAPTCHA_PrivateKey = 'PUT_YOUR_PRIVATE_KEY_HERE'
KeyCAPTCHA_UserID = 'PUT_YOUR_KEYCAPTCHA_USER_ID_HERE'

KeyCAPTCHA_Template = '''<!-- KeyCAPTCHA code (www.keycaptcha.com)-->
<input id="capcode" type="hidden" name="%s" value="123" />
<script language="JavaScript">
    var s_s_c_user_id = '#kc_user_id#';
    var s_s_c_session_id = '#kc_session_id#';
    var s_s_c_captcha_field_id = 'capcode';
    var s_s_c_submit_button_id = 'postbut';
    var s_s_c_web_server_sign = '#kc_s1#';
    var s_s_c_web_server_sign2 = '#kc_s2#';
</script>
<script language=JavaScript src="https://backs.keycaptcha.com/swfs/cap.js">
</script>
<!-- end of KeyCAPTCHA code-->
'''


def show_keycaptcha(remote_ip='127.0.0.1'):
    session_id = str(randint(100000000, 999999999999))
    s1 = md5(session_id + remote_ip + KeyCAPTCHA_PrivateKey).hexdigest()
    s2 = md5(session_id + KeyCAPTCHA_PrivateKey).hexdigest()
    rd = {
        'kc_user_id': KeyCAPTCHA_UserID,
        'kc_s1': s1,
        'kc_s2': s2,
        'kc_session_id': session_id,
    }
    st = KeyCAPTCHA_Template
    for k in rd.keys():
        st = st.replace('#' + k + '#', rd[k])
    return st


def validate_keycaptcha(capcode):
    cap = capcode.split('|')
    if len(cap) < 3:
        return False
    valid_cap_sign = md5(
        'accept' + cap[1] + KeyCAPTCHA_PrivateKey + cap[2]
    ).hexdigest()

    if valid_cap_sign != cap[0]:
        return False

    if cap[2].find('http://') == 0:
        try:
            f = urlopen(cap[2] + cap[1])
            st = f.read()
            f.close()
        except:
            return False
        if st != '1':
            return False
    else:
        return False

    return True


class Widget(forms.HiddenInput):

    def render(self, name, value, attrs=None):
        return mark_safe(show_keycaptcha(remote_ip=value) % name)


class Field(forms.CharField):

    def __init__(self):
        super(Field, self).__init__(widget=Widget())

    def validate(self, value):
        super(Field, self).validate(value)
        if not validate_keycaptcha(value):
            raise forms.ValidationError("Wrong keycaptcha")
