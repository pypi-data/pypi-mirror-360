/**
 * TaskPath2Constraint.h
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
#include "vsc/dm/impl/VisitorBase.h"

namespace vsc {
namespace solvers {

class TaskPath2Constraint : public virtual dm::VisitorBase {
public:

    TaskPath2Constraint(dm::IModelField *root_field) :
        m_root_field(root_field) { }

    virtual ~TaskPath2Constraint() { }

    dm::ITypeConstraint *toConstraint(
        const std::vector<int32_t>      &path) {
        m_ret = 0;
        m_c_offset = path.begin()+*path.begin();
        m_it = path.begin()+1;
        m_end = path.end();
        m_root_field->accept(m_this);
        return m_ret;
    }

    virtual void visitModelField(dm::IModelField *f) override {
        f->getDataType()->accept(m_this);
    }

	virtual void visitTypeConstraintScope(dm::ITypeConstraintScope *c) override {
        dm::ITypeConstraint *cc = c->getConstraints().at(*m_it).get();
        m_it++;
        if (m_it == m_end) {
            m_ret = cc;
        } else {
            cc->accept(m_this);
        }
    }

    virtual void visitDataTypeStruct(dm::IDataTypeStruct *i) override {
        if (m_it >= m_c_offset) {
            // Index constraints, not fields
            dm::ITypeConstraint *c = i->getConstraints().at(*m_it).get();
            m_it++;
            c->accept(m_this);
        } else {
            // Index the fields
            dm::ITypeField *f = i->getField(*m_it);
            m_it++;
            f->accept(m_this);
        }
    }

protected:
    dm::IModelField                             *m_root_field;
    std::vector<int32_t>::const_iterator        m_it;
    std::vector<int32_t>::const_iterator        m_end;
    std::vector<int32_t>::const_iterator        m_c_offset;
    dm::ITypeConstraint                         *m_ret;

};

} /* namespace solvers */
} /* namespace vsc */


