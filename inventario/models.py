from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(verbose_name="Cantidad en Stock")
    stock_minimo = models.PositiveIntegerField(verbose_name="Stock Mínimo", default=10)  # Campo para el stock mínimo
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen del Producto")

    def __str__(self):
        return f"{self.nombre} - ${self.precio} - Stock: {self.stock}"

    def tiene_stock(self, cantidad):
        """
        Verifica si el producto tiene suficiente stock para una cantidad específica.
        Retorna True si hay suficiente stock, de lo contrario False.
        """
        return self.stock >= cantidad

    def es_stock_bajo(self):
        """
        Verifica si el stock actual está por debajo del nivel mínimo.
        """
        return self.stock < self.stock_minimo

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']


class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.IntegerField(verbose_name="Cantidad de Movimiento")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Movimiento")
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción")
    tipo_movimiento = models.CharField(
        max_length=10,
        choices=[('entrada', 'Entrada'), ('salida', 'Salida')],
        verbose_name="Tipo de Movimiento"
    )

    def save(self, *args, **kwargs):
        """
        Actualiza el stock del producto al guardar un movimiento de inventario.
        Si el movimiento es de entrada, incrementa el stock.
        Si el movimiento es de salida, reduce el stock.
        """
        if self.pk is None:  # Solo aplicar el movimiento si es un nuevo registro
            if self.tipo_movimiento == 'entrada':
                self.producto.stock += self.cantidad
            elif self.tipo_movimiento == 'salida':
                if self.cantidad > self.producto.stock:
                    raise ValueError("No hay suficiente stock para realizar esta salida.")
                self.producto.stock -= self.cantidad
            self.producto.save()

            # Verificar si el stock está por debajo del mínimo después de la actualización
            if self.producto.es_stock_bajo():
                # Aquí podrías añadir lógica adicional, como enviar una alerta o registro.
                print(f"Advertencia: El stock de {self.producto.nombre} está por debajo del mínimo.")
                # Agrega más lógica si es necesario: por ejemplo, alertas por correo o logs

        super().save(*args, **kwargs)

    def __str__(self):
        movimiento = "Entrada" if self.tipo_movimiento == 'entrada' else "Salida"
        return f"{movimiento} - {self.producto.nombre} - Cantidad: {self.cantidad} - Fecha: {self.fecha.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']
