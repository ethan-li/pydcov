#include "algorithm.h"
#include <stdlib.h>

/* Dynamic array operations */
dynamic_array_t* create_array(int initial_capacity) {
    dynamic_array_t* arr;

    if (initial_capacity <= 0) return NULL;

    arr = (dynamic_array_t*)malloc(sizeof(dynamic_array_t));
    if (arr == NULL) return NULL;

    arr->data = (int*)malloc(initial_capacity * sizeof(int));
    if (arr->data == NULL) {
        free(arr);
        return NULL;
    }

    arr->size = 0;
    arr->capacity = initial_capacity;
    return arr;
}

void destroy_array(dynamic_array_t* arr) {
    if (arr == NULL) return;

    if (arr->data != NULL) {
        free(arr->data);
    }
    free(arr);
}

int push_array(dynamic_array_t* arr, int value) {
    int* new_data;
    int new_capacity;

    if (arr == NULL) return -1;

    if (arr->size >= arr->capacity) {
        new_capacity = arr->capacity * 2;
        new_data = (int*)realloc(arr->data, new_capacity * sizeof(int));
        if (new_data == NULL) return -1;

        arr->data = new_data;
        arr->capacity = new_capacity;
    }

    arr->data[arr->size] = value;
    arr->size++;
    return 0;
}

int pop_array(dynamic_array_t* arr, int* value) {
    if (arr == NULL || arr->size == 0) return -1;

    arr->size--;
    if (value != NULL) {
        *value = arr->data[arr->size];
    }
    return 0;
}

int get_array(const dynamic_array_t* arr, int index, int* value) {
    if (arr == NULL || index < 0 || index >= arr->size || value == NULL) {
        return -1;
    }

    *value = arr->data[index];
    return 0;
}
