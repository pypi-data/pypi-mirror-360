/**
 * TaskPath2Field.h
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
#include "vsc/solvers/impl/RefPathField.h"

namespace vsc {
namespace solvers {



class TaskPath2Field : dm::VisitorBase {
public:

    TaskPath2Field(dm::IModelField *root_field) : m_root_field(root_field) { }

    virtual ~TaskPath2Field() { }

    dm::ITypeField *toField(const RefPathField &path) {
        m_ret = 0;
        m_it = path.begin();
        m_end = path.end();
        m_root_field->accept(m_this);
        return m_ret;
    }

    virtual void visitModelField(dm::IModelField *f) override {
        f->getDataType()->accept(m_this);
    }

    virtual void visitDataTypeStruct(dm::IDataTypeStruct *i) override {
        dm::ITypeField *field = i->getField(*m_it);

        m_it++;

        if (m_it == m_end) {
            m_ret = field;
        } else {
            field->accept(m_this);
        }
    }


private:
    dm::IModelField                 *m_root_field;
    RefPathField::const_iterator    m_it;
    RefPathField::const_iterator    m_end;
    dm::ITypeField                  *m_ret;

};

} /* namespace solvers */
} /* namespace vsc */


