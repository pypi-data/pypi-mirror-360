# pyralgen

`pyralgen` is a lightweight Python-based UVM-RAL code generator. It leverages the
[SystemRDL](https://www.accellera.org/downloads/standards/systemrdl) standard to describe
the register specifications and extends the [PeakRDL-uvm](https://github.com/SystemRDL/PeakRDL-uvm)
framework to include build-in register coverage support.

## Features

- UVM-RAL code generation with automatic coverage model insertion
- Template-driven: easily extend or override code templates
- Industry best practices: idiomatic, maintainable SystemVerilog output
- Configurable: enable or disable coverage, factory usage, and more via CLI options

## Prerequisites

- Python 3.9.21 or later.

## Installing

**Note:** `pyralgen` is still under active development.

Clone the repository and set up the Python environment :

```bash
# Clone project
git clone https://github.com/cirofabianbermudez/pyralgen.git
cd pyralgen

# Bootstrap Python venv and install deps
./scripts/setup/setup_python_env.sh
source .venv/bin/activate

# Verify installation
pyuvcgen -h
```

## Example

The easiest way to use `pyralgen` is via the command line tool:

```bash
# Generate UVM-RAL
pyralgen -c registers.rdl -o ral_regs_pkg.sv
```

## Integration

Inside the `top_env.sv` make sure to **enable coverage models for register model** before
creating the register model and **enable sampling of coverage** after building the register
model.

```verilog
class top_env extends uvm_env;

  `uvm_component_utils(top_env)

  function void top_env::build_phase(uvm_phase phase);
    ...
    if (regmodel == null) begin

      // Enable Coverage models for register model <- Add this
      uvm_reg::include_coverage("*", UVM_CVR_ALL);

      // Create and build the register model
      regmodel = ral_reg_block::type_id::create("regmodel", this);
      uvm_config_db #(ral_reg_block)::set(this, "", "regmodel", regmodel);
      regmodel.build();

      // Enable sampling of coverage               <- Add this
      if (m_config.coverage_enable) begin
        regmodel.set_coverage(UVM_CVR_ALL);
      end

      // Lock and reset
      regmodel.lock_model();
      regmodel.reset()
    end
```

## Development

1. Clone de repository and navigate to its root directory:

    ```bash
    git clone https://github.com/cirofabianbermudez/pyralgen.git
    cd pyuvcgen
    ```

2. Create a Python virtual environment and install dependencies:

    ```bash
    ./script/setup/setup_python_env.sh
    source .venv/bin/activate
    ```

3. Verify installation:

    ```bash
    pyuvcgen -h
    ```

## License

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check issues or submit a pull request.
