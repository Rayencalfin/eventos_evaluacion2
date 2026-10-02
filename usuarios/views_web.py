"""
==============================================================================
MÓDULO: USUARIOS - VISTAS WEB (SESIÓN)
==============================================================================
Controladores para autenticación mediante sesión de Django en el frontend web.
==============================================================================
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import LoginForm, RegistroForm
from .models import Usuario


def login_web(request):
    """
    Procesa el inicio de sesión web mediante formularios y cookies de sesión.
    """
    if request.user.is_authenticated:
        return redirect('eventos_web:index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"¡Bienvenido de nuevo, {user.first_name or user.email}!")
            return redirect('eventos_web:index')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def registro_web(request):
    """
    Procesa el registro de un nuevo usuario asignando obligatoriamente el rol
    de Espectador y encriptando la clave mediante set_password().
    """
    if request.user.is_authenticated:
        return redirect('eventos_web:index')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.rol = Usuario.RolChoices.ESPECTADOR
            usuario.save()

            login(request, usuario)
            messages.success(request, "¡Cuenta creada con éxito! Se ha iniciado sesión automáticamente.")
            return redirect('eventos_web:index')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def logout_web(request):
    """
    Cierra la sesión web del usuario mediante petición POST segura.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('eventos_web:index')