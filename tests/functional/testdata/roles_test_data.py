import random
import sys
import uuid
from faker import Faker
faker = Faker()


async def get_admin_data():
    return {
        'login': 'admin',
        'password': 'admin123',
        'first_name': 'Vnya',
        'last_name': 'Ivanov',
        'email': str(random.randint(0, sys.maxsize)) + faker.email(),
        'superuser': True,
        'id': str(uuid.uuid4()),
        'created_at': faker.date_time_this_decade(),
        'modified_at': faker.date_time_this_decade()
    }
