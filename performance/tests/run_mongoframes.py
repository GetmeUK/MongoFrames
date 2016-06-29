from mongoframes import *

from __init__ import build_test_data, connect_to_db, time_it


# Define models

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


# Define tests

def test_flat_select():
    """Select all employees no dereferencing"""
    Employee.many()

def test_embedded_document_select():
    """Select all companies no dereferencing"""
    Company.many(projection={'departments': {'$sub': Department}})

def test_full_select():
    """Select all employees and their referenced companies"""
    Employee.many(projection={
        'company': {
            '$ref': Company,
            'departments': {'$sub': Department}
        }
    })


if __name__ == "__main__":

    # Connect to the database
    connect_to_db()

    # Build the test data
    build_test_data()

    # Run the tests
    #time_it(test_flat_select, 100)
    #time_it(test_embedded_document_select, 100)
    time_it(test_full_select, 100)
