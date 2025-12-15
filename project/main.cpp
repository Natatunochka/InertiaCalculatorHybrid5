#include "inertia_calculator.h"
#include <iostream>
#include <memory>

int main() {
    try {
        BodyCollection<Body> collection;
        
        auto sphere = std::make_shared<Sphere>(1.0);
        auto box = std::make_shared<Box>(2.0, 3.0, 4.0);
        auto cylinder = std::make_shared<Cylinder>(1.0, 2.0);
        
        collection.addBody(sphere);
        collection.addBody(box);
        collection.addBody(cylinder);
        
        double density = 7800; // сталь
        
        std::cout << "Моменты инерции тел:\n";
        for (size_t i = 0; i < collection.size(); ++i) {
            auto body = collection.getBody(i);
            double moment = body->calculateMomentOfInertia(density);
            std::cout << (i + 1) << ". " << body->getName() 
                      << ": " << moment << " кг·м²\n";
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << '\n';
        return 1;
    }
    
    return 0;
}