#ifndef _ccadical_up_h_INCLUDED
#define _ccadical_up_h_INCLUDED

/*------------------------------------------------------------------------*/
#ifdef __cplusplus
extern "C" {
#endif
/*------------------------------------------------------------------------*/

#include "../vendor/cadical/src/ccadical.h"

#include <stddef.h>
#include <stdint.h>

// C wrapper for CaDiCaL's C++ API following IPASIR-UP.

void ccadical_connect_external_propagator(
    CCaDiCaL *slv, void *propagator_data,
    void (*prop_notify_assignments)(void *prop, const int *lits, size_t size),
    void (*prop_notify_new_decision_level)(void *prop),
    void (*prop_notify_backtrack)(void *prop, size_t new_level, bool restart),
    bool (*prop_cb_check_found_model)(void *prop, const int *model,
                                      size_t size),
    bool (*prop_cb_has_external_clause)(void *prop, bool *is_forgettable),
    int (*prop_cb_add_external_clause_lit)(void *prop), bool is_lazy = false,
    bool forgettable_reasons = false, bool notify_fixed = false,
    int (*prop_cb_decide)(void *prop) = prop_decide_default,
    int (*prop_cb_propagate)(void *prop) = prop_propagate_default,
    int (*prop_cb_add_reason_clause_lit)(void *prop, int propagated_lit) =
        prop_add_reason_clause_lit_default,
    void (*prop_notify_fixed_assignment)(void *prop, int lit) =
        prop_notify_fixed_assignment_default);
void ccadical_disconnect_external_propagator(CCaDiCaL *);

void ccadical_add_observed_var(CCaDiCaL *, int var);
void ccadical_remove_observed_var(CCaDiCaL *, int var);
void ccadical_reset_observed_vars(CCaDiCaL *);
bool ccadical_is_decision(CCaDiCaL *, int lit);
void ccadical_force_backtrack(CCaDiCaL *, size_t new_level);

// Additional C bindings for C++ Cadical

CCaDiCaL *ccadical_copy(CCaDiCaL *slv);
bool ccadical_is_observed(CCaDiCaL *, int lit);
void ccadical_phase(CCaDiCaL *, int lit);
void ccadical_unphase(CCaDiCaL *, int lit);
void ccadical_enable_proof (CCaDiCaL *, const char *);

/*------------------------------------------------------------------------*/

/*------------------------------------------------------------------------*/
#ifdef __cplusplus
}
#endif
/*------------------------------------------------------------------------*/

#endif
