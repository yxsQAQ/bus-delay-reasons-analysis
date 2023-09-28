from django.shortcuts import render, HttpResponse, redirect
from django import forms
from app01 import models
from app01.utils.bootstrap import BootStrapForm
from app01.utils.encrypt import md5
from app01.utils.code import check_code
from io import BytesIO


class LoginForm(BootStrapForm):
    """ Form for user login """

    username = forms.CharField(
        label='Username',
        widget=forms.TextInput,
        required=True
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    code = forms.CharField(
        label='Verification Code',
        widget=forms.TextInput,
        required=True
    )

    def clean_password(self):
        """Encrypt the password using md5."""
        pwd = self.cleaned_data.get('password')
        return md5(pwd)


def login(request):
    """ Login view """
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # Successful validation, get the username and password
        # {'username': 'wupeiqi', 'password': 'ad6e1e6feac9c1baa389bd15aa7c993e', 'code': 'xxx'}
        # print(form.cleaned_data)
        user_input_code = form.cleaned_data.pop('code')
        code = request.session.get('img_code', '')
        if code.upper() != user_input_code.upper():
            form.add_error('code', 'Incorrect verification code')
            return render(request, 'login.html', {'form': form})

        # Database verification of username and password, get the user object, none
        # models.Admin.objects.filter(username='xx', password='xx').first()
        admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
        if not admin_object:
            form.add_error('password', 'Incorrect username or password')
            return render(request, 'login.html', {'form': form})

        # Username and password are correct
        # Generate a random string for the user, write it to the user's browser cookie, and then write it to the session
        request.session['info'] = {'id': admin_object.id, 'name': admin_object.username}
        # Session can be saved for 7 days
        request.session.set_expiry(60 * 60 * 24 * 7)

        return redirect('/admin/home/')
    return render(request, 'login.html', {'form': form})


def img_code(request):
    """ Generate image verification code """
    # Call the pillow function to generate the image
    img, code_string = check_code()
    print(code_string)

    # Write to the session for later verification of the code
    request.session['img_code'] = code_string
    # Set session timeout to 60 seconds
    request.session.set_expiry(60)

    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def logout(request):
    """ Logout """
    request.session.clear()

    return redirect('/login/')
