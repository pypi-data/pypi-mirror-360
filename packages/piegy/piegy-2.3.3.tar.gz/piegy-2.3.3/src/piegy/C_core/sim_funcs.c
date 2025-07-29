/**
 * This .c defines the simulation functions in piegy.simulation
*/

#include <stdbool.h>
#include <time.h>

#include "sim_funcs.h"
#include "patch.h"
#include "model.h"



static void find_nb_zero_flux(size_t* restrict nb, size_t i, size_t j, size_t N, size_t M, size_t NM) {
    // Up
    if (i != 0) {
        nb[0] = (i - 1) * M + j;
    } else {
        nb[0] = NM;  // N * M for nb doesn't exist
    }

    // Down
    if (i != N - 1) {
        nb[1] = (i + 1) * M + j;
    } else {
        nb[1] = NM;
    }

    // Left
    if (j != 0) {
        nb[2] = i * M + j - 1;
    } else {
        nb[2] = NM;
    }

    // Right
    if (j != M - 1) {
        nb[3] = i * M + j + 1;
    } else {
        nb[3] = NM;
    }
}


static void find_nb_periodical(size_t* restrict nb, size_t i, size_t j, size_t N, size_t M, size_t NM) {
    // up
    if (N != 1) {
        nb[0] = (i != 0) ? (i - 1) * M + j : (N - 1) * M + j;
    } else {
        nb[0] = NM;
    }

    // down
    if (N != 1) {
        nb[1] = (i != N - 1) ? (i + 1) * M + j : j;
    } else {
        nb[1] = NM;
    }

    // We explicitly asked for M > 1
    // left
    nb[2] = (j != 0) ? i * M + j - 1 : i * M + M - 1;

    // right
    nb[3] = (j != M - 1) ? i * M + j + 1 : i * M;
}



