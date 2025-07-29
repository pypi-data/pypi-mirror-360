from __future__ import annotations

import random
import tkinter as tk
import tkinter.font as tkfont

from typing import Any, Callable

from stanfordpy.graphics.click_tracker import ClickTracker
from stanfordpy.graphics.keyboard_tracker import KeyboardTracker

from .colors import get_html_color
from .utils import union_to_list

# In standard Tkinter, object IDs are integers. On web, they are strings.
ObjectId = int

# In standard Tkinter, colors are strings or None (transparent). On web, they
# are strings.
Color = str | None

# In standard Tkinter, transparent is None. On web, it's "transparent".
TRANSPARENT = None


class Canvas:

    DEFAULT_WIDTH = 400
    """The default width of the canvas is 400."""

    ANCHURA_PREDETERMINADA = DEFAULT_WIDTH
    """El ancho predeterminado del canvas es de 400."""

    ANCHO_PREDETERMINADO = DEFAULT_WIDTH
    """El ancho predeterminado del canvas es de 400."""

    DEFAULT_HEIGHT = 400
    """The default height of the canvas is 400."""

    ALTURA_PREDETERMINADA = DEFAULT_HEIGHT
    """La altura predeterminada del canvas es de 400."""

    def __init__(
        self,
        width: float | int = DEFAULT_WIDTH,
        height: float | int = DEFAULT_HEIGHT,
    ):
        self.canvas: tk.Canvas | None = None
        # If there is already a default root (e.g. in the REPL), use that.
        # Otherwise, create a new root.
        if not tk._default_root:
            self._root = tk.Tk()
        else:
            self._root = tk.Toplevel(tk._default_root)
        try:
            self.canvas = tk.Canvas(self._root, width=width, height=height)
            self.canvas.pack()
        except Exception as e:
            raise Exception(f"Error creating canvas: {e}")
        self.click_tracker = ClickTracker(self.canvas)
        self.keyboard_tracker = KeyboardTracker(self.canvas)

    def set_canvas_background_color(self, color: Color) -> None:
        self.__assert_param(
            color, union_to_list(Color), "color", "set_canvas_background_color"
        )
        self.canvas.configure(bg=get_html_color(color))
        self.canvas.update()

    def establecer_color_fondo(self, color: Color) -> None:
        """Compare with set_canvas_background_color"""
        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "establecer_color_fondo"
        )
        self.set_canvas_background_color(color)

    def get_canvas_background_color(self) -> Color:
        return self.canvas.cget("bg")

    def obtener_color_fondo(self) -> Color:
        """Compare with get_canvas_background_color"""
        return self.get_canvas_background_color()

    def get_width(self) -> float | int:
        return self.canvas.winfo_width()

    def obtener_anchura_lienzo(self) -> float | int:
        """Compare with get_width"""
        return self.get_width()

    def obtener_ancho_lienzo(self) -> float | int:
        """Compare with get_width"""
        return self.get_width()

    def get_height(self) -> float | int:
        return self.canvas.winfo_height()

    def obtener_altura_lienzo(self) -> float | int:
        """Compare with get_height"""
        return self.get_height()

    def create_line(
        self,
        x1: float | int,
        y1: float | int,
        x2: float | int,
        y2: float | int,
        color: Color = "black",
    ) -> ObjectId:
        self.__assert_param(x1, [float, int], "x1", "create_line")
        self.__assert_param(y1, [float, int], "y1", "create_line")
        self.__assert_param(x2, [float, int], "x2", "create_line")
        self.__assert_param(y2, [float, int], "y2", "create_line")
        self.__assert_param(color, union_to_list(Color), "color", "create_line")

        object_id = self.canvas.create_line(x1, y1, x2, y2, fill=get_html_color(color))
        self.canvas.update()
        return object_id

    def crear_línea(
        self,
        x1: float | int,
        y1: float | int,
        x2: float | int,
        y2: float | int,
        color: Color = "negro",
    ) -> ObjectId:
        """Compare with `create_line`"""
        self.__asegurar_parametro(x1, [float, int], "x1", "crear_línea")
        self.__asegurar_parametro(y1, [float, int], "y1", "crear_línea")
        self.__asegurar_parametro(x2, [float, int], "x2", "crear_línea")
        self.__asegurar_parametro(y2, [float, int], "y2", "crear_línea")
        self.__asegurar_parametro(color, union_to_list(Color), "color", "crear_línea")

        return self.create_line(x1, y1, x2, y2, color)

    def crear_linea(
        self,
        x1: float | int,
        y1: float | int,
        x2: float | int,
        y2: float | int,
        color: Color = "negro",
    ) -> ObjectId:
        """Compare with `create_line`"""
        self.__asegurar_parametro(x1, [float, int], "x1", "crear_linea")
        self.__asegurar_parametro(y1, [float, int], "y1", "crear_linea")
        self.__asegurar_parametro(x2, [float, int], "x2", "crear_linea")
        self.__asegurar_parametro(y2, [float, int], "y2", "crear_linea")
        self.__asegurar_parametro(color, union_to_list(Color), "color", "crear_linea")

        return self.create_line(x1, y1, x2, y2, color)

    def create_rectangle(
        self,
        leftX: float | int,
        topY: float | int,
        rightX: float | int,
        bottomY: float | int,
        color: Color = "black",
        outline: Color = TRANSPARENT,
    ) -> ObjectId:
        self.__assert_param(leftX, [float, int], "leftX", "create_rectangle")
        self.__assert_param(topY, [float, int], "topY", "create_rectangle")
        self.__assert_param(rightX, [float, int], "rightX", "create_rectangle")
        self.__assert_param(bottomY, [float, int], "bottomY", "create_rectangle")
        self.__assert_param(color, union_to_list(Color), "color", "create_rectangle")
        self.__assert_param(
            outline, union_to_list(Color), "outline", "create_rectangle"
        )

        object_id = self.canvas.create_rectangle(
            leftX,
            topY,
            rightX,
            bottomY,
            fill=get_html_color(color),
            outline=get_html_color(outline),
        )
        self.canvas.update()
        return object_id

    def crear_rectángulo(
        self,
        x_izquierda: float | int,
        y_superior: float | int,
        x_derecha: float | int,
        y_inferior: float | int,
        color: str = "negro",
        contorno: str = "transparente",
    ) -> ObjectId:
        """Compare with `create_rectangle`"""
        self.__asegurar_parametro(
            x_izquierda, [float, int], "x_izquierda", "crear_rectángulo"
        )
        self.__asegurar_parametro(
            y_superior, [float, int], "y_superior", "crear_rectángulo"
        )
        self.__asegurar_parametro(
            x_derecha, [float, int], "x_derecha", "crear_rectángulo"
        )
        self.__asegurar_parametro(
            y_inferior, [float, int], "y_inferior", "crear_rectángulo"
        )
        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "crear_rectángulo"
        )
        self.__asegurar_parametro(
            contorno, union_to_list(Color), "contorno", "crear_rectángulo"
        )
        return self.create_rectangle(
            x_izquierda, y_superior, x_derecha, y_inferior, color, contorno
        )

    def crear_rectangulo(
        self,
        x_izquierda: float | int,
        y_superior: float | int,
        x_derecha: float | int,
        y_inferior: float | int,
        color: str = "negro",
        contorno: str = "transparente",
    ) -> ObjectId:
        """Compare with create_rectangle"""
        self.__asegurar_parametro(
            x_izquierda, [float, int], "x_izquierda", "crear_rectangulo"
        )
        self.__asegurar_parametro(
            y_superior, [float, int], "y_superior", "crear_rectangulo"
        )
        self.__asegurar_parametro(
            x_derecha, [float, int], "x_derecha", "crear_rectangulo"
        )
        self.__asegurar_parametro(
            y_inferior, [float, int], "y_inferior", "crear_rectangulo"
        )
        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "crear_rectangulo"
        )
        self.__asegurar_parametro(
            contorno, union_to_list(Color), "contorno", "crear_rectangulo"
        )
        return self.create_rectangle(
            x_izquierda, y_superior, x_derecha, y_inferior, color, contorno
        )

    def create_oval(
        self,
        x1: float | int,
        y1: float | int,
        x2: float | int,
        y2: float | int,
        color: Color = "black",
        outline: Color = TRANSPARENT,
    ) -> ObjectId:
        self.__assert_param(x1, [float, int], "x1", "create_oval")
        self.__assert_param(y1, [float, int], "y1", "create_oval")
        self.__assert_param(x2, [float, int], "x2", "create_oval")
        self.__assert_param(y2, [float, int], "y2", "create_oval")
        self.__assert_param(color, union_to_list(Color), "color", "create_oval")
        self.__assert_param(outline, union_to_list(Color), "outline", "create_oval")

        object_id = self.canvas.create_oval(
            x1, y1, x2, y2, fill=get_html_color(color), outline=get_html_color(outline)
        )
        self.canvas.update()
        return object_id

    def crear_óvalo(
        self,
        x1: float | int,
        y1: float | int,
        x2: float | int,
        y2: float | int,
        color: Color = "negro",
        contorno: Color = TRANSPARENT,
    ) -> ObjectId:
        """Compare with `create_oval`"""
        self.__asegurar_parametro(x1, [float, int], "x1", "crear_óvalo")
        self.__asegurar_parametro(y1, [float, int], "y1", "crear_óvalo")
        self.__asegurar_parametro(x2, [float, int], "x2", "crear_óvalo")
        self.__asegurar_parametro(y2, [float, int], "y2", "crear_óvalo")
        self.__asegurar_parametro(color, union_to_list(Color), "color", "crear_óvalo")
        self.__asegurar_parametro(
            contorno, union_to_list(Color), "contorno", "crear_óvalo"
        )
        return self.create_oval(x1, y1, x2, y2, color, contorno)

    def crear_ovalo(
        self,
        x1: float | int,
        y1: float | int,
        x2: float | int,
        y2: float | int,
        color: Color = "negro",
        contorno: Color = TRANSPARENT,
    ) -> ObjectId:
        """Compare with `create_oval`"""
        self.__asegurar_parametro(x1, [float, int], "x1", "crear_ovalo")
        self.__asegurar_parametro(y1, [float, int], "y1", "crear_ovalo")
        self.__asegurar_parametro(x2, [float, int], "x2", "crear_ovalo")
        self.__asegurar_parametro(y2, [float, int], "y2", "crear_ovalo")
        self.__asegurar_parametro(color, union_to_list(Color), "color", "crear_ovalo")
        self.__asegurar_parametro(
            contorno, union_to_list(Color), "contorno", "crear_ovalo"
        )
        return self.create_oval(x1, y1, x2, y2, color, contorno)

    def create_image(self, x: float | int, y: float | int, filePath: str) -> ObjectId:
        self.__assert_param(x, [float, int], "x", "create_image")
        self.__assert_param(y, [float, int], "y", "create_image")
        self.__assert_param(filePath, [str], "filePath", "create_image")

        object_id = self.canvas.create_image(x, y, image=tk.PhotoImage(file=filePath))
        self.canvas.update()
        return object_id

    def crear_imagen(
        self,
        x: float | int,
        y: float | int,
        ruta_archivo: str,
    ) -> ObjectId:
        """Compare with `create_image`"""
        self.__asegurar_parametro(x, [float, int], "x", "crear_imagen")
        self.__asegurar_parametro(y, [float, int], "y", "crear_imagen")
        self.__asegurar_parametro(ruta_archivo, [str], "ruta_archivo", "crear_imagen")
        return self.create_image(x, y, ruta_archivo)

    def create_image_with_size(
        self,
        x: float | int,
        y: float | int,
        width: float | int,
        height: float | int,
        filePath: str,
    ) -> ObjectId:
        self.__assert_param(x, [float, int], "x", "create_image_with_size")
        self.__assert_param(y, [float, int], "y", "create_image_with_size")
        self.__assert_param(filePath, [str], "filePath", "create_image_with_size")
        self.__assert_param(width, [float, int], "width", "create_image_with_size")
        self.__assert_param(height, [float, int], "height", "create_image_with_size")

        object_id = self.canvas.create_image(
            x, y, image=tk.PhotoImage(file=filePath), width=width, height=height
        )
        self.canvas.update()
        return object_id

    def crear_imagen_con_tamaño(
        self,
        x: float | int,
        y: float | int,
        ancho: float | int,
        altura: float | int,
        ruta_archivo: str,
    ) -> ObjectId:
        """Compare with `create_image_with_size`"""
        self.__asegurar_parametro(x, [float, int], "x", "crear_imagen_con_tamaño")
        self.__asegurar_parametro(y, [float, int], "y", "crear_imagen_con_tamaño")
        self.__asegurar_parametro(
            ancho, [float, int], "ancho", "crear_imagen_con_tamaño"
        )
        self.__asegurar_parametro(
            altura, [float, int], "altura", "crear_imagen_con_tamaño"
        )
        self.__asegurar_parametro(
            ruta_archivo, [str], "ruta_archivo", "crear_imagen_con_tamaño"
        )
        return self.create_image_with_size(x, y, ancho, altura, ruta_archivo)

    def crear_imagen_con_tamano(
        self,
        x: float | int,
        y: float | int,
        ancho: float | int,
        altura: float | int,
        ruta_archivo: str,
    ) -> ObjectId:
        """Compare with `create_image_with_size`"""
        self.__asegurar_parametro(x, [float, int], "x", "crear_imagen_con_tamano")
        self.__asegurar_parametro(y, [float, int], "y", "crear_imagen_con_tamano")
        self.__asegurar_parametro(
            ancho, [float, int], "ancho", "crear_imagen_con_tamano"
        )
        self.__asegurar_parametro(
            altura, [float, int], "altura", "crear_imagen_con_tamano"
        )
        self.__asegurar_parametro(
            ruta_archivo, [str], "ruta_archivo", "crear_imagen_con_tamano"
        )
        return self.create_image_with_size(x, y, ancho, altura, ruta_archivo)

    # What is anchor
    def create_text(
        self,
        x: float | int,
        y: float | int,
        text: str,
        font: str = "Arial",
        font_size: str | int = "12px",
        color: Color = "BLACK",
        anchor: str = "NW",
    ) -> ObjectId:
        """Compare with `create_text`"""
        self.__assert_param(text, [str], "text", "create_text")
        self.__assert_param(x, [float, int], "x", "create_text")
        self.__assert_param(y, [float, int], "y", "create_text")
        self.__assert_param(font_size, [str, int], "font_size", "create_text")
        self.__assert_param(font, [str], "font_type", "create_text")
        self.__assert_param(color, union_to_list(Color), "font_color", "create_text")

        object_id = self.canvas.create_text(
            x,
            y,
            text=text,
            font=(font, self.__build_font_size(font_size)),
            fill=get_html_color(color),
            anchor=anchor,
        )
        self.canvas.update()
        return object_id

    def crear_texto(
        self,
        x: float | int,
        y: float | int,
        texto: str,
        fuente: str = "Arial",
        tamano: str | int = "12px",
        color: Color = "negro",
        ancla: str = "NW",
    ) -> ObjectId:
        """Compare with `create_text`"""
        self.__asegurar_parametro(x, [float, int], "x", "crear_texto")
        self.__asegurar_parametro(y, [float, int], "y", "crear_texto")
        self.__asegurar_parametro(texto, [str], "texto", "crear_texto")
        self.__asegurar_parametro(fuente, [str], "fuente", "crear_texto")
        self.__asegurar_parametro(tamano, [str, int], "tamano", "crear_texto")
        self.__asegurar_parametro(color, union_to_list(Color), "color", "crear_texto")
        self.__asegurar_parametro(ancla, [str], "ancla", "crear_texto")
        return self.create_text(x, y, texto, fuente, tamano, color, ancla)

    def delete(self, objectId: ObjectId) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "delete")
        self.canvas.delete(objectId)
        self.canvas.update()

    def eliminar(self, objectId: ObjectId) -> None:
        """Compare with `delete`"""
        self.__asegurar_parametro(objectId, [ObjectId], "objectId", "eliminar")
        self.delete(objectId)

    def clear(self) -> None:
        self.canvas.delete(tk.ALL)
        self.canvas.update()

    def eliminar_todo(self) -> None:
        """Compare with `clear`"""
        self.clear()

    def find_overlapping(
        self,
        leftX: float | int,
        topY: float | int,
        rightX: float | int,
        bottomY: float | int,
    ) -> list[ObjectId]:
        self.__assert_param(leftX, [float, int], "leftX", "find_overlapping")
        self.__assert_param(topY, [float, int], "topY", "find_overlapping")
        self.__assert_param(rightX, [float, int], "rightX", "find_overlapping")
        self.__assert_param(bottomY, [float, int], "bottomY", "find_overlapping")
        return self.canvas.find_overlapping(leftX, topY, rightX, bottomY)

    def encontrar_superposición(
        self,
        x_izquierda: float | int,
        y_superior: float | int,
        x_derecha: float | int,
        y_inferior: float | int,
    ) -> list[ObjectId]:
        """Compare with `find_overlapping`"""
        self.__asegurar_parametro(
            x_izquierda, [float, int], "x_izquierda", "encontrar_superposición"
        )
        self.__asegurar_parametro(
            y_superior, [float, int], "y_superior", "encontrar_superposición"
        )
        self.__asegurar_parametro(
            x_derecha, [float, int], "x_derecha", "encontrar_superposición"
        )
        self.__asegurar_parametro(
            y_inferior, [float, int], "y_inferior", "encontrar_superposición"
        )
        return self.find_overlapping(x_izquierda, y_superior, x_derecha, y_inferior)

    def encontrar_superposicion(
        self,
        x_izquierda: float | int,
        y_superior: float | int,
        x_derecha: float | int,
        y_inferior: float | int,
    ) -> list[str]:
        """Compare with `find_overlapping`"""
        self.__asegurar_parametro(
            x_izquierda, [float, int], "x_izquierda", "encontrar_superposicion"
        )
        self.__asegurar_parametro(
            y_superior, [float, int], "y_superior", "encontrar_superposicion"
        )
        self.__asegurar_parametro(
            x_derecha, [float, int], "x_derecha", "encontrar_superposicion"
        )
        self.__asegurar_parametro(
            y_inferior, [float, int], "y_inferior", "encontrar_superposicion"
        )
        return self.find_overlapping(x_izquierda, y_superior, x_derecha, y_inferior)

    def encontrar_superposiciones(
        self,
        x_izquierda: float | int,
        y_superior: float | int,
        x_derecha: float | int,
        y_inferior: float | int,
    ) -> list[ObjectId]:
        """Compare with `find_overlapping`"""
        self.__asegurar_parametro(
            x_izquierda, [float, int], "x_izquierda", "encontrar_superposiciones"
        )
        self.__asegurar_parametro(
            y_superior, [float, int], "y_superior", "encontrar_superposiciones"
        )
        self.__asegurar_parametro(
            x_derecha, [float, int], "x_derecha", "encontrar_superposiciones"
        )
        self.__asegurar_parametro(
            y_inferior, [float, int], "y_inferior", "encontrar_superposiciones"
        )
        return self.find_overlapping(x_izquierda, y_superior, x_derecha, y_inferior)

    def get_mouse_x(self) -> float | int:
        return self.canvas.winfo_pointerx()

    def obtener_mouse_x(self) -> float | int:
        """Compare with `get_mouse_x`"""
        return self.get_mouse_x()

    def get_mouse_y(self) -> float | int:
        return self.canvas.winfo_pointery()

    def obtener_mouse_y(self) -> float | int:
        """Compare with `get_mouse_y`"""
        return self.get_mouse_y()

    def get_last_click(self) -> tuple[float | int, float | int]:
        return self.click_tracker.get_last_click()

    def obtener_ultimo_clic_mouse(self) -> tuple[float | int, float | int]:
        """Compare with `get_last_click`"""
        return self.get_last_click()

    def get_last_key_press(self) -> str:
        return self.keyboard_tracker.get_last_key()

    def obtener_ultimo_clic_teclado(self) -> str:
        """Compare with `get_last_key_press`"""
        return self.get_last_key_press()

    def sleep(self, delta: float | int, callback: Callable[[], None] | None = None) -> None:
        self.__assert_param(delta, [int, float], "delta", "sleep")
        self.canvas.after(delta, callback)

    def dormir(self, delta: float | int) -> None:
        """Compare with `sleep`"""
        self.__asegurar_parametro(delta, [int, float], "delta", "dormir")
        self.sleep(delta)

    def esperar(self, delta: float | int, callback: Callable[[], None] | None = None) -> None:
        """Compare with `sleep`"""
        self.__asegurar_parametro(delta, [int, float], "delta", "esperar")
        self.sleep(delta, callback)

    def move(self, objectId: ObjectId, dx: float | int, dy: float | int) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "move")
        self.__assert_param(dx, [int, float], "dx", "move")
        self.__assert_param(dy, [int, float], "dy", "move")
        self.canvas.move(objectId, dx, dy)
        self.canvas.update()

    def mover(self, id_objeto: ObjectId, dx: float | int, dy: float | int) -> None:
        """Compare with `move`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "mover")
        self.__asegurar_parametro(dx, [int, float], "dx", "mover")
        self.__asegurar_parametro(dy, [int, float], "dy", "mover")
        self.move(id_objeto, dx, dy)

    def moverse(self, id_objeto: ObjectId, dx: float | int, dy: float | int) -> None:
        """Compare with `move`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "moverse")
        self.__asegurar_parametro(dx, [int, float], "dx", "moverse")
        self.__asegurar_parametro(dy, [int, float], "dy", "moverse")
        self.move(id_objeto, dx, dy)

    def moveto(self, objectId: ObjectId, newX: float | int, newY: float | int) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "moveto")
        self.__assert_param(newX, [int, float], "newX", "moveto")
        self.__assert_param(newY, [int, float], "newY", "moveto")

        self.canvas.moveto(objectId, newX, newY)
        self.canvas.update()

    def mover_hacia(
        self, id_objeto: ObjectId, x_nuevo: float | int, y_nuevo: float | int
    ) -> None:
        """Compare with `moveto`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "mover_hacia")
        self.__asegurar_parametro(x_nuevo, [int, float], "x_nuevo", "mover_hacia")
        self.__asegurar_parametro(y_nuevo, [int, float], "y_nuevo", "mover_hacia")
        self.moveto(id_objeto, x_nuevo, y_nuevo)

    def moverse_hacia(
        self, id_objeto: ObjectId, x_nuevo: float | int, y_nuevo: float | int
    ) -> None:
        """Compare with `moveto`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "moverse_hacia")
        self.__asegurar_parametro(x_nuevo, [int, float], "x_nuevo", "moverse_hacia")
        self.__asegurar_parametro(y_nuevo, [int, float], "y_nuevo", "moverse_hacia")
        self.moveto(id_objeto, x_nuevo, y_nuevo)

    def get_left_x(self, objectId: ObjectId) -> float | int | None:
        self.__assert_param(objectId, [ObjectId], "objectId", "get_left_x")

        return self.canvas.bbox(objectId)[0]

    def obtener_x_izquierda(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_left_x`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "obtener_x_izquierda"
        )
        return self.get_left_x(id_objeto)

    def obtener_x_izq(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_left_x`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "obtener_x_izq")
        return self.get_left_x(id_objeto)

    def get_top_y(self, objectId: ObjectId) -> float | int | None:
        self.__assert_param(objectId, [ObjectId], "objectId", "get_top_y")

        return self.canvas.bbox(objectId)[1]

    def obtener_y_superior(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_top_y`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "obtener_y_superior"
        )
        return self.get_top_y(id_objeto)

    def obtener_y_sup(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_top_y`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "obtener_y_sup")
        return self.get_top_y(id_objeto)

    def get_x(self, objectId: ObjectId) -> float | int | None:
        self.__assert_param(objectId, [ObjectId], "objectId", "get_x")

        return self.canvas.bbox(objectId)[0]

    def obtener_x(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_x`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "obtener_x")
        return self.get_x(id_objeto)

    def get_y(self, objectId: ObjectId) -> float | int | None:
        self.__assert_param(objectId, [ObjectId], "objectId", "get_y")

        return self.canvas.bbox(objectId)[1]

    def obtener_y(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_y`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "obtener_y")
        return self.get_y(id_objeto)

    def get_object_width(self, objectId: ObjectId) -> float | int | None:
        self.__assert_param(objectId, [ObjectId], "objectId", "get_object_width")

        return self.canvas.bbox(objectId)[2] - self.canvas.bbox(objectId)[0]

    def obtener_anchura(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_object_width`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "obtener_anchura")
        return self.get_object_width(id_objeto)

    def obtener_ancho(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_object_width`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "obtener_ancho")
        return self.get_object_width(id_objeto)

    def get_object_height(self, objectId: ObjectId) -> float | int | None:
        self.__assert_param(objectId, [ObjectId], "objectId", "get_object_height")
        bbox = self.canvas.bbox(objectId)
        if bbox is None:
            return None
        return bbox[3] - bbox[1]

    def obtener_altura(self, id_objeto: ObjectId) -> float | int | None:
        """Compare with `get_object_height`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "obtener_altura")
        return self.get_object_height(id_objeto)

    def mainloop(self) -> None:
        return self.canvas.mainloop()

    def repetir(self) -> None:
        """Compare with `mainloop`"""
        return self.mainloop()

    def set_hidden(self, objectId: ObjectId, is_hidden: bool) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "set_hidden")
        self.__assert_param(is_hidden, [bool], "is_hidden", "set_hidden")
        self.canvas.itemconfigure(
            objectId, state="hidden" if is_hidden else "normal"
        )
        self.canvas.update()

    def establecer_oculto(self, id_objeto: ObjectId, es_oculto: bool) -> None:
        """Compare with `set_hidden`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "establecer_oculto"
        )
        self.__asegurar_parametro(es_oculto, [bool], "es_oculto", "establecer_oculto")
        self.set_hidden(id_objeto, es_oculto)

    def set_color(self, objectId: ObjectId, color: Color) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "set_color")
        self.__assert_param(color, union_to_list(Color), "color", "set_color")
        self.canvas.itemconfigure(objectId, fill=get_html_color(color))
        self.canvas.update()

    def establecer_color(self, id_objeto: ObjectId, color: str) -> None:
        """Compare with `set_color`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "establecer_color"
        )
        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "establecer_color"
        )
        self.set_color(id_objeto, color)

    def set_fill_color(self, objectId: ObjectId, color: str) -> None:
        """Compare with `set_color`"""
        return self.set_color(objectId, color)

    def establecer_color_relleno(self, id_objeto: ObjectId, color: str) -> None:
        """Compare with `set_color`"""
        return self.establecer_color(id_objeto, color)

    def set_outline_color(self, objectId: ObjectId, color: Color) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "set_outline_color")
        self.__assert_param(color, union_to_list(Color), "color", "set_outline_color")
        self.canvas.itemconfigure(objectId, outline=get_html_color(color))
        self.canvas.update()

    def establecer_color_contorno(self, id_objeto: ObjectId, color: str) -> None:
        """Compare with `set_outline_color`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "establecer_color_contorno"
        )
        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "establecer_color_contorno"
        )
        return self.set_outline_color(id_objeto, color)

    def set_font(self, objectId: ObjectId, font: str) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "set_font")
        self.__assert_param(font, [str], "font", "set_font")
        font_spec = self.canvas.cget(objectId, "font")
        font_object = tkfont.Font(font=font_spec)
        font_object.configure(family=font)
        self.canvas.itemconfigure(objectId, font=font_object)
        self.canvas.update()

    def establecer_fuente(self, id_objeto: ObjectId, fuente: str) -> None:
        """Compare with `set_font`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "establecer_fuente"
        )
        self.__asegurar_parametro(fuente, [str], "fuente", "establecer_fuente")
        self.set_font(id_objeto, fuente)

    def set_font_size(self, objectId: ObjectId, font_size: str | int) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "set_font_size")
        self.__assert_param(font_size, [str, int], "font_size", "set_font_size")
        font_spec = self.canvas.cget(objectId, "font")
        font_object = tkfont.Font(font=font_spec)
        font_object.configure(size=self.__build_font_size(font_size))
        self.canvas.itemconfigure(objectId, font=font_object)
        self.canvas.update()

    def establecer_tamano_fuente(self, id_objeto: ObjectId, tamano: str | int) -> None:
        """Compare with `set_font_size`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "establecer_tamano_fuente"
        )
        self.__asegurar_parametro(
            tamano, [str, int], "tamano", "establecer_tamano_fuente"
        )
        self.set_font_size(id_objeto, tamano)

    def establecer_tamaño_fuente(self, id_objeto: ObjectId, tamano: str | int) -> None:
        """Compare with `set_font_size`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "establecer_tamaño_fuente"
        )
        self.__asegurar_parametro(
            tamano, [str, int], "tamano", "establecer_tamaño_fuente"
        )
        self.set_font_size(id_objeto, tamano)

    def wait_for_click(self) -> None:
        self.click_tracker.wait_for_click()

    def esperar_por_clic(self) -> None:
        """Compare with `wait_for_click`"""
        self.wait_for_click()

    def change_text(self, objectId: ObjectId, new_text: str) -> None:
        self.__assert_param(objectId, [ObjectId], "objectId", "change_text")
        self.__assert_param(new_text, [str], "new_text", "change_text")
        self.canvas.itemconfigure(objectId, text=new_text)
        self.canvas.update()

    def establecer_texto(self, id_objeto: ObjectId, nuevo_texto: str) -> None:
        """Compare with `change_text`"""
        self.__asegurar_parametro(
            id_objeto, [ObjectId], "id_objeto", "establecer_texto"
        )
        self.__asegurar_parametro(nuevo_texto, [str], "nuevo_texto", "establecer_texto")
        self.change_text(id_objeto, nuevo_texto)

    def cambiar_texto(self, id_objeto: ObjectId, nuevo_texto: str) -> None:
        """Compare with `change_text`"""
        self.__asegurar_parametro(id_objeto, [ObjectId], "id_objeto", "cambiar_texto")
        self.__asegurar_parametro(nuevo_texto, [str], "nuevo_texto", "cambiar_texto")
        self.change_text(id_objeto, nuevo_texto)

    def create_polygon(
        self,
        *args: float | int,
        color: Color = "BLACK",
        outline: Color = TRANSPARENT,
    ) -> ObjectId:
        # Extract the options, if any
        if len(args) % 2 != 0:
            raise ValueError("Coordinates must be provided in pairs.")

        # Process the coordinates
        assert all(
            isinstance(element, (int, float)) for element in args
        ), "Some coordinates are incorrect types. Accepted types include: int, float."

        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "create_polygon"
        )
        self.__asegurar_parametro(
            outline, union_to_list(Color), "outline", "create_polygon"
        )

        # Create your polygon using the coordinates and options
        object_id = self.canvas.create_polygon(
            *args, fill=get_html_color(color), outline=get_html_color(outline)
        )
        self.canvas.update()
        return object_id

    def crear_polígono(
        self,
        *args: float | int,
        color: Color = "negro",
        contorno: Color = TRANSPARENT,
    ) -> ObjectId:
        """Compare with `create_polygon`"""
        if len(args) % 2 != 0:
            raise ValueError("Las coordenadas deben proporcionarse en pares.")

        assert all(
            isinstance(element, (int, float)) for element in args
        ), "Algunas coordenadas son incorrectas. Los tipos aceptados incluyen: int, float."

        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "crear_polígono"
        )
        self.__asegurar_parametro(
            contorno, union_to_list(Color), "contorno", "crear_polígono"
        )
        return self.create_polygon(args, color, contorno)

    def crear_poligono(
        self,
        *args: float | int,
        color: Color = "negro",
        contorno: Color = TRANSPARENT,
    ) -> ObjectId:
        """Compare with `create_polygon`"""
        if len(args) % 2 != 0:
            raise ValueError("Las coordenadas deben proporcionarse en pares.")

        assert all(
            isinstance(element, (int, float)) for element in args
        ), "Algunas coordenadas son incorrectas. Los tipos aceptados incluyen: int, float."

        self.__asegurar_parametro(
            color, union_to_list(Color), "color", "crear_poligono"
        )
        self.__asegurar_parametro(
            contorno, union_to_list(Color), "contorno", "crear_poligono"
        )
        return self.create_polygon(args, color, contorno)

    def get_new_mouse_clicks(self) -> list[tuple[float | int, float | int]]:
        return self.click_tracker.get_new_clicks()

    def obtener_nuevos_clics_mouse(self) -> list[tuple[float | int, float | int]]:
        """Compare with `get_new_mouse_clicks`"""
        return self.get_new_mouse_clicks()

    def get_new_key_presses(self) -> list[str]:
        return self.keyboard_tracker.get_new_keys()

    def obtener_nuevos_clics_teclado(self) -> list[str]:
        """Compare with `get_new_key_presses`"""
        return self.get_new_key_presses()

    def coords(self, objectId: str) -> tuple[float | int, float | int]:
        self.__assert_param(objectId, [str], "objectId", "coords")
        return self.canvas.coords(objectId)

    def coordenadas(self, id_objeto: str) -> tuple[float | int, float | int]:
        """Compare with `coords`"""
        self.__asegurar_parametro(id_objeto, [str], "id_objeto", "coordenadas")
        return self.coords(id_objeto)

    def get_random_color(self) -> Color:
        return "#" + "".join([hex(random.randint(0, 255))[2:] for _ in range(3)])

    def obtener_color_aleatorio(self) -> Color:
        return self.get_random_color()

    # def create_button(self, title, location):
    #     self.__assert_param(title, [str], "title", "create_button")
    #     self.__assert_param(location, [str], "location", "create_button")
    #     return self.canvas.create_button(title, location)

    # def get_new_button_clicks(self):
    #     return self.canvas.get_new_button_clicks()

    # def create_text_field(self, label, location):
    #     self.__assert_param(label, [str], "label", "create_text_field")
    #     self.__assert_param(location, [str], "location", "create_text_field")
    #     return self.canvas.create_text_field(label, location)

    # def delete_text_field(self, text_field_name):
    #     self.__assert_param(text_field_name, [str], "text_field_name", "delete_text_field")
    #     return self.canvas.delete_text_field(text_field_name)

    # def get_text_field_text(self, text_field_name):
    #     self.__assert_param(text_field_name, [str], "text_field_name", "get_text_field_text")
    #     return self.canvas.get_text_field_text(text_field_name)

    def __assert_param(
        self,
        var: Any,
        var_types: list[type],
        param_name: str,
        function_name: str,
    ) -> None:
        assert type(var) in var_types, (
            param_name
            + " should be one of the following types: "
            + ", ".join([x.__name__ for x in var_types])
            + " in function "
            + function_name
            + ". Recieved "
            + type(var).__name__
            + " instead."
        )

    def __asegurar_parametro(
        self,
        var: Any,
        tipos_esperados: list[type],
        nombre_parametro: str,
        nombre_funcion: str,
    ) -> None:
        """Compare with `__assert_param`"""
        assert type(var) in tipos_esperados, (
            nombre_parametro
            + " debe ser uno de los siguientes tipos: "
            + ", ".join([x.__name__ for x in tipos_esperados])
            + " en la función "
            + nombre_funcion
            + ". En cambio, se recibió "
            + type(var).__name__
        )

    def __build_font_size(self, font_size: str | int) -> int:
        if isinstance(font_size, int):
            return font_size
        return int(font_size.replace("px", "").strip())


Lienzo = Canvas


def create_canvas(width: float | int, height: float | int) -> Canvas:
    return Canvas(width, height)


def crear_lienzo(anchura: float | int, altura: float | int) -> Lienzo:
    """Compare with `create_canvas`"""
    return Lienzo(anchura, altura)
