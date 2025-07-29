/**
 * This .c includes the patch struct and "member functions" 
 * that correponds to patch class in piegy.model module
*/

#include "patch.h"

void patch_init(patch_t* p, uint32_t U, uint32_t V, size_t i, size_t j) {
    if (p == NULL) return;
    p->i = i;
    p->j = j;

    p->U = U;
    p->V = V;
    p->U_pi = 0.0;
    p->V_pi = 0.0;

    for (size_t i = 0; i < 4; i++) {
        p->U_weight[i] = 0.0;
        p->V_weight[i] = 0.0;
        p->pi_death_rates[i] = 0.0;
    }
    for (size_t i = 0; i < 8; i++) {
        p->mig_rates[i] = 0.0;
    }
    p->sum_U_weight = 0.0;
    p->sum_V_weight = 0.0;
    p->sum_pi_death_rates = 0.0;
    p->sum_mig_rates = 0.0;
}


void set_nb(patch_t* world, size_t* nb_start, size_t ij, size_t NM) {
    // nb_start is the where patch ij's neighbor indices start
    for (size_t k = 0; k < 4; k++) {
        if (nb_start[k] != NM) {
            // neighbor is valid
            world[ij].nb[k] = &world[nb_start[k]];
        } else {
            world[ij].nb[k] = NULL;
        }
    }
}
