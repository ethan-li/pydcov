#pragma once

/**
 * Simple calculator class for demonstration purposes.
 */
class Calculator {
public:
    /**
     * Add two numbers.
     * @param a First number
     * @param b Second number
     * @return Sum of a and b
     */
    int add(int a, int b);
    
    /**
     * Subtract two numbers.
     * @param a First number
     * @param b Second number
     * @return Difference of a and b
     */
    int subtract(int a, int b);
    
    /**
     * Multiply two numbers.
     * @param a First number
     * @param b Second number
     * @return Product of a and b
     */
    int multiply(int a, int b);
    
    /**
     * Divide two numbers.
     * @param a Dividend
     * @param b Divisor
     * @return Quotient of a and b
     * @throws std::invalid_argument if b is zero
     */
    double divide(double a, double b);
};
