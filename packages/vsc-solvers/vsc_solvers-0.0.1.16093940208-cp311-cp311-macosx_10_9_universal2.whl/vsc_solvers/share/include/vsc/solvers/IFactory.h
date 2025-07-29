
#pragma once
#include "dmgr/IDebugMgr.h"
#include "vsc/solvers/ICompoundSolver.h"
#include "vsc/solvers/IRandState.h"
#include "vsc/solvers/ISolverFactory.h"

namespace vsc {
namespace solvers {

class IFactory {

public:
	virtual ~IFactory() { }

	virtual void init(dmgr::IDebugMgr *dmgr) = 0;

    virtual dmgr::IDebugMgr *getDebugMgr() = 0;

    virtual ISolverFactory *getSolverFactory() = 0;

	virtual ICompoundSolver *mkCompoundSolver() = 0;

    virtual IRandState *mkRandState(const std::string &seed) = 0;


};


}
}

