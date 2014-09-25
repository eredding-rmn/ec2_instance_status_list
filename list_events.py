#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script is centered around this call:
create_image(instance_id, name, description=None, no_reboot=False, block_device_mapping=None, dry_run=False)

"""
import re
import os
import sys
import acky
import json
import logging
import datetime
from argparse import ArgumentParser
from acky.aws import AWS
from collections import defaultdict


LOGFORMAT = "%(asctime)s %(levelname)s: (%(process)d) %(name)s: %(message)s"
LOGNAME = 'list_events.py'
OUTPUT_LINE = "{0[profile]},{0[region]},{0[hostname]},{0[InstanceId]},{0[Code]},{0[Description]},{0[NotAfter]},{0[NotBefore]}"
log = logging.getLogger(LOGNAME)


class InstanceNotFoundException(Exception):
    pass

def get_tag(tags, tagname):
    try:
        ltags = tags.get('Tags')
    except:
        ltags = None
    if not ltags:
        ltags = tags
    for tag in ltags:
        if tag.get('Key') == tagname:
            return tag.get('Value')


def describe_instance(session, instance_ids, return_keys):
    params = {}
    log.debug(
        'describe instance: {0}; return_keys: {1}'.format(instance_ids, return_keys))
    if instance_ids and isinstance(instance_ids, list):
        params['instance_ids'] = instance_ids
    else:
        params['instance_ids'] = [instance_ids]

    log.debug('describe instance params: {0}'.format(params))
    try:
        resp = session.ec2.Instances.get(**params)
    except acky.api.AWSCallError as e:
        raise InstanceNotFoundException(e.message)
    response_return = {}
    if resp:
        for instance_data in resp:
            log.debug('response data: {}'.format(instance_data))
            response_return[instance_data.get('InstanceId')] = dict(
                (k, v) for k, v in instance_data.iteritems() if k in return_keys
            )
        log.debug('response_return: {}'.format(response_return))
        return response_return
    else:
        return None

def define_arguments():
    """ Define command line arguments.
    :return: Argparser object
    """
    std_args = ArgumentParser()
    std_args.add_argument("profile", help="(aka environment)")
    std_args.add_argument("region", help="e.g. us-east-1, us-west-2, etc.")

    logging = std_args.add_mutually_exclusive_group()
    logging.add_argument("--verbose", action="store_true", default=False)
    logging.add_argument("--debug", action="store_true", default=False)

    return std_args

def resolve_arguments(ap):
    args = ap.parse_args()
    args.aws = AWS(args.region, args.profile)
    return args

def configure_logging(args):
    if args.debug:
        loglevel = "DEBUG"
    elif args.verbose:
        loglevel = "INFO"
    else:
        loglevel = "WARNING"
    logging.basicConfig(level=loglevel, format=LOGFORMAT)
    # logging.getLogger('botocore').setLevel("WARNING")

def get_events(session):
    return session.ec2.Instances.events()




if __name__ == '__main__':
    args = resolve_arguments(define_arguments())
    configure_logging(args)
    log.debug('finding events')
    event_list = get_events(args.aws)
    event_ids = [item.get("InstanceId") for item in event_list]
    return_keys = ['Tags']
    instance_info = describe_instance(args.aws,event_ids, return_keys)
    blank_event_keys = ['InstanceId', 'Code', 'Description', 'NotAfter', 'NotBefore']
    for event in event_list:
        blank_event = defaultdict(str)
        blank_event['profile'] = args.profile
        blank_event['region'] = args.region
        hn = get_tag(instance_info[event.get("InstanceId")].get('Tags'), 'Name')
        if hn:
            blank_event['hostname'] = hn
        else:
            blank_event['hostname'] = ""
        for k,v in event.items():
            blank_event[k] = v
        print OUTPUT_LINE.format(blank_event, profile=args.profile, region=args.region)

