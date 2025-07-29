/**
 * This .h includes the patch struct and "member functions" 
 * that correponds to patch class in piegy.model module
*/

#ifndef PATCH_H
#define PATCH_H

#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>



typedef struct patch_t {
    size_t i;
    size_t j;

    uint32_t U;
    uint32_t V;
    double U_pi;
    double V_pi;

    struct patch_t* nb[4];
    double U_weight[4];  // stores migration weight of each of the 4 neighbors
    double V_weight[4];
    double sum_U_weight; // sum of U_weight
    double sum_V_weight;
    double pi_death_rates[4];
    double mig_rates[8];
    double sum_pi_death_rates;
    double sum_mig_rates;
} patch_t;

// in .c
void patch_init(patch_t* p, uint32_t U, uint32_t V, size_t i, size_t j);
void set_nb(patch_t* world, size_t* nb_start, size_t ij, size_t NM);

#endif // PATCH_H

