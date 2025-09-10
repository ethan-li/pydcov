#include "statistics.h"
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

/* Helper function to sort array for median calculation */
static int compare_ints(const void* a, const void* b) {
    int ia = *(const int*)a;
    int ib = *(const int*)b;
    return (ia > ib) - (ia < ib);
}

/* Calculate mean of array */
int calculate_mean(const dynamic_array_t* arr, double* mean) {
    long sum;
    int i;

    if (arr == NULL || mean == NULL || arr->size == 0) {
        return -1;
    }

    sum = 0;
    for (i = 0; i < arr->size; i++) {
        sum += arr->data[i];
    }

    *mean = (double)sum / arr->size;
    return 0;
}

/* Calculate median of array */
int calculate_median(const dynamic_array_t* arr, double* median) {
    int* sorted_data;
    int i;
    
    if (arr == NULL || median == NULL || arr->size == 0) {
        return -1;
    }
    
    /* Create a copy of the data for sorting */
    sorted_data = (int*)malloc(arr->size * sizeof(int));
    if (sorted_data == NULL) {
        return -1;
    }
    
    for (i = 0; i < arr->size; i++) {
        sorted_data[i] = arr->data[i];
    }
    
    /* Sort the copy */
    qsort(sorted_data, arr->size, sizeof(int), compare_ints);
    
    /* Calculate median */
    if (arr->size % 2 == 0) {
        /* Even number of elements */
        *median = (sorted_data[arr->size/2 - 1] + sorted_data[arr->size/2]) / 2.0;
    } else {
        /* Odd number of elements */
        *median = sorted_data[arr->size/2];
    }
    
    free(sorted_data);
    return 0;
}

/* Calculate standard deviation */
int calculate_std_deviation(const dynamic_array_t* arr, double* std_dev) {
    double mean, variance, sum_squared_diff;
    int i;
    
    if (arr == NULL || std_dev == NULL || arr->size == 0) {
        return -1;
    }
    
    /* Calculate mean first */
    if (calculate_mean(arr, &mean) != 0) {
        return -1;
    }
    
    /* Calculate variance */
    sum_squared_diff = 0.0;
    for (i = 0; i < arr->size; i++) {
        double diff = arr->data[i] - mean;
        sum_squared_diff += diff * diff;
    }
    
    variance = sum_squared_diff / arr->size;
    *std_dev = sqrt(variance);
    
    return 0;
}

/* Find minimum and maximum values */
int find_min_max(const dynamic_array_t* arr, int* min_val, int* max_val) {
    int i;
    
    if (arr == NULL || min_val == NULL || max_val == NULL || arr->size == 0) {
        return -1;
    }
    
    *min_val = arr->data[0];
    *max_val = arr->data[0];
    
    for (i = 1; i < arr->size; i++) {
        if (arr->data[i] < *min_val) {
            *min_val = arr->data[i];
        }
        if (arr->data[i] > *max_val) {
            *max_val = arr->data[i];
        }
    }
    
    return 0;
}

/* Calculate all statistics at once */
int calculate_statistics(const dynamic_array_t* arr, statistics_result_t* result) {
    if (arr == NULL || result == NULL || arr->size == 0) {
        return -1;
    }
    
    /* Initialize result */
    memset(result, 0, sizeof(statistics_result_t));
    result->count = arr->size;
    
    /* Calculate all statistics */
    if (calculate_mean(arr, &result->mean) != 0) {
        return -1;
    }
    
    if (calculate_median(arr, &result->median) != 0) {
        return -1;
    }
    
    if (calculate_std_deviation(arr, &result->std_deviation) != 0) {
        return -1;
    }
    
    if (find_min_max(arr, &result->min_value, &result->max_value) != 0) {
        return -1;
    }
    
    return 0;
}

/* Print statistics in a formatted way */
void print_statistics(const statistics_result_t* result) {
    if (result == NULL) {
        printf("Error: NULL statistics result\n");
        return;
    }
    
    printf("Statistics Summary:\n");
    printf("  Count: %d\n", result->count);
    printf("  Mean: %.2f\n", result->mean);
    printf("  Median: %.2f\n", result->median);
    printf("  Std Deviation: %.2f\n", result->std_deviation);
    printf("  Min: %d\n", result->min_value);
    printf("  Max: %d\n", result->max_value);
}

/* Compare statistics between two arrays */
int compare_arrays_statistics(const dynamic_array_t* arr1, const dynamic_array_t* arr2, 
                             statistics_result_t* result1, statistics_result_t* result2) {
    if (arr1 == NULL || arr2 == NULL || result1 == NULL || result2 == NULL) {
        return -1;
    }
    
    if (calculate_statistics(arr1, result1) != 0) {
        return -1;
    }
    
    if (calculate_statistics(arr2, result2) != 0) {
        return -1;
    }
    
    return 0;
}
