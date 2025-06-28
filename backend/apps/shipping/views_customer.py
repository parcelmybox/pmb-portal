from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View
import json

User = get_user_model()

class CustomerSearchView(View):
    """
    View to handle customer search for autocomplete functionality
    """
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        
        if not term:
            return JsonResponse([], safe=False)
        
        # Search in username, email, first_name, and last_name
        users = User.objects.filter(
            Q(username__icontains=term) |
            Q(email__iexact=term) |
            Q(email__icontains=term) |
            Q(first_name__icontains=term) |
            Q(last_name__icontains=term) |
            Q(first_name__istartswith=term.split()[0] if term else '')
        ).distinct()[:10]  # Limit to 10 results
        
        results = []
        for user in users:
            display_name = f"{user.get_full_name() or user.username}"
            if user.email:
                display_name += f" ({user.email})"
                
            results.append({
                'id': user.id,
                'label': display_name,
                'value': user.get_full_name() or user.username
            })
        
        # If no results found, try a more flexible search
        if not results and ' ' in term:
            terms = term.split()
            if len(terms) > 1:
                users = User.objects.filter(
                    Q(first_name__icontains=terms[0]) & Q(last_name__icontains=terms[-1])
                ).distinct()[:10]
                
                for user in users:
                    display_name = f"{user.get_full_name() or user.username}"
                    if user.email:
                        display_name += f" ({user.email})"
                        
                    results.append({
                        'id': user.id,
                        'label': display_name,
                        'value': user.get_full_name() or user.username
                    })
        
        # Debug output
        print(f"\n=== CUSTOMER SEARCH ===")
        print(f"Term: {term}")
        print(f"Results: {json.dumps(results, indent=2, default=str)}")
        
        return JsonResponse(results, safe=False)
