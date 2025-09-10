#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <fstream>
#include <cstdio>
#include "algorithm.h"
#include "statistics.h"

const std::string ARRAY_FILE = "/tmp/pydcov_array.dat";

void print_usage(const char* program_name) {
    std::cout << "Usage: " << program_name << " <command> [arguments...]\n\n";
    std::cout << "Statistical Analysis Commands:\n";
    std::cout << "  analyze                         - Analyze array from file\n";
    std::cout << "  mean <val1> <val2> ...         - Calculate mean of values\n";
    std::cout << "  median <val1> <val2> ...       - Calculate median of values\n";
    std::cout << "  stddev <val1> <val2> ...       - Calculate standard deviation of values\n";
    std::cout << "  min <val1> <val2> ...          - Find minimum value\n";
    std::cout << "  max <val1> <val2> ...          - Find maximum value\n";
    std::cout << "  create <val1> <val2> ...       - Create array with values and analyze\n";
    std::cout << "  compare <val1> <val2> ... | <val3> <val4> ... - Compare two sets\n";
    std::cout << "\nExamples:\n";
    std::cout << "  " << program_name << " create 1 2 3 4 5\n";
    std::cout << "  " << program_name << " analyze\n";
    std::cout << "  " << program_name << " mean\n";
    std::cout << "  " << program_name << " compare 1 2 3 | 4 5 6\n";
}

dynamic_array_t* load_array_from_file() {
    std::ifstream file(ARRAY_FILE, std::ios::binary);
    if (!file) return nullptr;

    int size, capacity;
    file.read(reinterpret_cast<char*>(&size), sizeof(size));
    file.read(reinterpret_cast<char*>(&capacity), sizeof(capacity));

    if (!file.good() || size < 0 || capacity < 0 || size > capacity) {
        return nullptr;
    }

    dynamic_array_t* arr = create_array(capacity);
    if (!arr) return nullptr;

    arr->size = size;
    if (size > 0) {
        file.read(reinterpret_cast<char*>(arr->data), size * sizeof(int));
        if (!file.good()) {
            destroy_array(arr);
            return nullptr;
        }
    }

    return arr;
}

dynamic_array_t* create_array_from_values(const std::vector<int>& values) {
    if (values.empty()) return nullptr;
    
    dynamic_array_t* arr = create_array(values.size());
    if (!arr) return nullptr;
    
    for (size_t i = 0; i < values.size(); ++i) {
        if (push_array(arr, values[i]) != 0) {
            destroy_array(arr);
            return nullptr;
        }
    }
    
    return arr;
}

int handle_analyze_command() {
    dynamic_array_t* arr = load_array_from_file();
    if (!arr) {
        std::cerr << "Error: No array data found. Create an array first using the algorithm CLI.\n";
        return 1;
    }
    
    statistics_result_t result;
    if (calculate_statistics(arr, &result) != 0) {
        std::cerr << "Error: Failed to calculate statistics\n";
        destroy_array(arr);
        return 1;
    }
    
    print_statistics(&result);
    destroy_array(arr);
    return 0;
}

int handle_single_stat_command(const std::string& stat_type) {
    dynamic_array_t* arr = load_array_from_file();
    if (!arr) {
        std::cerr << "Error: No array data found. Create an array first using the algorithm CLI.\n";
        return 1;
    }
    
    int result = 0;
    
    if (stat_type == "mean") {
        double mean;
        if (calculate_mean(arr, &mean) == 0) {
            std::cout << "Mean: " << mean << std::endl;
        } else {
            std::cerr << "Error: Failed to calculate mean\n";
            result = 1;
        }
    } else if (stat_type == "median") {
        double median;
        if (calculate_median(arr, &median) == 0) {
            std::cout << "Median: " << median << std::endl;
        } else {
            std::cerr << "Error: Failed to calculate median\n";
            result = 1;
        }
    } else if (stat_type == "stddev") {
        double stddev;
        if (calculate_std_deviation(arr, &stddev) == 0) {
            std::cout << "Standard Deviation: " << stddev << std::endl;
        } else {
            std::cerr << "Error: Failed to calculate standard deviation\n";
            result = 1;
        }
    } else if (stat_type == "minmax") {
        int min_val, max_val;
        if (find_min_max(arr, &min_val, &max_val) == 0) {
            std::cout << "Min: " << min_val << ", Max: " << max_val << std::endl;
        } else {
            std::cerr << "Error: Failed to find min/max\n";
            result = 1;
        }
    }
    
    destroy_array(arr);
    return result;
}

