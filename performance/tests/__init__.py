import random
import time

from faker import Faker
from mongoengine import *
from mongoframes import *
from pymongo import MongoClient

__all__ = [
    'build_test_data',
    'connect_to_db',
    'time_it'
    ]


class Company(Frame):

    _fields = {
        'name',
        'departments',
        'address',
        'tel',
        'website_url'
        }


class Department(SubFrame):

    _fields = {
        'name',
        'year_end',
        'annual_budget'
        }


class Employee(Frame):

    _fields = {
        'first_name',
        'last_name',
        'dob',
        'role',
        'tel',
        'email',
        'annual_salary',
        'ssn',
        'company',
        'department'
        }


def build_test_data(
        total_companies=100,
        total_departments_per_company=10,
        total_employees_per_company=50
        ):
    """Add a context in which we can run the tests with the test data"""

    print('Building test data...')

    # Drop the database collections
    Company.get_collection().drop()
    Employee.get_collection().drop()

    # Create a faker object
    fake = Faker()
    fake.seed(11061979)
    random.seed(11061979)

    # Build companies
    companies = []
    for company_index in range(0, total_companies):
        company = Company(
            name=fake.company(),
            departments=[],
            address=fake.address(),
            tel=fake.phone_number(),
            website_url=fake.uri()
            )

        # Build departments
        for department_index in range(0, total_departments_per_company):
            department = Department(
                name=fake.word(),
                year_end=fake.date_time_this_year(False, True),
                annual_budget=fake.pyint()
                )
            company.departments.append(department)

        companies.append(company)

    Company.insert_many(companies)

    # Build employees
    for company in companies:
        for employee_index in range(0, total_employees_per_company):
            employee = Employee(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                dob=fake.date(),
                role=fake.job(),
                tel=fake.phone_number(),
                email=fake.email(),
                annual_salary=fake.pyint(),
                ssn=fake.ssn(),
                company=company,
                department=random.choice(company.departments)
                )
            employee.insert()

def connect_to_db():
    """Connect to the database"""

    print('Connecting to database...')

    # Connect to database via MongoEngine
    connect('mongo_performance_tests')

    # Connect to database via MongoFrames
    Frame._client = MongoClient(
        'mongodb://localhost:27017/mongo_performance_tests'
        )

def time_it(func, calls, *args, **kwargs):
    """
    Call the given function X times and output the best, worst and average
    execution time.
    """

    # Call the function X times and record the times
    times = []
    for call_index in range(calls):
        start_time = time.time()
        func(*args, **kwargs)
        times.append(time.time() - start_time)

    # Get the best, worst and average times
    times.sort()
    best = times[0]
    worst = times[-1]
    average = sum(times) / float(len(times))

    print(
        '{func_name: <32} {best: 02.3f} {worst: 02.3f} {average: 02.3f}'.format(
            func_name=func.__name__,
            best=best,
            worst=worst,
            average=average
            )
        )