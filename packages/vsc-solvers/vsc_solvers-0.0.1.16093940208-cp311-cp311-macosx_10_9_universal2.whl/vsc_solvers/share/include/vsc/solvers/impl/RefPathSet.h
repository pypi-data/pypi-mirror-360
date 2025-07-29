/**
 * RefPathSet.h
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
#include <string.h>
#include <vector>

namespace vsc {
namespace solvers {



class RefPathSet {
public:
public:
    RefPathSet() : m_size(0) {
        m_root = allocNonLeaf(8);
    }

    virtual ~RefPathSet() {

    }

    bool add(const std::vector<int32_t> &path) {
        bool ret = true;
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
                    // We're at the last path entry, but we're looking at
                    // a non-leaf node. 
                    // Use the leaf-node pointer
                    if (!n->leafNode) {
                        n->leafNode = allocLeaf((*it)+1);
                    } else if (n->leafNode->base.sz <= *it) {
                        // Need to realloc for more space
                        n->leafNode = reallocLeaf(n->leafNode, (*it)+1);
                    }
                    leaf_np = &n->leafNode;
                } else {
                    leaf_np = reinterpret_cast<LeafNode **>(npp);
                }

                // Calculate how many words we need to store 
                uint32_t req_words = (((*it))/(8*sizeof(uintptr_t)))+1;

                if (req_words > (*leaf_np)->base.sz) {
                    LeafNode *leaf_p = *leaf_np;
                    (*leaf_np) = reallocLeaf(leaf_p, req_words);
                }

                uint32_t idx = (*it)/(sizeof(uintptr_t)*8);
                uint32_t off = (*it) % (sizeof(uintptr_t)*8);
                if ((*leaf_np)->leaves[idx] & (1ULL << off)) {
                    // This element already exists
                    ret = false;
                } else {
                    (*leaf_np)->leaves[idx] |= (1ULL << off);
                }
            } else {
                // Not last
                NonLeafNode **nleaf_np;
                if ((*npp)->isLeaf) {
                    // We need to replace this leaf node with a non-leaf node
                    // that references the leaf node
                    NonLeafNode *n = allocNonLeaf((*it)+1);
                    n->leafNode = reinterpret_cast<LeafNode *>(*npp);
                    (*npp) = &n->base;
                }
                nleaf_np = reinterpret_cast<NonLeafNode **>(npp);

                if (*it >= (*nleaf_np)->base.sz) {
                    // Need to resize
                    (*nleaf_np) = reallocNonLeaf(*nleaf_np, (*it)+1);
                }

                if (!(*nleaf_np)->nodes[(*it)]) {
                    // Need to add 
                    if (it_nn == path.end()) {
                        // The next element will be a leaf index
                        (*nleaf_np)->nodes[(*it)] = reinterpret_cast<Node *>(allocLeaf(*(it+1)+1));
                    } else {
                        // The next element is still a non-leaf index
                        (*nleaf_np)->nodes[(*it)] = reinterpret_cast<Node *>(allocNonLeaf(*(it+1)+1));
                    }
                }
                npp = reinterpret_cast<Node **>(&(*nleaf_np)->nodes[(*it)]);
            }
        }

        if (ret) {
            m_size++;
        }

        return ret;
    }

    bool remove(const std::vector<int32_t> &path) const {
        Node *n = &m_root->base;
        for (std::vector<int32_t>::const_iterator
            it=path.begin();
            it!=path.end(); it++) {
            if (it+1 == path.end()) {
                LeafNode *leaf = 0;
                if (n->isLeaf) {
                    leaf = reinterpret_cast<LeafNode *>(n);
                } else if (reinterpret_cast<NonLeafNode *>(n)->leafNode) {
                    leaf = reinterpret_cast<NonLeafNode *>(n)->leafNode;
                }
                if (leaf) {
                    uint32_t idx = *it/(8*sizeof(uintptr_t));
                    uint32_t off = *it % (8*sizeof(uintptr_t));
                    if (idx < leaf->base.sz && (leaf->leaves[idx]&(1ULL << off))) {
                        leaf->leaves[idx] &= (1ULL << off);
                    } else {
                        break;
                    }
                } else {
                    return false;
                }
            } else if (!n->isLeaf) {
                // Intermediate node
                NonLeafNode *nleaf = reinterpret_cast<NonLeafNode *>(n);
                if (*it < n->sz && nleaf->nodes[*it]) {
                    n = nleaf->nodes[*it];
                } else {
                    break;
                }
            } else {
                break;
            }
        }

        return false;
    }
    
    bool empty() const {
        return m_size == 0;
    }

    int32_t size() const {
        return m_size;
    }

    bool find(const std::vector<int32_t> &path) const {
        Node *n = &m_root->base;
        for (std::vector<int32_t>::const_iterator
            it=path.begin();
            it!=path.end(); it++) {
            if (it+1 == path.end()) {
                LeafNode *leaf = 0;
                if (n->isLeaf) {
                    leaf = reinterpret_cast<LeafNode *>(n);
                } else if (reinterpret_cast<NonLeafNode *>(n)->leafNode) {
                    leaf = reinterpret_cast<NonLeafNode *>(n)->leafNode;
                }
                if (leaf) {
                    uint32_t idx = *it/(8*sizeof(uintptr_t));
                    uint32_t off = *it % (8*sizeof(uintptr_t));
                    return (idx < leaf->base.sz && (leaf->leaves[idx]&(1ULL << off)));
                } else {
                    return false;
                }
            } else if (!n->isLeaf) {
                // Intermediate node
                NonLeafNode *nleaf = reinterpret_cast<NonLeafNode *>(n);
                if (*it < n->sz && nleaf->nodes[*it]) {
                    n = nleaf->nodes[*it];
                } else {
                    break;
                }
            } else {
                break;
            }
        }

        return false;
    }

private:

    struct Node {
        bool        isLeaf;
        uint32_t    sz;
    };

    struct LeafNode {
        Node        base;
        uintptr_t   leaves[1];
    };

    struct NonLeafNode {
        Node        base;
        LeafNode    *leafNode;
        Node        *nodes[1];
    };

private:
    bool empty(Node *n) const {
        if (n->isLeaf) {
            LeafNode *leaf = reinterpret_cast<LeafNode *>(n);
            for (uint32_t i=0; i<leaf->base.sz; i++) {
                if (leaf->leaves[i]) {
                    return false;
                }
            }
        } else {
            NonLeafNode *nleaf = reinterpret_cast<NonLeafNode *>(n);
            // To qualify as empty, all sub-trees must report empty
            // and any leafNode must be empty as well
            if (nleaf->leafNode) {
                if (!empty(&nleaf->leafNode->base)) {
                    return false;
                }
            }

            for (uint32_t i=0; i<n->sz; i++) {
                if (nleaf->nodes[i] && !empty(nleaf->nodes[i])) {
                    return false;
                }
            }
        }
        return true;
    }

public:
    class iterator {
    public:
        iterator(NonLeafNode *root) {
            m_node_s.push_back(&root->base);
            m_path.push_back(-1);
        }

        iterator(const iterator &rhs) :
            m_node_s(rhs.m_node_s.begin(), rhs.m_node_s.end()),
            m_path(rhs.m_path.begin(), rhs.m_path.end()) { }

        void operator =(const iterator &rhs) {
            m_node_s.clear();
            m_node_s.insert(m_node_s.begin(), rhs.m_node_s.begin(), rhs.m_node_s.end());
            m_path.clear();
            m_path.insert(m_path.begin(), rhs.m_path.begin(), rhs.m_path.end());
        }

        bool next() {
            bool found = false;
            while (m_node_s.size()) {
                // If we're at leaf level, see if there's more for us
                if (m_node_s.back()->isLeaf) {
                    LeafNode *leaf = reinterpret_cast<LeafNode *>(m_node_s.back());
                    m_path.back()++;
                    while (m_path.back() < (8*sizeof(uintptr_t)*leaf->base.sz)) {
                        uint32_t word_idx = m_path.back()/(8*sizeof(uintptr_t));
                        uint32_t bit_idx = m_path.back()%(8*sizeof(uintptr_t));
                        if (!leaf->leaves[word_idx]) {
                            m_path.back() += (8*sizeof(uintptr_t));
                        } else if (leaf->leaves[word_idx] & (1ULL << bit_idx)) {
                            found = true;
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

        const std::vector<int32_t> &path() const {
            return m_path;
        }

    private:
        std::vector<Node *>         m_node_s;
        std::vector<int32_t>        m_path;
    };

    iterator begin() const {
        return iterator(m_root);
    }

private:
    NonLeafNode *allocNonLeaf(uint32_t max) {
        uint32_t sz_p2 = 0;
        uint32_t max_t = max-1;

        // Round size up to the nearest power of 2
        while (max_t) {
            sz_p2 += 1;
            max_t >>= 1;
        } 
        max_t = (1ULL << sz_p2);

        NonLeafNode *node = reinterpret_cast<NonLeafNode *>(::operator new(
            sizeof(NonLeafNode) + ((max_t-1)*sizeof(Node *))
        ));

        memset(node, 0, sizeof(NonLeafNode)+((max_t-1)*sizeof(Node *)));
        node->base.isLeaf = false;
        node->base.sz = max_t;

        return node;
    }

    LeafNode *allocLeaf(uint32_t max) {
        uint32_t sz_p2 = 0;
        uint32_t max_t = max-1;

        // Round size up to the nearest power of 2
        while (max_t) {
            sz_p2 += 1;
            max_t >>= 1;
        } 
        max_t = (1ULL << sz_p2);

        LeafNode *node = reinterpret_cast<LeafNode *>(::operator new(
            sizeof(LeafNode)+((max_t-1)*sizeof(uintptr_t))
        ));

        memset(node, 0, sizeof(LeafNode) + ((max_t-1)*sizeof(uintptr_t)));
        node->base.isLeaf = true;
        node->base.sz = max_t;

        return node;
    }

    NonLeafNode *reallocNonLeaf(NonLeafNode *node, uint32_t max) {
        uint32_t sz_p2 = 0;
        uint32_t max_t = max-1;

        // Round size up to the nearest power of 2
        while (max_t) {
            sz_p2 += 1;
            max_t >>= 1;
        } 
        max_t = (1ULL << sz_p2);

        NonLeafNode *nnode = reinterpret_cast<NonLeafNode *>(::operator new(
            sizeof(NonLeafNode) + ((max_t-1)*sizeof(Node *))
        ));

        nnode->base.isLeaf = false;
        nnode->base.sz = max_t;
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
        uint32_t sz_p2 = 0;
        uint32_t max_t = max-1;

        // Round size up to the nearest power of 2
        while (max_t) {
            sz_p2 += 1;
            max_t >>= 1;
        } 
        max_t = (1ULL << sz_p2);

        LeafNode *nnode = reinterpret_cast<LeafNode *>(::operator new(
            sizeof(LeafNode)+((max_t-1)*sizeof(uintptr_t))
        ));

        nnode->base.isLeaf = true;
        nnode->base.sz = max_t;

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
    int32_t         m_size;

};

}
}


