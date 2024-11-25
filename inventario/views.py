from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Producto
from .forms import ProductoForm
from usuarios.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def inventario_view(request):
    productos = Producto.objects.all()

    # Filtrar los productos con stock bajo y crear mensajes de advertencia
    low_stock_messages = [
        f"Advertencia: El stock de '{producto.nombre}' es bajo ({producto.stock} unidades)."
        for producto in productos if producto.es_stock_bajo()
    ]

    # Obtener el tipo de usuario y verificar si es 'jefe' o 'empleado'
    user_type = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_type = user_profile.user_type  # Esto debería ser 'jefe' o 'empleado'
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado.')
        return redirect('inventario')  # Redireccionar si el perfil no existe

    # Verificar si success=true está en los parámetros de la URL
    success = request.GET.get('success') == 'true'

    return render(request, 'inventario/inventario.html', {
        'productos': productos,
        'low_stock_messages': low_stock_messages,  # Pasar los mensajes de advertencia de stock bajo
        'user_type': user_type,
        'success': success  # Pasar el indicador de éxito al contexto
    })

@login_required
def agregar_producto(request):
    # Verificar que el usuario sea jefe antes de permitir la adición de productos
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'jefe':
            messages.error(request, 'No tienes permisos para agregar productos.')
            return redirect('inventario')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado.')
        return redirect('inventario')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirigir con el parámetro de éxito
            return HttpResponseRedirect(f"{reverse('inventario')}?success=true")
    else:
        form = ProductoForm()

    return render(request, 'inventario/agregar_producto.html', {'form': form})

@login_required
def editar_producto(request, id):
    # Verificar que el usuario sea jefe antes de permitir la edición de productos
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'jefe':
            messages.error(request, 'No tienes permisos para editar productos.')
            return redirect('inventario')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado.')
        return redirect('inventario')

    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto editado correctamente.')
            return redirect('inventario')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/editar_producto.html', {'form': form, 'producto': producto})

@login_required
def eliminar_producto(request, id):
    # Verificar que el usuario sea jefe antes de permitir la eliminación de productos
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'jefe':
            messages.error(request, 'No tienes permisos para eliminar productos.')
            return redirect('inventario')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado.')
        return redirect('inventario')

    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('inventario')
    return render(request, 'inventario/eliminar_producto.html', {'producto': producto})
