from authtools.forms import AdminUserChangeForm


class StaffChangeForm(AdminUserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            self.fields['password'].help_text = ("Raw passwords are not stored, so there is "
                        "no way to see this user's password, but "
                        "you can change the password using "
                        "<a href=\"../password/\">this form</a>.")