#include <cassert>
#include <iostream>
#include <stdexcept>
#include "calculator.hpp"

void test_add() {
    Calculator calc;
    assert(calc.add(2, 3) == 5);
    assert(calc.add(-1, 1) == 0);
    assert(calc.add(0, 0) == 0);
    std::cout << "✓ Add tests passed\n";
}

void test_subtract() {
    Calculator calc;
    assert(calc.subtract(5, 3) == 2);
    assert(calc.subtract(1, 1) == 0);
    assert(calc.subtract(0, 5) == -5);
    std::cout << "✓ Subtract tests passed\n";
}

void test_multiply() {
    Calculator calc;
    assert(calc.multiply(3, 4) == 12);
    assert(calc.multiply(-2, 3) == -6);
    assert(calc.multiply(0, 100) == 0);
    std::cout << "✓ Multiply tests passed\n";
}

void test_divide() {
    Calculator calc;
    assert(calc.divide(10.0, 2.0) == 5.0);
    assert(calc.divide(7.0, 2.0) == 3.5);
    
    // Test division by zero
    try {
        calc.divide(5.0, 0.0);
        assert(false); // Should not reach here
    } catch (const std::invalid_argument&) {
        // Expected exception
    }
    
    std::cout << "✓ Divide tests passed\n";
}

int main() {
    std::cout << "Running {{PROJECT_NAME}} tests...\n";
    std::cout << "================================\n";
    
    test_add();
    test_subtract();
    test_multiply();
    test_divide();
    
    std::cout << "\n✅ All tests passed!\n";
    return 0;
}
