from django.shortcuts import render

def site_home_page(request):
    """Renders the main site home page."""
    return render(request, 'pages/home.html', {'title': 'Home'})
