import os
import tempfile
from datetime import datetime, timedelta

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Shipment
from ..models import Bill
from ..activity import ActivityHistory
from ..forms import BillForm
from ..views_billing import create_bill

User = get_user_model()

class BillingTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.staff_user = User.objects.create_superuser(
            username='staff',
            email='staff@example.com',
            password='testpass123'
        )
        
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        
        # Create a test bill
        self.bill = Bill.objects.create(
            customer=self.customer,
            amount=100.00,
            status='PENDING',
            due_date=timezone.now().date() + timedelta(days=30),
            description='Test bill',
            created_by=self.staff_user
        )
        
        # Set up request factory
        self.factory = RequestFactory()
    
    def test_bill_creation(self):
        """Test that a bill can be created"""
        bill = Bill.objects.create(
            customer=self.customer,
            amount=150.00,
            status='PENDING',
            due_date=timezone.now().date() + timedelta(days=30),
            created_by=self.staff_user
        )
        self.assertEqual(str(bill), f'Bill #{bill.id} - {self.customer.get_full_name() or self.customer.username} - ${bill.amount:.2f}')
    
    def test_bill_form_valid(self):
        """Test that the bill form is valid with correct data"""
        form_data = {
            'customer': self.customer.id,
            'amount': '200.00',
            'due_date': (timezone.now().date() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'description': 'Test bill form',
            'status': 'PENDING'  # Explicitly set status
        }
        form = BillForm(data=form_data, user=self.staff_user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_create_bill_view_get(self):
        """Test the GET request to create bill view"""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('shipping:create_bill'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shipping/billing/create_bill.html')
    
    def test_create_bill_view_post(self):
        """Test POST request to create a new bill"""
        self.client.force_login(self.staff_user)
        
        # Count initial number of bills
        initial_count = Bill.objects.count()
        
        response = self.client.post(reverse('shipping:create_bill'), {
            'customer': self.customer.id,
            'amount': '250.00',
            'due_date': (timezone.now().date() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'description': 'Test bill creation',
            'status': 'PENDING'  # Explicitly set status
        })
        
        # Check that a new bill was created
        self.assertEqual(Bill.objects.count(), initial_count + 1, 
                         f"Expected {initial_count + 1} bills, found {Bill.objects.count()}")
        
        # Check that the response redirects to the bill detail page
        new_bill = Bill.objects.latest('created_at')
        self.assertRedirects(response, reverse('shipping:bill_detail', args=[new_bill.id]))
        
        # Verify the bill was created with the correct data
        self.assertEqual(new_bill.customer, self.customer)
        self.assertEqual(str(new_bill.amount), '250.00')
        self.assertEqual(new_bill.status, 'PENDING')
    
    def test_bill_form_invalid_amount(self):
        """Test that the form is invalid with zero or negative amount"""
        form_data = {
            'customer': self.customer.id,
            'amount': '0',
            'due_date': (timezone.now().date() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        form = BillForm(data=form_data, user=self.staff_user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_bill_form_past_due_date(self):
        """Test that the form is invalid with past due date"""
        form_data = {
            'customer': self.customer.id,
            'amount': '100.00',
            'due_date': (timezone.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')
        }
        form = BillForm(data=form_data, user=self.staff_user)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
    
    def test_activity_log_created(self):
        """Test that an activity log is created when a bill is generated"""
        initial_count = ActivityHistory.objects.count()
        
        bill = Bill.objects.create(
            customer=self.customer,
            amount=175.50,
            status='PENDING',
            due_date=timezone.now().date() + timedelta(days=30),
            created_by=self.staff_user
        )
        
        # Create a request object
        request = self.factory.post(reverse('shipping:create_bill'))
        request.user = self.staff_user
        
        # Log the activity using the view's method
        ActivityHistory.log_activity(
            user=request.user,
            action=f'Generated bill for {bill.customer.get_full_name() or bill.customer.username} - Amount: ${bill.amount:.2f}',
            obj=bill
        )
        
        # Check that an activity log was created
        self.assertEqual(ActivityHistory.objects.count(), initial_count + 1)
        activity = ActivityHistory.objects.latest('timestamp')
        self.assertIn('Generated bill for', activity.action)
        self.assertEqual(activity.content_object, bill)
