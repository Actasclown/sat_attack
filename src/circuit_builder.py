from z3 import *

class CircuitBuilder():
    def build_miter(self, ckt0, ckt1):
        output_xors = [Xor(ckt0.outputs()[name], ckt1.outputs()[name]) for name in ckt0.outputs()]
        diff = Or(*output_xors)
        return {"diff": diff}

    def build(self, nodes, output_names, key_suffix = "", spec_inputs = None):
        self.visited_nodes = []
        self.inputs = []
        self.specified_inputs = spec_inputs
        outputs = {}

        for name in output_names:
            outputs[name] = self._build_node(nodes, name, key_suffix)

        return outputs, self.inputs

    def _build_node(self, nodes, name, key_suffix):
        node = nodes[name]

        if name in self.visited_nodes:
            return node.z3_repr

        self.visited_nodes.append(name)

        if node.type == "Key Input":
            self._build_key(node, name, key_suffix)
        elif node.type == "Primary Input":
            self._build_input(node, name)
        else:
            fanin = [self._build_node(nodes, child_name, key_suffix) for child_name in node.inputs]
            self._build_gate(node, fanin)

        return node.z3_repr

    def _build_gate(self, node, fanin):

        if node.type == "And":
            node.z3_repr = And(*fanin)
        elif node.type == "Xor":
            node.z3_repr = Xor(*fanin)
        elif node.type == "Or":
            node.z3_repr = Or(*fanin)
        elif node.type == "Not":
            node.z3_repr = Not(*fanin)
        elif node.type == "Nand":
            node.z3_repr = Not(And(*fanin))
        elif node.type == "Xnor":
            node.z3_repr = Not(Xor(*fanin))
        elif node.type == "Nor":
            node.z3_repr = Not(Or(*fanin))
        else:
            print("Unknown node type " + str(node))

    def _build_key(self, node, name, key_suffix):
        key_name = name + key_suffix
        self.inputs.append(key_name)
        node.z3_repr = Bool(key_name)

    def _build_input(self, node, name):
        if self.specified_inputs is not None and name in self.specified_inputs:
            node.z3_repr = self.specified_inputs[name]
        else:
            self.inputs.append(name)
            node.z3_repr = Bool(name)

class CircuitBuilderOld():
    def build_miter(self, nodes, outputs):
        ckt0, p_input_names, key_input_names0 = self.build(nodes, outputs, "ckt0")
        ckt1, p_input_names, key_input_names1 = self.build(nodes, outputs, "ckt1")

        output_xors = [None] * len(ckt0)
        for i in range(len(ckt0)):
            output_xors[i] = Xor(ckt0[i], ckt1[i])

        miter_circuit = Or(*output_xors)
        return miter_circuit, p_input_names, key_input_names0 + key_input_names1

    def build(self, nodes, outputs, key_suffix = None):
        self.key_input_names = []
        self.p_input_names = []
        circuit_outputs = []

        for output_name in outputs:
            circuit_outputs.append(self.__construct(nodes, output_name, key_suffix))

        return circuit_outputs, self.p_input_names, self.key_input_names

    def __construct(self, nodes, name, key_suffix):
        node = nodes[name]

        if node.z3_repr is not None:
            return node.z3_repr

        input_names = node.inputs

        if node.type == "Key Input":
            key_name = self.__key_name(name, key_suffix)
            if key_name not in self.key_input_names:
                self.key_input_names.append(key_name)

            node.z3_repr = Bool(key_name)
            return node.z3_repr
        elif node.type == "Primary Input":
            if name not in self.p_input_names:
                self.p_input_names.append(name)

            node.z3_repr = Bool(name)
            return node.z3_repr

        input_logic = []
        for input_name in input_names:
            input_logic.append(self.__construct(nodes, input_name, key_suffix))

        if node.type == "And":
            node.z3_repr = And(*input_logic)
        elif node.type == "Xor":
            node.z3_repr = Xor(*input_logic)
        elif node.type == "Or":
            node.z3_repr = Or(*input_logic)
        elif node.type == "Not":
            node.z3_repr = Not(*input_logic)
        elif node.type == "Nand":
            node.z3_repr = Not(And(*input_logic))
        elif node.type == "Xnor":
            node.z3_repr = Not(Xor(*input_logic))
        elif node.type == "Nor":
            node.z3_repr = Not(Or(*input_logic))
        else:
            print("Unknown node type " + str(node))

        return node.z3_repr

    def __key_name(self, name, key_suffix):
        if key_suffix is None:
            return name
        else:
            return name + "__" + key_suffix


