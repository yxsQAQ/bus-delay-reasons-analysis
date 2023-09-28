from django.shortcuts import render, redirect
from django import forms

from app01 import models
from app01.utils.pagination import Pagination
from app01.utils.bootstrap import BootStrapModelForm
from django.core.exceptions import ValidationError
from app01.utils.encrypt import md5


def admin_home(request):
    return render(request, 'admin_home.html')

def admin_about(request):
    return render(request, 'admin_about.html')

def admin_list(request):
    """ Display the list of administrators """

    # Check if the user is logged in. If not, redirect to the login page. If yes, continue.
    # The user sends a request, obtain the cookie string, and check if there is any session info.
    # info_dict = request.session['info']

    # Construct the search query
    data_dict = {}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['username__contains'] = search_data

    # Retrieve data from the database based on the search criteria
    queryset = models.Admin.objects.filter(**data_dict)

    # Pagination
    page_object = Pagination(request, queryset)

    context = {
        'queryset': page_object.page_queryset,
        'page_string': page_object.html(),
        'search_data': search_data,
    }

    return render(request, 'admin_list.html', context)


class AdminModelForm(BootStrapModelForm):

    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Admin
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm = md5(self.cleaned_data.get('confirm_password'))
        if confirm != pwd:
            raise ValidationError('Passwords do not match')

        # Return what to save in this field in the database.
        return confirm


class AdminResetModelForm(BootStrapModelForm):

    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Admin
        fields = ['password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        md5_pwd = md5(pwd)

        # Check whether the current password matches the new input password in the database.
        exists = models.Admin.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
        if exists:
            raise ValidationError("Cannot be the same as the previous password")

        return md5_pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm = md5(self.cleaned_data.get('confirm_password'))
        if confirm != pwd:
            raise ValidationError('Passwords do not match')

        # Return what to save in this field in the database.
        return confirm


def admin_add(request):
    """ Add an administrator """

    title = 'Add User'
    if request.method == 'GET':
        form = AdminModelForm()
        return render(request, 'change.html', {'form': form, 'title': title})

    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        # Validation successful
        form.save()
        return redirect('/admin/list/')

    # Validation failed
    print(form.errors)
    return render(request, 'change.html', {'form': form})

def admin_delete(request, nid):
    """ Delete an administrator """

    models.Admin.objects.filter(id=nid).delete()
    return redirect('/admin/list/')


def admin_reset(request, nid):
    """ Reset the password for an administrator """

    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect('/admin/list/')

    title = 'Reset Password - {}'.format(row_object.username)

    if request.method == 'GET':
        form = AdminResetModelForm()
        return render(request, 'change.html', {'form': form, 'title': title})

    form = AdminResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')

    return render(request, 'change.html', {'form': form, 'title': title})
