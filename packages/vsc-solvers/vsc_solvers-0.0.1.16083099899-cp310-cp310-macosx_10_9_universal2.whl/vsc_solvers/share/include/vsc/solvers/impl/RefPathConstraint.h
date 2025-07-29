/**
 * RefPathConstraint.h
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
#include <stdint.h>
#include <stdio.h>
#include <string>
#include <vector>



class RefPathConstraint : public std::vector<int32_t> {
public:

    RefPathConstraint(const std::vector<int32_t> &p) :
        std::vector<int32_t>(p.begin(), p.end()) { }

    virtual ~RefPathConstraint() { }

    std::vector<int32_t>::const_iterator constraint() const {
        return std::vector<int32_t>::begin()+(*std::vector<int32_t>::begin());
    }

    virtual std::vector<int32_t>::const_iterator begin() const {
        return std::vector<int32_t>::begin()+1;
    }

    std::string toString() const {
        char tmp[32];
        std::string ret = "[";

        for (std::vector<int32_t>::const_iterator
            it=begin(); it!=end(); it++) {
            if (it!=begin()) {
                ret += ",";
            }
            sprintf(tmp, "%d", *it);
            if (it == constraint()) {
                ret += "{";
                ret += tmp;
                ret += "}";
            } else {
                ret += tmp;
            }
        }

        ret += "]";

        return ret;
    }
};


