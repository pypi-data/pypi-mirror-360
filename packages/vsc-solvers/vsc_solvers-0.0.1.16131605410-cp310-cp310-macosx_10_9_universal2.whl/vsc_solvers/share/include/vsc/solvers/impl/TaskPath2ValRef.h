/**
 * TaskPath2ValRef.h
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
#include <vector>
#include "vsc/dm/IModelField.h"
#include "vsc/dm/impl/ValRefStruct.h"
#include "vsc/dm/impl/VisitorBase.h"

namespace vsc {
namespace solvers {



class TaskPath2ValRef : public virtual dm::VisitorBase {
public:
    TaskPath2ValRef(dm::IModelField *root_field) :
        m_root_field(root_field) { }

    virtual ~TaskPath2ValRef() { }

    dm::ValRef toMutVal(const std::vector<int32_t> &path) {
        m_it = path.begin();
        m_it_end = path.end();
        dm::IDataType *field_t = m_root_field->getDataType();
        m_val = m_root_field->getMutVal();

        field_t->accept(m_this);

        return m_val;
    }

	virtual void visitDataTypeStruct(dm::IDataTypeStruct *t) override {
        dm::ValRefStruct val_s(m_val);

        m_val = val_s.getFieldRef(*m_it);
        dm::ITypeField *field = t->getField(*m_it);

        m_it++;

        if (m_it != m_it_end) {
            field->accept(m_this);
        }
    }

private:
    dm::IModelField                             *m_root_field;
    std::vector<int32_t>::const_iterator        m_it;
    std::vector<int32_t>::const_iterator        m_it_end;
    dm::ValRef                                  m_val;

};

}
}


