"""
Core functionality for the graphlib package.
"""
from typing import Optional

from relationalai.early_access.builder import Concept, Relationship
from relationalai.early_access.builder import Integer, Float
from relationalai.early_access.builder import where, define, count, sum, not_, min, union
from relationalai.early_access.builder import avg
from relationalai.early_access.builder.std.math import abs, natural_log, sqrt

class Graph():
    def __init__(self,
            *,
            directed: bool,
            weighted: bool,
            aggregator: Optional[str] = None,
        ):
        assert isinstance(directed, bool), "The `directed` argument must be a boolean."
        assert isinstance(weighted, bool), "The `weighted` argument must be a boolean."
        self.directed = directed
        self.weighted = weighted

        assert isinstance(aggregator, type(None)), "Weight aggregation not yet supported."
        # TODO: In the hopefully not-too-distant future, this argument will
        #   allow the user to specify whether and how to aggregate weights
        #   for multi-edges that exist at the user interface (Edge) level
        #   to construct the internal edge/weight list representation.
        #   The `str` type is just a placeholder; it should be something else.

        # Introduce Node and Edge concepts.
        Node = Concept("Node")
        Edge = Concept("Edge")
        Edge.src = Relationship("{edge:Edge} has source {src:Node}")
        Edge.dst = Relationship("{edge:Edge} has destination {dst:Node}")
        Edge.weight = Relationship("{edge:Edge} has weight {weight:Float}")
        self.Node = Node
        self.Edge = Edge

        # TODO: Require that each Edge has an Edge.src.
        # TODO: Require that each Edge has an Edge.dst.
        # TODO: If weighted, require that each Edge has an Edge.weight.
        # TODO: If not weighted, require that each Edge does not have an Edge.weight.

        # TODO: Suppose that type checking should in future restrict `src` and
        #   `dst` to be `Node`s, but at the moment we may need a require for that.
        # TODO: Suppose that type checking should in future restrict `weight` to be
        #   `Float`s, but at the moment we may need a require for that.

        # TODO: Transform Node and Edge into underlying edge-/weight-list representation.
        # NOTE: Operate under the assumption that `Node` contains all
        #   possible nodes, i.e. we can use the `Node` Concept directly as
        #   the node list. Has the additional benefit of allowing relationships
        #   (for which it makes sense) to be properties of `Node` rather than standalone.
        self._define_edge_relationships()
 
        self._define_num_nodes_relationship()
        self._define_num_edges_relationship()

        self._define_neighbor_relationships()
        self._define_count_neighbor_relationships()
        self._define_common_neighbor_relationship()
        self._define_count_common_neighbor_relationship()

        self._define_degree_relationships()
        self._define_weighted_degree_relationships()

        self._define_degree_centrality_relationship()

        self._define_reachable_from()

        # Helper relationship for preferential attachment.
        self._define_isolated_node_relationship()

        self._define_preferential_attachment_relationship()

        # Helper relationships for triangle functionality.
        self._define_no_loop_edge_relationship()
        self._define_oriented_edge_relationship()
        self._define_reversed_oriented_edge_relationship()

        self._define_triangle_count_relationship()
        self._define_unique_triangle_relationship()
        self._define_num_triangles_relationship()
        self._define_triangle_relationship()

        # Helper relationships for local clustering coefficient.
        self._define_degree_no_self_relationship()

        self._define_local_clustering_coefficient_relationship()
        self._define_average_clustering_coefficient_relationship()
        self._define_adamic_adar_relationship()

        self._define_weakly_connected_component()

        self._define_distance_relationship()

        self._define_jaccard_similarity()
        self._define_cosine_similarity()

    def _define_edge_relationships(self):
        """
        Define the self._edge and self._weight relationships,
        consuming the Edge concept's `src`, `dst`, and `weight` relationships.
        """
        self._edge = Relationship("{src:Node} has edge to {dst:Node}")
        self._weight = Relationship("{src:Node} has edge to {dst:Node} with weight {weight:Float}")

        Edge = self.Edge
        if self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._edge(Edge.src, Edge.dst)
            )
        elif self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._edge(Edge.src, Edge.dst)
            )
        elif not self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._weight(Edge.dst, Edge.src, Edge.weight),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )
        elif not self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._weight(Edge.dst, Edge.src, 1.0),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )

    def _define_num_nodes_relationship(self):
        """Define the self._num_nodes relationship."""
        self._num_nodes = Relationship("The graph has {num_nodes:Integer} nodes")
        define(self._num_nodes(count(self.Node) | 0))

    def _define_num_edges_relationship(self):
        """Define the self._num_edges relationship."""
        self._num_edges = Relationship("The graph has {num_edges:Integer} edges")

        src, dst = self.Node.ref(), self.Node.ref()

        if self.directed:
            define(self._num_edges(count(src, dst, self._edge(src, dst)) | 0))
        elif not self.directed:
            define(self._num_edges(count(src, dst, self._edge(src, dst), src <= dst) | 0))
            # TODO: Generates an UnresolvedOverload warning from the typer.
            #   Should be sorted out by improvements in the typer (to allow
            #   comparisons between instances of concepts).


    def _define_neighbor_relationships(self):
        """Define the self.[in,out]neighbor relationships."""
        self._neighbor = Relationship("{src:Node} has neighbor {dst:Node}")
        self._inneighbor = Relationship("{dst:Node} has inneighbor {src:Node}")
        self._outneighbor = Relationship("{src:Node} has outneighbor {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self._edge(src, dst)).define(self._neighbor(src, dst), self._neighbor(dst, src))
        where(self._edge(dst, src)).define(self._inneighbor(src, dst))
        where(self._edge(src, dst)).define(self._outneighbor(src, dst))
        # Note that these definitions happen to work for both
        # directed and undirected graphs due to `edge` containing
        # each edge's symmetric partner in the undirected case.

    def _define_count_neighbor_relationships(self):
        """
        Define the self._count_[in,out]neighbor relationships.
        Note that these relationships differ from corresponding
        [in,out]degree relationships in that they yield empty
        rather than zero absent [in,out]neighbors.
        Primarily for internal consumption.
        """
        self._count_neighbor = Relationship("{src:Node} has neighbor count {count:Integer}")
        self._count_inneighbor = Relationship("{dst:Node} has inneighbor count {count:Integer}")
        self._count_outneighbor = Relationship("{src:Node} has outneighbor count {count:Integer}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self._neighbor(src, dst)).define(self._count_neighbor(src, count(dst).per(src)))
        where(self._inneighbor(dst, src)).define(self._count_inneighbor(dst, count(src).per(dst)))
        where(self._outneighbor(src, dst)).define(self._count_outneighbor(src, count(dst).per(src)))


    def _define_common_neighbor_relationship(self):
        """Define the self._common_neighbor relationship."""
        self._common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor {node_c:Node}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self._neighbor(node_a, node_c), self._neighbor(node_b, node_c)).define(self._common_neighbor(node_a, node_b, node_c))

    def _define_count_common_neighbor_relationship(self):
        """Define the self._count_common_neighbor relationship."""
        self._count_common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor count {count:Integer}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self._common_neighbor(node_a, node_b, node_c)).define(self._count_common_neighbor(node_a, node_b, count(node_c).per(node_a, node_b)))


    def _define_degree_relationships(self):
        """Define the self._[in,out]degree relationships."""
        self._degree = Relationship("{node:Node} has degree {count:Integer}")
        self._indegree = Relationship("{node:Node} has indegree {count:Integer}")
        self._outdegree = Relationship("{node:Node} has outdegree {count:Integer}")

        incount, outcount = Integer.ref(), Integer.ref()

        where(
            self.Node,
            _indegree := where(self._count_inneighbor(self.Node, incount)).select(incount) | 0,
        ).define(self._indegree(self.Node, _indegree))

        where(
            self.Node,
            _outdegree := where(self._count_outneighbor(self.Node, outcount)).select(outcount) | 0,
        ).define(self._outdegree(self.Node, _outdegree))

        if self.directed:
            where(
                self._indegree(self.Node, incount),
                self._outdegree(self.Node, outcount),
            ).define(self._degree(self.Node, incount + outcount))
        elif not self.directed:
            neighcount = Integer.ref()
            where(
                self.Node,
                _degree := where(self._count_neighbor(self.Node, neighcount)).select(neighcount) | 0,
            ).define(self._degree(self.Node, _degree))

    def _define_reachable_from(self):
        """Define the self.reachable_from relationship"""
        self._reachable_from = Relationship("{node_a:Node} reaches {node_b:Node}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        define(self._reachable_from(node_a, node_a))
        define(self._reachable_from(node_a, node_c)).where(self._reachable_from(node_a, node_b), self._edge(node_b, node_c))


    def _define_weighted_degree_relationships(self):
        """Define the self._weighted_[in,out]degree relationships."""
        self._weighted_degree = Relationship("{node:Node} has weighted degree {weight:Float}")
        self._weighted_indegree = Relationship("{node:Node} has weighted indegree {weight:Float}")
        self._weighted_outdegree = Relationship("{node:Node} has weighted outdegree {weight:Float}")

        src, dst = self.Node.ref(), self.Node.ref()
        inweight, outweight = Float.ref(), Float.ref()

        where(
            self.Node,
            _weighted_indegree := sum(src, inweight).per(self.Node).where(self._weight(src, self.Node, inweight)) | 0.0,
        ).define(self._weighted_indegree(self.Node, _weighted_indegree))

        where(
            self.Node,
            _weighted_outdegree := sum(dst, outweight).per(self.Node).where(self._weight(self.Node, dst, outweight)) | 0.0,
        ).define(self._weighted_outdegree(self.Node, _weighted_outdegree))

        if self.directed:
            where(
                self._weighted_indegree(self.Node, inweight),
                self._weighted_outdegree(self.Node, outweight),
            ).define(self._weighted_degree(self.Node, inweight + outweight))
        elif not self.directed:
            weight = Float.ref()
            where(
                self.Node,
                _weighted_degree := sum(dst, weight).per(self.Node).where(self._weight(self.Node, dst, weight)) | 0.0,
            ).define(self._weighted_degree(self.Node, _weighted_degree))

    def _define_degree_centrality_relationship(self):
        """Define the self._degree_centrality relationship."""
        self._degree_centrality = Relationship("{node:Node} has {degree_centrality:Float}")

        degree = Integer.ref()
        weighted_degree = Float.ref()

        # A single isolated node has degree centrality zero.
        where(
            self._num_nodes(1),
            self._degree(self.Node, 0)
        ).define(self._degree_centrality(self.Node, 0.0))

        # A single non-isolated node has degree centrality one.
        where(
            self._num_nodes(1),
            self._degree(self.Node, degree),
            degree > 0
        ).define(self._degree_centrality(self.Node, 1.0))

        # General case, i.e. with more than one node.
        num_nodes = Integer.ref()
        if self.weighted:
            where(
                self._num_nodes(num_nodes),
                num_nodes > 1,
                self._weighted_degree(self.Node, weighted_degree)
            ).define(self._degree_centrality(self.Node, weighted_degree / (num_nodes - 1.0)))
        elif not self.weighted:
            where(
                self._num_nodes(num_nodes),
                num_nodes > 1,
                self._degree(self.Node, degree)
            ).define(self._degree_centrality(self.Node, degree / (num_nodes - 1.0)))


    def _define_isolated_node_relationship(self):
        """Define the self._isolated_node (helper, non-public) relationship."""
        self._isolated_node = Relationship("{node:Node} is isolated")

        dst = self.Node.ref()
        where(
            self.Node,
            not_(self._neighbor(self.Node, dst))
        ).define(self._isolated_node(self.Node))

    def _define_preferential_attachment_relationship(self):
        """Define the self._preferential_attachment relationship."""
        self._preferential_attachment = Relationship("{node_u:Node} and {node_v:Node} have preferential attachment score {score:Integer}")

        node_u, node_v = self.Node.ref(), self.Node.ref()
        count_u, count_v = Integer.ref(), Integer.ref()

        # NOTE: We consider isolated nodes separately to maintain
        #   the dense behavior of preferential attachment.

        # Case where node u is isolated, and node v is any node: score 0.
        where(
            self._isolated_node(node_u),
            self.Node(node_v),
        ).define(self._preferential_attachment(node_u, node_v, 0))

        # Case where node u is any node, and node v is isolated: score 0.
        where(
            self.Node(node_u),
            self._isolated_node(node_v)
        ).define(self._preferential_attachment(node_u, node_v, 0))

        # Case where neither node is isolated: score is count_neighbor[u] * count_neighbor[v].
        where(
            self._count_neighbor(node_u, count_u),
            self._count_neighbor(node_v, count_v)
        ).define(self._preferential_attachment(node_u, node_v, count_u * count_v))

    def _define_weakly_connected_component(self):
        """Defines the self.weakly_connected_component relationship"""
        self._weakly_connected_component = Relationship("{node:Node} is in the connected component {id:Node}")

        node, node_v, component = self.Node.ref(), self.Node.ref(), self.Node.ref()
        node, component = union(
            # A node starts with itself as the component id.
            where(node == component).select(node, component),
            # Recursive case.
            where(self._weakly_connected_component(node, component), self._neighbor(node, node_v)).select(node_v, component)
        )
        define(self._weakly_connected_component(node, min(component).per(node)))

    def _define_no_loop_edge_relationship(self):
        """Define the self._no_loop_edge (helper, non-public) relationship."""
        self._no_loop_edge = Relationship("{src:Node} has nonloop edge to {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src != dst
        ).define(self._no_loop_edge(src, dst))

    def _define_oriented_edge_relationship(self):
        """Define the self._oriented_edge (helper, non-public) relationship."""
        self._oriented_edge = Relationship("{src:Node} has oriented edge to {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src < dst
        ).define(self._oriented_edge(src, dst))

    def _define_reversed_oriented_edge_relationship(self):
        """Define the self._reversed_oriented_edge (helper, non-public) relationship."""
        self._reversed_oriented_edge = Relationship("{src:Node} has reversed oriented edge to {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src > dst
        ).define(self._reversed_oriented_edge(src, dst))


    def _define_triangle_count_relationship(self):
        """Define self._triangle_count relationship."""
        self._triangle_count = Relationship("{node:Node} belongs to {count:Integer} triangles")

        where(
            self.Node,
            _count := self._nonzero_triangle_count_fragment(self.Node) | 0
        ).define(self._triangle_count(self.Node, _count))

    def _nonzero_triangle_count_fragment(self, node):
        """
        Helper function that returns a fragment, specifically a count
        of the number of triangles containing the given node.
        """
        node_a, node_b = self.Node.ref(), self.Node.ref()

        if self.directed:
            # For directed graphs, count triangles with any circulation.
            # For example, count both (1-2-3-1) and (1-3-2-1) as triangles.
            return count(node_a, node_b).per(node).where(
                self._no_loop_edge(node, node_a),
                self._no_loop_edge(node_a, node_b),
                self._no_loop_edge(node_b, node)
            )
        else:
            # For undirected graphs, count triangles with a specific circulation.
            # For example, count (1-2-3-1) but not (1-3-2-1) as a triangle.
            return count(node_a, node_b).per(node).where(
                self._no_loop_edge(node, node_a),
                self._oriented_edge(node_a, node_b),
                self._no_loop_edge(node, node_b)
            )


    def _define_unique_triangle_relationship(self):
        """Define self._unique_triangle relationship."""
        self._unique_triangle = Relationship("{node_a:Node} and {node_b:Node} and {node_c:Node} form unique triangle")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        where(
            self._unique_triangle_fragment(node_a, node_b, node_c)
        ).define(self._unique_triangle(node_a, node_b, node_c))

    def _unique_triangle_fragment(self, node_a, node_b, node_c):
        """
        Helper function that returns a fragment, specifically a where clause
        constraining the given triplet of nodes to unique triangles in the graph.
        """
        if self.directed:
            return where(
                self._oriented_edge(node_a, node_b),
                self._no_loop_edge(node_b, node_c),
                self._reversed_oriented_edge(node_c, node_a)
            )
        else:
            return where(
                self._oriented_edge(node_a, node_b),
                self._oriented_edge(node_b, node_c),
                self._oriented_edge(node_a, node_c)
            )


    def _define_num_triangles_relationship(self):
        """Define self._num_triangles relationship."""
        self._num_triangles = Relationship("The graph has {num_triangles:Integer} triangles")

        _num_triangles = Integer.ref()
        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        where(
            _num_triangles := count(
                node_a, node_b, node_c
            ).where(
                self._unique_triangle_fragment(node_a, node_b, node_c)
            ) | 0,
        ).define(self._num_triangles(_num_triangles))

    def _define_triangle_relationship(self):
        """Define self._triangle relationship."""
        self._triangle = Relationship("{node_a:Node} and {node_b:Node} and {node_c:Node} form a triangle")

        a, b, c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        if self.directed:
            where(self._unique_triangle(a, b, c)).define(self._triangle(a, b, c))
            where(self._unique_triangle(b, c, a)).define(self._triangle(a, b, c))
            where(self._unique_triangle(c, a, b)).define(self._triangle(a, b, c))
        else:
            where(self._unique_triangle(a, b, c)).define(self._triangle(a, b, c))
            where(self._unique_triangle(a, c, b)).define(self._triangle(a, b, c))
            where(self._unique_triangle(b, a, c)).define(self._triangle(a, b, c))
            where(self._unique_triangle(b, c, a)).define(self._triangle(a, b, c))
            where(self._unique_triangle(c, a, b)).define(self._triangle(a, b, c))
            where(self._unique_triangle(c, b, a)).define(self._triangle(a, b, c))


    def _define_degree_no_self_relationship(self):
        """
        Define self._degree_no_self relationship
        (non-public helper for local clustering coefficient).
        """
        self._degree_no_self = Relationship("{node:Node} has degree excluding self loops {num:Integer}")

        node, neighbor = self.Node.ref(), self.Node.ref()
        where(
            self.Node(node),
            _dns := count(neighbor).per(node).where(self._no_loop_edge(node, neighbor)) | 0,
        ).define(self._degree_no_self(node, _dns))

    def _define_local_clustering_coefficient_relationship(self):
        """
        Define self._local_clustering_coefficient relationship.
        Note that local_clustering_coefficient only applies to undirected graphs.
        """
        self._local_clustering_coefficient = Relationship("{node:Node} has local clustering coefficient {coefficient:Float}")

        if self.directed:
            return

        node = self.Node.ref()
        degree_no_self = Integer.ref()
        triangle_count = Integer.ref()
        where(
            node,
            _lcc := where(
                self._degree_no_self(node, degree_no_self),
                self._triangle_count(node, triangle_count),
                degree_no_self > 1
            ).select(
                2.0 * triangle_count / (degree_no_self * (degree_no_self - 1.0))
            ) | 0.0,
        ).define(self._local_clustering_coefficient(node, _lcc))

    def _define_average_clustering_coefficient_relationship(self):
        """
        Define self._average_clustering_coefficient relationship.
        Note that average_clustering_coefficient only applies to undirected graphs.
        """
        self._average_clustering_coefficient = Relationship("The graph has average clustering coefficient {coefficient:Float}")

        if self.directed:
            return

        node = self.Node.ref()
        coefficient = Float.ref()
        where(
            _avg_coefficient := avg(node, coefficient).where(
                    self._local_clustering_coefficient(node, coefficient)
                ) | 0.0
        ).define(self._average_clustering_coefficient(_avg_coefficient))

    def _define_distance_relationship(self):
        """Define self._distance relationship."""
        if not self.weighted:
            self._distance = Relationship("{node_u:Node} and {node_v:Node} have a distance of {d:Integer}")
            node_u, node_v, node_n, d1 = self.Node.ref(), self.Node.ref(), self.Node.ref(), Integer.ref()
            node_u, node_v, d = union(
                where(node_u == node_v, d1 == 0).select(node_u, node_v, d1), # Base case.
                where(self._edge(node_n, node_v),
                      d2 := self._distance(node_u, node_n, Integer) + 1).select(node_u, node_v, d2) # Recursive case.
            )
            define(self._distance(node_u, node_v, min(d).per(node_u, node_v)))
        else:
            self._distance = Relationship("{node_u:Node} and {node_v:Node} have a distance of {d:Float}")
            node_u, node_v, node_n, w, d1 = self.Node.ref(), self.Node.ref(),\
                self.Node.ref(), Float.ref(), Float.ref()
            node_u, node_v, d = union(
                where(node_u == node_v, d1 == 0.0).select(node_u, node_v, d1), # Base case.
                where(self._weight(node_n, node_v, w), d2 := self._distance(node_u, node_n, Float) + abs(w))\
                .select(node_u, node_v, d2) # Recursive case.
            )
            define(self._distance(node_u, node_v, min(d).per(node_u, node_v)))

    def _define_adamic_adar_relationship(self):
        """Define self._adamic_adar relationship."""
        self._adamic_adar = Relationship("{node_u:Node} and {node_v:Node} have adamic adar score {score:Float}")

        node_u, node_v, common_neighbor = self.Node.ref(), self.Node.ref(), self.Node.ref()
        neighbor_count = Integer.ref()

        where(
            _score := sum(common_neighbor, 1.0 / natural_log(neighbor_count)).per(node_u, node_v).where(
                self._common_neighbor(node_u, node_v, common_neighbor),
                self._count_neighbor(common_neighbor, neighbor_count),
            )
        ).define(self._adamic_adar(node_u, node_v, _score))

    def _count_common_outneighbor_fragment(self, node_a, node_b):
        """
        Helper function that returns a fragment, specifically a count of
        common outneighbors of two nodes.
        """

        node_c = self.Node.ref()
            
        return count(node_c).per(node_a, node_b) \
                            .where(self._outneighbor(node_a, node_c), self._outneighbor(node_b, node_c))

    def _define_jaccard_similarity(self):
        self._jaccard_similarity = Relationship("{node_u:Node} has a similarity to {node_v:Node} of {similarity:Float}")

        if not self.weighted:
            node_u, node_v = self.Node.ref(), self.Node.ref()
            num_union_outneighbors, num_u_outneigbor, num_v_outneigbor, f = Integer.ref(),\
                Integer.ref(), Integer.ref(), Float.ref()

            where(num_common_outneighbor := self._count_common_outneighbor_fragment(node_u, node_v),
                  self._count_outneighbor(node_u, num_u_outneigbor),
                  self._count_outneighbor(node_v, num_v_outneigbor),
                  num_union_outneighbors := num_u_outneigbor + num_v_outneigbor - num_common_outneighbor,
                  f := num_common_outneighbor / num_union_outneighbors).define(self._jaccard_similarity(node_u, node_v, f))
        else:
            # TODO (dba) Annotate local relationships in this scope with `@ondemand` once available.

            # (1) The numerator: For every node `k` in the graph, find the minimum weight of
            #     the out-edges from `u` and `v` to `k`, and sum those minimum weights.
    
            #     Note that for any node `k` that is not a common out-neighbor of nodes `u` and `v`,
            #     the minimum weight of the out-edges from `u` and `v` to `k` is zero/empty,
            #     so the sum here reduces to a sum over the common out-neighbors of `u` and `v`.
            min_weight_to_common_outneighbor = Relationship("{node_u:Node} and {node_v:Node} have common outneighbor {node_k:Node} with minimum weight {minweight:Float}")

            node_u, node_v, node_k, w1, w2 = self.Node.ref(), self.Node.ref(), self.Node.ref(), Float.ref(), Float.ref()
            w = union(where(self._weight(node_u, node_k, w1)).select(w1),
                      where(self._weight(node_v, node_k, w2)).select(w2))
            where(self._edge(node_u, node_k),
                  self._edge(node_v, node_k))\
                  .define(min_weight_to_common_outneighbor(node_u, node_v, node_k, min(w).per(node_u, node_v, node_k)))

            sum_of_min_weights_to_common_outneighbors = Relationship("{node_u:Node} and {node_v:Node} have a sum of minweights of {minsum:Float}")

            minweight = Float.ref()
            where(min_weight_to_common_outneighbor(node_u, node_v, node_k, minweight)
                  ).define(sum_of_min_weights_to_common_outneighbors(node_u, node_v, sum(node_k, minweight).per(node_u, node_v)))

            # (2) The denominator: For every node `k` in the graph, find the maximum weight of
            #     the out-edges from `u` and `v` to `k`, and sum those maximum weights.
            #
            #     Note that in general the sum of the maximum of two quantities,
            #     say \sum_i max(a_i, b_i), can be reexpressed via the following identity
            #     \sum_i max(a_i, b_i) = \sum_i a_i + \sum_i b_i - \sum_i min(a_i, b_i).
            #     This identity allows us to reexpress the sum here:
            #
            #     \sum_{k in self.Node} max(self._weight(u, k), self._weight(v, k)) =
            #         \sum_{k in self.Node} self._weight(u, k) +
            #         \sum_{k in self.Node} self._weight(v, k) -
            #         \sum_{k in self.Node} min(self._weight(u, k), self._weight(v, k))
            #
            #     To simplify this expression, note that `self._weight(u, k)` is zero/empty
            #     for all `k` that aren't out-neighbors of `u`. It follows that
            #
            #     \sum_{k in self.Node} self._weight(u, k)
            #         = \sum_{k in self._outneighbor(u)} self._weight(u, k)
            #         = self._weighted_outdegree(u)
            #
            #     and similarly
            #
            #     \sum_{k in self.Node} self._weight(v, k) = self._weighted_outdegree(v)
            #
            #     Additionally, observe that `min(self._weight(u, k), self._weight(v, k))` is zero/empty
            #     for all `k` that aren't out-neighbors of both `u` and `v`. It follows that
            #
            #     \sum_{k in self.Node} min(self._weight(u, k), self._weight(v, k))
            #         = \sum_{k in self._common_outneighbor(u, v)} min(self._weight(u, k), self._weight(v, k))
            #
            #     which is _sum_of_min_weights_to_common_outneighbors above, which we
            #     can reuse to avoid computation. Finally:
            #
            #     \sum_{k in self.Node} max(self._weight(u, k), self._weight(v, k)) =
            #         self._weighted_outdegree(u) +
            #         self._weighted_outdegree(v) -
            #         _sum_of_min_weights_to_common_outneighbors(u, v)
            sum_of_max_weights_to_other_nodes = Relationship("{node_u:Node} and {node_v:Node} have a maxsum of {maxum:Float}")

            u_outdegree, v_outdegree, maxsum, minsum = Float.ref(), Float.ref(), Float.ref(), Float.ref()
            where(self._weighted_outdegree(node_u, u_outdegree),
                  self._weighted_outdegree(node_v, v_outdegree),
                  sum_of_min_weights_to_common_outneighbors(node_u, node_v, minsum),
                  maxsum == u_outdegree + v_outdegree - minsum
                  ).define(sum_of_max_weights_to_other_nodes(node_u, node_v, maxsum))

            score = Float.ref()
            where(sum_of_min_weights_to_common_outneighbors(node_u, node_v, minsum),
                  sum_of_max_weights_to_other_nodes(node_u, node_v, maxsum),
                  score == minsum/maxsum
                  ).define(self._jaccard_similarity(node_u, node_v, score))

    def _define_cosine_similarity(self):
        """Define the self._cosine_similarity relationship"""
        self._cosine_similarity = Relationship("{node_u:Node} has a cosine similarity to {node_v:Node} of {score:Float}")

        if not self.weighted:
            node_u, node_v, c_outneighor_u, c_outneighor_v, score = self.Node.ref(), self.Node.ref(),\
                Integer.ref(), Integer.ref(), Float.ref()

            where(c_common := self._count_common_outneighbor_fragment(node_u, node_v),
                  self._count_outneighbor(node_u, c_outneighor_u),
                  self._count_outneighbor(node_v, c_outneighor_v),
                  score := c_common/(sqrt(c_outneighor_u * c_outneighor_v))
                  ).define(self._cosine_similarity(node_u, node_v, score))
        else:
            def _wu_dot_wv_fragment(node_u, node_v):
                node_k, wu, wv = self.Node.ref(), Float.ref(), Float.ref()
                return sum(node_k, wu * wv).per(node_u, node_v)\
                                           .where(self._weight(node_u, node_k, wu), self._weight(node_v, node_k, wv))

            node_u, node_v, node_k, wu, wv = self.Node.ref(), self.Node.ref(), self.Node.ref(), Float.ref(), Float.ref()
            where(
                self._weight(node_u, node_k, wu),
                self._weight(node_v, node_k, wv),
                sum_of_square_weights := sum(node_k, wu * wu).per(node_u) * sum(node_k, wv * wv).per(node_v),
                wu_dot_wv := _wu_dot_wv_fragment(node_u, node_v),
                score := wu_dot_wv / sqrt(sum_of_square_weights))\
                .define(self._cosine_similarity(node_u, node_v, score))

    # Public accessor methods for private relationships.
    def num_nodes(self):
        """Returns a unary relationship containing the number of nodes in the graph.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A unary relationship containing the number of nodes in the graph.

        Relationship Schema
        -------------------
        ``num_nodes(count)``

        * **count** (*Integer*): The number of nodes in the graph.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.early_access.builder import define
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up the graph and concepts
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define some nodes
        >>> node1, node2, node3, node4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(node1, node2, node3, node4)
        >>>
        >>> # 3. Define the full set of edges
        >>> define(
        ...     Edge(src=node1, dst=node2),
        ...     Edge(src=node2, dst=node3),
        ...     Edge(src=node3, dst=node3),
        ...     Edge(src=node2, dst=node4)
        ... )
        >>>
        >>> # 4. The relationship contains the number of nodes
        >>> graph.num_nodes().inspect()
        4

        See Also
        --------
        num_edges

        """
        return self._num_nodes

    def num_edges(self):
        """Returns a unary relationship containing the number of edges in the graph.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A unary relationship containing the number of edges in the graph.

        Relationship Schema
        -------------------
        ``num_edges(count)``

        * **count** (*Integer*): The number of edges in the graph.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.early_access.builder import define
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up the graph and concepts
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define some nodes
        >>> node1, node2, node3, node4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(node1, node2, node3, node4)
        >>>
        >>> # 3. Define the edges
        >>> define(
        ...     Edge(src=node1, dst=node2),
        ...     Edge(src=node2, dst=node3),
        ...     Edge(src=node3, dst=node3),
        ...     Edge(src=node2, dst=node4)
        ... )
        >>>
        >>> # 4. The relationship contains the number of edges
        >>> graph.num_edges().inspect()
        4

        See Also
        --------
        num_nodes

        """
        return self._num_edges

    def neighbor(self):
        """Returns a binary relationship containing all neighbor pairs in the graph.

        For directed graphs, a node's neighbors include both its in-neighbors
        and out-neighbors.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and one
            of its neighbors.

        Relationship Schema
        -------------------
        ``neighbor(node, neighbor_node)``

        * **node** (*Node*): A node in the graph.
        * **neighbor_node** (*Node*): A neighbor of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                           |
        | :--------- | :-------- | :---------------------------------------------- |
        | Undirected | Yes       |                                                 |
        | Directed   | Yes       | Same as the union of `inneighbor` and `outneighbor`. |
        | Weighted   | Yes       | Weights are ignored.                            |

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the IDs from the neighbor relationship and inspect
        >>> u, v = Node.ref("u"), Node.ref("v")
        >>> neighbor = graph.neighbor()
        >>> select(u.id, v.id).where(neighbor(u, v)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 2)
        # (2, 1)
        # (2, 3)
        # (2, 4)
        # (3, 2)
        # (3, 3)
        # (4, 2)

        See Also
        --------
        inneighbor
        outneighbor

        """
        return self._neighbor

    def inneighbor(self):
        """Returns a binary relationship of all nodes and their in-neighbors.

        An in-neighbor of a node `u` is any node `v` where an edge from `v`
        to `u` exists. For undirected graphs, this is identical to `neighbor`.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a destination node
            and one of its in-neighbors.

        Relationship Schema
        -------------------
        ``inneighbor(node, inneighbor_node)``

        * **node** (*Node*): The destination node.
        * **inneighbor_node** (*Node*): The in-neighbor of the node (i.e., the source of an incoming edge).

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes               |
        | :--------- | :-------- | :------------------ |
        | Undirected | Yes       | Same as `neighbor`. |
        | Directed   | Yes       |                     |
        | Weighted   | Yes       | Weights are ignored.|

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> graph = Graph(directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the IDs from the in-neighbor relationship and inspect
        >>> node, inneighbor_node = Node.ref("node"), Node.ref("inneighbor_node")
        >>> inneighbor = graph.inneighbor()
        >>> select(
        ...     node.id,
        ...     inneighbor_node.id
        ... ).where(
        ...     inneighbor(node, inneighbor_node)
        ... ).inspect()
        # The output will show the resulting pairs, for instance:
        # (2, 1)
        # (3, 2)
        # (3, 3)
        # (4, 2)

        See Also
        --------
        neighbor
        outneighbor

        """
        return self._inneighbor

    def outneighbor(self):
        """Returns a binary relationship of all nodes and their out-neighbors.

        An out-neighbor of a node `u` is any node `v` where an edge from `u`
        to `v` exists. For undirected graphs, this is identical to `neighbor`.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a source node
            and one of its out-neighbors.

        Relationship Schema
        -------------------
        ``outneighbor(node, outneighbor_node)``

        * **node** (*Node*): The source node.
        * **outneighbor_node** (*Node*): The out-neighbor of the node (i.e., the destination of an outgoing edge).

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes               |
        | :--------- | :-------- | :------------------ |
        | Undirected | Yes       | Same as `neighbor`. |
        | Directed   | Yes       |                     |
        | Weighted   | Yes       | Weights are ignored.|

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> graph = Graph(directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the IDs from the out-neighbor relationship and inspect
        >>> node, outneighbor_node = Node.ref("node"), Node.ref("outneighbor_node")
        >>> outneighbor = graph.outneighbor()
        >>> select(
        ...     node.id,
        ...     outneighbor_node.id
        ... ).where(
        ...     outneighbor(node, outneighbor_node)
        ... ).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 2)
        # (2, 3)
        # (2, 4)
        # (3, 3)

        See Also
        --------
        neighbor
        inneighbor

        """
        return self._outneighbor

    def common_neighbor(self): return self._common_neighbor

    def degree(self): return self._degree
    def indegree(self):
        """Returns a binary relationship containing the indegree of each node.

        A node's indegree is the number of incoming edges. For undirected
        graphs, a node's indegree is identical to its degree.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            indegree.

        Relationship Schema
        -------------------
        ``indegree(node, node_indegree)``

        * **node** (*Node*): The node.
        * **node_indegree** (*Integer*): The indegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                   |
        | :--------- | :-------- | :---------------------- |
        | Undirected | Yes       | Identical to `degree`.  |
        | Directed   | Yes       |                         |
        | Weighted   | Yes       | Weights are ignored.    |

        Examples
        --------
        **Undirected Graph Example**

        >>> from relationalai.early_access.builder import define, select, Integer
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n3, dst=n4)
        ... )
        >>>
        >>> # 3. Select the indegree of each node and inspect
        >>> node, node_indegree = Node.ref("node"), Integer.ref("node_indegree")
        >>> indegree = graph.indegree()
        >>> select(node.id, node_indegree).where(indegree(node, node_indegree)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1)
        # (2, 2)
        # (3, 3)
        # (4, 1)

        **Directed Graph Example**

        >>> from relationalai.early_access.builder import define, select, Integer
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> graph = Graph(directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n3, dst=n4)
        ... )
        >>>
        >>> # 3. Select the indegree of each node and inspect
        >>> node, node_indegree = Node.ref("node"), Integer.ref("node_indegree")
        >>> indegree = graph.indegree()
        >>> select(node.id, node_indegree).where(indegree(node, node_indegree)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 0)
        # (2, 1)
        # (3, 2)
        # (4, 1)

        See Also
        --------
        degree
        outdegree

        """
        return self._indegree

    def outdegree(self):
        """Returns a binary relationship containing the outdegree of each node.

        A node's outdegree is the number of outgoing edges. For undirected
        graphs, a node's outdegree is identical to its degree.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            outdegree.

        Relationship Schema
        -------------------
        ``outdegree(node, node_outdegree)``

        * **node** (*Node*): The node.
        * **node_outdegree** (*Integer*): The outdegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                   |
        | :--------- | :-------- | :---------------------- |
        | Undirected | Yes       | Identical to `degree`.  |
        | Directed   | Yes       |                         |
        | Weighted   | Yes       | Weights are ignored.    |

        Examples
        --------
        **Undirected Graph Example**

        >>> from relationalai.early_access.builder import define, select, Integer
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the outdegree of each node and inspect
        >>> node, node_outdegree = Node.ref("node"), Integer.ref("node_outdegree")
        >>> outdegree = graph.outdegree()
        >>> select(node.id, node_outdegree).where(outdegree(node, node_outdegree)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1)
        # (2, 3)
        # (3, 2)
        # (4, 1)

        **Directed Graph Example**

        >>> from relationalai.early_access.builder import define, select, Integer
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> graph = Graph(directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the outdegree of each node and inspect
        >>> node, node_outdegree = Node.ref("node"), Integer.ref("node_outdegree")
        >>> outdegree = graph.outdegree()
        >>> select(node.id, node_outdegree).where(outdegree(node, node_outdegree)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1)
        # (2, 2)
        # (3, 1)
        # (4, 0)

        See Also
        --------
        degree
        indegree

        """
        return self._outdegree

    def weighted_degree(self):
        """Returns a binary relationship containing the weighted degree of each node.

        A node's weighted degree is the sum of the weights of all edges
        connected to it. For directed graphs, this is the sum of the weights
        of both incoming and outgoing edges. For unweighted graphs, all edge
        weights are considered to be 1.0.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            weighted degree.

        Relationship Schema
        -------------------
        ``weighted_degree(node, node_weighted_degree)``

        * **node** (*Node*): The node.
        * **node_weighted_degree** (*Float*): The weighted degree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type   | Supported | Notes                              |
        | :----------- | :-------- | :--------------------------------- |
        | Undirected   | Yes       |                                    |
        | Directed     | Yes       |                                    |
        | Weighted     | Yes       |                                    |
        | Unweighted   | Yes       | Edge weights are considered to be 1.0. |

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select, Float
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed, weighted graph
        >>> graph = Graph(directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge(src=n1, dst=n2, weight=1.0),
        ...     Edge(src=n2, dst=n1, weight=-1.0),
        ...     Edge(src=n2, dst=n3, weight=1.0)
        ... )
        >>>
        >>> # 3. Select the weighted degree of each node and inspect
        >>> node, node_weighted_degree = Node.ref("node"), Float.ref("node_weighted_degree")
        >>> weighted_degree = graph.weighted_degree()
        >>> select(node.id, node_weighted_degree).where(weighted_degree(node, node_weighted_degree)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 0.0)
        # (2, 1.0)
        # (3, 1.0)

        See Also
        --------
        weighted_indegree
        weighted_outdegree

        """
        return self._weighted_degree

    def weighted_indegree(self):
        """Returns a binary relationship containing the weighted indegree of each node.

        A node's weighted indegree is the sum of the weights of all incoming
        edges. For undirected graphs, this is identical to `weighted_degree`.
        For unweighted graphs, all edge weights are considered to be 1.0.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            weighted indegree.

        Relationship Schema
        -------------------
        ``weighted_indegree(node, node_weighted_indegree)``

        * **node** (*Node*): The node.
        * **node_weighted_indegree** (*Float*): The weighted indegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type   | Supported | Notes                                  |
        | :----------- | :-------- | :------------------------------------- |
        | Undirected   | Yes       | Identical to `weighted_degree`.        |
        | Directed     | Yes       |                                        |
        | Weighted     | Yes       |                                        |
        | Unweighted   | Yes       | Edge weights are considered to be 1.0. |

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select, Float
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed, weighted graph
        >>> graph = Graph(directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge(src=n1, dst=n2, weight=1.0),
        ...     Edge(src=n2, dst=n1, weight=-1.0),
        ...     Edge(src=n2, dst=n3, weight=1.0)
        ... )
        >>>
        >>> # 3. Select the weighted indegree of each node and inspect
        >>> node, node_weighted_indegree = Node.ref("node"), Float.ref("node_weighted_indegree")
        >>> weighted_indegree = graph.weighted_indegree()
        >>> select(
        ...     node.id, node_weighted_indegree
        ... ).where(
        ...     weighted_indegree(node, node_weighted_indegree)
        ... ).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, -1.0)
        # (2, 1.0)
        # (3, 1.0)

        See Also
        --------
        weighted_degree
        weighted_outdegree

        """
        return self._weighted_indegree

    def weighted_outdegree(self):
        """Returns a binary relationship containing the weighted outdegree of each node.

        A node's weighted outdegree is the sum of the weights of all outgoing
        edges. For undirected graphs, this is identical to `weighted_degree`.
        For unweighted graphs, all edge weights are considered to be 1.0.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            weighted outdegree.

        Relationship Schema
        -------------------
        ``weighted_outdegree(node, node_weighted_outdegree)``

        * **node** (*Node*): The node.
        * **node_weighted_outdegree** (*Float*): The weighted outdegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type   | Supported | Notes                                  |
        | :----------- | :-------- | :------------------------------------- |
        | Undirected   | Yes       | Identical to `weighted_degree`.        |
        | Directed     | Yes       |                                        |
        | Weighted     | Yes       |                                        |
        | Unweighted   | Yes       | Edge weights are considered to be 1.0. |

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select, Float
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed, weighted graph
        >>> graph = Graph(directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge(src=n1, dst=n2, weight=1.0),
        ...     Edge(src=n2, dst=n1, weight=-1.0),
        ...     Edge(src=n2, dst=n3, weight=1.0)
        ... )
        >>>
        >>> # 3. Select the weighted outdegree of each node and inspect
        >>> node, node_weighted_outdegree = Node.ref("node"), Float.ref("node_weighted_outdegree")
        >>> weighted_outdegree = graph.weighted_outdegree()
        >>> select(
        ...     node.id, node_weighted_outdegree
        ... ).where(
        ...     weighted_outdegree(node, node_weighted_outdegree)
        ... ).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1.0)
        # (2, 0.0)
        # (3, 0.0)

        See Also
        --------
        weighted_degree
        weighted_indegree

        """
        return self._weighted_outdegree

    def degree_centrality(self):
        """Returns a binary relationship containing the degree centrality of each node.

        Degree centrality is a measure of a node's importance, defined as its
        degree (or weighted degree for weighted graphs) divided by the number
        of other nodes in the graph. For simple graphs without self-loops, this
        value will be at most 1.0; graphs with self-loops might have nodes
        with a degree centrality greater than 1.0.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            degree centrality.

        Relationship Schema
        -------------------
        ``degree_centrality(node, centrality)``

        * **node** (*Node*): The node.
        * **centrality** (*Float*): The degree centrality of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                         |
        | :--------- | :-------- | :-------------------------------------------- |
        | Undirected | Yes       |                                               |
        | Directed   | Yes       |                                               |
        | Weighted   | Yes       | The calculation uses the node's weighted degree. |

        Examples
        --------
        **Unweighted Graph Example**

        >>> from relationalai.early_access.builder import define, select, Float
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up an unweighted graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the degree centrality of each node and inspect
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> degree_centrality = graph.degree_centrality()
        >>> select(node.id, centrality).where(degree_centrality(node, centrality)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 0.3333333333333333)
        # (2, 1.0)
        # (3, 0.6666666666666666)
        # (4, 0.3333333333333333)

        **Weighted Graph Example**

        >>> # 1. Set up a weighted graph
        >>> graph = Graph(directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge(src=n1, dst=n2, weight=2.0),
        ...     Edge(src=n1, dst=n3, weight=0.5),
        ...     Edge(src=n2, dst=n3, weight=1.5)
        ... )
        >>>
        >>> # 3. Select the degree centrality using weighted degrees
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> degree_centrality = graph.degree_centrality()
        >>> select(node.id, centrality).where(degree_centrality(node, centrality)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1.25)
        # (2, 1.75)
        # (3, 1.0)

        See Also
        --------
        degree
        weighted_degree

        """
        return self._degree_centrality

    def eigenvector_centrality(self):
        """Returns a binary relationship containing the eigenvector centrality of each node.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            eigenvector centrality.

        Relationship Schema
        -------------------
        ``eigenvector_centrality(node, centrality)``

        * **node** (*Node*): The node.
        * **centrality** (*Float*): The eigenvector centrality of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                     |
        | :--------- | :-------- | :---------------------------------------- |
        | Undirected | Yes       | See Notes for convergence criteria.       |
        | Directed   | No        | Will not converge.                        |
        | Weighted   | Yes       | Assumes non-negative weights.             |

        Notes
        -----
        Eigenvector centrality is a measure of the centrality or importance
        of a node in a graph based on finding the eigenvector associated
        with the top eigenvalue of the adjacency matrix. We use the power
        method to compute the eigenvector in our implementation. Note that
        the power method `requires the adjacency matrix to be diagonalizable <https://en.wikipedia.org/wiki/Power_iteration>`_
        and will only converge if the absolute value of the top 2
        eigenvalues is distinct. Thus, if the graph you are using has an
        adjacency matrix that is not diagonalizable or the top two
        eigenvalues are not distinct, this method will not converge.

        In the case of weighted graphs, weights are assumed to be non-negative.

        Examples
        --------
        **Unweighted Graph Example**

        >>> from relationalai.early_access.builder import define, select, Float
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up an unweighted, undirected graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n4)
        ... )
        >>>
        >>> # 3. Select the eigenvector centrality for each node and inspect
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> eigenvector_centrality = graph.eigenvector_centrality()
        >>> select(node.id, centrality).where(eigenvector_centrality(node, centrality)).inspect()
        # The output will show the resulting scores, for instance:
        # (1, 0.3717480344601844)
        # (2, 0.6015009550075456)
        # (3, 0.6015009550075456)
        # (4, 0.3717480344601844)

        **Weighted Graph Example**

        >>> # 1. Set up a weighted, undirected graph
        >>> graph = Graph(directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2, weight=0.8),
        ...     Edge(src=n2, dst=n3, weight=0.7),
        ...     Edge(src=n3, dst=n3, weight=2.0),
        ...     Edge(src=n2, dst=n4, weight=1.5)
        ... )
        >>>
        >>> # 3. Select the eigenvector centrality for each node and inspect
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> eigenvector_centrality = graph.eigenvector_centrality()
        >>> select(node.id, centrality).where(eigenvector_centrality(node, centrality)).inspect()
        # The output will show the resulting scores, for instance:
        # (1, 0.15732673092171892)
        # (2, 0.4732508189314368)
        # (3, 0.8150240891426493)
        # (4, 0.2949876204782229)

        """
        raise NotImplementedError("eigenvector_centrality is not yet implemented")

    def reachable_from(self):
        """Returns a binary relationship of all pairs of nodes (u, v) where v is reachable from u.

        A node `v` is considered reachable from a node `u` if there is a path
        of edges from `u` to `v`.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a start node and a
            node that is reachable from it.

        Relationship Schema
        -------------------
        ``reachable_from(start_node, end_node)``

        * **start_node** (*Node*): The node from which the path originates.
        * **end_node** (*Node*): The node that is reachable from the start node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        There is a slight difference between `transitive closure` and
        `reachable_from`. The transitive closure of a binary relation E is the
        smallest relation that contains E and is transitive. When E is the
        edge set of a graph, the transitive closure of E does not include
        (u, u) if u is isolated. `reachable_from` is a different binary
        relation in which any node u is always reachable from u. In
        particular, `transitive closure` is a more general concept than
        `reachable_from`.

        Examples
        --------
        **Directed Graph Example**

        >>> from relationalai.early_access.builder import define, select
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> graph = Graph(directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n3, dst=n2)
        ... )
        >>>
        >>> # 3. Select all reachable pairs and inspect
        >>> start_node, end_node = Node.ref("start"), Node.ref("end")
        >>> reachable_from = graph.reachable_from()
        >>> select(start_node.id, end_node.id).where(reachable_from(start_node, end_node)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1)
        # (1, 2)
        # (2, 2)
        # (3, 2)
        # (3, 3)

        **Undirected Graph Example**

        >>> # 1. Set up an undirected graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n3, dst=n2)
        ... )
        >>>
        >>> # 3. Select all reachable pairs and inspect
        >>> start_node, end_node = Node.ref("start"), Node.ref("end")
        >>> reachable_from = graph.reachable_from()
        >>> select(start_node.id, end_node.id).where(reachable_from(start_node, end_node)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1)
        # (1, 2)
        # (1, 3)
        # (2, 1)
        # (2, 2)
        # (2, 3)
        # (3, 1)
        # (3, 2)
        # (3, 3)

        """
        return self._reachable_from

    def preferential_attachment(self):
        """Returns a ternary relationship containing the preferential attachment score for all pairs of nodes.

        The preferential attachment score between two nodes `u` and `v` is the
        number of nodes adjacent to `u` multiplied by the number of nodes
        adjacent to `v`.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and their preferential attachment score.

        Relationship Schema
        -------------------
        ``preferential_attachment(node_u, node_v, score)``

        * **node_u** (*Node*): The first node in the pair.
        * **node_v** (*Node*): The second node in the pair.
        * **score** (*Integer*): The preferential attachment score of the pair.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select, Integer
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3),
        ...     Edge(src=n2, dst=n4),
        ...     Edge(src=n4, dst=n3)
        ... )
        >>>
        >>> # 3. Select the preferential attachment score for the pair (1, 3)
        >>> u, v = Node.ref("u"), Node.ref("v")
        >>> score = Integer.ref("score")
        >>> preferential_attachment = graph.preferential_attachment()
        >>> select(
        ...     u.id, v.id, score
        ... ).where(
        ...     preferential_attachment(u, v, score),
        ...     u.id == 1,
        ...     v.id == 3
        ... ).inspect()
        # The output will show the resulting triplet:
        # (1, 3, 3)

        """
        return self._preferential_attachment

    def triangle_count(self):
        """Returns a binary relationship containing the number of unique triangles each node belongs to.

        A triangle is a set of three nodes where each node has a directed
        or undirected edge to the other two nodes, forming a 3-cycle.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and the
            number of unique triangles it is a part of.

        Relationship Schema
        -------------------
        ``triangle_count(node, count)``

        * **node** (*Node*): The node.
        * **count** (*Integer*): The number of unique triangles the node belongs to.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select, Integer
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> graph = Graph(directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5 = [Node.new(id=i) for i in range(1, 6)]
        >>> define(n1, n2, n3, n4, n5)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n2, dst=n4),
        ...     Edge(src=n3, dst=n1),
        ...     Edge(src=n3, dst=n4),
        ...     Edge(src=n5, dst=n1)
        ... )
        >>>
        >>> # 3. Select the triangle count for each node and inspect
        >>> node, count = Node.ref("node"), Integer.ref("count")
        >>> triangle_count = graph.triangle_count()
        >>> select(node.id, count).where(triangle_count(node, count)).inspect()
        # The output will show the resulting pairs, for instance:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 0)
        # (5, 0)

        See Also
        --------
        triangle
        unique_triangle
        num_triangles

        """
        return self._triangle_count

    def unique_triangle(self): return self._unique_triangle
    def num_triangles(self): return self._num_triangles
    def triangle(self): return self._triangle

    def triangle_community(self):
        """Returns a binary relationship that partitions nodes into communities based on the graph's triangle structure.

        This method finds K-clique communities (with K=3) using the
        percolation method.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            community assignment.

        Relationship Schema
        -------------------
        ``triangle_community(node, community_label)``

        * **node** (*Node*): The node.
        * **community_label** (*Integer*): The node's community assignment.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | No        |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        This method finds K-clique communities (with `K = 3`) using the
        `percolation method <https://en.wikipedia.org/wiki/Clique_percolation_method>`_.
        A triangle community is the union of nodes of all triangles that can
        be reached from one another by adjacent triangles---that is,
        triangles that share exactly two nodes.

        For a given undirected graph `G`, the algorithm works as follows:
        First, all triangles in `G` are enumerated and assigned a unique
        label, each of which becomes a node in a new graph called the
        **clique-graph** of `G`, where two nodes in this new graph are
        connected by an edge if the corresponding triangles share exactly two
        nodes, i.e., the corresponding triangles are adjacent in `G`. Next,
        the connected components of the clique-graph of `G` are computed and
        then assigned community labels. Finally, each node in the original
        graph is assigned the community label of the triangle to which it
        belongs. Nodes that are not contained in any triangle are not
        assigned a community label. This algorithm is not supported for
        directed graphs since adjacency is not defined for directed
        triangles.

        Examples
        --------
        >>> from relationalai.early_access.builder import define, select, Integer
        >>> from graphlib.core import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     Edge(src=n1, dst=n2),
        ...     Edge(src=n1, dst=n3),
        ...     Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n4),
        ...     Edge(src=n4, dst=n5),
        ...     Edge(src=n4, dst=n6),
        ...     Edge(src=n5, dst=n6)
        ... )
        >>>
        >>> # 3. Select the community label for each node and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> triangle_community = graph.triangle_community()
        >>> select(node.id, label).where(triangle_community(node, label)).inspect()
        # The output will show each node in a triangle mapped to a community:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        """
        raise NotImplementedError("triangle_community is not yet implemented")

    def local_clustering_coefficient(self):
        if self.directed:
            # TODO: Eventually make this error more similar to
            #   the corresponding error emitted from the pyrel graphlib wrapper.
            raise NotImplementedError(
                "Local clustering coefficient is not applicable to directed graphs"
            )
        return self._local_clustering_coefficient

    def average_clustering_coefficient(self):
        if self.directed:
            raise NotImplementedError(
                "Average clustering coefficient is not applicable to directed graphs"
            )
        return self._average_clustering_coefficient

    def weakly_connected_component(self): return self._weakly_connected_component

    def distance(self): return self._distance
    def adamic_adar(self): return self._adamic_adar

    def jaccard_similarity(self):
        """Returns a ternary relationship containing the Jaccard similarity for all pairs of nodes.

        The Jaccard similarity is a measure between two nodes that ranges from
        0.0 to 1.0, where higher values indicate greater similarity.

        Parameters
        ----------
        This method takes no parameters.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and their Jaccard similarity.

        Relationship Schema
        -------------------
        ``jaccard_similarity(node_u, node_v, score)``

        * **node_u** (*Node*): The first node in the pair.
        * **node_v** (*Node*): The second node in the pair.
        * **score** (*Float*): The Jaccard similarity of the pair.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                      |
        | :--------- | :-------- | :----------------------------------------- |
        | Undirected | Yes       |                                            |
        | Directed   | Yes       | Based on out-neighbors.                    |
        | Weighted   | Yes       |                                            |
        | Unweighted | Yes       | Each edge weight is taken to be 1.0.       |

        Notes
        -----
        The **unweighted** Jaccard similarity between two nodes is the ratio of
        the size of the intersection to the size of the union of their
        neighbors (or out-neighbors for directed graphs).

        The **weighted** Jaccard similarity considers the weights of the edges.
        The definition used here is taken from the reference noted below. It is
        the ratio between two quantities:

        1.  **Numerator**: For every other node `w` in the graph, find the
            minimum of the edge weights `(u, w)` and `(v, w)`, and sum these
            minimums.
        2.  **Denominator**: For every other node `w` in the graph, find the
            maximum of the edge weights `(u, w)` and `(v, w)`, and sum these
            maximums.

        If an edge does not exist, its weight is considered 0.0. This can be
        better understood via the following calculation for the weighted
        example below.

        | node id | edge weights to node 1 | edge weights to node 2 | min  | max  |
        | :------ | :--------------------- | :--------------------- | :--- | :--- |
        | 1       | 0.0                    | 1.6                    | 0.0  | 1.6  |
        | 2       | 1.6                    | 0.0                    | 0.0  | 1.6  |
        | 3       | 1.4                    | 0.46                   | 0.46 | 1.4  |
        | 4       | 0.0                    | 0.0                    | 0.0  | 0.0  |

        The weighted Jaccard similarity between node 1 and 2 is then:
        `0.46 / (1.6 + 1.6 + 1.4) = 0.1`.

        Examples
        --------
        **Unweighted Graph Examples**

        *Undirected Graph*
        >>> from relationalai.early_access.builder import define, select, Float
        >>> from graphlib.core import Graph
        >>>
        >>> graph = Graph(directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2), Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3), Edge(src=n2, dst=n4), Edge(src=n4, dst=n3)
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> jaccard = graph.jaccard_similarity()
        >>> select(score).where(jaccard(u, v, score), u.id == 2, v.id == 4).inspect()
        # The output will show the resulting score:
        # 0.25

        *Directed Graph*
        >>> graph = Graph(directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2), Edge(src=n2, dst=n3),
        ...     Edge(src=n3, dst=n3), Edge(src=n2, dst=n4), Edge(src=n4, dst=n3)
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> jaccard = graph.jaccard_similarity()
        >>> select(score).where(jaccard(u, v, score), u.id == 2, v.id == 4).inspect()
        # The output will show the resulting score:
        # 0.5

        **Weighted Graph Example**

        >>> # 1. Set up a weighted, undirected graph
        >>> graph = Graph(directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge(src=n1, dst=n2, weight=1.6),
        ...     Edge(src=n1, dst=n3, weight=1.4),
        ...     Edge(src=n2, dst=n3, weight=0.46),
        ...     Edge(src=n3, dst=n4, weight=2.5)
        ... )
        >>>
        >>> # 3. Select the weighted Jaccard similarity for the pair (1, 2)
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> jaccard = graph.jaccard_similarity()
        >>> select(score).where(jaccard(u, v, score), u.id == 1, v.id == 2).inspect()
        # The output will show the resulting score:
        # 0.1

        References
        ----------
        Frigo M, Cruciani E, Coudert D, Deriche R, Natale E, Deslauriers-Gauthier S.
        Network alignment and similarity reveal atlas-based topological differences
        in structural connectomes. Netw Neurosci. 2021 Aug 30;5(3):711-733.
        doi: 10.1162/netn_a_00199. PMID: 34746624; PMCID: PMC8567827.

        """
        return self._jaccard_similarity

    def cosine_similarity(self): return self._cosine_similarity