// single_init function: initializes world, runs 1 event, returns updated variables
static double single_init(const model_t* mod, patch_t* world, size_t* nb_indices, 
                    double* patch_rates, double* sum_rates_by_row, double* sum_rates_p, signal_t* sig_p, patch_picked_t* picked_p) {

    size_t N = mod->N;
    size_t M = mod->M;
    size_t NM = N * M;
    size_t max_record = mod->max_record;
    size_t ij = 0;  // used to track index i * M + j in double for loops

    // init world
    for (size_t i = 0; i < N; i++) {
        for (size_t j = 0; j < M; j++) {
            patch_init(&world[ij], mod->I[ij * 2], mod->I[ij * 2 + 1], i, j);
            ij++;
        }
    }

    // init nb_indices
    ij = 0;
    if (mod->boundary) {
        for (size_t i = 0; i < N; i++) {
            for (size_t j = 0; j < M; j++) {
                find_nb_zero_flux(&nb_indices[ij * 4], i, j, N, M, NM);
                ij++;
            }
        }
    } else {
        for (size_t i = 0; i < N; i++) {
            for (size_t j = 0; j < M; j++) {
                find_nb_periodical(&nb_indices[ij * 4], i, j, N, M, NM);
                ij++;
            }
        }
    }


    // set nb pointers for patches
    ij = 0;
    for (size_t i = 0; i < N; i++) {
        for (size_t j = 0; j < M; j++) {
            set_nb(world, &nb_indices[ij * 4], ij, NM);
            ij++;
        }
    }

    //////// Begin Running ////////

    // init payoff & natural death rates
    ij = 0;
    for (size_t i = 0; i < N; i++) {
        for (size_t j = 0; j < M; j++) {
            update_pi_k(&world[ij], &(mod->X[ij * 4]), &(mod->P[ij * 6]));
            ij++;
        }
    }

    // init migration rates & store patch rates
    ij = 0;
    for (size_t i = 0; i < N; i++) {
        for (size_t j = 0; j < M; j++) {
            uint8_t mig_result = init_mig(&world[ij], &(mod->P[ij * 6]));  // init mig rates for all 4 directions
            if (mig_result == SIM_OVERFLOW) {
                return -1 * SIM_OVERFLOW;
            }
            double ij_rates = world[ij].sum_pi_death_rates + world[ij].sum_mig_rates;
            patch_rates[ij] = ij_rates;
            sum_rates_by_row[i] += ij_rates;
            *sum_rates_p = *sum_rates_p + ij_rates;  // can't do *sum_rates_p += ij_rates
            ij++;
        }
    }

    // pick the first random event
    double expected_sum = random01() * *sum_rates_p;
    find_patch(picked_p, expected_sum, patch_rates, sum_rates_by_row, *sum_rates_p, N, M);
    size_t picked_idx = picked_p->i * M + picked_p->j;
    size_t e0 = find_event(&world[picked_idx], expected_sum - picked_p->current_sum);

    // make signal
    if (mod->boundary) {
        make_signal_zero_flux(picked_p->i, picked_p->j, e0, sig_p); 
    } else {
        make_signal_periodical(N, M, picked_p->i, picked_p->j, e0, sig_p);
    }
    sig_p->ij1 = sig_p->i1 * M + sig_p->j1;
    sig_p->ij2 = sig_p->i2 * M + sig_p->j2; 

    // update patch based on signal
    change_popu(&world[sig_p->ij1], sig_p->e1);
    if (sig_p->rela_loc != NO_MIG) {
        change_popu(&world[sig_p->ij2], sig_p->e2);
    }

    // time increment
    double time = (1.0 / *sum_rates_p) * log(1.0 / random01());

    if (time > mod->maxtime) {
        // maxtime too small
        return -1 * SMALL_MAXTIME;
    }

    // store data
    if (time > mod->record_itv) {
        size_t recod_idx = (size_t) (time / mod->record_itv);
        ij = 0;
        for (size_t i = 0; i < N; i++) {
            for (size_t j = 0; j < M; j++) {
                for (size_t k = 0; k < recod_idx; k++) {
                    mod->U1d[ij * max_record + k] += world[ij].U;
                    mod->V1d[ij * max_record + k] += world[ij].V;
                    mod->Upi_1d[ij * max_record + k] += world[ij].U_pi;
                    mod->Vpi_1d[ij * max_record + k] += world[ij].V_pi;
                }
                ij++;
            }
        } 
    }

    return time;
}



