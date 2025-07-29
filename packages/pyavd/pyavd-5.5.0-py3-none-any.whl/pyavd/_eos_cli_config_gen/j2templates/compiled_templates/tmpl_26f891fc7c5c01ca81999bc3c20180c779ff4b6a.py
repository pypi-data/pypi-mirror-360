from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/recirculation-interfaces.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_recirculation_interfaces = resolve('recirculation_interfaces')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3((undefined(name='recirculation_interfaces') if l_0_recirculation_interfaces is missing else l_0_recirculation_interfaces)):
        pass
        yield '\n### Recirculation Interfaces\n\n#### Recirculation Interfaces Summary\n\n| Interface | Description | Shutdown | Recirculation Features |\n| --------- | ----------- | -------- | ---------------------- |\n'
        for l_1_recirculation_interface in t_2((undefined(name='recirculation_interfaces') if l_0_recirculation_interfaces is missing else l_0_recirculation_interfaces), 'name'):
            l_1_description = l_1_shutdown = l_1_recirculation_features = missing
            _loop_vars = {}
            pass
            l_1_description = t_1(environment.getattr(l_1_recirculation_interface, 'description'), '-')
            _loop_vars['description'] = l_1_description
            l_1_shutdown = t_1(environment.getattr(l_1_recirculation_interface, 'shutdown'), '-')
            _loop_vars['shutdown'] = l_1_shutdown
            l_1_recirculation_features = t_1(environment.getattr(l_1_recirculation_interface, 'recirculation_features'), '-')
            _loop_vars['recirculation_features'] = l_1_recirculation_features
            yield '| '
            yield str(environment.getattr(l_1_recirculation_interface, 'name'))
            yield ' | '
            yield str((undefined(name='description') if l_1_description is missing else l_1_description))
            yield ' | '
            yield str((undefined(name='shutdown') if l_1_shutdown is missing else l_1_shutdown))
            yield ' | '
            yield str((undefined(name='recirculation_features') if l_1_recirculation_features is missing else l_1_recirculation_features))
            yield ' |\n'
        l_1_recirculation_interface = l_1_description = l_1_shutdown = l_1_recirculation_features = missing
        yield '\n#### Recirculation Interfaces Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/recirculation-interfaces.j2', 'documentation/recirculation-interfaces.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=30&15=33&16=37&17=39&18=41&19=44&25=54'