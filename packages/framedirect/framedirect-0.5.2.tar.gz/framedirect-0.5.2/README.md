# FrameDirect

**FrameDirect** es una librería en Python para dibujar píxeles directamente en el framebuffer de Linux. Perfecta para proyectos que necesitan control directo del hardware gráfico sin depender de entornos gráficos como X11 o Wayland.


## Características

- Acceso directo al framebuffer `/dev/fb0`
- Dibujo de píxeles a bajo nivel
- Compatible con pantallas de 32 bits de color
- Colores predefinidos para facilitar el uso
- Colores en formato ARGB (en hexadecimal)
- Simple, ligera y sin dependencias pesadas


## Requisitos

- Linux con framebuffer habilitado y acceso a `/dev/fb0`
- Python 3.6 o superior


## Instalación

Puedes instalar la libreria desde PyPi:
```bash
pip install FrameDirect
```

O directamente desde GitHub:

```bash
pip install git+https://github.com/gneval9/FrameDirect.git
```

## Uso básico

```python
import framedirect

framedirect.init()                                              # Inicializa el framebuffer
framedirect.resolution()                                        # Imprime la resolución de la pantalla (Variables: screen_width y screen_height)
                                                                 
framedirect.draw_pixel(100, 100, framedirect.RED)               # Dibuja un píxel rojo en (100, 100)
framedirect.draw_line(200, 200, 300, 300, framedirect.GREEN)    # Dibuja una línea verde de (200, 200) a (300, 300)
framedirect.draw_circle(400, 400, 50, 0xFF0000FF)               # Dibuja un circulo azul en (400, 400) con radio 50px

framedirect.close()                                             # Cierra el framebuffer
```

## Licencia

MIT License


## Autor

Hecho con amor por gneval9 Software <3       Contacto: gneval99@gmail.com
