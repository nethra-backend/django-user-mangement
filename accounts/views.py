from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import CustomUser
from .forms import RegisterForm, UpdateForm

# Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

# Logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')

# Dashboard
@login_required
def dashboard(request):
    total = CustomUser.objects.count()
    active = CustomUser.objects.filter(is_active=True).count()
    admins = CustomUser.objects.filter(role='admin').count()
    return render(request, 'accounts/dashboard.html', {
        'total': total,
        'active': active,
        'admins': admins,
    })

# List all users
@login_required
def user_list(request):
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    users = CustomUser.objects.all()
    if query:
        users = users.filter(username__icontains=query)
    if role:
        users = users.filter(role=role)
    paginator = Paginator(users, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'accounts/user_list.html', {
        'page_obj': page,
        'query': query,
        'role': role
    })

# Create user
@login_required
def user_create(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('user_list')
    else:
        form = RegisterForm()
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Create User'
    })

# Update user
@login_required
def user_update(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
    else:
        form = UpdateForm(instance=user)
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Edit User'
    })

# Delete user
@login_required
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

# Register
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})