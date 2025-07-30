import pytest

from livenodes import Node, Connection, Ports_collection
from utils import Port_Ints, Port_Str

class Ports_simple(Ports_collection):
    data: Port_Ints = Port_Ints("Data")

class SimpleNode(Node):
    ports_in = Ports_simple()
    ports_out = Ports_simple()

class Ports_complex_in(Ports_collection):
    data: Port_Ints = Port_Ints("Data")
    meta: Port_Ints = Port_Ints("Meta")

class Ports_complex_out(Ports_collection):
    data: Port_Ints = Port_Ints("Data")
    meta: Port_Ints = Port_Ints("Meta")
    info: Port_Str = Port_Str("Info")

class ComplexNode(Node):
    ports_in = Ports_complex_in()
    ports_out = Ports_complex_out()

# Arrange
@pytest.fixture
def create_simple_graph():
    node_a = SimpleNode(name='A')
    node_b = SimpleNode(name='B')
    node_c = SimpleNode(name='C')
    node_d = SimpleNode()
    node_e = SimpleNode()

    node_c.add_input(node_a, emit_port=SimpleNode.ports_out.data, recv_port=SimpleNode.ports_in.data)
    node_c.add_input(node_b, emit_port=SimpleNode.ports_out.data, recv_port=SimpleNode.ports_in.data)

    node_d.add_input(node_c, emit_port=SimpleNode.ports_out.data, recv_port=SimpleNode.ports_in.data)
    node_e.add_input(node_c, emit_port=SimpleNode.ports_out.data, recv_port=SimpleNode.ports_in.data)

    return node_a, node_b, node_c, node_d, node_e


@pytest.fixture
def create_simple_graph_complex_nodes():
    node_a = ComplexNode()
    node_b = ComplexNode()
    node_c = ComplexNode()

    node_b.add_input(node_a, emit_port=node_a.ports_out.data, recv_port=node_b.ports_in.data)
    node_b.add_input(node_a, emit_port=node_a.ports_out.meta, recv_port=node_b.ports_in.meta)
    node_c.add_input(node_b, emit_port=node_b.ports_out.data, recv_port=node_b.ports_in.data)
    node_c.add_input(node_b, emit_port=node_b.ports_out.meta, recv_port=node_b.ports_in.meta)

    return node_a, node_b, node_c


class TestGraphOperations():

    def test_name_conversion(self, create_simple_graph):
        node_a, node_b, node_c, node_d, node_e = create_simple_graph
        assert node_a.output_connections[0].serialize_compact() == "A [SimpleNode].data -> C [SimpleNode].data"
        assert node_a.output_connections[0].to_dict() == Connection.deserialize_compact(node_a.output_connections[0].serialize_compact())

    def test_relationships(self, create_simple_graph):
        node_a, node_b, node_c, node_d, node_e = create_simple_graph

        # direct relationships
        assert node_c.requires_input_of(node_a)
        assert node_a.provides_input_to(node_c)

        # further relationships
        assert node_d.requires_input_of(node_a)
        assert node_a.provides_input_to(node_d)

    def test_remove_connection(self, create_simple_graph_complex_nodes):
        node_a, node_b, _ = create_simple_graph_complex_nodes

        assert node_b.requires_input_of(node_a)

        # Remove the "Data" connection
        node_b.remove_input(node_a, 
                    emit_port=ComplexNode.ports_out.data,
                    recv_port=ComplexNode.ports_in.data)

        # They are still children, as the "Meta" connection remains
        assert node_b.requires_input_of(node_a)

        # Remove the "Meta" connection
        node_b.remove_input(node_a,
                            emit_port=ComplexNode.ports_out.meta,
                            recv_port=ComplexNode.ports_in.meta)

        # Now they shouldn't be related anymore
        assert not node_b.requires_input_of(node_a)

    def test_incompatible_nodes(self):
        a = ComplexNode()
        b = ComplexNode()

        with pytest.raises(ValueError):
            b.add_input(a, emit_port=a.ports_out.info, recv_port=b.ports_in.data)


# if __name__ == "__main__":
    # TestGraphOperations().test_relationships(create_simple_graph())
    # TestGraphOperations().test_remove_connection(create_simple_graph_complex_nodes())