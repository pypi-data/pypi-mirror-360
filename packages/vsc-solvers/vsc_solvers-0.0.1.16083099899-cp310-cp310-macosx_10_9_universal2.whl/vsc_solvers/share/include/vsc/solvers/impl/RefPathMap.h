/**
 * RefPathMap.h
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
#include <vector>

namespace vsc {
namespace solvers {



template <class T> class RefPathMap {
public:
/*
    struct const_iterator {
        std::vector<std::pair<int32_t, Node *>> node_s;

    }
 */


public:
    RefPathMap(int sz=2) : m_root(allocNonLeaf(sz)), m_size(0) { }

    virtual ~RefPathMap() {}

    int32_t size() const { return m_size; }


    bool add(
        const std::vector<int32_t>  &path,
        const T                     &data,
        bool                        overwrite=false) {
        LeafNode *node = findLeaf(path, true);

        if (!node->leaves[path.back()].valid || overwrite) {
            node->leaves[path.back()].valid = true;
            node->leaves[path.back()].value = data;
            m_size++;
            return true;
        } else {
            return false;
        }
    }

    bool find(
        const std::vector<int32_t> &path,
        T                          &data) { 
        LeafNode *node = findLeaf(path, false);

        if (node && path.back() < node->base.sz &&
                        node->leaves[path.back()].valid) {
            data = node->leaves[path.back()].value;
            return true;
        } else {
            return false;
        }
    }

private:

    struct Node {
        bool        isLeaf;
        uint32_t    sz;
    };

    struct Value {
        T           value;
        bool        valid;
    };

    struct LeafNode {
        Node        base;
        Value       leaves[1];
    };

    struct NonLeafNode {
        Node        base;
        LeafNode    *leafNode;
        Node        *nodes[1];
    };

public:
    struct iterator {
        iterator(NonLeafNode *root) {
            m_node_s.push_back(&root->base);
            m_path.push_back(-1);
        }
        iterator(const iterator &rhs) :
            m_node_s(rhs.m_node_s.begin(), rhs.m_node_s.end()),
            m_path(rhs.m_path.begin(), rhs.m_path.end()),
            m_value(rhs.m_value) { }
        void operator =(const iterator &rhs) {
            m_node_s.clear();
            m_node_s.insert(m_node_s.begin(), 
                rhs.m_node_s.begin(), rhs.m_node_s.end());
            m_path.clear();
            m_path.insert(m_path.begin(), rhs.m_path.begin(), rhs.m_path.end());
        }

        std::vector<int32_t>                    m_path;
        T                                       m_value;
        std::vector<Node *>                     m_node_s;

        const std::vector<int32_t> &path() const {
            return m_path;
        }

        T value() const {
            return m_value;
        }

        bool next() {
            bool found = false;
            while (m_node_s.size()) {
                // If we're at leaf level, see if there's more for us
                if (m_node_s.back()->isLeaf) {
                    LeafNode *leaf = reinterpret_cast<LeafNode *>(m_node_s.back());
                    m_path.back()++;
                    while (m_path.back() < leaf->base.sz) {
                        if (leaf->leaves[m_path.back()].valid) {
                            found = true;
                            m_value = leaf->leaves[m_path.back()].value;
                            break;
                        } else {
                            m_path.back()++;
                        }
                    }

                    if (!found) {
                        m_node_s.pop_back();
                        m_path.pop_back();
                    }
                } else {
                    NonLeafNode *nleaf = reinterpret_cast<NonLeafNode *>(m_node_s.back());
                    bool have_subnode = false;

                    m_path.back()++;
                    while (m_path.back() < nleaf->base.sz) {
                        if (nleaf->nodes[m_path.back()]) {
                            m_node_s.push_back(nleaf->nodes[m_path.back()]);
                            m_path.push_back(-1);
                            have_subnode = true;
                            break;
                        } else {
                            m_path.back()++;
                        }
                    }

                    if (!have_subnode) {
                        if (nleaf->leafNode) {
                            // Replace the compound node with a leaf node
                            m_node_s.pop_back();
                            m_path.pop_back();
                            m_node_s.push_back(&nleaf->leafNode->base);
                            m_path.push_back(-1);
                        } else {
                            // Nothing more to do in the compound node, so
                            // move back up the stack
                            m_node_s.pop_back();
                            m_path.pop_back();
                        }
                    }
                }
                if (found) {
                    break;
                }
            }

            return found;
        }
    };

    iterator begin() const {
        return iterator(m_root);
    }

