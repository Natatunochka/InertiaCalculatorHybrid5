import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QListWidget, QFileDialog, QTabWidget, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from inertia_wrapper import Sphere, Box, Cylinder, BodyContainer, ResultExporter

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


class InertiaGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор моментов инерции твердых тел (ООП + C++ ядро)")
        self.body_container = BodyContainer()
        self.calculation_history = []
        
        self.init_ui()
        self.resize(1200, 700)

    def init_ui(self):
        tabs = QTabWidget()
        
        calc_tab = QWidget()
        self.setup_calculator_tab(calc_tab)
        
        instruction_tab = QWidget()
        self.setup_instruction_tab(instruction_tab)
        
        visualization_tab = QWidget()
        self.setup_visualization_tab(visualization_tab)
        
        tabs.addTab(calc_tab, "Калькулятор")
        tabs.addTab(instruction_tab, "Инструкция")
        tabs.addTab(visualization_tab, "Визуализация")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

    def setup_calculator_tab(self, tab):
        self.shape_box = QComboBox()
        self.shape_box.addItems(["Сфера", "Параллелепипед", "Цилиндр"])
        self.shape_box.currentTextChanged.connect(self.on_shape_changed)

        self.param1 = QLineEdit()
        self.param2 = QLineEdit()
        self.param3 = QLineEdit()
        self.density = QLineEdit("1000")

        self.add_btn = QPushButton("Добавить тело")
        self.calc_btn = QPushButton("Рассчитать все")
        self.clear_btn = QPushButton("Очистить")
        self.export_btn = QPushButton("Экспорт результатов")

        self.result_label = QLabel("Результат: ")
        self.body_list = QListWidget()

        self.figure = Figure(figsize=(6, 5))
        self.canvas = FigureCanvas(self.figure)

        self.add_btn.clicked.connect(self.add_body)
        self.calc_btn.clicked.connect(self.calculate_all)
        self.clear_btn.clicked.connect(self.clear_all)
        self.export_btn.clicked.connect(self.export_results)
        self.body_list.currentRowChanged.connect(self.on_body_selected)

        controls_layout = QVBoxLayout()
        
        params_group = QGroupBox("Параметры тела")
        params_layout = QVBoxLayout()
        params_layout.addWidget(QLabel("Выберите фигуру:"))
        params_layout.addWidget(self.shape_box)
        params_layout.addWidget(QLabel("Параметр 1 (r / a):"))
        params_layout.addWidget(self.param1)
        params_layout.addWidget(QLabel("Параметр 2 (h / b):"))
        params_layout.addWidget(self.param2)
        params_layout.addWidget(QLabel("Параметр 3 (c):"))
        params_layout.addWidget(self.param3)
        params_layout.addWidget(QLabel("Плотность (кг/м³):"))
        params_layout.addWidget(self.density)
        params_group.setLayout(params_layout)
        
        control_group = QGroupBox("Управление")
        control_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.calc_btn)
        buttons_layout.addWidget(self.clear_btn)
        control_layout.addLayout(buttons_layout)
        control_layout.addWidget(self.export_btn)
        control_layout.addWidget(self.result_label)
        control_layout.addWidget(QLabel("Добавленные тела:"))
        control_layout.addWidget(self.body_list)
        control_group.setLayout(control_layout)
        
        controls_layout.addWidget(params_group)
        controls_layout.addWidget(control_group)

        main_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout, 1)
        main_layout.addWidget(self.canvas, 2)
        
        tab.setLayout(main_layout)
        self.on_shape_changed()

    def setup_instruction_tab(self, tab):
        layout = QVBoxLayout()
        instruction_text = QTextEdit()
        instruction_text.setReadOnly(True)
        
        html_content = """
        <h1>Инструкция по использованию калькулятора моментов инерции</h1>
        
        <h2>Что такое момент инерции?</h2>
        <p><b>Момент инерции</b> — это физическая величина, характеризующая распределение массы в теле относительно оси вращения. 
        Он определяет, насколько трудно изменить угловую скорость вращения тела.</p>
        
        <p>Формула момента инерции: <b>I = ∫ r² dm</b>, где:</p>
        <ul>
            <li><b>I</b> — момент инерции (кг·м²)</li>
            <li><b>r</b> — расстояние от элемента массы до оси вращения (м)</li>
            <li><b>dm</b> — элементарная масса (кг)</li>
        </ul>
        
        <h2>Типы тел и формулы</h2>
        
        <h3>1. Сфера</h3>
        <p><b>Формула:</b> I = (2/5) × m × r²</p>
        <p><b>Параметры:</b></p>
        <ul>
            <li><b>Радиус (r)</b> — радиус сферы в метрах</li>
            <li><b>Плотность</b> — плотность материала в кг/м³</li>
        </ul>
        <p><b>Пример:</b> Стальная сфера радиусом 0.5 м и плотностью 7800 кг/м³</p>
        
        <h3>2. Параллелепипед</h3>
        <p><b>Формула:</b> I = (1/12) × m × (b² + c²)</p>
        <p><b>Параметры:</b></p>
        <ul>
            <li><b>a, b, c</b> — размеры сторон в метрах</li>
            <li><b>Плотность</b> — плотность материала в кг/м³</li>
        </ul>
        <p><b>Пример:</b> Алюминиевый параллелепипед 1×2×3 м с плотностью 2700 кг/м³</p>
        
        <h3>3. Цилиндр</h3>
        <p><b>Формула:</b> I = (1/2) × m × r²</p>
        <p><b>Параметры:</b></p>
        <ul>
            <li><b>Радиус (r)</b> — радиус основания в метрах</li>
            <li><b>Высота (h)</b> — высота цилиндра в метрах</li>
            <li><b>Плотность</b> — плотность материала в кг/м³</li>
        </ul>
        <p><b>Пример:</b> Медный цилиндр радиусом 0.3 м, высотой 2 м с плотностью 8960 кг/м³</p>
        
        <h2>Инструкция по использованию</h2>
        <ol>
            <li><b>Выберите тип тела</b> из выпадающего списка</li>
            <li><b>Введите параметры</b> тела в соответствующие поля</li>
            <li><b>Укажите плотность</b> материала в кг/м³</li>
            <li><b>Нажмите "Добавить тело"</b> для добавления в список расчета</li>
            <li><b>Нажмите "Рассчитать все"</b> для вычисления моментов инерции</li>
            <li><b>Выберите тело в списке</b> для просмотра его 3D-визуализации</li>
            <li><b>Используйте "Экспорт результатов"</b> для сохранения данных в файл</li>
            <li><b>Перейдите во вкладку "Визуализация"</b> для анализа результатов</li>
        </ol>
        
        <h2>Полезные значения плотности</h2>
        <ul>
            <li>Алюминий: 2700 кг/м³</li>
            <li>Сталь: 7800 кг/м³</li>
            <li>Медь: 8960 кг/м³</li>
            <li>Дерево: 500-800 кг/м³</li>
            <li>Вода: 1000 кг/м³</li>
        </ul>
        
        <h2>Физический смысл</h2>
        <p>Момент инерции играет во вращательном движении ту же роль, что масса в поступательном. 
        Чем больше момент инерции, тем труднее раскрутить или остановить тело.</p>
        
        <p><b>Применение:</b> расчет маховиков, роторов, маятников, спортивных снарядов и т.д.</p>
        """
        
        instruction_text.setHtml(html_content)
        layout.addWidget(instruction_text)
        tab.setLayout(layout)

    def setup_visualization_tab(self, tab):
        layout = QVBoxLayout()
        self.calc_figure = Figure(figsize=(10, 8))
        self.calc_canvas = FigureCanvas(self.calc_figure)
        self.viz_btn = QPushButton("Сгенерировать визуализацию на основе расчетов")
        self.viz_btn.clicked.connect(self.generate_calculation_visualization)
        layout.addWidget(self.viz_btn)
        layout.addWidget(self.calc_canvas)
        tab.setLayout(layout)

    def generate_calculation_visualization(self):
        self.calc_figure.clear()
        
        if not hasattr(self, 'results') or not self.results:
            ax = self.calc_figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Нет данных для визуализации.\nСначала рассчитайте моменты инерции.', 
                    transform=ax.transAxes, ha='center', va='center', fontsize=12)
            ax.set_axis_off()
            self.calc_canvas.draw()
            return
        
        grid = self.calc_figure.add_gridspec(2, 2)
        
        ax1 = self.calc_figure.add_subplot(grid[0, 0])
        self.plot_actual_inertia_comparison(ax1)
        
        ax2 = self.calc_figure.add_subplot(grid[0, 1])
        self.plot_inertia_contribution(ax2)
        
        ax3 = self.calc_figure.add_subplot(grid[1, 0])
        self.plot_mass_inertia_correlation(ax3)
        
        ax4 = self.calc_figure.add_subplot(grid[1, 1], projection='3d')
        self.plot_actual_mass_distribution(ax4)
        
        self.calc_figure.tight_layout()
        self.calc_canvas.draw()

    def plot_actual_inertia_comparison(self, ax):
        if not hasattr(self, 'results'):
            return
            
        body_names = []
        moments = []
        
        for i, (body, density, moment) in enumerate(self.results):
            dims = body.get_dimensions()
            if body.name == "Sphere":
                name = f"Сфера\nr={dims.get('radius', 0):.2f}м"
            elif body.name == "Box":
                name = f"Пар-д\n{dims.get('a', 0):.1f}×{dims.get('b', 0):.1f}×{dims.get('c', 0):.1f}м"
            elif body.name == "Cylinder":
                name = f"Цилиндр\nr={dims.get('radius', 0):.2f}м"
            else:
                name = f"Тело {i+1}"
                
            body_names.append(name)
            moments.append(moment)
        
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'gold', 'lightpink', 'lightcyan']
        bars = ax.bar(body_names, moments, color=colors[:len(body_names)])
        ax.set_title('Сравнение моментов инерции')
        ax.set_ylabel('Момент инерции (кг·м²)')
        ax.tick_params(axis='x', rotation=45)
        
        for bar, moment in zip(bars, moments):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{moment:.4f}', ha='center', va='bottom', fontsize=9)

    def plot_inertia_contribution(self, ax):
        if not hasattr(self, 'results'):
            return
            
        moments = [moment for _, _, moment in self.results]
        total = sum(moments)
        
        if total == 0:
            ax.text(0.5, 0.5, 'Нет данных', transform=ax.transAxes, ha='center')
            return
        
        labels = []
        for i, (body, density, moment) in enumerate(self.results):
            dims = body.get_dimensions()
            percentage = (moment / total) * 100
            
            if body.name == "Sphere":
                label = f"Сфера\n{percentage:.1f}%"
            elif body.name == "Box":
                label = f"Пар-д\n{percentage:.1f}%"
            elif body.name == "Cylinder":
                label = f"Цил.\n{percentage:.1f}%"
            else:
                label = f"Тело {i+1}\n{percentage:.1f}%"
                
            labels.append(label)
        
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'gold', 'lightpink', 'lightcyan']
        wedges, texts, autotexts = ax.pie(moments, labels=labels, autopct='%1.1f%%', 
                                         colors=colors[:len(moments)])
        ax.set_title('Вклад тел в общий момент инерции')

    def plot_mass_inertia_correlation(self, ax):
        if not hasattr(self, 'results'):
            return
            
        masses = []
        moments = []
        colors = []
        markers = []
        
        for i, (body, density, moment) in enumerate(self.results):
            try:
                if body.name == "Sphere":
                    r = body.get_radius()
                    mass = (4/3) * np.pi * r**3 * density
                    color = 'blue'
                    marker = 'o'
                elif body.name == "Box":
                    dims = body.get_dimensions()
                    mass = dims['a'] * dims['b'] * dims['c'] * density
                    color = 'green'
                    marker = 's'
                elif body.name == "Cylinder":
                    dims = body.get_dimensions()
                    mass = np.pi * dims['radius']**2 * dims['height'] * density
                    color = 'red'
                    marker = '^'
                else:
                    continue
                    
                masses.append(mass)
                moments.append(moment)
                colors.append(color)
                markers.append(marker)
            except:
                continue
        
        if not masses:
            return
            
        for i, (mass, moment, color, marker) in enumerate(zip(masses, moments, colors, markers)):
            ax.scatter(mass, moment, c=color, marker=marker, s=100, alpha=0.7)
            ax.annotate(f'Тело {i+1}', (mass, moment), 
                       xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        if len(masses) > 1:
            z = np.polyfit(masses, moments, 1)
            p = np.poly1d(z)
            mass_range = np.linspace(min(masses), max(masses), 100)
            ax.plot(mass_range, p(mass_range), "r--", alpha=0.5, label='Тренд')
            ax.legend()
        
        ax.set_xlabel('Масса (кг)')
        ax.set_ylabel('Момент инерции (кг·м²)')
        ax.set_title('Корреляция массы и момента инерции')
        ax.grid(True, alpha=0.3)

    def plot_actual_mass_distribution(self, ax):
        if not hasattr(self, 'results'):
            return
            
        if self.results:
            body, density, moment = self.results[0]
            try:
                dims = body.get_dimensions()
                
                if body.name == "Sphere":
                    r = dims.get('radius', 1.0)
                    self.plot_sphere_mass_distribution(ax, r, density)
                    ax.set_title(f"Распределение масс: Сфера r={r:.2f}м")
                elif body.name == "Box":
                    a = dims.get('a', 1.0)
                    b = dims.get('b', 1.0)
                    c = dims.get('c', 1.0)
                    self.plot_box_mass_distribution(ax, a, b, c, density)
                    ax.set_title(f"Распределение масс: Параллелепипед {a:.1f}×{b:.1f}×{c:.1f}м")
                elif body.name == "Cylinder":
                    r = dims.get('radius', 1.0)
                    h = dims.get('height', 1.0)
                    self.plot_cylinder_mass_distribution(ax, r, h, density)
                    ax.set_title(f"Распределение масс: Цилиндр r={r:.2f}м, h={h:.2f}м")
            except Exception as e:
                ax.text(0.5, 0.5, 0.5, f"Ошибка визуализации:\n{e}", 
                        transform=ax.transAxes, ha='center')
        else:
            ax.text(0.5, 0.5, 0.5, "Нет данных", 
                    transform=ax.transAxes, ha='center')

    def plot_sphere_mass_distribution(self, ax, r, density):
        try:
            u = np.linspace(0, 2 * np.pi, 30)
            v = np.linspace(0, np.pi, 30)
            x = r * np.outer(np.cos(u), np.sin(v))
            y = r * np.outer(np.sin(u), np.sin(v))
            z = r * np.outer(np.ones(np.size(u)), np.cos(v))
            
            ax.plot_surface(x, y, z, color='lightblue', alpha=0.3)
            
            for i in range(3):
                ri = r * (i + 1) / 4
                ui = np.linspace(0, 2 * np.pi, 6)
                vi = np.linspace(0, np.pi, 6)
                
                for u_val in ui:
                    for v_val in vi:
                        x_point = ri * np.cos(u_val) * np.sin(v_val)
                        y_point = ri * np.sin(u_val) * np.sin(v_val)
                        z_point = ri * np.cos(v_val)
                        
                        size = (ri / r) ** 2 * 80
                        ax.scatter(x_point, y_point, z_point, s=size, 
                                  color='red', alpha=0.6)
        except Exception as e:
            print(f"Ошибка визуализации сферы: {e}")

    def plot_box_mass_distribution(self, ax, a, b, c, density):
        try:
            vertices = np.array([
                [-a/2, -b/2, -c/2], [a/2, -b/2, -c/2],
                [a/2, b/2, -c/2], [-a/2, b/2, -c/2],
                [-a/2, -b/2, c/2], [a/2, -b/2, c/2],
                [a/2, b/2, c/2], [-a/2, b/2, c/2]
            ])
            
            faces = [
                [vertices[0], vertices[1], vertices[2], vertices[3]],
                [vertices[4], vertices[5], vertices[6], vertices[7]],
                [vertices[0], vertices[1], vertices[5], vertices[4]],
                [vertices[2], vertices[3], vertices[7], vertices[6]],
                [vertices[0], vertices[3], vertices[7], vertices[4]],
                [vertices[1], vertices[2], vertices[6], vertices[5]]
            ]
            
            ax.add_collection3d(Poly3DCollection(faces, facecolors='lightgreen', 
                                               alpha=0.3, linewidths=1))
            
            n_points = 3
            for i in range(n_points):
                for j in range(n_points):
                    for k in range(n_points):
                        x = -a/2 + (i + 0.5) * a / n_points
                        y = -b/2 + (j + 0.5) * b / n_points
                        z = -c/2 + (k + 0.5) * c / n_points
                        
                        distance_sq = x**2 + z**2
                        max_distance_sq = (a/2)**2 + (c/2)**2
                        size = (distance_sq / max_distance_sq) * 150 if max_distance_sq > 0 else 50
                        
                        ax.scatter(x, y, z, s=size, color='red', alpha=0.6)
            
            ax.set_xlim(-a/2, a/2)
            ax.set_ylim(-b/2, b/2)
            ax.set_zlim(-c/2, c/2)
        except Exception as e:
            print(f"Ошибка визуализации параллелепипеда: {e}")

    def plot_cylinder_mass_distribution(self, ax, r, h, density):
        try:
            z = np.linspace(-h/2, h/2, 20)
            theta = np.linspace(0, 2*np.pi, 20)
            theta_grid, z_grid = np.meshgrid(theta, z)
            x_grid = r * np.cos(theta_grid)
            y_grid = r * np.sin(theta_grid)
            
            ax.plot_surface(x_grid, y_grid, z_grid, color='lightcoral', alpha=0.3)
            
            n_radial = 3
            n_angular = 6
            n_height = 3
            
            for i in range(n_radial):
                ri = r * (i + 0.5) / n_radial
                for j in range(n_angular):
                    theta = 2 * np.pi * j / n_angular
                    for k in range(n_height):
                        z_val = -h/2 + (k + 0.5) * h / n_height
                        x = ri * np.cos(theta)
                        y = ri * np.sin(theta)
                        size = (ri / r) ** 2 * 80
                        ax.scatter(x, y, z_val, s=size, color='red', alpha=0.6)
        except Exception as e:
            print(f"Ошибка визуализации цилиндра: {e}")

    def on_shape_changed(self):
        shape = self.shape_box.currentText()
        self.param3.setVisible(shape == "Параллелепипед")
        self.clear_plot()

    def add_body(self):
        try:
            shape = self.shape_box.currentText()
            p1 = float(self.param1.text())
            p2 = float(self.param2.text())
            p3 = float(self.param3.text()) if self.param3.isVisible() else 0
            
            if any(x <= 0 for x in [p1, p2] if p1 and p2) or (self.param3.isVisible() and p3 <= 0):
                raise ValueError("Все параметры должны быть положительными числами")
            
            if shape == "Сфера":
                body = Sphere(p1)
            elif shape == "Параллелепипед":
                body = Box(p1, p2, p3)
            elif shape == "Цилиндр":
                body = Cylinder(p1, p2)
            else:
                raise ValueError("Неизвестная фигура")
            
            self.body_container.add_body(body)
            display_text = f"{body.name}: "
            if shape == "Сфера":
                display_text += f"r={p1}"
            elif shape == "Параллелепипед":
                display_text += f"{p1}×{p2}×{p3}"
            elif shape == "Цилиндр":
                display_text += f"r={p1}, h={p2}"
            
            self.body_list.addItem(display_text)
            self.result_label.setText(f"Тело добавлено. Всего тел: {self.body_list.count()}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления тела: {str(e)}")

    def calculate_all(self):
        try:
            density = float(self.density.text())
            if density <= 0:
                raise ValueError("Плотность должна быть положительной")
            
            self.results = self.body_container.calculate_all_moments(density)
            total = sum(moment for _, _, moment in self.results)
            self.result_label.setText(f"Суммарный момент инерции: {total:.6f} кг·м²")
            
            self.calculation_history.append({
                'timestamp': np.datetime64('now'),
                'results': self.results,
                'total_inertia': total
            })
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка расчета: {str(e)}")

    def clear_all(self):
        self.body_container.clear()
        self.body_list.clear()
        self.result_label.setText("Результат: ")
        self.clear_plot()

    def export_results(self):
        if not hasattr(self, 'results') or not self.results:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для экспорта")
            return
            
        filename, filter = QFileDialog.getSaveFileName(
            self, "Экспорт результатов", "", 
            "Text files (*.txt);;PDF files (*.pdf)"
        )
        
        if filename:
            try:
                if filter == "Text files (*.txt)":
                    ResultExporter.export_to_txt(self.results, filename)
                elif filter == "PDF files (*.pdf)":
                    ResultExporter.export_to_pdf(self.results, filename)
                
                QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def on_body_selected(self, index):
        if index >= 0 and hasattr(self, 'results') and index < len(self.results):
            body, density, moment = self.results[index]
            self.plot_body(body, moment)

    def plot_body(self, body, moment=None):
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        
        try:
            if hasattr(body, 'get_dimensions'):
                dims = body.get_dimensions()
                
                if body.name == "Sphere":
                    r = dims.get('radius', 1.0)
                    self.plot_sphere_3d(ax, r)
                    title = f"Сфера\nРадиус: {r:.2f} м"
                    
                elif body.name == "Box":
                    a = dims.get('a', 1.0)
                    b = dims.get('b', 1.0)
                    c = dims.get('c', 1.0)
                    self.plot_box_3d(ax, a, b, c)
                    title = f"Параллелепипед\nРазмеры: {a:.2f}×{b:.2f}×{c:.2f} м"
                    
                elif body.name == "Cylinder":
                    r = dims.get('radius', 1.0)
                    h = dims.get('height', 1.0)
                    self.plot_cylinder_3d(ax, r, h)
                    title = f"Цилиндр\nРадиус: {r:.2f} м, Высота: {h:.2f} м"
                else:
                    title = "Неизвестное тело"
            else:
                title = "Тело (данные недоступны)"
            
            if moment is not None:
                title += f"\nМомент инерции: {moment:.4f} кг·м²"
                
            ax.set_title(title)
            ax.set_box_aspect([1, 1, 1])
            
        except Exception as e:
            print(f"Ошибка визуализации: {e}")
            ax.text(0.5, 0.5, 0.5, f"Ошибка визуализации:\n{e}", 
                    transform=ax.transAxes, ha='center')
        
        self.canvas.draw()

    def plot_sphere_3d(self, ax, r):
        try:
            u = np.linspace(0, 2 * np.pi, 30)
            v = np.linspace(0, np.pi, 30)
            x = r * np.outer(np.cos(u), np.sin(v))
            y = r * np.outer(np.sin(u), np.sin(v))
            z = r * np.outer(np.ones(np.size(u)), np.cos(v))
            ax.plot_surface(x, y, z, color='lightblue', alpha=0.7)
            ax.plot([0, 0], [0, 0], [-r, r], 'r-', linewidth=2, label='Ось вращения')
            ax.legend()
        except Exception as e:
            print(f"Ошибка визуализации сферы: {e}")

    def plot_box_3d(self, ax, a, b, c):
        try:
            vertices = np.array([
                [-a/2, -b/2, -c/2], [a/2, -b/2, -c/2],
                [a/2, b/2, -c/2], [-a/2, b/2, -c/2],
                [-a/2, -b/2, c/2], [a/2, -b/2, c/2],
                [a/2, b/2, c/2], [-a/2, b/2, c/2]
            ])
            
            faces = [
                [vertices[0], vertices[1], vertices[2], vertices[3]],
                [vertices[4], vertices[5], vertices[6], vertices[7]],
                [vertices[0], vertices[1], vertices[5], vertices[4]],
                [vertices[2], vertices[3], vertices[7], vertices[6]],
                [vertices[0], vertices[3], vertices[7], vertices[4]],
                [vertices[1], vertices[2], vertices[6], vertices[5]]
            ]
            
            collection = Poly3DCollection(faces, 
                                        facecolors='lightgreen', 
                                        edgecolors='black',
                                        alpha=0.7,
                                        linewidths=1)
            ax.add_collection3d(collection)
            
            ax.plot([-a/2, a/2], [0, 0], [0, 0], 'r-', linewidth=2, label='Ось вращения')
            ax.legend()
            
            ax.set_xlim(-a/2, a/2)
            ax.set_ylim(-b/2, b/2)
            ax.set_zlim(-c/2, c/2)
            
        except Exception as e:
            print(f"Ошибка визуализации параллелепипеда: {e}")

    def plot_cylinder_3d(self, ax, r, h):
        try:
            z = np.linspace(-h/2, h/2, 30)
            theta = np.linspace(0, 2*np.pi, 30)
            theta_grid, z_grid = np.meshgrid(theta, z)
            x_grid = r * np.cos(theta_grid)
            y_grid = r * np.sin(theta_grid)
            
            ax.plot_surface(x_grid, y_grid, z_grid, color='lightcoral', alpha=0.7)
            
            theta_base = np.linspace(0, 2*np.pi, 30)
            r_base = np.linspace(0, r, 10)
            R_base, Theta_base = np.meshgrid(r_base, theta_base)
            
            X_top = R_base * np.cos(Theta_base)
            Y_top = R_base * np.sin(Theta_base)
            Z_top = np.full_like(X_top, h/2)
            
            X_bottom = R_base * np.cos(Theta_base)
            Y_bottom = R_base * np.sin(Theta_base)
            Z_bottom = np.full_like(X_bottom, -h/2)
            
            ax.plot_surface(X_top, Y_top, Z_top, color='lightcoral', alpha=0.5)
            ax.plot_surface(X_bottom, Y_bottom, Z_bottom, color='lightcoral', alpha=0.5)
            
            ax.plot([0, 0], [0, 0], [-h/2, h/2], 'r-', linewidth=2, label='Ось вращения')
            ax.legend()
            
        except Exception as e:
            print(f"Ошибка визуализации цилиндра: {e}")

    def clear_plot(self):
        self.figure.clear()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = InertiaGUI()
    gui.show()
    sys.exit(app.exec())