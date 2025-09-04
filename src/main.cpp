#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cstring>
#include <fstream>
#include <cstdio>
#include "algorithm.h"

void print_usage(const char* program_name) {
    std::cout << "Usage: " << program_name << " dynarray <command> [arguments...]\n\n";
    std::cout << "Dynamic Array Commands:\n";
    std::cout << "  dynarray create <capacity>      - Create dynamic array\n";
    std::cout << "  dynarray push <val1> <val2> ... - Push values to array\n";
    std::cout << "  dynarray pop [count]            - Pop count values from array (default: 1)\n";
    std::cout << "  dynarray get <index>            - Get value at index\n";
    std::cout << "  dynarray cleanup                - Clean up array data\n";
    std::cout << "\nExamples:\n";
    std::cout << "  " << program_name << " dynarray create 10\n";
    std::cout << "  " << program_name << " dynarray push 1 2 3 4 5\n";
    std::cout << "  " << program_name << " dynarray get 0\n";
    std::cout << "  " << program_name << " dynarray pop 2\n";
    std::cout << "  " << program_name << " dynarray cleanup\n";
}




// File-based dynamic array storage
const std::string ARRAY_FILE = "/tmp/pydcov_array.dat";

// Helper functions for file-based array storage
bool save_array_to_file(const dynamic_array_t* arr) {
    if (!arr) return false;

    std::ofstream file(ARRAY_FILE, std::ios::binary);
    if (!file) return false;

    file.write(reinterpret_cast<const char*>(&arr->size), sizeof(arr->size));
    file.write(reinterpret_cast<const char*>(&arr->capacity), sizeof(arr->capacity));
    file.write(reinterpret_cast<const char*>(arr->data), arr->size * sizeof(int));

    return file.good();
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

void remove_array_file() {
    std::remove(ARRAY_FILE.c_str());
}

int handle_dynarray_commands(const std::vector<std::string>& args) {
    if (args.size() < 2) {
        std::cerr << "Error: Dynamic array commands require operation\n";
        return 1;
    }

    const std::string& operation = args[1];

    if (operation == "create") {
        if (args.size() != 3) {
            std::cerr << "Error: create requires exactly one argument\n";
            return 1;
        }

        // Remove existing array file
        remove_array_file();

        int capacity = std::stoi(args[2]);
        dynamic_array_t* arr = create_array(capacity);
        if (arr == nullptr) {
            std::cerr << "Error: Failed to create array\n";
            return 1;
        }

        if (!save_array_to_file(arr)) {
            std::cerr << "Error: Failed to save array\n";
            destroy_array(arr);
            return 1;
        }

        destroy_array(arr);
        std::cout << "Array created with capacity " << capacity << std::endl;
    }
    else if (operation == "push") {
        if (args.size() < 3) {
            std::cerr << "Error: push requires at least one value\n";
            return 1;
        }

        dynamic_array_t* arr = load_array_from_file();
        if (arr == nullptr) {
            std::cerr << "Error: No array created. Use 'dynarray create' first\n";
            return 1;
        }

        for (size_t i = 2; i < args.size(); ++i) {
            int value = std::stoi(args[i]);
            if (push_array(arr, value) != 0) {
                std::cerr << "Error: Failed to push value " << value << std::endl;
                destroy_array(arr);
                return 1;
            }
        }

        if (!save_array_to_file(arr)) {
            std::cerr << "Error: Failed to save array\n";
            destroy_array(arr);
            return 1;
        }

        std::cout << "Pushed " << (args.size() - 2) << " values. Array size: " << arr->size << std::endl;
        destroy_array(arr);
    }
    else if (operation == "pop") {
        dynamic_array_t* arr = load_array_from_file();
        if (arr == nullptr) {
            std::cerr << "Error: No array created. Use 'dynarray create' first\n";
            return 1;
        }

        int count = 1;
        if (args.size() >= 3) {
            count = std::stoi(args[2]);
        }

        for (int i = 0; i < count; ++i) {
            int value;
            if (pop_array(arr, &value) != 0) {
                std::cerr << "Error: Cannot pop from empty array\n";
                destroy_array(arr);
                return 1;
            }
            std::cout << value;
            if (i < count - 1) std::cout << " ";
        }
        std::cout << std::endl;

        if (!save_array_to_file(arr)) {
            std::cerr << "Error: Failed to save array\n";
            destroy_array(arr);
            return 1;
        }

        destroy_array(arr);
    }
    else if (operation == "get") {
        dynamic_array_t* arr = load_array_from_file();
        if (arr == nullptr) {
            std::cerr << "Error: No array created. Use 'dynarray create' first\n";
            return 1;
        }

        if (args.size() != 3) {
            std::cerr << "Error: get requires exactly one argument\n";
            destroy_array(arr);
            return 1;
        }

        int index = std::stoi(args[2]);
        int value;
        if (get_array(arr, index, &value) != 0) {
            std::cerr << "Error: Invalid index " << index << std::endl;
            destroy_array(arr);
            return 1;
        }
        std::cout << value << std::endl;
        destroy_array(arr);
    }
    else if (operation == "cleanup") {
        remove_array_file();
        std::cout << "Array cleaned up" << std::endl;
    }
    else {
        std::cerr << "Error: Unknown dynarray operation '" << operation << "'\n";
        return 1;
    }

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
        if (command == "dynarray") {
            return handle_dynarray_commands(args);
        }
        else {
            std::cerr << "Error: Unknown command '" << command << "'. Only 'dynarray' commands are supported.\n";
            print_usage(argv[0]);
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    // No cleanup needed as we use file-based storage

    return 0;
}
