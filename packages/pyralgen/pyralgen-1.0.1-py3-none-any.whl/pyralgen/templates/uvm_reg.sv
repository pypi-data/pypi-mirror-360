{%- import 'utils.sv' as utils with context -%}


//------------------------------------------------------------------------------
// uvm_reg() definition
//------------------------------------------------------------------------------
{%- macro class_definition(node) -%}
{%- if class_needs_definition(node) %}
// {{get_class_friendly_name(node)}}
class {{get_class_name(node)}} extends uvm_reg;
{%- if use_uvm_factory %}
    `uvm_object_utils({{get_class_name(node)}})
{% endif -%}

    {{child_insts(node)|indent}}

    {{get_inst_name(top_node)}} reg_block;

    {{covergroup_inst(node)|indent}}

    {{function_new(node)|indent}}

    {{post_write_inst(node)|indent}}

    {{post_read_inst(node)|indent}}

    {{sample_values_inst(node)|indent}}

    {{function_build(node)|indent}}

endclass : {{get_class_name(node)}}
{% endif -%}
{%- endmacro -%}


//------------------------------------------------------------------------------
// Child instances
//------------------------------------------------------------------------------
{% macro child_insts(node) -%}
{%- for field in node.fields() %}
rand uvm_reg_field {{get_inst_name(field)}};
{%- endfor %}
{%- endmacro %}


//------------------------------------------------------------------------------
// Function: coverage
//------------------------------------------------------------------------------
{% macro covergroup_inst(node) -%}
// Function: coverage
covergroup cg_vals;
    option.per_instance = 1;
    {%- for field in node.fields() %}
    {{ get_inst_name(field) }} : coverpoint {{get_inst_name(field)}}.value[{{field.width-1}}:0];
    {%- endfor %}
endgroup : cg_vals
{%- endmacro %}


//------------------------------------------------------------------------------
// new() function
//------------------------------------------------------------------------------
{% macro function_new(node) -%}
// Function: new
function new(string name = "{{get_class_name(node)}}");
    super.new(name, {{node.get_property('regwidth')}}, build_coverage(UVM_CVR_FIELD_VALS));
    add_coverage(build_coverage(UVM_CVR_FIELD_VALS));
	if (has_coverage(UVM_CVR_FIELD_VALS)) begin
        cg_vals = new();
        cg_vals.set_inst_name(name);
    end
endfunction : new
{%- endmacro %}


//------------------------------------------------------------------------------
// Function: sample
//------------------------------------------------------------------------------
{% macro sample_inst(node) -%}
// Function: sample
virtual function void sample(uvm_reg_data_t  data,
                             uvm_reg_data_t  byte_en,
                             bit             is_read,
                             uvm_reg_map     map);
    cg_vals.sample();
endfunction : sample
{%- endmacro %}


//------------------------------------------------------------------------------
// Function: sample_values
//------------------------------------------------------------------------------
{% macro sample_values_inst(node) -%}
// Function: sample_values
virtual function void sample_values();
   super.sample_values();
   if (get_coverage(UVM_CVR_FIELD_VALS)) begin
       cg_vals.sample();
   end
endfunction : sample_values
{%- endmacro %}


//------------------------------------------------------------------------------
// Function: post_write
//------------------------------------------------------------------------------
{% macro post_write_inst(node) -%}
// Function: post_write
virtual task post_write(uvm_reg_item rw);
    super.post_write(rw);
    if (rw.status == UVM_IS_OK && rw.map != null) begin
        uvm_reg_addr_t offset = get_address(rw.map);
        reg_block.sample_map_values(offset, 0, rw.map);
        this.sample_values();
        `uvm_info(get_type_name(), $sformatf("POST_WRITE"), UVM_DEBUG)
    end
endtask : post_write
{%- endmacro %}


