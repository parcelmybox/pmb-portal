from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from ..models import SupportRequest
from ..serializers import SupportRequestSerializer

User = get_user_model()

class SupportRequestAssignmentTest(APITestCase):
    def setUp(self):
        # Create test staff users
        self.staff1 = User.objects.create_user(
            username='staff1',
            email='staff1@example.com',
            password='testpass123',
            is_staff=True
        )
        self.staff2 = User.objects.create_user(
            username='staff2',
            email='staff2@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = '/api/support-requests/'  # Using direct URL since we don't have a namespace
        
    def test_support_request_assignment(self):
        """Test that support requests are assigned to staff members"""
        # Create multiple support requests
        for i in range(5):
            data = {
                'contact': f'test{i}@example.com',
                'subject': f'Test Support Request {i}',
                'message': 'This is a test message',
                'name': f'Test User {i}'
            }
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify the ticket was created and assigned
            ticket_id = response.data.get('id')
            self.assertIsNotNone(ticket_id)
            
            # Check the ticket in the database
            ticket = SupportRequest.objects.get(id=ticket_id)
            self.assertIsNotNone(ticket.assigned_to)
            self.assertTrue(ticket.assigned_to.is_staff)
            
            # Print assignment info for debugging
            print(f"Ticket {ticket_id} assigned to: {ticket.assigned_to.username}")
        
        # Verify distribution of tickets
        staff1_count = SupportRequest.objects.filter(assigned_to=self.staff1).count()
        staff2_count = SupportRequest.objects.filter(assigned_to=self.staff2).count()
        
        print(f"\nTicket distribution - Staff1: {staff1_count}, Staff2: {staff2_count}")
        
        # Verify that both staff members received at least one ticket
        self.assertGreater(staff1_count, 0, "Staff1 should have at least one ticket")
        self.assertGreater(staff2_count, 0, "Staff2 should have at least one ticket")
        
    def test_unauthenticated_request(self):
        """Test that unauthenticated users can create support requests"""
        self.client.logout()  # Ensure no user is authenticated
        
        data = {
            'contact': 'anon@example.com',
            'subject': 'Anonymous Support Request',
            'message': 'This is an anonymous test message',
            'name': 'Anonymous User'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the ticket was created and assigned
        ticket_id = response.data.get('id')
        ticket = SupportRequest.objects.get(id=ticket_id)
        
        self.assertIsNotNone(ticket.assigned_to)
        self.assertTrue(ticket.assigned_to.is_staff)
        self.assertIsNone(ticket.created_by)  # Should be None for anonymous users
