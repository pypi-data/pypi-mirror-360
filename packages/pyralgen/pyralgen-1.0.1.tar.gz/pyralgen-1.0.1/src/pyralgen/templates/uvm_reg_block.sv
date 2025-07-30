{%- import 'utils.sv' as utils with context -%}


//------------------------------------------------------------------------------
// uvm_reg_block() definition
//------------------------------------------------------------------------------
{%- macro class_definition(node) -%}
{% if class_needs_definition(node) %}
// Map Coverage Object
class {{get_class_name(node)}}_default_map_coverage extends uvm_object;
{%- if use_uvm_factory %}
    `uvm_object_utils({{get_class_name(node)}}_default_map_coverage)
{%- endif %}

    {{function_covergroup(node)|indent}}

    {{function_new_cov(node)|indent}}

    {{function_sample_cov(node)|indent}}

endclass : {{get_class_name(node)}}_default_map_coverage

// {{get_class_friendly_name(node)}}
class {{get_class_name(node)}} extends uvm_reg_block;
{%- if use_uvm_factory %}
    `uvm_object_utils({{get_class_name(node)}})
{%- endif %}

    {{child_insts(node)|indent}}
    {{get_class_name(node)}}_default_map_coverage default_map_cg;

    {{function_new(node)|indent}}

    {{function_build(node)|indent}}

    {{function_sample_map_values(node)|indent}}

endclass : {{get_class_name(node)}}
{% endif -%}
{%- endmacro -%}


//------------------------------------------------------------------------------
// Child instances
//------------------------------------------------------------------------------
{% macro child_insts(node) -%}
{%- for child in node.children() if isinstance(child, AddressableNode) -%}
rand {{get_class_name(child)}} {{get_inst_name(child)}}{{utils.array_inst_suffix(child)}};
{% endfor -%}
{%- endmacro %}


//------------------------------------------------------------------------------
// new() function
//------------------------------------------------------------------------------
{% macro function_new(node) -%}
// Function: new
function new(string name = "{{get_class_name(node)}}");
    super.new(name, build_coverage(UVM_CVR_ALL));
endfunction : new
{%- endmacro %}


//------------------------------------------------------------------------------
// build() function
//------------------------------------------------------------------------------
{% macro function_build(node) -%}
// Function: build
virtual function void build();

    if(has_coverage(UVM_CVR_ADDR_MAP)) begin
        default_map_cg = {{get_class_name(node)}}_default_map_coverage::type_id::create("default_map_cg");
        default_map_cg.ra_cov.set_inst_name(this.get_full_name());
        void'(set_coverage(UVM_CVR_ADDR_MAP));
    end

    this.default_map = create_map("default_map", 0, {{get_bus_width(node)}}, {{get_endianness(node)}});
    {% for child in node.children() -%}
        {%- if isinstance(child, RegNode) -%}
            {{uvm_reg.build_instance(child)|indent}}
        {% elif isinstance(child, (RegfileNode, AddrmapNode)) -%}
            {{build_instance(child)|indent}}
        {%- elif isinstance(child, MemNode) -%}
            {{uvm_reg_block_mem.build_instance(child)|indent}}
        {%- endif -%}
    {%- endfor %}
endfunction : build
{%- endmacro %}


