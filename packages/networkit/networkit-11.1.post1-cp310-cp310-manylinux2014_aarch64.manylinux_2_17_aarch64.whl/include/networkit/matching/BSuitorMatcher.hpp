/*
 * BSuitorMatcher.hpp
 *
 *  Created on: 07.08.2023
 *      Author: Fabian Brandt-Tumescheit
 *              Frieda Gerharz
 */

#ifndef NETWORKIT_MATCHING_B_SUITOR_MATCHER_HPP_
#define NETWORKIT_MATCHING_B_SUITOR_MATCHER_HPP_

#include <algorithm>
#include <ranges>

#include <networkit/graph/Graph.hpp>
#include <networkit/matching/BMatcher.hpp>

namespace NetworKit {

/**
 * @ingroup matching
 * B-Suitor matching finding algorithm.
 */
class BSuitorMatcher : public BMatcher {
protected:
    struct MatchingNode {
        node id;
        edgeweight weight;

        MatchingNode() : id(none), weight(0) {}
        MatchingNode(node n, edgeweight w) : id(n), weight(w) {}

        // If the edgeweight is the same for two MatchingNodes
        // then we compare the node id, where a smaller id is
        // ranked higher.
        std::partial_ordering operator<=>(const MatchingNode &other) const {
            if (auto cmp = weight <=> other.weight; cmp != 0)
                return cmp;

            return -static_cast<int64_t>(id) <=> -static_cast<int64_t>(other.id);
        }

        bool operator==(const MatchingNode &other) const = default;
    };

    struct MatchingNodeInfo {
        std::vector<MatchingNode> partners;
        MatchingNode min; // (none, 0) if partners still has free capacity
        count max_size;

        MatchingNodeInfo() = default;

        MatchingNodeInfo(count b) {
            partners.reserve(b);
            max_size = b;
        }

        bool hasPartner(node u) const {
            return std::ranges::find_if(partners, [u](const MatchingNode &v) { return v.id == u; })
                   != partners.end();
        }

        MatchingNode popMinIfFull() {
            if (partners.size() < max_size) {
                return {none, 0};
            } else {
                MatchingNode min_copy = min;
                remove(min.id);
                return min_copy;
            }
        }

        MatchingNode insert(const MatchingNode &u) {
            if (hasPartner(u.id))
                return {none, 0};

            MatchingNode prevMin = popMinIfFull();

            partners.emplace_back(u);
            if (partners.size() == max_size && !partners.empty()) {
                min = *std::ranges::min_element(partners);
            }
            return prevMin;
        }

        void remove(node u) {
            partners.erase(std::remove_if(partners.begin(), partners.end(),
                                          [u](const MatchingNode &v) { return v.id == u; }),
                           partners.end());
            min = MatchingNode();
        }
    };

public:
    /**
     * Computes a 1/2-approximate maximum weight b-matching of an undirected weighted Graph @c G
     * using the sequential b-Suitor algorithm published by Khan et al. in "Efficient Approximation
     * Algorithms For Weighted B-Matching", SIAM Journal on Scientific Computing, Vol. 38, Iss. 5
     * (2016).
     *
     * @param G An undirected graph.
     * @param b A vector of @a b values that represents the max number of edges per vertex @a v in
     * the b-Matching (b.at(v)).
     */
    BSuitorMatcher(const Graph &G, const std::vector<count> &b);

    /**
     * @param G An undirected graph.
     * @param b A value @a b that represents the max number of edges per vertex in the b-Matching.
     * Defaults to the ordinary 1-Matching.
     */
    BSuitorMatcher(const Graph &G, count b = 1);

    ~BSuitorMatcher() override = default;

    /**
     * Runs the algorithm.
     */
    void run() override;

    /**
     * Creates the b-matching for given graph G. Function run() automatically invokes
     * buildMatching. After invoking buildBMatching(), use getBMatching() to retrieve the resulting
     * b-matching.
     */
    void buildBMatching();

protected:
    std::vector<MatchingNodeInfo> suitors;
    std::vector<MatchingNodeInfo> proposed;
    const std::vector<count> b;

    /**
     * Iterates up to @a b times over the heaviest neighbors of node @a u and makes
     * them to suitors if eligible.
     *
     * @param u
     */
    void findSuitors(node u);

    /**
     * Finds the heaviest unmatched neighbor that @a u has not yet proposed to
     * if it exists. For equally weighted edges w(u, t), w(u, v) and t < v, w(u, t) is considered
     * smaller than w(u, v) to break ties.
     *
     * @param y
     * @return Node
     */
    MatchingNode findPreferred(node u);

    /**
     * Makes @a v a suitor of @a u and recursively calls itself for previous worse
     * suitors of @a u that got replaced with their new best match.
     *
     * @param u
     * @param w
     * @param v
     */
    void makeSuitor(node u, edgeweight w, node v);

    /**
     * Checks the symmetry of pairs of nodes. It must hold that v is in suitors(u) iff u is
     * in suitors(v).
     *
     */
    bool isSymmetrical() const;
};
} // namespace NetworKit

#endif // NETWORKIT_MATCHING_B_SUITOR_MATCHER_HPP_
