/*
 * IRandomizer.h
 *
 *  Created on: Feb 13, 2022
 *      Author: mballance
 */

#pragma once
#include "vsc/dm/IModelField.h"
#include "vsc/dm/IModelConstraint.h"

namespace vsc {
namespace solvers {

class IRandomizer {
public:

	virtual ~IRandomizer() { }

	virtual bool randomize(
			const std::vector<dm::IModelField *>		&fields,
			const std::vector<dm::IModelConstraint *>	&constraints,
			bool						diagnost_failures) = 0; 
};

}
}
