from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal
from shipping.models import Bill

class PDFExportTest(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        
        # Create a test bill
        self.bill = Bill.objects.create(
            customer=self.user,
            amount=Decimal('100.00'),
            status='PENDING',
            due_date=datetime.now().date() + timedelta(days=15),
            description='Test Bill'
        )
    
    def test_export_bill_pdf(self):
        """Test that PDF export works correctly"""
        # Login the user
        self.client.force_login(self.user)
        
        # Get the PDF export URL
        url = reverse('shipping:export_bill_pdf', args=[self.bill.id])
        
        # Make the request
        response = self.client.get(url)
        
        # Check that the response is a PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn(f'bill_{self.bill.id}.pdf', response['Content-Disposition'])
        
        # Check that the PDF content is not empty
        self.assertGreater(len(response.content), 1000)  # PDF should be at least 1KB
        
        # Check for some expected content in the PDF
        self.assertIn(b'ParcelMyBox', response.content)  # Company name should be in the PDF
        self.assertIn(b'INVOICE', response.content.upper())
        self.assertIn(str(self.bill.id).encode(), response.content)
