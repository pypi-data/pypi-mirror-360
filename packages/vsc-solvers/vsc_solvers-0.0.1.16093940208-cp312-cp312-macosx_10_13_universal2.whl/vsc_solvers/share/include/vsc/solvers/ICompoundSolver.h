/*
 * ICompoundSolver.h
 *
 *  Created on: Mar 23, 2022
 *      Author: mballance
 */

#pragma once
#include <memory>
#include "vsc/dm/IModelField.h"
#include "vsc/dm/ITypeConstraint.h"
#include "vsc/solvers/IRandState.h"
#include "vsc/solvers/impl/RefPathSet.h"

namespace vsc {
namespace solvers {

enum class SolveFlags {
	NoFlags = 0,

	// Randomize fields that are marked used-random (not resolved)
	// Without Randomize set, only SAT/UNSAT is evaluated
	Randomize = (1 << 0),

	// Randomize all decl-rand fields even if they are initially
	// marked 'not UseRandom'
	RandomizeDeclRand = (1 << 1),

	// Consider top fields (and any decl-rand) to be used-random
	// RandomizeTopFields implies Randomize
	RandomizeTopFields = (1 << 2),

	// Produce diagnostics if a failure occurs
	DiagnoseFailures = (1 << 3)
};

static inline SolveFlags operator | (const SolveFlags lhs, const SolveFlags rhs) {
	return static_cast<SolveFlags>(
			static_cast<uint32_t>(lhs) | static_cast<uint32_t>(rhs));
}

static inline SolveFlags operator & (const SolveFlags lhs, const SolveFlags rhs) {
	return static_cast<SolveFlags>(static_cast<uint32_t>(lhs) & static_cast<uint32_t>(rhs));
}

static inline bool operator && (const SolveFlags lhs, const SolveFlags rhs) {
	return (static_cast<uint32_t>(lhs) && static_cast<uint32_t>(rhs));
}

static inline bool operator || (const SolveFlags lhs, const SolveFlags rhs) {
	return (static_cast<uint32_t>(lhs) || static_cast<uint32_t>(rhs));
}

static inline SolveFlags operator ~ (const SolveFlags lhs) {
	return static_cast<SolveFlags>(~static_cast<uint32_t>(lhs));
}

class ICompoundSolver;
using ICompoundSolverUP=std::unique_ptr<ICompoundSolver>;
class ICompoundSolver {
public:

	virtual ~ICompoundSolver() { }

	virtual bool randomize(
			IRandState								    *randstate,
            dm::IModelField                             *root_field,
            const RefPathSet                            &target_fields,
            const RefPathSet                            &fixed_fields,
            const RefPathSet                            &include_constraints,
            const RefPathSet                            &exclude_constraints,
			SolveFlags								    flags) = 0;

	virtual bool sat(
            dm::IModelField                             *root_field,
            const RefPathSet                            &target_fields,
            const RefPathSet                            &fixed_fields,
            const RefPathSet                            &include_constraints,
            const RefPathSet                            &exclude_constraints,
			SolveFlags								    flags) = 0;
};

}
}


