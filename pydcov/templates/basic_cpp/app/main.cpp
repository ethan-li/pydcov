#include <iostream>
#include "calculator.hpp"

int main() {
    Calculator calc;
    
    std::cout << "{{PROJECT_NAME}} - Simple Calculator Demo\n";
    std::cout << "========================================\n";
    
    // Demonstrate basic operations
    int a = 10, b = 5;
    
    std::cout << "a = " << a << ", b = " << b << "\n";
    std::cout << "a + b = " << calc.add(a, b) << "\n";
    std::cout << "a - b = " << calc.subtract(a, b) << "\n";
    std::cout << "a * b = " << calc.multiply(a, b) << "\n";
    std::cout << "a / b = " << calc.divide(a, b) << "\n";
    
    return 0;
}
