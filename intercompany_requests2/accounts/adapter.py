from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):

    def populate_username(self, request, user):
        """
        usernameフィールドがないカスタムユーザーモデルの場合、
        この処理をスキップします。
        """
        # usernameフィールドを使用しないので、何もしないでパス
        pass

    def save_user(self, request, user, form, commit=True):
        """
        ユーザー保存処理のカスタマイズ
        """
        # ユーザーデータの保存
        user = super().save_user(request, user, form, commit=False)
        
        # フォームから追加フィールドを取得
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.position = form.cleaned_data.get('position', '')
        user.phone_number = form.cleaned_data.get('phone_number', '')
        
        if commit:
            user.save()
        return user