//------------------------------------------------------------------------------
// Function: post_read
//------------------------------------------------------------------------------
{% macro post_read_inst(node) -%}
// Function: post_read
virtual task post_read(uvm_reg_item rw);
    super.post_read(rw);
    if (rw.status == UVM_IS_OK && rw.map != null) begin
        uvm_reg_addr_t offset = get_address(rw.map);
        reg_block.sample_map_values(offset, 1, rw.map);
        this.sample_values();
        `uvm_info(get_type_name(), $sformatf("POST_READ"), UVM_DEBUG)
    end
endtask : post_read
{%- endmacro %}


//------------------------------------------------------------------------------
// build() function
//------------------------------------------------------------------------------
{% macro function_build(node) -%}
// Function build
virtual function void build();
    if(!$cast(reg_block, get_parent())) begin
        `uvm_fatal("CAST_ERROR", "Cannot get parent reg_block")
    end
    {%- for field in node.fields() %}
    {%- if use_uvm_factory %}
    this.{{get_inst_name(field)}} = uvm_reg_field::type_id::create("{{get_inst_name(field)}}");
    {%- else %}
    this.{{get_inst_name(field)}} = new("{{get_inst_name(field)}}");
    {%- endif %}
    this.{{get_inst_name(field)}}.configure(this, {{field.width}}, {{field.lsb}}, "{{get_field_access(field)}}", {{field.is_volatile|int}}, {{"'h%x" % field.get_property('reset', default=0)}}, {{field.get_property('reset') is not none|int}}, 1, 0);
    {%- endfor %}
endfunction : build
{%- endmacro %}


//------------------------------------------------------------------------------
// build() actions for uvm_reg instance (called by parent)
//------------------------------------------------------------------------------
{% macro build_instance(node) -%}
{%- if node.is_array %}
foreach(this.{{get_inst_name(node)}}[{{utils.array_iterator_list(node)}}]) begin
    {%- if use_uvm_factory %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = {{get_class_name(node)}}::type_id::create($sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}));
    {%- else %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = new($sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}));
    {%- endif %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.configure(this);
    {{add_hdl_path_slices(node, get_inst_name(node) + utils.array_iterator_suffix(node))|trim|indent}}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.build();
    this.default_map.add_reg(this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}, {{get_array_address_offset_expr(node)}});
end
{%- else %}
{%- if use_uvm_factory %}
this.{{get_inst_name(node)}} = {{get_class_name(node)}}::type_id::create("{{get_inst_name(node)}}");
{%- else %}
this.{{get_inst_name(node)}} = new("{{get_inst_name(node)}}");
{%- endif %}
this.{{get_inst_name(node)}}.configure(this);
{%- set hdl = add_hdl_path_slices(node, get_inst_name(node))|trim%}
{%- if hdl %}
{{hdl}}
{%- endif %}
this.{{get_inst_name(node)}}.build();
this.default_map.add_reg(this.{{get_inst_name(node)}}, {{"'h%x" % node.raw_address_offset}});
{%- endif %}
{%- endmacro %}


//------------------------------------------------------------------------------
// Load HDL path slices for this reg instance
//------------------------------------------------------------------------------
{% macro add_hdl_path_slices(node, inst_ref) -%}
{%- if node.get_property('hdl_path') %}
{{inst_ref}}.add_hdl_path_slice("{{node.get_property('hdl_path')}}", -1, -1);
{%- endif -%}

{%- if node.get_property('hdl_path_gate') %}
{{inst_ref}}.add_hdl_path_slice("{{node.get_property('hdl_path_gate')}}", -1, -1, 0, "GATE");
{%- endif -%}

{%- for field in node.fields() %}
{%- if field.get_property('hdl_path_slice') is none -%}
{%- elif field.get_property('hdl_path_slice')|length == 1 %}
{{inst_ref}}.add_hdl_path_slice("{{field.get_property('hdl_path_slice')[0]}}", {{field.lsb}}, {{field.width}});
{%- elif field.get_property('hdl_path_slice')|length == field.width %}
{%- for slice in field.get_property('hdl_path_slice') %}
{%- if field.msb > field.lsb %}
{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb - loop.index0}}, 1);
{%- else %}
{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb + loop.index0}}, 1);
{%- endif %}
{%- endfor %}
{%- endif %}
{%- endfor -%}

{%- for field in node.fields() %}
{%- if field.get_property('hdl_path_gate_slice') is none -%}
{%- elif field.get_property('hdl_path_gate_slice')|length == 1 %}
{{inst_ref}}.add_hdl_path_slice("{{field.get_property('hdl_path_gate_slice')[0]}}", {{field.lsb}}, {{field.width}}, 0, "GATE");
{%- elif field.get_property('hdl_path_gate_slice')|length == field.width %}
{%- for slice in field.get_property('hdl_path_gate_slice') %}
{%- if field.msb > field.lsb %}
{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb - loop.index0}}, 1, 0, "GATE");
{%- else %}
{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb + loop.index0}}, 1, 0, "GATE");
{%- endif %}
{%- endfor %}
{%- endif %}
{%- endfor %}
{%- endmacro %}