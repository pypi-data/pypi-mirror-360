/**
 * RefPathPtrMap.h
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



template <class T> class RefPathPtrMap {
public:
/*
    struct const_iterator {
        std::vector<std::pair<int32_t, Node *>> node_s;

    }

    struct iterator {
        bool                                    m_valid;
        std::vector<std::pair<int32_t, Node *>> m_node_s;

        void operator ++() {
            // Find the next 

        }

        bool valid() const {
            return m_valid;
        }
    };
 */
public:
    RefPathPtrMap(int sz=2) : m_root(allocNonLeaf(sz)) { }

    virtual ~RefPathPtrMap() {}

    bool add(
        const std::vector<int32_t>  &path,
        T                           *data) {
        LeafNode *node = findLeaf(path, true);

        if (!node->leaves[path.back()]) {
            node->leaves[path.back()] = data;
            return true;
        } else {
            return false;
        }
    }

    T *find(const std::vector<int32_t> &path) const {
        const LeafNode *node = findLeaf(path);

        if (node && path.back() < node->base.sz) {
            return node->leaves[path.back()];
        } else {
            return 0;
        }
    }

/*
    iterator begin() {
        iterator ret;
        ret.node_s.push_back({-1, m_root});
        return ret;
    }
 */

private:

    struct Node {
        bool        isLeaf;
        uint32_t    sz;
    };

    struct LeafNode {
        Node        base;
        T           *leaves[1];
    };

    struct NonLeafNode {
        Node        base;
        LeafNode    *leafNode;
        Node        *nodes[1];
    };

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
                        NonLeafNode *n = allocNonLeaf((*it)+1);
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

    const LeafNode *findLeaf(const std::vector<int32_t>  &path) const {
        const LeafNode *ret = 0;
        Node * const*npp = reinterpret_cast<Node * const*>(&m_root);

        for (std::vector<int32_t>::const_iterator 
            it=path.begin();
            it!=path.end(); it++) {
            std::vector<int32_t>::const_iterator it_nn = it+2;
            bool is_last = (it+1 == path.end());

            if (is_last) {
                LeafNode * const*leaf_np;
                if (!(*npp)->isLeaf) {
                    const NonLeafNode *n = reinterpret_cast<const NonLeafNode *>(*npp);
                    if (n->leafNode) {
                        leaf_np = &n->leafNode;
                    } else {
                        break;
                    }
                } else {
                    leaf_np = reinterpret_cast<LeafNode * const*>(npp);
                }

                ret = (*leaf_np);
            } else {
                // Not last
                NonLeafNode * const*nleaf_np;
                if ((*npp)->isLeaf) {
                    // We need to replace this leaf node with a non-leaf node
                    // that references the leaf node
                    break;
                }
                nleaf_np = reinterpret_cast<NonLeafNode * const*>(npp);

                if (*it >= (*nleaf_np)->base.sz || !(*nleaf_np)->nodes[(*it)]) {
                    break;
                }
                npp = reinterpret_cast<Node * const*>(&(*nleaf_np)->nodes[(*it)]);
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
            sizeof(NonLeafNode) + ((max_t-1)*sizeof(Node *))
        ));

        memset(node, 0, sizeof(NonLeafNode)+((max_t-1)*sizeof(Node *)));
        node->base.isLeaf = false;
        node->base.sz = max_t;

        return node;
    }

    LeafNode *allocLeaf(uint32_t max) {
        uint32_t max_t = pow2(max);

        LeafNode *node = reinterpret_cast<LeafNode *>(::operator new(
            sizeof(LeafNode)+((max_t)*sizeof(T *))
        ));

        memset(node, 0, sizeof(LeafNode) + ((max_t)*sizeof(T *)));
        node->base.isLeaf = true;
        node->base.sz = max_t;

        return node;
    }

    NonLeafNode *reallocNonLeaf(NonLeafNode *node, uint32_t max) {
        uint32_t max_t = pow2(max);

        NonLeafNode *nnode = reinterpret_cast<NonLeafNode *>(::operator new(
            sizeof(NonLeafNode) + ((max_t)*sizeof(Node *))
        ));

        nnode->base.isLeaf = false;
        nnode->base.sz = max_t+1;
        nnode->leafNode = node->leafNode;
        for (uint32_t i=0; i<node->base.sz; i++) {
            nnode->nodes[i] = node->nodes[i];
        }

        for (uint32_t i=node->base.sz; i<nnode->base.sz; i++) {
            nnode->nodes[i] = 0;
        }

        ::operator delete(node);

        return nnode;
    }

    LeafNode *reallocLeaf(LeafNode *node, uint32_t max) {
        uint32_t max_t = pow2(max);

        LeafNode *nnode = reinterpret_cast<LeafNode *>(::operator new(
            sizeof(LeafNode)+((max_t)*sizeof(T *))
        ));

        nnode->base.isLeaf = true;
        nnode->base.sz = max_t+1;

        for (uint32_t i=0; i<node->base.sz; i++) {
            nnode->leaves[i] = node->leaves[i];
        }
        for (uint32_t i=node->base.sz; i<nnode->base.sz; i++) {
            nnode->leaves[i] = 0;
        }

        ::operator delete(node);

        return nnode;
    }


private:
    NonLeafNode     *m_root;

};


}
}


