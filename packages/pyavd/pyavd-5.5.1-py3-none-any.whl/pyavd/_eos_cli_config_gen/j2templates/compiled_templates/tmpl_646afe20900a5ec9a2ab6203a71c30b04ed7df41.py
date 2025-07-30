from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/load-balance.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_load_balance = resolve('load_balance')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'policies')):
        pass
        yield '\n## Load Balance\n\n### Load Balance Profiles\n'
        for l_1_profile in t_1(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'policies'), 'sand_profiles'), 'name'):
            _loop_vars = {}
            pass
            yield '\n#### '
            yield str(environment.getattr(l_1_profile, 'name'))
            yield '\n'
            if t_2(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp')):
                pass
                yield '\n##### UDP Fields Settings\n\n| Setting | Value |\n| ------- | ----- |\n| Destination Port | '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'dst_port'))
                yield ' |\n'
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match')):
                    pass
                    yield '| Match Payload Bits | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'payload_bits'))
                    yield ' |\n| Match Pattern | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'pattern'))
                    yield ' |\n| Match Hash Payload Bytes | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'hash_payload_bytes'))
                    yield ' |\n'
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'payload_bytes')):
                    pass
                    yield '| UDP Payload | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'payload_bytes'))
                    yield ' |\n'
        l_1_profile = missing
        yield '\n### Load Balance Configuration\n\n```eos\n'
        template = environment.get_template('eos/load-balance.j2', 'documentation/load-balance.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=24&12=27&14=31&15=33&21=36&22=38&23=41&24=43&25=45&27=47&28=50&36=54'