static uint8_t single_test(model_t* restrict mod, uint32_t update_sum_freq, char* message) {
    // bring some dimensions to the front
    size_t N = mod->N;
    size_t M = mod->M;
    size_t NM = N * M;
    double maxtime = mod->maxtime;
    size_t max_record = mod->max_record;
    double record_itv = mod->record_itv;
    bool boundary = mod->boundary;

    double one_time = maxtime / (double)(update_sum_freq > 100 ? update_sum_freq : 100);
    double one_progress = 0.0;
    
    if (mod->print_pct != -1) {
        one_progress = maxtime * mod->print_pct / 100.0;
        fprintf(stdout, "\r                     ");
        fprintf(stdout, "\r%s: 0 %%", message);
        fflush(stdout);
    } else {
        one_progress = 2.0 * maxtime;
    }

    double one_update_sum = maxtime / (double) (update_sum_freq + 1);

    double current_time = one_time;
    double current_progress = one_progress;
    double current_update_sum = one_update_sum;

    // Initialize simulation
    patch_t* world = (patch_t*) calloc(NM, sizeof(patch_t));
    size_t* nb_indices = (size_t*) calloc(NM * 4, sizeof(size_t));

    double* patch_rates = (double*) calloc(NM, sizeof(double));
    double* sum_rates_by_row = (double*) calloc(N, sizeof(double));
    double sum_rates = 0;

    signal_t signal;
    patch_picked_t picked;

    double time = single_init(mod, world, nb_indices, patch_rates, sum_rates_by_row, &sum_rates, &signal, &picked);
    if (time == -1 * SMALL_MAXTIME) {
        // time too small
        fprintf(stdout, "\nError: maxtime too small.\n");
        fflush(stdout);
        single_test_free(&world, &nb_indices, &patch_rates,  &sum_rates_by_row);
        return SMALL_MAXTIME;
    } else if (time == -1 * SIM_OVERFLOW) {
        fprintf(stdout, "\nError: overflow at t = 0\n");
        fflush(stdout);
        single_test_free(&world, &nb_indices, &patch_rates,  &sum_rates_by_row);
        return SIM_OVERFLOW;
    }
    size_t record_index = time / mod->record_itv;
    double record_time = time - record_index * record_itv;


    while (time < maxtime) {

        // Print progress and update sums if needed
        if (time > current_time) {
            current_time += one_time;
            if (time > current_progress) {
                uint8_t curr_prog = (uint8_t)(time * 100 / maxtime);
                if (curr_prog < 10) {
                    fprintf(stdout, "\r%s: %d %%", message, (int)(time * 100 / maxtime));
                } else {
                    fprintf(stdout, "\r%s: %d%%", message, (int)(time * 100 / maxtime));
                }
                fflush(stdout);
                //fflush(stdout);  // Make sure it prints immediately
                current_progress += one_progress;
            }
            if (time > current_update_sum) {
                current_update_sum += one_update_sum;

                // recalculate sum
                size_t ij = 0;
                for (size_t i = 0; i < N; i++) {
                    for (size_t j = 0; j < M; j++) {
                        world[ij].sum_U_weight = 0;
                        world[ij].sum_V_weight = 0;
                        for (size_t k = 0; k < 4; k++) {
                            world[ij].sum_U_weight += world[ij].U_weight[k];
                            world[ij].sum_V_weight += world[ij].V_weight[k];
                        }
                    }
                }
                ij = 0;
                for (size_t i = 0; i < N; i++) {
                    sum_rates_by_row[i] = 0;
                    for (size_t j = 0; j < M; j++) {
                        sum_rates_by_row[i] += patch_rates[ij];
                        ij++;
                    }
                }
                sum_rates = 0;
                for (size_t i = 0; i < N; i++) {
                    sum_rates += sum_rates_by_row[i];
                }
            }
        }

        // update last-changed patches
        // subtract old rates first, then update patch, then add new rates
        // and split into cases whether there are two or one last-changed patches (because need to update all payoffs first and then mig rates)
        size_t si1 = signal.i1;
        size_t si2 = signal.i2;
        size_t sij1 = signal.ij1;
        size_t sij2 = signal.ij2;
        uint8_t rela_loc = signal.rela_loc;
        if (rela_loc == NO_MIG) {
            // if only one
            sum_rates_by_row[si1] -= patch_rates[sij1];
            sum_rates -= patch_rates[sij1];

            update_pi_k(&world[sij1], &(mod->X[sij1 * 4]), &(mod->P[sij1 * 6]));
            init_mig(&world[sij1], &(mod->P[sij1 * 6]));

            patch_rates[sij1] = world[sij1].sum_pi_death_rates + world[sij1].sum_mig_rates;
            sum_rates_by_row[si1] += patch_rates[sij1];
            sum_rates += patch_rates[sij1];
        } else {
            // two
            sum_rates_by_row[si1] -= patch_rates[sij1];
            sum_rates_by_row[si2] -= patch_rates[sij2];
            sum_rates -= patch_rates[sij1];
            sum_rates -= patch_rates[sij2];

            update_pi_k(&world[sij1], &(mod->X[sij1 * 4]), &(mod->P[sij1 * 6]));  // update both patches' payoffs first
            update_pi_k(&world[sij2], &(mod->X[sij2 * 4]), &(mod->P[sij2 * 6]));

            if (update_mig_weight_rate(&world[sij1], &(mod->P[sij1 * 6]), rela_loc) == SIM_OVERFLOW || 
                update_mig_weight_rate(&world[sij2], &(mod->P[sij2 * 6]), rela_loc ^ 1) == SIM_OVERFLOW) {

                fprintf(stdout, "\nError: overflow at t = %f\n", time);
                fflush(stdout);
                single_test_free(&world, &nb_indices, &patch_rates,  &sum_rates_by_row);
                return SIM_OVERFLOW;
            }

            patch_rates[sij1] = world[sij1].sum_pi_death_rates + world[sij1].sum_mig_rates;
            patch_rates[sij2] = world[sij2].sum_pi_death_rates + world[sij2].sum_mig_rates;
            sum_rates_by_row[si1] += patch_rates[sij1];
            sum_rates_by_row[si2] += patch_rates[sij2];
            sum_rates += patch_rates[sij1];
            sum_rates += patch_rates[sij2];
        }

        // update neighbors of last-changed patches
        if (rela_loc == NO_MIG) {
            for (uint8_t k = 0; k < 4; k++) {
                size_t nb_idx = nb_indices[sij1 * 4 + k];
                if (nb_idx == NM) { continue; }  // invalid neighbor
                // all neighbors, as long as exists, need to change
                if (update_mig_weight_rate(&world[nb_idx], &(mod->P[nb_idx * 6]), k ^ 1) == SIM_OVERFLOW) {
                    fprintf(stdout, "\nError: overflow at t = %f\n", time);
                    fflush(stdout);
                    single_test_free(&world, &nb_indices, &patch_rates,  &sum_rates_by_row);
                    return SIM_OVERFLOW;
                }
                // patch_rates, and sums of rates is not changed
            }
        } else {
            // the first patch
            for (uint8_t k = 0; k < 4; k++) {
                size_t nb_idx = nb_indices[sij1 * 4 + k];
                if (nb_idx == NM) { continue; }
                if (nb_need_change(nb_idx, sij1, sij2)) {
                    if (update_mig_weight_rate(&world[nb_idx], &(mod->P[nb_idx * 6]), k ^ 1) == SIM_OVERFLOW) {
                        fprintf(stdout, "\nError: overflow at t = %f\n", time);
                        fflush(stdout);
                        single_test_free(&world, &nb_indices, &patch_rates,  &sum_rates_by_row);
                        return SIM_OVERFLOW;
                    }
                }
            }
            // the second patch
            for (uint8_t k = 0; k < 4; k++) {
                size_t nb_idx = nb_indices[sij2 * 4 + k];
                if (nb_idx == NM) { continue; }
                if (nb_need_change(nb_idx, sij1, sij2)) {
                    if (update_mig_weight_rate(&world[nb_idx], &(mod->P[nb_idx * 6]), k ^ 1) == SIM_OVERFLOW) {
                        fprintf(stdout, "\nError: overflow at t = %f\n", time);
                        fflush(stdout);
                        single_test_free(&world, &nb_indices, &patch_rates,  &sum_rates_by_row);
                        return SIM_OVERFLOW;
                    }
                }
            }
        }


        // pick a random event
        double expected_sum = random01() * sum_rates;
        find_patch(&picked, expected_sum, patch_rates, sum_rates_by_row, sum_rates, N, M);
        size_t picked_idx = picked.i * M + picked.j;
        uint8_t e0 = find_event(&world[picked_idx], expected_sum - picked.current_sum);

        // make signal
        if (boundary) {
            make_signal_zero_flux(picked.i, picked.j, e0, &signal);
        } else {
            make_signal_periodical(N, M, picked.i, picked.j, e0, &signal);
        }
        signal.ij1 = signal.i1 * M + signal.j1;
        signal.ij2 = signal.i2 * M + signal.j2; 

        // let the event happenn
        change_popu(&world[signal.ij1], signal.e1);
        if (signal.rela_loc != NO_MIG) {
            change_popu(&world[signal.ij2], signal.e2);
        }

        // increase time
        double dt = (1.0 / sum_rates) * log(1.0 / random01());
        time += dt;
        record_time += dt;

        // record data
        if (time < maxtime) {
            if (record_time > record_itv) {
                size_t multi_records = record_time / record_itv;
                record_time -= multi_records * record_itv;
                size_t upper = record_index + multi_records;

                size_t ij = 0;
                for (size_t i = 0; i < N; i++) {
                    for (size_t j = 0; j < M; j++) {
                        for (size_t k = record_index; k < upper; k++) {
                            mod->U1d[ij * max_record + k] += world[ij].U;
                            mod->V1d[ij * max_record + k] += world[ij].V;
                            mod->Upi_1d[ij * max_record + k] += world[ij].U_pi;
                            mod->Vpi_1d[ij * max_record + k] += world[ij].V_pi;
                        }
                        ij++;
                    }
                }
                record_index += multi_records;
            }

        } else {
            // if already exceeds maxtime
            size_t ij = 0;
            for (size_t i = 0; i < N; i++) {
                for (size_t j = 0; j < M; j++) {
                    for (size_t k = record_index; k < max_record; k++) {
                        mod->U1d[ij * max_record + k] += world[ij].U;
                        mod->V1d[ij * max_record + k] += world[ij].V;
                        mod->Upi_1d[ij * max_record + k] += world[ij].U_pi;
                        mod->Vpi_1d[ij * max_record + k] += world[ij].V_pi;
                    }
                    ij++;
                }
            }
        }
    }

    //////// End of while loop ////////

    /*if (mod->print_pct != -1) {
        fprintf(stdout, "\r%s: 100%%", message);
        fflush(stdout);
    }*/

    single_test_free(&world, &nb_indices, &patch_rates,  &sum_rates_by_row);

    return SUCCESS;
}



