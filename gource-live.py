#!/usr/bin/env python
#

import os
DIRNAME = os.path.abspath(os.path.dirname(__file__))

import argparse
import subprocess

if os.path.isdir('.git'):
    repo_type = 'git'
elif os.path.isdir('.bzr'):
    repo_type = 'bzr'
elif os.path.isdir('.svn'):
    repo_type = 'svn'
else:
    repo_type = None

parser = argparse.ArgumentParser(description='Generate a live feed of VCS changes as input for Gource')
# common params
parser.add_argument('--show-feed', action='store_true',
        help='Show the feed and do not pipe it to gource')
parser.add_argument('--interval', default='5',
        help='The repository polling interval to check for changes')
parser.add_argument('--start', default='',
        help='The start revision to use instead of the default')
# git specific
parser.add_argument('--remote', default='origin',
        help='The remote to use instead of "origin" (Git only)')
parser.add_argument('--branch', default='master',
        help='The branch to use instead of "master" (Git only)')

args = parser.parse_args()

if not repo_type:
    parser.error('Current directory is either not the root directory of a project, or this VCS is not supported. Currently supported VCS: Git, Bazaar, Subversion. Change into the root directory of your project (in a supported VCS) and re-run the same command.')
elif repo_type == 'git':
    feeder_script = os.path.join(DIRNAME, 'feeders/feeder-git.sh')
    feeder_args = [feeder_script, args.remote, args.branch, args.interval, args.start]
elif repo_type == 'bzr':
    feeder_script = os.path.join(DIRNAME, 'feeders/feeder-bzr.sh')
    feeder_args = [feeder_script, args.interval, args.start]
elif repo_type == 'svn':
    feeder_script = os.path.join(DIRNAME, 'feeders/feeder-svn.sh')
    feeder_args = [feeder_script, args.interval, args.start]

if args.show_feed:
    feeder = subprocess.Popen(feeder_args)
    feeder.wait()
else:
    feeder = subprocess.Popen(feeder_args, stdout=subprocess.PIPE)

    gource2 = subprocess.Popen('gource --log-format git --file-idle-time 0 -640x480 -s 20 --hide filenames,dirnames,mouse --title "Gource Live" --bloom-intensity 0.25 --key --max-file-lag 0.1 --output-ppm-stream - | ffmpeg -y -r 30 -f image2pipe -vcodec ppm -i - -vcodec libvpx -b 1000K http://127.0.0.1:8090/feed1.ffm', shell=True, stdin=feeder.stdout) 
    
    # gource = subprocess.Popen(['gource', '--log-format', 'git', '--file-idle-time', '0', '-1280x720', '--hide', 'filenames,dirnames,mouse', '--bloom-intensity', '0.25', '--key', '--max-file-lag', '0.1', ' --output-ppm-stream', '-'], shell=True, stdin=feeder.stdout, stdout=subprocess.PIPE)
    
    # ffmpeg = subprocess.Popen(['ffmpeg', '-y', '-r', '30', '-f', 'image2pipe', '-vcodec', 'ppm', '-i', '-', '-vcodec', 'libvpx', '-b', '1000K', 'http://127.0.0.1:8090/feed1.ffm'], shell=True, stdin=gource.stdout, stdout=subprocess.PIPE)
    
    gource2.communicate()