from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from companies.models import Company

User = get_user_model()

class Command(BaseCommand):
    help = 'デモ企業とテストユーザーを作成する'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='企業名', default='デモ企業')
        parser.add_argument('--email', type=str, help='管理者メールアドレス', default='admin@example.com')
        parser.add_argument('--password', type=str, help='管理者パスワード', default='password123')

    def handle(self, *args, **options):
        company_name = options['name']
        admin_email = options['email']
        admin_password = options['password']
        
        # 企業を作成
        company, created = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'industry': 'IT',
                'description': 'デモ用企業',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'企業 "{company_name}" を作成しました'))
        else:
            self.stdout.write(self.style.WARNING(f'企業 "{company_name}" はすでに存在します'))
        
        # 管理者ユーザーを作成
        admin_user, user_created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'company': company,
                'is_active': True,
            }
        )
        
        if user_created:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'管理者ユーザー "{admin_email}" を作成しました'))
        else:
            if not admin_user.company:
                admin_user.company = company
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f'既存ユーザー "{admin_email}" を企業に所属させました'))
            else:
                self.stdout.write(self.style.WARNING(f'ユーザー "{admin_email}" はすでに存在し、企業に所属しています'))
        
        # 招待コードを表示
        self.stdout.write(self.style.SUCCESS(f'企業の招待コード: {company.invitation_code}'))