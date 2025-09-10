#ifndef STATISTICS_H
#define STATISTICS_H

#include "algorithm.h"  /* For dynamic_array_t */

#ifdef __cplusplus
extern "C" {
#endif

/* Statistics result structure */
typedef struct {
    double mean;
    double median;
    double std_deviation;
    int min_value;
    int max_value;
    int count;
} statistics_result_t;

/* Statistics operations */
int calculate_statistics(const dynamic_array_t* arr, statistics_result_t* result);
int calculate_mean(const dynamic_array_t* arr, double* mean);
int calculate_median(const dynamic_array_t* arr, double* median);
int calculate_std_deviation(const dynamic_array_t* arr, double* std_dev);
int find_min_max(const dynamic_array_t* arr, int* min_val, int* max_val);

/* Utility functions */
void print_statistics(const statistics_result_t* result);
int compare_arrays_statistics(const dynamic_array_t* arr1, const dynamic_array_t* arr2, 
                             statistics_result_t* result1, statistics_result_t* result2);

#ifdef __cplusplus
}
#endif

#endif /* STATISTICS_H */
