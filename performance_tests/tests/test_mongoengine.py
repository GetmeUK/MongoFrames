from mongoengine import *

from __init__ import build_test_data, connect_to_db, time_it


# Define models

class Company(Document):

    meta = {'collection': 'Company'}

    name = StringField()
    departments = EmbeddedDocumentListField('Department')
    address = StringField()
    tel = StringField()
    website_url = URLField()


class Department(EmbeddedDocument):

    meta = {'collection': 'Department'}

    name = StringField()
    year_end = DateTimeField()
    annual_budget = IntField()


class Employee(Document):

    meta = {'collection': 'Employee'}

    first_name = StringField()
    last_name = StringField()
    dob = StringField()
    role = StringField()
    tel = StringField()
    email = EmailField()
    annual_salary = IntField()
    ssn = StringField()
    company = ReferenceField(Company)
    department = StringField()


# Define tests

def test_flat_select():
    """Select all employees no dereferencing"""
    list(Employee.objects.no_dereference())

def test_embedded_document_select():
    """Select all companies no dereferencing"""
    list(Company.objects.no_dereference())

def test_full_select():
    """Select all employees and their referenced companies"""
    [e.company for e in Employee.objects]

if __name__ == "__main__":

    # Connect to the database
    connect_to_db()

    # Build the test data
    build_test_data()

    # Run the tests
    #time_it(test_flat_select, 100)
    #time_it(test_embedded_document_select, 100)
    time_it(test_full_select, 100)