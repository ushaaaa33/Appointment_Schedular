"""
Management command to create sample data for testing.
Usage: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.services.models import Service
from apps.appointments.models import Appointment
from decimal import Decimal
from datetime import datetime, timedelta, time

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates sample data for testing the appointment system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create users
        self.stdout.write('Creating users...')
        
        # Admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Admin user created (username: admin, password: admin123)'))
        
        # Regular users
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'phone': '555-0101'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'phone': '555-0102'},
            {'username': 'bob_wilson', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Wilson', 'phone': '555-0103'},
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ User created: {user.username}'))
            users.append(user)
        
        # Create services
        self.stdout.write('Creating services...')
        
        # Find the services_data section and replace with:

        services_data = [
        {
            'name': 'General Consultation',
            'description': 'Comprehensive health consultation with our experienced doctors. Discuss your health concerns and get professional medical advice.',
            'category': 'consultation',
            'duration_minutes': 30,
            'price': Decimal('50.00'),
        },
        {
            'name': 'Dental Checkup',
            'description': 'Complete dental examination including teeth cleaning and oral health assessment. Maintain your perfect smile with regular checkups.',
            'category': 'dental',
            'duration_minutes': 45,
            'price': Decimal('75.00'),
        },
        {
            'name': 'Physical Therapy Session',
            'description': 'Professional physical therapy session for rehabilitation and pain management. Customized treatment plans for your specific needs.',
            'category': 'therapy',
            'duration_minutes': 60,
            'price': Decimal('90.00'),
        },
        {
            'name': 'Mental Health Counseling',
            'description': 'Confidential counseling session with licensed therapists. Talk about your mental health in a safe and supportive environment.',
            'category': 'mental_health',
            'duration_minutes': 50,
            'price': Decimal('100.00'),
        },
        {
            'name': 'Nutritional Consultation',
            'description': 'Expert nutritional guidance and personalized meal planning. Achieve your health goals with professional dietary advice.',
            'category': 'wellness',
            'duration_minutes': 40,
            'price': Decimal('65.00'),
        },
        {
            'name': 'Eye Examination',
            'description': 'Complete eye health examination and vision testing. Get prescription updates and eye health recommendations.',
            'category': 'diagnostic',
            'duration_minutes': 30,
            'price': Decimal('55.00'),
        },
        {
            'name': 'X-Ray Imaging',
            'description': 'Digital X-ray imaging for accurate diagnosis. Quick and safe radiographic examination.',
            'category': 'diagnostic',
            'duration_minutes': 20,
            'price': Decimal('85.00'),
        },
        {
            'name': 'Blood Test Panel',
            'description': 'Comprehensive blood testing including CBC, lipid profile, and glucose levels.',
            'category': 'diagnostic',
            'duration_minutes': 15,
            'price': Decimal('120.00'),
        },
        {
            'name': 'Cardiac Consultation',
            'description': 'Specialist consultation for heart-related concerns with experienced cardiologist.',
            'category': 'specialist',
            'duration_minutes': 45,
            'price': Decimal('150.00'),
        },
        ]
        
        services = []
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Service created: {service.name}'))
            services.append(service)
        
        # Create sample appointments
        self.stdout.write('Creating appointments...')
        
        today = datetime.now().date()
        appointments_data = [
            # Pending appointments
            {
                'user': users[0],
                'service': services[0],
                'appointment_date': today + timedelta(days=3),
                'appointment_time': time(10, 0),
                'status': 'pending',
                'notes': 'First time visit. Please send reminder.',
            },
            {
                'user': users[1],
                'service': services[1],
                'appointment_date': today + timedelta(days=5),
                'appointment_time': time(14, 0),
                'status': 'pending',
                'notes': 'Need teeth cleaning.',
            },
            # Approved appointments
            {
                'user': users[0],
                'service': services[2],
                'appointment_date': today + timedelta(days=7),
                'appointment_time': time(9, 0),
                'status': 'approved',
                'notes': 'Knee pain treatment.',
                'admin_notes': 'Approved. Please bring previous medical records.',
            },
            {
                'user': users[2],
                'service': services[3],
                'appointment_date': today + timedelta(days=10),
                'appointment_time': time(15, 0),
                'status': 'approved',
                'notes': '',
                'admin_notes': 'Session confirmed with Dr. Smith.',
            },
            # Rejected appointment
            {
                'user': users[1],
                'service': services[4],
                'appointment_date': today + timedelta(days=2),
                'appointment_time': time(16, 0),
                'status': 'rejected',
                'notes': 'Urgent consultation needed.',
                'admin_notes': 'Sorry, this time slot is fully booked. Please choose another time.',
            },
            # Completed appointment
            {
                'user': users[2],
                'service': services[5],
                'appointment_date': today - timedelta(days=5),
                'appointment_time': time(11, 0),
                'status': 'completed',
                'notes': 'Annual checkup.',
                'admin_notes': 'Completed successfully. Next checkup in 6 months.',
            },
        ]
        
        for apt_data in appointments_data:
            appointment, created = Appointment.objects.get_or_create(
                user=apt_data['user'],
                service=apt_data['service'],
                appointment_date=apt_data['appointment_date'],
                appointment_time=apt_data['appointment_time'],
                defaults={
                    'status': apt_data['status'],
                    'notes': apt_data['notes'],
                    'admin_notes': apt_data.get('admin_notes', ''),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Appointment created: {appointment.user.username} - {appointment.service.name} ({appointment.status})'
                ))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Users: username=john_doe/jane_smith/bob_wilson, password=password123')
        self.stdout.write('\nYou can now access:')
        self.stdout.write('  - Web Interface: http://127.0.0.1:8000/')
        self.stdout.write('  - Admin Panel: http://127.0.0.1:8000/admin/')