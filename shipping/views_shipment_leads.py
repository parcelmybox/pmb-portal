from django.views.generic import ListView
from .models import ShipmentQuote

class ShipmentLeadsListView(ListView):
    model = ShipmentQuote
    template_name = 'shipping/shipment_leads_list.html'
    context_object_name = 'quotes'
    paginate_by = 20 

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Non staff users see only their own quotes by email
            queryset = queryset.filter(email=self.request.user.email)
        return queryset.order_by('-id')
