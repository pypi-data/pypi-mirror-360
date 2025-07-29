#include <stdbool.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

#include "model.h"
#include "patch.h"
#include "sim_funcs.h"


int main() {
    size_t N = 1;
    size_t M = 100;
    double maxtime = 300;
    double record_itv = 0.1;
    size_t sim_time = 1;
    bool boundary = true;
    uint32_t I_single[2] = {3, 3};
    double X_single[4] = {-1, 4, 0, 2};
    double P_single[6] = {0.5, 0.5, 80, 80, 0.001, 0.001};
    int32_t print_pct = 1;
    int32_t seed = 36;  // -1 for None

    uint32_t I[N * M * 2];
    double X[N * M * 4];
    double P[N * M * 6];

    //printf("sizeof(patch_t) = %zu bytes\n", sizeof(patch_t));
    size_t ij = 0;
    for (size_t i = 0; i < N; i++) {
        for (size_t j = 0; j < M; j++) {
            I[ij * 2] = I_single[0];
            I[ij * 2 + 1] = I_single[1];

            for (size_t k = 0; k < 4; k++) {
                X[ij * 4 + k] = X_single[k];
            }
            for (size_t k = 0; k < 6; k++) {
                P[ij * 6 + k] = P_single[k];
            }
            ++ij;
        }
    }

    model_t* mod = malloc(sizeof(model_t));
    mod_init(mod, N, M, maxtime, record_itv, sim_time, boundary, I, X, P, print_pct, seed);

    char message[20] = "";  // writable buffer with enough space
    uint8_t result = run(mod, message, 20);
    
    /*for (size_t i = 0; i < mod->max_record; i++) {
        fprintf(stdout, "%f ", mod->U1d[i]);
    }
    fprintf(stdout, "\n");
    for (size_t i = 0; i < mod->max_record; i++) {
        fprintf(stdout, "%f ", mod->Upi_1d[i]);
    }*/
    mod_free(mod);
    mod = NULL;
}

