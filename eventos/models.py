from django.db import models


class Artista(models.Model):
    """Modelo para representar a los artistas o bandas musicales."""
    nombre = models.CharField(max_length=150, unique=True)
    genero = models.CharField(max_length=100, default='Música')
    # Campo para almacenar la URL de la imagen del artista/grupo sin límite estricto
    imagen = models.URLField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Recinto(models.Model):
    """Modelo para representar los lugares o recintos donde se realizan los eventos."""
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100, default='Santiago')

    def __str__(self):
        return f"{self.nombre} ({self.ciudad})"


class Evento(models.Model):
    """Modelo principal de eventos o conciertos."""
    titulo = models.CharField(max_length=100)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='eventos')
    recinto = models.ForeignKey(Recinto, on_delete=models.CASCADE, related_name='eventos')
    fecha_hora = models.DateTimeField()
    descripcion = models.TextField(blank=True, null=True)
    
    # Campo extendido para aceptar URLs de imágenes largas (evita el DataError)
    banner = models.URLField(max_length=1000, blank=True, null=True)
    
    estado = models.CharField(max_length=50, default='Activo')

    def __str__(self):
        return self.titulo


class Sector(models.Model):
    """Modelo para los sectores de entradas por cada evento."""
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='sectores')
    nombre_sector = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Se adapta al nombre de capacidad/stock según tu base de datos
    capacidad = models.PositiveIntegerField(default=100)
    stock_disponible = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.nombre_sector} - {self.evento.titulo} (${self.precio})"