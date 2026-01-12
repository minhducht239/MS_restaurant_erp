"""
Management command to create default permissions
Run: python manage.py create_default_permissions
"""
from django.core.management.base import BaseCommand
from authentication.models import Permission, Role


class Command(BaseCommand):
    help = 'Create default permissions and roles'

    def handle(self, *args, **options):
        # Simplified permissions - only keep what's actually used
        # Since the system uses IsAuthenticated and IsAdminUser checks,
        # we define module-level access permissions instead of granular CRUD
        permissions_data = [
            # Admin Access
            ('admin.full_access', 'Quyền quản trị toàn hệ thống', 'user'),
            
            # Module Access Permissions
            ('menu.access', 'Truy cập quản lý thực đơn', 'menu'),
            ('table.access', 'Truy cập quản lý bàn', 'table'),
            ('order.access', 'Truy cập quản lý đơn hàng', 'order'),
            ('billing.access', 'Truy cập thanh toán và hóa đơn', 'billing'),
            ('customer.access', 'Truy cập quản lý khách hàng', 'customer'),
            ('staff.access', 'Truy cập quản lý nhân viên', 'staff'),
            ('reservation.access', 'Truy cập quản lý đặt bàn', 'reservation'),
            ('report.access', 'Truy cập báo cáo và thống kê', 'report'),
            ('settings.access', 'Truy cập cài đặt hệ thống', 'settings'),
        ]

        # Create permissions
        created_permissions = []
        for code, name, category in permissions_data:
            perm, created = Permission.objects.get_or_create(
                code=code,
                defaults={'name': name, 'category': category}
            )
            if created:
                created_permissions.append(code)
                self.stdout.write(f'  Created permission: {code}')
            else:
                self.stdout.write(f'  Permission already exists: {code}')

        self.stdout.write(self.style.SUCCESS(f'\nCreated {len(created_permissions)} new permissions'))

        # Create default roles with simplified permissions
        roles_data = [
            {
                'name': 'admin',
                'display_name': 'Quản trị viên',
                'description': 'Có tất cả quyền trong hệ thống',
                'is_system': True,
                'permissions': ['*'],  # All permissions
            },
            {
                'name': 'manager',
                'display_name': 'Quản lý',
                'description': 'Quản lý nhà hàng, nhân viên, báo cáo',
                'is_system': True,
                'permissions': [
                    'menu.access', 'order.access', 'billing.access',
                    'table.access', 'reservation.access', 'staff.access',
                    'customer.access', 'report.access',
                ],
            },
            {
                'name': 'staff',
                'display_name': 'Nhân viên',
                'description': 'Nhân viên phục vụ',
                'is_system': True,
                'permissions': [
                    'menu.access', 'order.access', 'table.access',
                    'reservation.access', 'customer.access',
                ],
            },
            {
                'name': 'cashier',
                'display_name': 'Thu ngân',
                'description': 'Nhân viên thu ngân',
                'is_system': True,
                'permissions': [
                    'menu.access', 'order.access', 'billing.access',
                    'table.access', 'customer.access',
                ],
            },
            {
                'name': 'chef',
                'display_name': 'Đầu bếp',
                'description': 'Đầu bếp nhà hàng',
                'is_system': True,
                'permissions': [
                    'menu.access', 'order.access',
                ],
            },
        ]

        for role_data in roles_data:
            perm_codes = role_data.pop('permissions')
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            
            if created:
                self.stdout.write(f'  Created role: {role.display_name}')
            else:
                self.stdout.write(f'  Role already exists: {role.display_name}')
            
            # Assign permissions
            if perm_codes == ['*']:
                # All permissions
                role.permissions.set(Permission.objects.all())
            else:
                perms = Permission.objects.filter(code__in=perm_codes)
                role.permissions.set(perms)

        self.stdout.write(self.style.SUCCESS('\nDefault permissions and roles created successfully!'))