private:

    LeafNode *findLeaf(
        const std::vector<int32_t>  &path,
        bool                        create) {
        LeafNode *ret = 0;
        Node    **npp = reinterpret_cast<Node **>(&m_root);

        for (std::vector<int32_t>::const_iterator 
            it=path.begin();
            it!=path.end(); it++) {
            std::vector<int32_t>::const_iterator it_nn = it+2;
            bool is_last = (it+1 == path.end());

            if (is_last) {
                LeafNode **leaf_np;
                if (!(*npp)->isLeaf) {
                    NonLeafNode *n = reinterpret_cast<NonLeafNode *>(*npp);
                    if (n->leafNode && *it < n->leafNode->base.sz) {
                        leaf_np = &n->leafNode;
                    } else if (create) {
                        // We're at the last path entry, but we're looking at
                        // a non-leaf node. 
                        // Use the leaf-node pointer
                        if (!n->leafNode) {
                            n->leafNode = allocLeaf((*it));
                        } else if (*it >= n->leafNode->base.sz) {
                            // Need to realloc for more space
                            n->leafNode = reallocLeaf(n->leafNode, (*it));
                        }
                        leaf_np = &n->leafNode;
                    } else {
                        break;
                    }
                } else {
                    leaf_np = reinterpret_cast<LeafNode **>(npp);
                }

                if ((*it) < (*leaf_np)->base.sz) {
                    ret = (*leaf_np);
                } else if (create) {
                    LeafNode *leaf_p = *leaf_np;
                    (*leaf_np) = reallocLeaf(leaf_p, (*it));
                    ret = (*leaf_np);
                }
            } else {
                // Not last
                NonLeafNode **nleaf_np;
                if ((*npp)->isLeaf) {
                    // We need to replace this leaf node with a non-leaf node
                    // that references the leaf node
                    if (create) {
                        NonLeafNode *n = allocNonLeaf((*it));
                        n->leafNode = reinterpret_cast<LeafNode *>(*npp);
                        (*npp) = &n->base;
                    } else {
                        break;
                    }
                }
                nleaf_np = reinterpret_cast<NonLeafNode **>(npp);

                if (*it >= (*nleaf_np)->base.sz) {
                    // Need to resize
                    (*nleaf_np) = reallocNonLeaf(*nleaf_np, (*it));
                }

                if (!(*nleaf_np)->nodes[(*it)]) {
                    if (create) {
                        // Need to add 
                        if (it_nn == path.end()) {
                            // The next element will be a leaf index
                            (*nleaf_np)->nodes[(*it)] = reinterpret_cast<Node *>(allocLeaf(*(it+1)));
                        } else {
                            // The next element is still a non-leaf index
                            (*nleaf_np)->nodes[(*it)] = reinterpret_cast<Node *>(allocNonLeaf(*(it+1)));
                        }
                    } else {
                        break;
                    }
                }
                npp = reinterpret_cast<Node **>(&(*nleaf_np)->nodes[(*it)]);
            }
        }
        return ret;
    }

    static uint32_t pow2(uint32_t n) {
        uint32_t n_t=n-1;
        uint32_t n_p2 = 0;
        while (n_t) {
            n_p2 += 1;
            n_t >>= 1;
        }
        return (1 << n_p2);
    }

    NonLeafNode *allocNonLeaf(uint32_t max) {
        uint32_t max_t = pow2(max);

        NonLeafNode *node = reinterpret_cast<NonLeafNode *>(::operator new(
            sizeof(NonLeafNode) + ((max_t)*sizeof(Node *))
        ));

        memset(node, 0, sizeof(NonLeafNode)+((max_t)*sizeof(Node *)));
        node->base.isLeaf = false;
        node->base.sz = max_t+1;

        return node;
    }

    LeafNode *allocLeaf(uint32_t max) {
        uint32_t max_t = pow2(max);

        LeafNode *node = reinterpret_cast<LeafNode *>(::operator new(
            sizeof(LeafNode)+((max_t)*sizeof(Value))
        ));

        memset(node, 0, sizeof(LeafNode) + ((max_t)*sizeof(Value)));
        node->base.isLeaf = true;
        node->base.sz = max_t+1;

        return node;
    }

    NonLeafNode *reallocNonLeaf(NonLeafNode *node, uint32_t max) {
        uint32_t max_t = pow2(max);

        NonLeafNode *nnode = reinterpret_cast<NonLeafNode *>(::operator new(
            sizeof(NonLeafNode) + ((max_t)*sizeof(Node *))
        ));

        nnode->base.isLeaf = false;
        nnode->leafNode = node->leafNode;
        for (uint32_t i=0; i<node->base.sz; i++) {
            nnode->nodes[i] = node->nodes[i];
        }

        for (uint32_t i=node->base.sz; i<max_t+1; i++) {
            nnode->nodes[i] = 0;
        }
        nnode->base.sz = max_t+1;

        ::operator delete(node);

        return nnode;
    }

    LeafNode *reallocLeaf(LeafNode *node, uint32_t max) {
        uint32_t max_t = pow2(max);

        LeafNode *nnode = reinterpret_cast<LeafNode *>(::operator new(
            sizeof(LeafNode)+((max_t)*sizeof(Value))
        ));

        nnode->base.isLeaf = true;
        nnode->base.sz = max_t+1;

        for (uint32_t i=0; i<node->base.sz; i++) {
            nnode->leaves[i] = node->leaves[i];
        }
        for (uint32_t i=node->base.sz; i<nnode->base.sz; i++) {
            nnode->leaves[i].valid = false;
        }

        ::operator delete(node);

        return nnode;
    }


private:
    NonLeafNode     *m_root;
    int32_t         m_size;

};


}
}


