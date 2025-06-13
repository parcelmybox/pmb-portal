from django.views.generic import ListView
from django.db.models import Q
from .bill_models import Bill
from .forms import BillFilterForm

class BillFilterView(ListView):
    model = Bill
    template_name = 'shipping/billing/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
            
        if search:
            queryset = queryset.filter(
                Q(customer__username__icontains=search) |
                Q(description__icontains=search) |
                Q(id__icontains=search)
            )
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = BillFilterForm(self.request.GET or None)
        return context
