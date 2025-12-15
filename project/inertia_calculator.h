#pragma once
#include <cmath>
#include <memory>
#include <vector>
#include <stdexcept>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifdef _WIN32
  #ifdef BUILDING_INERTIA_DLL
    #define INERTIA_API __declspec(dllexport)
  #else
    #define INERTIA_API __declspec(dllimport)
  #endif
#else
  #define INERTIA_API
#endif

// Базовый класс для всех тел
class INERTIA_API Body {
public:
    virtual ~Body() = default;
    virtual double calculateMomentOfInertia(double density) const = 0;
    virtual double calculateMass(double density) const = 0;
    virtual const char* getName() const = 0;
};

// Конкретные классы тел
class INERTIA_API Sphere : public Body {
    double radius;
public:
    Sphere(double r);
    double calculateMomentOfInertia(double density) const override;
    double calculateMass(double density) const override;
    const char* getName() const override;
    double getRadius() const;
};

class INERTIA_API Box : public Body {
    double a, b, c;
public:
    Box(double a, double b, double c);
    double calculateMomentOfInertia(double density) const override;
    double calculateMass(double density) const override;
    const char* getName() const override;
    void getDimensions(double& a, double& b, double& c) const;
};

class INERTIA_API Cylinder : public Body {
    double radius, height;
public:
    Cylinder(double r, double h);
    double calculateMomentOfInertia(double density) const override;
    double calculateMass(double density) const override;
    const char* getName() const override;
    void getDimensions(double& r, double& h) const;
};

// C-интерфейс для совместимости с Python
extern "C" {
    INERTIA_API void* create_sphere(double radius);
    INERTIA_API void* create_box(double a, double b, double c);
    INERTIA_API void* create_cylinder(double radius, double height);
    INERTIA_API double calculate_moment(void* body, double density);
    INERTIA_API void delete_body(void* body);
    INERTIA_API const char* get_body_name(void* body);
    INERTIA_API double get_sphere_radius(void* body);
    INERTIA_API void get_box_dimensions(void* body, double* a, double* b, double* c);
    INERTIA_API void get_cylinder_dimensions(void* body, double* r, double* h);
}