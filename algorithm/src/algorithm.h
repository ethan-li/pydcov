#ifndef ALGORITHM_H
#define ALGORITHM_H

#ifdef __cplusplus
extern "C" {
#endif

/* Dynamic array data structure */
typedef struct {
    int* data;
    int size;
    int capacity;
} dynamic_array_t;

/* Dynamic array operations */
dynamic_array_t* create_array(int initial_capacity);
void destroy_array(dynamic_array_t* arr);
int push_array(dynamic_array_t* arr, int value);
int pop_array(dynamic_array_t* arr, int* value);
int get_array(const dynamic_array_t* arr, int index, int* value);

#ifdef __cplusplus
}
#endif

#endif /* ALGORITHM_H */
