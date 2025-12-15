import ctypes
import os
from ctypes import c_double, c_void_p, POINTER

DLL_PATH = os.path.join(os.path.dirname(__file__), "..", "cpp", "build", "Release", "inertia.dll")

try:
    lib = ctypes.CDLL(DLL_PATH)
    
    # Объявляем прототипы функций C-интерфейса
    lib.create_sphere.argtypes = [c_double]
    lib.create_sphere.restype = c_void_p

    lib.create_box.argtypes = [c_double, c_double, c_double]
    lib.create_box.restype = c_void_p

    lib.create_cylinder.argtypes = [c_double, c_double]
    lib.create_cylinder.restype = c_void_p

    lib.calculate_moment.argtypes = [c_void_p, c_double]
    lib.calculate_moment.restype = c_double

    lib.delete_body.argtypes = [c_void_p]
    
    lib.get_body_name.argtypes = [c_void_p]
    lib.get_body_name.restype = ctypes.c_char_p
    
    lib.get_sphere_radius.argtypes = [c_void_p]
    lib.get_sphere_radius.restype = c_double
    
    lib.get_box_dimensions.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    
    lib.get_cylinder_dimensions.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double)]
    
except Exception as e:
    print(f"Ошибка загрузки DLL: {e}")
    print("Убедитесь, что DLL скомпилирована и находится по пути:", DLL_PATH)
    lib = None

# Базовый класс для всех тел
class Body:
    def __init__(self, ptr):
        self._ptr = ptr
        
    def __del__(self):
        if self._ptr and lib:
            lib.delete_body(self._ptr)
            
    def calculate_moment(self, density):
        if not lib:
            raise RuntimeError("DLL не загружена")
        return lib.calculate_moment(self._ptr, density)
    
    @property
    def name(self):
        if not lib:
            return "Unknown"
        return lib.get_body_name(self._ptr).decode('utf-8')
    
    def get_dimensions(self):
        """Возвращает размеры тела в виде словаря"""
        if not lib:
            return {}
        
        if self.name == "Sphere":
            r = lib.get_sphere_radius(self._ptr)
            return {"radius": r}
        elif self.name == "Box":
            a, b, c = c_double(), c_double(), c_double()
            lib.get_box_dimensions(self._ptr, ctypes.byref(a), ctypes.byref(b), ctypes.byref(c))
            return {"a": a.value, "b": b.value, "c": c.value}
        elif self.name == "Cylinder":
            r, h = c_double(), c_double()
            lib.get_cylinder_dimensions(self._ptr, ctypes.byref(r), ctypes.byref(h))
            return {"radius": r.value, "height": h.value}
        return {}

# Конкретные классы тел
class Sphere(Body):
    def __init__(self, radius):
        if not lib:
            raise RuntimeError("DLL не загружена")
        ptr = lib.create_sphere(radius)
        if not ptr:
            raise ValueError("Invalid sphere parameters")
        super().__init__(ptr)

class Box(Body):
    def __init__(self, a, b, c):
        if not lib:
            raise RuntimeError("DLL не загружена")
        ptr = lib.create_box(a, b, c)
        if not ptr:
            raise ValueError("Invalid box parameters")
        super().__init__(ptr)

class Cylinder(Body):
    def __init__(self, radius, height):
        if not lib:
            raise RuntimeError("DLL не загружена")
        ptr = lib.create_cylinder(radius, height)
        if not ptr:
            raise ValueError("Invalid cylinder parameters")
        super().__init__(ptr)

# Класс для работы с файлами
class ResultExporter:
    @staticmethod
    def export_to_txt(results, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Моменты инерции тел:\n")
            f.write("=" * 50 + "\n")
            for i, (body, density, moment) in enumerate(results, 1):
                f.write(f"{i}. {body.name}\n")
                f.write(f"   Плотность: {density} кг/м³\n")
                f.write(f"   Момент инерции: {moment:.6f} кг·м²\n")
                f.write("-" * 30 + "\n")
    
    @staticmethod
    def export_to_pdf(results, filename):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            # Заголовок
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Моменты инерции тел")
            c.line(50, height - 55, width - 50, height - 55)
            
            # Содержание
            c.setFont("Helvetica", 12)
            y = height - 80
            for i, (body, density, moment) in enumerate(results, 1):
                if y < 100:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 12)
                
                text = f"{i}. {body.name}: плотность={density} кг/м³, момент инерции={moment:.6f} кг·м²"
                c.drawString(50, y, text)
                y -= 20
            
            c.save()
        except ImportError:
            raise ImportError("reportlab required for PDF export")

# Контейнер для хранения тел
class BodyContainer:
    def __init__(self):
        self.bodies = []
    
    def add_body(self, body):
        self.bodies.append(body)
    
    def calculate_all_moments(self, density):
        return [(body, density, body.calculate_moment(density)) for body in self.bodies]
    
    def clear(self):
        self.bodies.clear()