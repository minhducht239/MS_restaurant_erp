"""
Management command to create default permissions
Run: python manage.py create_default_permissions
"""
from django.core.management.base import BaseCommand
from authentication.models import Permission, Role


class Command(BaseCommand):
    help = 'Create default permissions and roles'

    def handle(self, *args, **options):
        # Default permissions
        permissions_data = [
            # User Management
            ('user.view', 'Xem người dùng', 'user'),
            ('user.create', 'Tạo người dùng', 'user'),
            ('user.edit', 'Sửa người dùng', 'user'),
            ('user.delete', 'Xóa người dùng', 'user'),
            ('user.change_role', 'Thay đổi vai trò', 'user'),
            ('user.reset_password', 'Đặt lại mật khẩu', 'user'),
            
            # Menu Management
            ('menu.view', 'Xem thực đơn', 'menu'),
            ('menu.create', 'Tạo món ăn', 'menu'),
            ('menu.edit', 'Sửa món ăn', 'menu'),
            ('menu.delete', 'Xóa món ăn', 'menu'),
            
            # Order Management
            ('order.view', 'Xem đơn hàng', 'order'),
            ('order.create', 'Tạo đơn hàng', 'order'),
            ('order.edit', 'Sửa đơn hàng', 'order'),
            ('order.cancel', 'Hủy đơn hàng', 'order'),
            
            # Billing Management
            ('billing.view', 'Xem hóa đơn', 'billing'),
            ('billing.create', 'Tạo hóa đơn', 'billing'),
            ('billing.edit', 'Sửa hóa đơn', 'billing'),
            ('billing.delete', 'Xóa hóa đơn', 'billing'),
            
            # Table Management
            ('table.view', 'Xem bàn', 'table'),
            ('table.create', 'Tạo bàn', 'table'),
            ('table.edit', 'Sửa bàn', 'table'),
            ('table.delete', 'Xóa bàn', 'table'),
            
            # Reservation Management
            ('reservation.view', 'Xem đặt bàn', 'reservation'),
            ('reservation.create', 'Tạo đặt bàn', 'reservation'),
            ('reservation.edit', 'Sửa đặt bàn', 'reservation'),
            ('reservation.cancel', 'Hủy đặt bàn', 'reservation'),
            
            # Staff Management
            ('staff.view', 'Xem nhân viên', 'staff'),
            ('staff.create', 'Tạo nhân viên', 'staff'),
            ('staff.edit', 'Sửa nhân viên', 'staff'),
            ('staff.delete', 'Xóa nhân viên', 'staff'),
            
            # Customer Management
            ('customer.view', 'Xem khách hàng', 'customer'),
            ('customer.create', 'Tạo khách hàng', 'customer'),
            ('customer.edit', 'Sửa khách hàng', 'customer'),
            ('customer.delete', 'Xóa khách hàng', 'customer'),
            
            # Reports & Analytics
            ('report.view', 'Xem báo cáo', 'report'),
            ('report.export', 'Xuất báo cáo', 'report'),
            
            # System Settings
            ('settings.view', 'Xem cài đặt', 'settings'),
            ('settings.edit', 'Sửa cài đặt', 'settings'),
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

        # Create default roles
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
                    'user.view', 'menu.view', 'menu.create', 'menu.edit', 'menu.delete',
                    'order.view', 'order.create', 'order.edit', 'order.cancel',
                    'billing.view', 'billing.create', 'billing.edit',
                    'table.view', 'table.create', 'table.edit', 'table.delete',
                    'reservation.view', 'reservation.create', 'reservation.edit', 'reservation.cancel',
                    'staff.view', 'staff.create', 'staff.edit',
                    'customer.view', 'customer.create', 'customer.edit',
                    'report.view', 'report.export',
                ],
            },
            {
                'name': 'staff',
                'display_name': 'Nhân viên',
                'description': 'Nhân viên phục vụ',
                'is_system': True,
                'permissions': [
                    'menu.view', 'order.view', 'order.create', 'order.edit',
                    'table.view', 'reservation.view', 'reservation.create',
                    'customer.view', 'customer.create',
                ],
            },
            {
                'name': 'cashier',
                'display_name': 'Thu ngân',
                'description': 'Nhân viên thu ngân',
                'is_system': True,
                'permissions': [
                    'menu.view', 'order.view', 'billing.view', 'billing.create',
                    'table.view', 'customer.view',
                ],
            },
            {
                'name': 'chef',
                'display_name': 'Đầu bếp',
                'description': 'Đầu bếp nhà hàng',
                'is_system': True,
                'permissions': [
                    'menu.view', 'menu.create', 'menu.edit',
                    'order.view',
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
