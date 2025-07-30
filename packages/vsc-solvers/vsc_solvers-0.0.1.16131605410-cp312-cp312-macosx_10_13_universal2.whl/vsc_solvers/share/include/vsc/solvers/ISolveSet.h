/**
 * ISolveSet.h
 *
 * Copyright 2023 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 *
 * Created on:
 *     Author: 
 */
#pragma once
#include "vsc/dm/impl/UP.h"
#include "vsc/solvers/impl/RefPathMap.h"
#include "vsc/solvers/impl/RefPathSet.h"

namespace vsc {
namespace solvers {

enum class SolveSetFlags {
    NoFlags   = 0,
    Linear    = (1 << 0),
    NonLinear = (1 << 1),
    Iterative = (1 << 2),
    ArraySize = (1 << 3),
    Soft      = (1 << 4)
};

enum class SolveSetFieldType {
    Target,
    NonTarget,
    Fixed,
    NumTypes
};

class ISolveSet;
using ISolveSetUP=dm::UP<ISolveSet>;
class ISolveSet {
public:

    virtual ~ISolveSet() { }

    virtual SolveSetFlags getFlags() const = 0;

    virtual const RefPathMap<SolveSetFieldType> &getFields() const = 0;

    virtual const RefPathSet &getConstraints() const = 0;

};

} /* namespace solvers */
} /* namespace vsc */


