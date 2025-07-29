from pysmspp import SMSNetwork, Block, Variable
from conftest import (
    add_base_ucblock,
    add_ucblock_with_one_unit,
    add_tub_to_ucblock,
    add_bub_to_ucblock,
    add_hub_to_ucblock,
    add_iub_to_ucblock,
    build_base_investmentblock,
)


def test_blocks_entry():
    from pysmspp import blocks

    assert "ThermalUnitBlock" in blocks.keys()


def test_components_entry():
    from pysmspp import components

    assert "ThermalUnitBlock" in components.index


def test_attribute():
    b = SMSNetwork()

    b.add("Attribute", "test_attr", "test_value")
    assert b.attributes["test_attr"] == "test_value"
    b.add("Attribute", "test_attr_num", 1)
    assert b.attributes["test_attr_num"] == 1

    b.remove("Attribute", "test_attr")
    assert "test_attr" not in b.attributes


def test_dimension():
    b = SMSNetwork()
    b.add("Dimension", "test_dim", 1)
    assert b.dimensions["test_dim"] == 1

    b.remove("Dimension", "test_dim")
    assert "test_dim" not in b.dimensions


def test_variable():
    b = SMSNetwork()
    b.add(
        "Variable",
        "test_var",
        var_type="int",
        dimensions=tuple(),
        data=1,
    )
    assert b.variables["test_var"].data == 1

    b.remove("Variable", "test_var")
    assert "test_var" not in b.variables


def test_fromkwargs():
    tb = Block().from_kwargs(
        block_type="ThermalUnitBlock",
        MinPower=Variable("MinPower", "float", None, 0.0),
        MaxPower=Variable("MaxPower", "float", None, 100.0),
        LinearTerm=Variable("LinearTerm", "float", None, 0.3),
    )
    assert tb.block_type == "ThermalUnitBlock"
    assert tb.variables["MinPower"].data == 0


def test_block_constructor():
    kwargs = {
        "block_type": "ThermalUnitBlock",
        "MinPower": Variable("MinPower", "float", None, 0.0),
        "MaxPower": Variable("MaxPower", "float", None, 100.0),
        "LinearTerm": Variable("LinearTerm", "float", None, 0.3),
    }
    tb1 = Block().from_kwargs(**kwargs)
    tb2 = Block(**kwargs)
    assert tb1.block_type == tb2.block_type
    assert tb1.variables["MinPower"].data == tb2.variables["MinPower"].data


def test_add_block():
    b = SMSNetwork()
    add_base_ucblock(b)


def test_add_block_with_subblocks():
    b = SMSNetwork()
    add_ucblock_with_one_unit(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "ThermalUnitBlock"


def test_add_tub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_tub_to_ucblock(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "ThermalUnitBlock"


def test_add_bub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_bub_to_ucblock(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "BatteryUnitBlock"


def test_add_hub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_hub_to_ucblock(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "HydroUnitBlock"


def test_add_iub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_iub_to_ucblock(b)

    assert (
        b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "IntermittentUnitBlock"
    )


def test_investment_block():
    b = SMSNetwork()
    build_base_investmentblock(b)
    print(b)
    assert b.blocks["InvestmentBlock"].block_type == "InvestmentBlock"
    assert b.blocks["InvestmentBlock"].blocks["InnerBlock"].block_type == "UCBlock"
