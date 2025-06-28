from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category
from .forms import CategoryForm

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category/category_list.html', {'categories': categories})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Category created successfully')
            return redirect('category:category_list')
    else:
        form = CategoryForm()
    return render(request, 'category/category_form.html', {'form': form})

def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('category:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category/category_form.html', {'form': form})

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully')
        return redirect('category:category_list')
    return render(request, 'category/category_confirm_delete.html', {'category': category})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'category/category_detail.html', {'category': category})