int handle_single_stat_command_with_args(const std::string& stat_type, const std::vector<std::string>& args) {
    if (args.size() < 2) {
        std::cerr << "Error: No values provided for " << stat_type << " calculation\n";
        return 1;
    }

    // Create array from command line arguments
    dynamic_array_t* arr = create_array(args.size() - 1);
    if (!arr) {
        std::cerr << "Error: Failed to create array\n";
        return 1;
    }

    // Parse and add values
    for (size_t i = 1; i < args.size(); i++) {
        try {
            int value = std::stoi(args[i]);
            if (push_array(arr, value) != 0) {
                std::cerr << "Error: Failed to add value to array\n";
                destroy_array(arr);
                return 1;
            }
        } catch (const std::exception& e) {
            std::cerr << "Error: Invalid number '" << args[i] << "'\n";
            destroy_array(arr);
            return 1;
        }
    }

    int result = 0;

    if (stat_type == "mean") {
        double mean;
        if (calculate_mean(arr, &mean) == 0) {
            std::cout << mean << std::endl;
        } else {
            std::cerr << "Error: Failed to calculate mean\n";
            result = 1;
        }
    } else if (stat_type == "median") {
        double median;
        if (calculate_median(arr, &median) == 0) {
            std::cout << median << std::endl;
        } else {
            std::cerr << "Error: Failed to calculate median\n";
            result = 1;
        }
    } else if (stat_type == "stddev") {
        double stddev;
        if (calculate_std_deviation(arr, &stddev) == 0) {
            std::cout << stddev << std::endl;
        } else {
            std::cerr << "Error: Failed to calculate standard deviation\n";
            result = 1;
        }
    } else if (stat_type == "min") {
        int min_val, max_val;
        if (find_min_max(arr, &min_val, &max_val) == 0) {
            std::cout << min_val << std::endl;
        } else {
            std::cerr << "Error: Failed to find min\n";
            result = 1;
        }
    } else if (stat_type == "max") {
        int min_val, max_val;
        if (find_min_max(arr, &min_val, &max_val) == 0) {
            std::cout << max_val << std::endl;
        } else {
            std::cerr << "Error: Failed to find max\n";
            result = 1;
        }
    }

    destroy_array(arr);
    return result;
}

int handle_create_command(const std::vector<std::string>& args) {
    if (args.size() < 2) {
        std::cerr << "Error: create requires at least one value\n";
        return 1;
    }
    
    std::vector<int> values;
    for (size_t i = 1; i < args.size(); ++i) {
        try {
            values.push_back(std::stoi(args[i]));
        } catch (const std::exception& e) {
            std::cerr << "Error: Invalid number '" << args[i] << "'\n";
            return 1;
        }
    }
    
    dynamic_array_t* arr = create_array_from_values(values);
    if (!arr) {
        std::cerr << "Error: Failed to create array\n";
        return 1;
    }
    
    statistics_result_t result;
    if (calculate_statistics(arr, &result) != 0) {
        std::cerr << "Error: Failed to calculate statistics\n";
        destroy_array(arr);
        return 1;
    }
    
    std::cout << "Created array with " << values.size() << " values:\n";
    print_statistics(&result);
    
    destroy_array(arr);
    return 0;
}

int handle_compare_command(const std::vector<std::string>& args) {
    // Find the separator '|'
    size_t separator_pos = 0;
    for (size_t i = 1; i < args.size(); ++i) {
        if (args[i] == "|") {
            separator_pos = i;
            break;
        }
    }
    
    if (separator_pos == 0 || separator_pos == 1 || separator_pos == args.size() - 1) {
        std::cerr << "Error: compare requires two sets of values separated by '|'\n";
        std::cerr << "Example: compare 1 2 3 | 4 5 6\n";
        return 1;
    }
    
    // Parse first set
    std::vector<int> values1;
    for (size_t i = 1; i < separator_pos; ++i) {
        try {
            values1.push_back(std::stoi(args[i]));
        } catch (const std::exception& e) {
            std::cerr << "Error: Invalid number '" << args[i] << "' in first set\n";
            return 1;
        }
    }
    
    // Parse second set
    std::vector<int> values2;
    for (size_t i = separator_pos + 1; i < args.size(); ++i) {
        try {
            values2.push_back(std::stoi(args[i]));
        } catch (const std::exception& e) {
            std::cerr << "Error: Invalid number '" << args[i] << "' in second set\n";
            return 1;
        }
    }
    
    // Create arrays
    dynamic_array_t* arr1 = create_array_from_values(values1);
    dynamic_array_t* arr2 = create_array_from_values(values2);
    
    if (!arr1 || !arr2) {
        std::cerr << "Error: Failed to create arrays\n";
        if (arr1) destroy_array(arr1);
        if (arr2) destroy_array(arr2);
        return 1;
    }
    
    // Calculate statistics
    statistics_result_t result1, result2;
    if (compare_arrays_statistics(arr1, arr2, &result1, &result2) != 0) {
        std::cerr << "Error: Failed to calculate statistics\n";
        destroy_array(arr1);
        destroy_array(arr2);
        return 1;
    }
    
    std::cout << "Array 1 Statistics:\n";
    print_statistics(&result1);
    std::cout << "\nArray 2 Statistics:\n";
    print_statistics(&result2);
    
    destroy_array(arr1);
    destroy_array(arr2);
    return 0;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    std::vector<std::string> args;
    for (int i = 1; i < argc; ++i) {
        args.push_back(std::string(argv[i]));
    }

    const std::string& command = args[0];

    try {
        if (command == "analyze") {
            return handle_analyze_command();
        } else if (command == "mean" || command == "median" ||
                   command == "stddev" || command == "min" || command == "max") {
            return handle_single_stat_command_with_args(command, args);
        } else if (command == "create") {
            return handle_create_command(args);
        } else if (command == "compare") {
            return handle_compare_command(args);
        } else {
            std::cerr << "Error: Unknown command '" << command << "'\n";
            print_usage(argv[0]);
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