//------------------------------------------------------------------------------
// build() actions for uvm_reg_block instance (called by parent)
//------------------------------------------------------------------------------
{% macro build_instance(node) -%}
{%- if node.is_array %}
foreach(this.{{get_inst_name(node)}}[{{utils.array_iterator_list(node)}}]) begin
    {%- if use_uvm_factory %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = {{get_class_name(node)}}::type_id::create($sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}));
    {%- else %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = new($sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}));
    {%- endif %}
    {%- if node.get_property('hdl_path') %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.configure(this, "{{node.get_property('hdl_path')}}");
    {%- else %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.configure(this);
    {%- endif %}
    {%- if node.get_property('hdl_path_gate') %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.add_hdl_path("{{node.get_property('hdl_path_gate')}}", "GATE");
    {%- endif %}
    this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.build();
    this.default_map.add_submap(this.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.default_map, {{get_array_address_offset_expr(node)}});
end
{%- else %}
{%- if use_uvm_factory %}
this.{{get_inst_name(node)}} = {{get_class_name(node)}}::type_id::create("{{get_inst_name(node)}}");
{%- else %}
this.{{get_inst_name(node)}} = new("{{get_inst_name(node)}}");
{%- endif %}
{%- if node.get_property('hdl_path') %}
this.{{get_inst_name(node)}}.configure(this, "{{node.get_property('hdl_path')}}");
{%- else %}
this.{{get_inst_name(node)}}.configure(this);
{%- endif %}
{%- if node.get_property('hdl_path_gate') %}
this.{{get_inst_name(node)}}.add_hdl_path("{{node.get_property('hdl_path_gate')}}", "GATE");
{%- endif %}
this.{{get_inst_name(node)}}.build();
this.default_map.add_submap(this.{{get_inst_name(node)}}.default_map, {{"'h%x" % node.raw_address_offset}});
{%- endif %}
{%- endmacro %}


//------------------------------------------------------------------------------
// Covergroup function
//------------------------------------------------------------------------------
{% macro function_covergroup(node) -%}
covergroup ra_cov(string name) with function sample(uvm_reg_addr_t addr, bit is_read);

    option.per_instance = 1;
    option.name = name;

    ADDR: coverpoint addr {
        {{- addr_coverpoint_calculate(node)|indent }}
    }

    RW: coverpoint is_read {
        bins RD = {1};
        bins WR = {0};
    }

    ACCESS: cross ADDR, RW {
    }

endgroup: ra_cov
{%- endmacro %}


//------------------------------------------------------------------------------
// new() function for coverage object
//------------------------------------------------------------------------------
{% macro function_new_cov(node) -%}
// Function: new
function new(string name = "{{get_class_name(node)}}_default_map_coverage");
    ra_cov = new(name);
endfunction : new
{%- endmacro %}


//------------------------------------------------------------------------------
// sample() function for coverage object
//------------------------------------------------------------------------------
{% macro function_sample_cov(node) -%}
// Function: sample
function void sample(uvm_reg_addr_t offset, bit is_read);
    ra_cov.sample(offset, is_read);
endfunction: sample
{%- endmacro %}


//------------------------------------------------------------------------------
// addr_coverpoint_calculate() function
//------------------------------------------------------------------------------
{%- macro addr_coverpoint_calculate(node) -%}
{%- for child in node.children() %}
    bins {{get_inst_name(child)}} = { {{"'h%x" % child.raw_address_offset}} };
{%- endfor -%}
{%- endmacro -%}


//------------------------------------------------------------------------------
// ro_addr_calculate() function
//------------------------------------------------------------------------------
{%- macro ro_addr_calculate(node) -%}
{%- set out = namespace(str = "") -%}

{%- for child in node.children() %}
    {%- set ns = namespace(all_ro = true)  %}
    {%- for field in child.fields() -%}
        {%- if get_field_access(field) != 'RO' -%}
            {%- set ns.all_ro = false -%}
        {%- endif %}
    {%- endfor -%}
    
    {%- if ns.all_ro %}
        {%- set out.str = out.str ~ ("'h%x" % child.raw_address_offset) ~ "," -%}
    {%- endif %}
{%- endfor -%}
{{ out.str[:-1] }}
{%- endmacro -%}


//------------------------------------------------------------------------------
// function_sample_map_values() function
//------------------------------------------------------------------------------
{% macro function_sample_map_values(node) -%}
// Function: sample_map_values
function void sample_map_values(uvm_reg_addr_t offset, bit is_read, uvm_reg_map map);
   if(get_coverage(UVM_CVR_ADDR_MAP)) begin
      if(map.get_name() == "default_map") begin
         default_map_cg.sample(offset, is_read);
         `uvm_info(get_type_name(), $sformatf("SAMPLE_MAP_VALUES: %3d %3d", offset, is_read), UVM_DEBUG)
      end
   end
endfunction: sample_map_values
{%- endmacro %}