static void single_test_free(patch_t** world, size_t** nb_indices, double** patch_rates, double** sum_rates_by_row) {
    free(*world);
    free(*nb_indices);
    free(*patch_rates);
    free(*sum_rates_by_row);
    *world = NULL;
    *nb_indices = NULL;
    *patch_rates = NULL;
    *sum_rates_by_row = NULL;
}



uint8_t run(model_t* mod, char* message, size_t msg_len, uint32_t update_sum_freq) {
    if (!mod->data_empty) {
        // this won't happen if called from python, the ``simulation.run`` caller has checked it.
        fprintf(stdout, "Error: mod has non-empty data\n");
        fflush(stdout);
        return DATA_NOT_EMPTY;
    }

    double start = clock();

    mod->data_empty = false;

    // initialize random
    if (mod->seed != -1) {
        srand((uint32_t) mod->seed);
    } else {
        srand(time(NULL));
    }

    if (mod->seed == -1){
        srand(time(NULL));
    } else {
        srand(mod->seed);
    }

    if (mod->print_pct == 0) {
        mod->print_pct = 5;  // default print_pct
    }

    size_t i = 0;

    while (i < mod->sim_time) {
        char curr_msg[100 + msg_len];  // message for current round
        strcpy(curr_msg, message);
        strcat(curr_msg, "round ");
        snprintf(curr_msg + strlen(curr_msg), sizeof(curr_msg) - strlen(curr_msg), "%zu", i);

        /*if (predict_runtime && i > 0) {
            double time_elapsed = timer() - start;
            double pred_runtime = time_elapsed / i * (mod->sim_time - i);
            snprintf(end_info, sizeof(end_info), ", ~%.2fs left", pred_runtime);
        }*/

        uint8_t result = single_test(mod, update_sum_freq, curr_msg);
        
        switch (result) {
            case SUCCESS:
                i++;
                break;
            case SMALL_MAXTIME:
                // error message is handled by single_test
                return SMALL_MAXTIME;
            case SIM_OVERFLOW:
                // error message is handled by single_test
                return SIM_OVERFLOW;
        }
    }

    calculate_ave(mod);

    double stop = clock();

    fprintf(stdout, "\r%sruntime: %.3fs             \n", message, (double)(stop - start) / CLOCKS_PER_SEC);
    fflush(stdout);
    return SUCCESS;
}



