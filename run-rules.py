#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    run-rules [options] <rules.yml> <vars.yml> <inventory.yml>

Options:
    -h, --help        Show this page
    --debug            Show debug logging
    --verbose        Show verbose logging
"""
from docopt import docopt
import os
import logging
import sys
import yaml
import rules_parser
import multiprocessing as mp
import runpy
import jinja2
import asyncio
from faster_than_light import run_module, load_inventory

logger = logging.getLogger('run-rules')


def load_vars(parsed_args):
    with open(parsed_args['<vars.yml>']) as f:
        return yaml.safe_load(f.read())


def load_rules(parsed_args):
    with open(parsed_args['<rules.yml>']) as f:
        return rules_parser.parse_rule_sets(yaml.safe_load(f.read()))


def substitute_variables(value, context):
    return jinja2.Template(value, undefined=jinja2.StrictUndefined).render(context)


def start_sources(sources, variables, queue):

    for source in sources:
        module = runpy.run_path(os.path.join('sources', source.source_name + '.py'))
        args = {k: substitute_variables(v, variables) for k, v in source.source_args.items()}
        module.get('main')(queue, args)


def run_rules(rules, variables, inventory, queue):

    while True:
        data = queue.get()
        print(data)
        variables_copy = variables.copy()
        variables_copy['event'] = str(data)
        for rule in rules:
            print(rule)
            if rule.condition.value:
                asyncio.run(run_module(inventory,
                                       ['modules'],
                                       rule.action.module,
                                       modules=[rule.action.module],
                                       module_args={k: substitute_variables(v, variables_copy) for k, v in rule.action.module_args.items()}))


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = docopt(__doc__, args)
    if parsed_args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    variables = load_vars(parsed_args)
    rulesets = load_rules(parsed_args)
    inventory = load_inventory(parsed_args['<inventory.yml>'])

    print(variables)
    print(rulesets)

    tasks = []

    for ruleset in rulesets:
        sources = ruleset.sources
        rules = ruleset.rules
        queue = mp.Queue()

        tasks.append(mp.Process(target=start_sources, args=(sources, variables, queue)))
        tasks.append(mp.Process(target=run_rules, args=(rules, variables, inventory, queue,)))

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
