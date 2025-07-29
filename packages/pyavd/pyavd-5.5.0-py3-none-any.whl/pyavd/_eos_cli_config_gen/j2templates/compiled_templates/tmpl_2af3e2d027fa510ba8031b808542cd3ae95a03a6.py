from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/recirculation-interfaces.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_recirculation_interfaces = resolve('recirculation_interfaces')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    for l_1_recirculation_interface in t_1((undefined(name='recirculation_interfaces') if l_0_recirculation_interfaces is missing else l_0_recirculation_interfaces), 'name'):
        _loop_vars = {}
        pass
        yield '!\ninterface '
        yield str(environment.getattr(l_1_recirculation_interface, 'name'))
        yield '\n'
        if t_3(environment.getattr(l_1_recirculation_interface, 'description')):
            pass
            yield '   description '
            yield str(environment.getattr(l_1_recirculation_interface, 'description'))
            yield '\n'
        if t_3(environment.getattr(l_1_recirculation_interface, 'shutdown'), True):
            pass
            yield '   shutdown\n'
        elif t_3(environment.getattr(l_1_recirculation_interface, 'shutdown'), False):
            pass
            yield '   no shutdown\n'
        if t_3(environment.getattr(l_1_recirculation_interface, 'recirculation_features')):
            pass
            yield '   switchport recirculation features '
            yield str(environment.getattr(l_1_recirculation_interface, 'recirculation_features'))
            yield '\n'
        if t_3(environment.getattr(l_1_recirculation_interface, 'eos_cli')):
            pass
            yield '   '
            yield str(t_2(environment.getattr(l_1_recirculation_interface, 'eos_cli'), 3, False))
            yield '\n'
    l_1_recirculation_interface = missing

blocks = {}
debug_info = '7=30&9=34&10=36&11=39&13=41&15=44&18=47&19=50&21=52&22=55'