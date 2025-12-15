#include "inertia_calculator.h"

// Реализация Sphere
Sphere::Sphere(double r) : radius(r) {
    if (r <= 0) throw std::invalid_argument("Radius must be positive");
}

double Sphere::calculateMomentOfInertia(double density) const {
    double mass = calculateMass(density);
    return 0.4 * mass * radius * radius;
}

double Sphere::calculateMass(double density) const {
    return (4.0 / 3.0) * M_PI * pow(radius, 3) * density;
}

const char* Sphere::getName() const { return "Sphere"; }
double Sphere::getRadius() const { return radius; }

// Реализация Box
Box::Box(double a, double b, double c) : a(a), b(b), c(c) {
    if (a <= 0 || b <= 0 || c <= 0) 
        throw std::invalid_argument("All dimensions must be positive");
}

double Box::calculateMomentOfInertia(double density) const {
    double mass = calculateMass(density);
    return (1.0 / 12.0) * mass * (b * b + c * c);
}

double Box::calculateMass(double density) const {
    return a * b * c * density;
}

const char* Box::getName() const { return "Box"; }
void Box::getDimensions(double& a, double& b, double& c) const {
    a = this->a; b = this->b; c = this->c;
}

// Реализация Cylinder
Cylinder::Cylinder(double r, double h) : radius(r), height(h) {
    if (r <= 0 || h <= 0) 
        throw std::invalid_argument("Radius and height must be positive");
}

double Cylinder::calculateMomentOfInertia(double density) const {
    double mass = calculateMass(density);
    return 0.5 * mass * radius * radius;
}

double Cylinder::calculateMass(double density) const {
    return M_PI * radius * radius * height * density;
}

const char* Cylinder::getName() const { return "Cylinder"; }
void Cylinder::getDimensions(double& r, double& h) const {
    r = radius; h = height;
}

// Реализация C-интерфейса
extern "C" {
    void* create_sphere(double radius) {
        try {
            return new Sphere(radius);
        } catch (...) {
            return nullptr;
        }
    }
    
    void* create_box(double a, double b, double c) {
        try {
            return new Box(a, b, c);
        } catch (...) {
            return nullptr;
        }
    }
    
    void* create_cylinder(double radius, double height) {
        try {
            return new Cylinder(radius, height);
        } catch (...) {
            return nullptr;
        }
    }
    
    double calculate_moment(void* body, double density) {
        if (!body || density <= 0) return -1.0;
        try {
            Body* b = static_cast<Body*>(body);
            return b->calculateMomentOfInertia(density);
        } catch (...) {
            return -1.0;
        }
    }
    
    void delete_body(void* body) {
        delete static_cast<Body*>(body);
    }
    
    const char* get_body_name(void* body) {
        Body* b = static_cast<Body*>(body);
        return b ? b->getName() : "Unknown";
    }
    
    double get_sphere_radius(void* body) {
        Sphere* sphere = dynamic_cast<Sphere*>(static_cast<Body*>(body));
        return sphere ? sphere->getRadius() : -1.0;
    }
    
    void get_box_dimensions(void* body, double* a, double* b, double* c) {
        Box* box = dynamic_cast<Box*>(static_cast<Body*>(body));
        if (box) {
            box->getDimensions(*a, *b, *c);
        }
    }
    
    void get_cylinder_dimensions(void* body, double* r, double* h) {
        Cylinder* cylinder = dynamic_cast<Cylinder*>(static_cast<Body*>(body));
        if (cylinder) {
            cylinder->getDimensions(*r, *h);
        }
    }
}