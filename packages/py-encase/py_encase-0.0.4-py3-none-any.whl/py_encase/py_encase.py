#!/usr/bin/env python3

import sys
import os
import datetime
import pathlib
import argparse
import shutil
import subprocess
import inspect
import filecmp
import textwrap
import re
import typing
import io
import getpass
import socket
import json

class PyEncase(object):

    VERSION          = '0.0.4'
    PIP_MODULE_NAME  = 'py-encase'
    ENTYTY_FILE_NAME = pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name
    #    ENTYTY_FILE_NAME = pathlib.Path(__file__).resolve().name


    MNG_SCRIPT = 'mng_encase'
    MNG_OPT    = '--manage'

    PIP_SBCMDS_ACCEPT = {'install':   None,
                         'download':  None,
#                         'uninstall': None,
                         'freeze':    None,
                         'inspect':   None,
                         'list':      None,
#                         'show':      None,
#                         'check':     None,
#                         'search':    None,
                         'cache':     None,
#                         'index':     None,
#                         'wheel':     None,
#                         'hash':      None,
                         'help':      'piphelp'}

    SCRIPT_STD_LIB = {}

    FILENAME_DEFAULT = { '____GIT_DUMMYFILE____': '.gitkeep',
                         '____README_NAME____':   'README.md',
                        }

    def __init__(self, argv:list=sys.argv, 
                 python_cmd:str=None, pip_cmd:str=None, 
                 prefix_cmd:str=None, git_cmd:str=None, 
                 verbose:bool=False, dry_run:bool=False, encoding='utf-8'):

        self.argv         = argv
        self.path_invoked = pathlib.Path(self.argv[0])
        self.flg_symlink  = self.path_invoked.is_symlink()
        self.encoding     = encoding
        self.set_python_path(python_cmd=python_cmd,
                             pip_cmd=pip_cmd, prefix_cmd=prefix_cmd)
        self.set_git_path(git_cmd=git_cmd)
        self.verbose      = verbose
        self.dry_run      = dry_run

        self.__class__.SCRIPT_STD_LIB['pkg_cache'] = {'creator'     : self.python_pkg_cache_template_save,
                                                      'description' : 'Module for cache file under package directory',
                                                      'depends'     : ['intrinsic_format'],
                                                      'pip_module'  : ['PyYAML', 'pkgstruct']}

        self.__class__.SCRIPT_STD_LIB['intrinsic_format'] = {'creator'     : self.python_intrinsic_format_template_save,
                                                             'description' : 'Module for intrinsic data formater',
                                                             'depends'     : [],
                                                             'pip_module'  : ['PyYAML']}

    def set_python_path(self, python_cmd=None, pip_cmd=None, prefix_cmd=None):
        self.python_select = (python_cmd if isinstance(python_cmd,str) and python_cmd
                              else os.environ.get('PYTHON', os.environ.get('PYTHON3', 'python3')))

        self.python_shebang = (("#!"+self.python_select) if self.python_select.startswith('/') 
                               else ("#!"+shutil.which('env')+' '+self.python_select) )

        self.python_use = pathlib.Path(shutil.which(python_cmd) if isinstance(python_cmd,str) and python_cmd 
                                       else shutil.which(os.environ.get('PYTHON',
                                                                        os.environ.get('PYTHON3',
                                                                                       shutil.which('python3') or shutil.which('python')))))

        self.pip_use = pathlib.Path(shutil.which(pip_cmd) if isinstance(pip_cmd,str) and pip_cmd 
                                    else shutil.which(os.environ.get('PIP',
                                                                     os.environ.get('PIP3',
                                                                                    shutil.which('pip3') or shutil.which('pip')))))
        
        if sys.executable == self.python_use.absolute():
            self.python_vertion_str = '.'.join(sys.version_info[:2])
        else:
            py_version_fetch = subprocess.run([str(self.python_use), '--version'], encoding=self.encoding, stdout=subprocess.PIPE)
            self.python_vertion_str = py_version_fetch.stdout.split()[1]

        pip_version_fetch = subprocess.run([str(self.pip_use), '--version'], encoding=self.encoding, stdout=subprocess.PIPE)
        self.pip_vertion_str = pip_version_fetch.stdout.split()[1]

        if isinstance(prefix_cmd,str) and prefix_cmd:
            self.prefix = os.path.expandvars(os.path.expanduser(prefix_cmd))
            flg_substructure = not ( os.path.exists(os.path.join(self.prefix, self.path_invoked.name)) or 
                                     os.path.exists(os.path.join(self.prefix, self.path_invoked.name)+'.py') )
        else:
            path_abs     = self.path_invoked.absolute()
            flg_substructure = (path_abs.parent.name=='bin')
            self.prefix  = str(path_abs.parent.parent) if flg_substructure else str(path_abs.parent)

        self.bindir  = os.path.join(self.prefix, 'bin') if flg_substructure else self.prefix
        self.libdir  = os.path.join(self.prefix, 'lib') if flg_substructure else self.prefix
        self.vardir  = os.path.join(self.prefix, 'var') if flg_substructure else self.prefix
        self.srcdir  = os.path.join(self.prefix, 'src') if flg_substructure else self.prefix

        self.tmpdir            = os.path.join(self.vardir, 'tmp', 'python', 'packages', self.python_vertion_str)
        self.logdir            = os.path.join(self.vardir, 'log')

        self.python_path         = os.path.join(self.libdir, 'python')
        self.python_pip_path     = os.path.join(self.libdir, 'python', 'site-packages', self.python_vertion_str)
        self.python_pip_cache    = os.path.join(self.vardir, 'cache', 'python', 'packages', self.python_vertion_str)
        self.python_pip_src      = os.path.join(self.srcdir, 'python', 'packages', self.python_vertion_str)
        self.python_pip_logdir   = os.path.join(self.logdir, 'pip', self.pip_vertion_str)
        self.python_pip_log_path = os.path.join(self.python_pip_logdir, 'pip-log.txt')
        self.git_keepdirs = [os.path.dirname(self.python_pip_path),
                             os.path.dirname(self.python_pip_cache),
                             os.path.dirname(self.python_pip_src),
                             os.path.dirname(self.python_pip_logdir), 
                             os.path.dirname(self.tmpdir)]


    def set_git_path(self, git_cmd:str=None):
        self.git_path = shutil.which(git_cmd if isinstance(git_cmd,str) and git_cmd else os.environ.get('GIT', 'git'))

    def main(self):
        argprsr = argparse.ArgumentParser(add_help=False)
        if self.flg_symlink:
            argprsr.set_defaults(manage=(self.path_invoked.name
                                         in (self.MNG_SCRIPT, self.MNG_SCRIPT+'.py')))
        else:
            argprsr.add_argument(self.MNG_OPT, action='store_true') 

        args, rest = argprsr.parse_known_args()

        if not args.manage:

            if self.flg_symlink:
                scriptname = self.path_invoked.name
                scriptargs = rest
            else:
                argprsr.add_argument('script', nargs='?', default=None, const=None, help='script name/path')
                narg,rest = argprsr.parse_known_args()
                scriptname = narg.script
                scriptargs = rest

            self.run_script(script=scriptname, args=rest)
        else:
            argprsrm = argparse.ArgumentParser(add_help=False, exit_on_error=False)
            argprsrm.add_argument('-P', '--python', default=None, help='Python path / command')
            argprsrm.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            argprsrm.add_argument('-p', '--prefix',  default=None, help=('prefix of the directory tree. ' +
                                                                         '(Default: Grandparent directory' +
                                                                         ' if the name of parent directory of %s is bin,'
                                                                         ' otherwise current working directory.' 
                                                                         % (self.path_invoked.name, )))
            argprsrm.add_argument('-G', '--git-command', default=None, help='git path / command')
            argprsrm.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
            argprsrm.add_argument('-n', '--dry-run', action='store_true', help='Dry Run Mode')

            argpre,restpre = argprsrm.parse_known_args(rest) 
            self.verbose = argpre.verbose
            self.dry_run = argpre.dry_run

            self.set_python_path(python_cmd=argpre.python, pip_cmd=argpre.pip, 
                                 prefix_cmd=(argpre.prefix if hasattr(argpre, 'prefix') else None))
            self.set_git_path(git_cmd=argpre.git_command)

            argprsrm.add_argument('-h', '--help', action='help') 

            sbprsrs = argprsrm.add_subparsers(dest='subcommand')
            
            parser_add_info = sbprsrs.add_parser('info', help='Show information')
            parser_add_info.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_info.add_argument('-l', '--long', action='store_true', help='Show all information')
            parser_add_info.set_defaults(handler=self.show_info)

            parser_add_init = sbprsrs.add_parser('init', help='Initialise Environment')
            parser_add_init.add_argument('-P', '--python', default=None, help='Python path / command')
            parser_add_init.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            parser_add_init.add_argument('-p', '--prefix',  default=self.prefix, help=('prefix of the directory tree. ' +
                                                                                       '(Default: Grandparent directory' +
                                                                                       ' if the name of parent directory of %s is bin,'
                                                                                       ' otherwise current working directory.' 
                                                                                       % (self.path_invoked.name, )))
            parser_add_init.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_init.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_init.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')


            parser_add_init.add_argument('-M', '--move', action='store_true', help='moving this script body into instead of copying')
            parser_add_init.add_argument('-g', '--git',  action='store_true', help='setup files for git')
            parser_add_init.add_argument('-e', '--git-email',  type=str, help='git user e-mail address')
            parser_add_init.add_argument('-u', '--git-user',   type=str, help='git user name ')
            parser_add_init.add_argument('-U', '--git-remote-url', type=str, help='git remote URL')

            parser_add_init.add_argument('-y', '--git-set-upstream', action='store_true', default=False, help='git set upstream')

            parser_add_init.add_argument('-r', '--readme', action='store_true', help='setup/update README.md')
            parser_add_init.add_argument('-t', '--title',  help='Project title')
            parser_add_init.add_argument('-m', '--module', default=[], action='append', help='install module by pip')
            parser_add_init.add_argument('-s', '--script-lib', default=[], action='append', help='install library script from template.')
            parser_add_init.add_argument('-S', '--std-script-lib', action='store_true', help=('install standard library scripts. (equivalent to "' +
                                                                                         ' '.join(['-s %s' % (m, ) for m 
                                                                                                   in self.__class__.SCRIPT_STD_LIB.keys() ])
                                                                                         +')"'))
            parser_add_init.add_argument('scriptnames', nargs='*', help='script file name to be created')
            parser_add_init.set_defaults(handler=self.manage_env)
          
            parser_add_add = sbprsrs.add_parser('add', help='add new script files')
            parser_add_add.add_argument('-P', '--python', default=None, help='Python path / command')
            parser_add_add.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            parser_add_add.add_argument('-p', '--prefix',  default=self.prefix, help=('prefix of the directory tree. ' +
                                                                                      '(Default: Grandparent directory' +
                                                                                      ' if the name of parent directory of %s is bin,'
                                                                                      ' otherwise current working directory.' 
                                                                                      % (self.path_invoked.name, )))
            parser_add_add.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_add.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_add.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')

            parser_add_add.add_argument('-r', '--readme', action='store_true', help='setup/update README.md')
            parser_add_add.add_argument('-m', '--module', default=[], action='append', help='install module by pip')
            parser_add_add.add_argument('-s', '--script-lib', default=[], action='append', help='install library script from template.')
            parser_add_add.add_argument('-S', '--std-script-lib', action='store_true', help=('install standard library scripts. (equivalent to "' +
                                                                                             ' '.join(['-s %s' % (m, ) for m 
                                                                                                       in self.__class__.SCRIPT_STD_LIB.keys() ])
                                                                                             +'"'))
            parser_add_add.add_argument('scriptnames', nargs='+', help='all files')
            parser_add_add.set_defaults(handler=self.manage_env)

            parser_add_addlib = sbprsrs.add_parser('addlib', help='add new script files')
            parser_add_addlib.add_argument('-P', '--python', default=None, help='Python path / command')
            parser_add_addlib.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            parser_add_addlib.add_argument('-p', '--prefix',  default=self.prefix, help=('prefix of the directory tree. ' +
                                                                                         '(Default: Grandparent directory' +
                                                                                         ' if the name of parent directory of %s is bin,'
                                                                                         ' otherwise current working directory.' 
                                                                                        % (self.path_invoked.name, )))
            parser_add_addlib.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_addlib.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_addlib.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            parser_add_addlib.add_argument('-r', '--readme', action='store_true', help='setup/update README.md')
            parser_add_addlib.add_argument('-m', '--module', default=[], action='append', help='install module by pip')
            parser_add_addlib.add_argument('-S', '--std-script-lib', action='store_true', help=('install standard library scripts. (equivalent to "' +
                                                                                                ' '.join(['-s %s' % (m, ) for m 
                                                                                                          in self.__class__.SCRIPT_STD_LIB.keys() ])
                                                                                                +'"'))
            parser_add_addlib.add_argument('script_lib', nargs='+', help='all files')
            parser_add_addlib.set_defaults(handler=self.manage_env)
            
            parser_add_clean = sbprsrs.add_parser('clean', help='clean-up')

            parser_add_clean.set_defaults(handler=self.clean_env)
            parser_add_clean.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_clean.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')

            parser_add_distclean = sbprsrs.add_parser('distclean', help='Entire clean-up')
            parser_add_distclean.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_distclean.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            parser_add_distclean.set_defaults(handler=self.clean_env)

            #parser_add_selfupdate = sbprsrs.add_parser('selfupdate', help='Self update of '+os.path.basename(__file__))
            parser_add_selfupdate = sbprsrs.add_parser('selfupdate', 
                                                       help='Self update of '
                                                       +pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name)

            parser_add_selfupdate.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_selfupdate.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            parser_add_selfupdate.add_argument('-f', '--force-install', action='store_true', help='Force install')

            parser_add_selfupdate.set_defaults(handler=self.self_update)

            for c,cc in self.__class__.PIP_SBCMDS_ACCEPT.items():
                _scmd = c if cc is None else cc
                _prsr_add = sbprsrs.add_parser(_scmd, 
                                               help=('PIP command : %s' % (c,)))
                _prsr_add.add_argument('pip_subcommand_args', nargs='*', help='Arguments for pip subcommands')
                _prsr_add.set_defaults(handler=self.invoke_pip)

            #argps= argprsrm.parse_args()

            argps,restps = argprsrm.parse_known_args(rest) 

            #self.set_python_path(python_cmd=argps.python, pip_cmd=argps.pip, 
            #                     prefix_cmd=(argps.prefix if hasattr(argps, 'prefix') else None))
            
            if hasattr(argps, 'handler'):
                argps.handler(argps, restps)
            else:
                argprsrm.print_help()
            
    def invoke_pip(self, args:argparse.Namespace, rest:list=[]):
        flg_verbose = args.verbose if hasattr(args, 'verbose') else False
        flg_dry_run  = args.dry_run  if hasattr(args, 'dry_run') else False
        return self.run_pip(subcmd=args.subcommand,
                            args=args.pip_subcommand_args+rest,
                            verbose=flg_verbose, dry_run=flg_dry_run)
    @classmethod
    def version_compare(cls, v1:str, v2:str):
        """
        v1 < v2: -1, v1 == v2 :0, v1 > v2: 1
        """
        ibuf1  = [int(x) for x in v1.split('.')]
        ibuf2  = [int(x) for x in v2.split('.')]
        l_ibuf = max(len(ibuf1), len(ibuf2))
        ibuf1 += [0] * (l_ibuf- len(ibuf1))
        ibuf2 += [0] * (l_ibuf- len(ibuf2))
        for i1, i2 in zip(ibuf1, ibuf2):
            if i1 < i2:
                return -1
            elif i1 > i2:
                return 1
        return 0

    def self_update(self, args:argparse.Namespace, rest:list=[]):
        subcmd = args.subcommand if hasattr(args, 'subcommand') else 'unknown'
        self.set_python_path(python_cmd=(args.python if (hasattr(args, 'python') and
                                                         args.python is not None) else self.python_select),
                             pip_cmd=(args.pip if (hasattr(args, 'pip') and
                                                   args.pip is not None) else str(self.pip_use)),
                             prefix_cmd=( args.prefix if (hasattr(args, 'prefix') and
                                                          args.prefix  is not None) else self.prefix))
        flg_verbose   = args.verbose       if hasattr(args, 'verbose')       else self.verbose
        flg_dry_run   = args.dry_run       if hasattr(args, 'dry_run')       else False
        force_install = args.force_install if hasattr(args, 'force_install') else False

        pip_install_out = self.run_pip(subcmd='install', 
                                       args=['--upgrade', '--force-reinstall', 
                                             self.__class__.PIP_MODULE_NAME],
                                       verbose=flg_verbose, dry_run=False)

        pip_list_out = self.run_pip(subcmd='list', args=['--format', 'json'],
                                    verbose=flg_verbose, dry_run=False, capture_output=True)
        pip_installed = json.loads(pip_list_out.stdout)
        latest_version="0.0.0"
        for minfo in pip_installed:
            if ( (not isinstance(minfo, dict)) or 
                 minfo.get('name', "") != self.__class__.PIP_MODULE_NAME):
                continue
            latest_version=minfo.get('version', "0.0.0")

        if self.__class__.version_compare(self.__class__.VERSION, latest_version)<0 or force_install:
            orig_path = self.path_invoked.resolve()
            if orig_path.name != self.__class__.ENTYTY_FILE_NAME:
                sys.stderr.write("[%s.%s:%d] selfupdate: Current version=='%s', Latest version=='%s', Force install?: %s \n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno,
                                  self.__class__.VERSION, latest_version, str(force_install)))
                raise ValueError("Filename is not proper: '"+orig_path.name+"' != '"+self.__class__.ENTYTY_FILE_NAME+"'")

            if flg_verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] selfupdate: Current version=='%s', Latest version=='%s', Force install?: %s \n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno,
                                  self.__class__.VERSION, latest_version, str(force_install)))

            new_version_path = os.path.join(self.python_pip_path,
                                            self.__class__.PIP_MODULE_NAME.replace('-', '_'),
                                            self.__class__.ENTYTY_FILE_NAME)
            
            if not os.path.isfile(new_version_path):
                sys.stderr.write("[%s.%s:%d] selfupdate: Internal error: file not found: '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno,
                                  self.__class__.VERSION, latest_version, str(force_install)))
                raise FileNotFoundError("Is not file: "+new_version_path)

            bkup_path = self.__class__.rename_with_mtime_suffix(orig_path,
                                                                add_sufix=("-"+self.__class__.VERSION),
                                                                dest_dir=self.tmpdir,
                                                                verbose=flg_verbose,
                                                                dry_run=flg_dry_run)
            if flg_verbose or flg_dry_run:
                sys.stderr.write("[%s.%s:%d] selfupdate: Backup current file: '%s' --> '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, orig_path, bkup_path))
                                 
            if flg_verbose or flg_dry_run:
                sys.stderr.write("[%s.%s:%d] selfupdate: Copy file: '%s' --> '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, new_version_path, orig_path))
            if not flg_dry_run:
                shutil.copy2(new_version_path, orig_path, follow_symlinks=True)
                os.chmod(orig_path, mode=0o755, follow_symlinks=True)
        else:
            if flg_verbose:
                sys.stderr.write("[%s.%s:%d] selfupdate: skip (up-to-date) : Current version=='%s', Latest version=='%s', Force install?: %s \n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno,
                                  self.__class__.VERSION, latest_version, str(force_install)))

    def run_pip(self, subcmd:str, args=[], verbose=False, dry_run=False, **popen_kwargs):
        
        argprsrx = argparse.ArgumentParser(add_help=False, exit_on_error=False)
        argprsrx.add_argument('--isolated',  action='store_true')
        argprsrx.add_argument('--python',    default=str(self.python_use.absolute()))
        argprsrx.add_argument('--cache-dir', default=self.python_pip_cache)
        argprsrx.add_argument('--log',       default=self.python_pip_log_path)

        if subcmd == 'install':
            argprsrx.add_argument('-t', '--target', default=self.python_pip_path)
            argprsrx.add_argument('-s', '--src',    default=self.python_pip_src)
        elif subcmd == 'download':
            argprsrx.add_argument('-d', '--dest',   default=self.python_pip_path)
            argprsrx.add_argument('-s', '--src',    default=self.python_pip_src)
        elif subcmd in ('freeze', 'inspect', 'list'):
            argprsrx.add_argument('--path', default=self.python_pip_path)

        argsx, restx = argprsrx.parse_known_args(args)

        cmdargs = [ str(self.pip_use.absolute()) ]
        if argsx.isolated:
            cmdargs.append('--isolated')

        if self.__class__.version_compare(self.pip_vertion_str, "23.1")>=0:
            # python option is available for pip >= 23.1
            for opt in ['python']:
                if not hasattr(argsx, opt.replace('-', '_')):
                    continue
                cmdargs.extend(['--'+opt.replace('_', '-'), getattr(argsx,opt.replace('-', '_')) ] )

        cmdargs.append(subcmd)

        for opt in ['cache-dir', 'log', 'target', 'src', 'dest', 'path']:
            if not hasattr(argsx, opt.replace('-', '_')):
                continue
            cmdargs.extend(['--'+opt.replace('_', '-'), getattr(argsx,opt.replace('-', '_')) ] )

        cmdargs.extend(restx)

        if verbose or dry_run:
            sys.stderr.write("[%s.%s:%d] Exec: '%s'\n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, (" ".join(cmdargs))))
        if not dry_run:
            return subprocess.run(cmdargs, shell=False,
                                  encoding=self.encoding, **popen_kwargs)

    def run_script(self, script:str, args:list=[]):
        os.environ['PYTHONPATH'] = "%s:%s:%s" % (self.python_path,
                                                 self.python_pip_path,
                                                 os.environ.get('PYTHONPATH',''))

        if script is None:
            cmd_args = [self.python_use ] + args
        elif isinstance(script, str) and script and os.path.isfile(script):
            cmd_args = [self.python_use, script ] + args
        else:
            script_path = os.path.join(self.python_path, script if script.endswith('.py') else script+'.py')
            
            if os.path.isdir(script_path):
                sys.stderr.write("[%s.%s:%d] Error: '%s' is directory\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, script_path))
                raise IsADirectoryError()
            elif not os.path.isfile(script_path):
                sys.stderr.write("[%s.%s:%d] Error: File not found '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, script_path))
                raise FileNotFoundError()

            cmd_args = [self.python_use, script_path ] + args

        if self.verbose:
            sys.stderr.write("[%s.%s:%d] Exec: '%s' with PYTHONPATH='%s'\n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, 
                              "".join(cmd_args), os.environ['PYTHONPATH']))
        sys.stdout.flush()
        sys.stderr.flush()
        os.execvpe(cmd_args[0], cmd_args, os.environ)


    def description(self):
        return "%s (Version: %s : %s)" % (self.__class__.PIP_MODULE_NAME, 
                                          self.__class__.VERSION, 
                                          pathlib.Path(__file__).resolve())

    def show_info(self, args:argparse.Namespace, rest:list=[]):

        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_long    = args.long    if hasattr(args, 'long')    else False

        if not(flg_verbose or flg_long):
            print(self.description())
            return

        print("Description            : ", self.description())
        print("Python command         : ", str(self.python_use))
        print("Python select          : ", self.python_select)
        print("Python full path       : ", self.python_use.absolute())
        print("Command invoked        : ", self.path_invoked, "(LINK? : ", self.flg_symlink, ")")
        print("This file              : ", __file__)
        print("(source)               : ", pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve())
        print("Top of work directory  : ", self.prefix)
        print("bin directory          : ", self.bindir)
        print("var directory          : ", self.vardir)
        print("src directory          : ", self.srcdir)
        print("tmp directory          : ", self.tmpdir)
        print("log directory          : ", self.logdir)
        print("script directory       : ", self.python_path)
        print("python module directory: ", self.python_pip_path)
        print("PIP command            : ", str(self.pip_use))
        print("PIP full path          : ", self.pip_use.absolute())
        print("PIP cache directory    : ", self.python_pip_cache)
        print("PIP src directory      : ", self.python_pip_src)
        print("PIP log directory      : ", self.python_pip_logdir)
        print("PIP log path           : ", self.python_pip_log_path)
        print("Python shebang         : ", self.python_shebang)

    def pkg_dir_list(self):
        return [self.prefix, self.bindir, self.vardir, 
                self.srcdir, self.tmpdir, self.logdir, self.python_path]

    def pip_dir_list(self):
        return [self.python_pip_path, self.python_pip_cache,
                self.python_pip_src, self.python_pip_logdir]

    def all_dir_list(self):
        return self.pkg_dir_list() + self.pip_dir_list()

    def make_directory_structure(self, dry_run=False, verbose=False):
        # Make directory structure 
        for dd in self.all_dir_list():
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] mkdir -p : '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, dd))
            if not dry_run:
                os.makedirs(dd, mode=0o755, exist_ok=True)
        return

    def put_this_into_structure(self, flg_move=False, dry_run=False, verbose=False):

        #orig_path   = pathlib.Path(__file__).resolve() # self.path_invoked.absolute().name
        orig_path   = pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve()
        script_dest = os.path.join(self.bindir, orig_path.name)
        
        if os.path.exists(script_dest):
            if filecmp.cmp(orig_path, script_dest, shallow=False):
                if verbose:
                    sys.stderr.write("[%s.%s:%d] Warning : same file already exists: '%s'\n" %
                                     (self.__class__.__name__, 
                                      inspect.currentframe().f_code.co_name,
                                      inspect.currentframe().f_lineno, script_dest))
            else:
                sys.stderr.write("[%s.%s:%d] Error : (different) file already exists: '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, script_dest))
                # raise FileExistsError
            return
        else:
            # Copy script into bindir 
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] %s '%s' '%s' \n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno,
                                  'mv -i' if flg_move else 'cp -ai',
                                  orig_path, script_dest))
            if not dry_run:
                if flg_move:
                    try:
                        os.rename(orig_path, script_dest)
                    except OSError:
                        shutil.move(orig_path, script_dest)
                    except Exception as e:
                        sys.stderr.write("[%s.%s:%d] Error: Can not meve : '%s' --> '%s' \n" %
                                         (self.__class__.__name__, 
                                          inspect.currentframe().f_code.co_name,
                                          inspect.currentframe().f_lineno,
                                          orig_path, script_dest))
                        raise(e)
                else:
                    shutil.copy2(orig_path, script_dest, follow_symlinks=True)
                    os.chmod(script_dest, mode=0o755, follow_symlinks=True)
        return

    def mksymlink_this_in_structure(self, link_name, strip_py=True,
                                    dry_run=False, verbose=False):
        #entiry_name = self.path_invoked.resolve().name
        #entiry_name = pathlib.Path(__file__).resolve().name
        entiry_name = pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name
        link_dest   = os.path.join(self.bindir, 
                                   link_name.removesuffix('.py')
                                   if strip_py and link_name.endswith('.py') else link_name)

        if os.path.exists(link_dest):
            if pathlib.Path(link_dest).resolve() == self.path_invoked.absolute():
                sys.stderr.write("[%s.%s:%d] Symbolic link already exists: '%s' --> '%s' \n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, link_dest, entiry_name))
            else:
                sys.stderr.write("[%s.%s:%d] (different) Symbolic link already exists: '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, link_dest))
                #raise FileExistsError
            return

        if verbose or dry_run:
            sys.stderr.write("[%s.%s:%d] make symbolic link : '%s' --> '%s' \n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, link_dest, entiry_name))
        if not dry_run:
            os.symlink(entiry_name, link_dest)


    @classmethod
    def rename_with_mtime_suffix(cls, file_path, add_sufix=None, dest_dir=None, verbose=False, dry_run=False):
        if not os.path.exists(file_path):
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] File not found : '%s' \n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, file_path))
            return None

        mtime  = os.path.getmtime(file_path)
        tmstmp = datetime.datetime.fromtimestamp(mtime).strftime("%Y%m%d_%H%M%S")

        bn, ext = os.path.splitext(os.path.basename(file_path))
        dest = os.path.dirname(file_path) if dest_dir is None else dest_dir
        
        if isinstance(add_sufix,str) and add_sufix:
            new_path = os.path.join(dest, ("%s%s.%s%s" % (bn, add_sufix, tmstmp, ext)))
        else:
            new_path = os.path.join(dest, ("%s.%s%s" % (bn, tmstmp, ext)))

        if not os.path.isdir(dest):
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] Make directory: '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, dest))
            if not dry_run:
                os.makedirs(dest, exist_ok=True)

        if verbose or dry_run:
            sys.stderr.write("[%s.%s:%d] Move file: '%s' --> '%s'\n" %
                             (cls.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, file_path, new_path))
        if not dry_run:
            try:
                os.rename(file_path, new_path)
            except OSError:
                shutil.move(file_path, new_path)
            except Exception as e:
                sys.stderr.write("[%s.%s:%d] Error: Can not rename file '%s' --> '%s': %s\n" %
                                 (cls.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, file_path, new_path, str(e)))
                return None

        return new_path

    @classmethod
    def remove_dircontents(cls, path_dir:str, 
                           dir_itself:bool=False,
                           verbose:bool=False, dry_run:bool=False):
        pdir = pathlib.Path(path_dir)

        if ((pdir.is_file() or pdir.is_symlink() )
            and ( not pdir.name.startswith('.'))):
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] Remove file or symblic-link: '%s'\n" %
                                 (cls.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, str(pdir)))
            if not dry_run:
                try:
                    pdir.unlink()
                except Exception as e:
                    sys.stderr.write("[%s.%s:%d] Error: removin file or symblic-link: '%s' : %s\n" %
                                     (cls.__name__, 
                                      inspect.currentframe().f_code.co_name,
                                      inspect.currentframe().f_lineno, str(pdir), str(e)))
                    # raise(e)
        elif (pdir.is_dir() and (not pdir.name.startswith('.'))):

            if dir_itself:

                if verbose or dry_run:
                    sys.stderr.write("[%s.%s:%d] Remove directory: '%s'\n" %
                                     (cls.__name__, 
                                      inspect.currentframe().f_code.co_name,
                                      inspect.currentframe().f_lineno, str(pdir)))
                if not dry_run:
                    shutil.rmtree(pdir)

            else:
                for ifp in pdir.iterdir():
                    if ifp.name.startswith('.'):
                        continue
                    if verbose or dry_run:
                        sys.stderr.write("[%s.%s:%d] Remove file or symblic-link: '%s'\n" %
                                         (cls.__name__, 
                                          inspect.currentframe().f_code.co_name,
                                          inspect.currentframe().f_lineno, str(ifp)))

                    if not dry_run:
                        try:
                            if ifp.is_file() or ifp.is_symlink():
                                ifp.unlink()
                            elif ifp.is_dir():
                                shutil.rmtree(ifp)
                        except Exception as e:
                            sys.stderr.write("[%s.%s:%d] Error: removing file or symblic-link: '%s' : %s\n" %
                                             (cls.__name__, 
                                              inspect.currentframe().f_code.co_name,
                                              inspect.currentframe().f_lineno, str(ifp), str(e)))
                            # raise(e)
        else:
            sys.stderr.write("[%s.%s:%d] Error: Unknown file type: '%s'\n" %
                             (cls.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, pdir.name))
            # raise(NotADirectoryError)

    def clean_env(self, args:argparse.Namespace, rest:list=[]):
        subcmd = args.subcommand if hasattr(args, 'subcommand') else 'unknown'
        
        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_dry_run = args.dry_run if hasattr(args, 'dry_run') else False

        rmlist = []
        if subcmd == 'distclean':
            rmlist.extend(self.git_keepdirs)
        else:
            rmlist.extend(self.pip_dir_list())
            rmlist.append(self.tmpdir)
            
        if flg_verbose or flg_dry_run:
            sys.stderr.write("[%s.%s:%d] %s : '%s'\n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, subcmd, ", ".join(rmlist)))
        for pdir in rmlist:
            self.__class__.remove_dircontents(path_dir=pdir, 
                                              dir_itself=False,
                                              verbose=flg_verbose, dry_run=flg_dry_run)

    def check_git_config_value(self, key='user.email', mode='--global'):
        try:
            result = subprocess.run([self.git_path, 'config', mode, '--get', key],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            value = result.stdout.strip()
            return bool(value)
        except subprocess.CalledProcessError:
            return False

    def setup_git(self, git_user=None, git_email=None, git_url=None, verbose=False, dry_run=False, origin=True):
        dot_git_path = os.path.join(self.prefix, '.git')
        if os.path.exists(dot_git_path):
            if verbose:
                sys.stderr.write("[%s.%s:%d] : Directory already exists: '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, dot_git_path))
                return

        git_commands = []
        
        git_commands.append([self.git_path, 'init', self.prefix])

        if isinstance(git_user, str) and git_user:
            git_commands.append([self.git_path, 'config',
                                 '--file', os.path.join(dot_git_path, 'config'),
                                 'user.name', git_user])
        elif not self.check_git_config_value(key='user.name', mode='--global'):
            git_commands.append([self.git_path, 'config',
                                 '--file', os.path.join(dot_git_path, 'config'),
                                 'user.name', getpass.getuser()])

        if isinstance(git_email, str) and git_email:
            git_commands.append([self.git_path, 'config',
                                 '--file', os.path.join(dot_git_path, 'config'),
                                 'user.email', git_email])
        elif not self.check_git_config_value(key='user.email', mode='--global'):
            git_commands.append([self.git_path, 'config',
                                 '--file', os.path.join(dot_git_path, 'config'),
                                 'user.email', getpass.getuser()+'@'+socket.gethostname()])
            
        if isinstance(git_url, str) and git_url:
            git_commands.append([self.git_path, 
                                 '--git-dir', dot_git_path, '--work-tree', self.prefix, 
                                 'remote', 'add', ('origin' if origin else 'upstream'), git_url])
            git_commands.append([self.git_path, 'config',
                                 '--file', os.path.join(dot_git_path, 'config'),
                                 'push.default', current])

        for _gitcmd in git_commands:
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] : Exec : '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                inspect.currentframe().f_lineno, " ".join(_gitcmd)))
            if not dry_run:
                gitcmdio = subprocess.run(_gitcmd, encoding=self.encoding, 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if verbose:
                    sys.stdout.write("[%s.%s:%d] git output : '%s'\n" %
                                     (self.__class__.__name__, 
                                      inspect.currentframe().f_code.co_name,
                                      inspect.currentframe().f_lineno, gitcmdio.stdout))
                    sys.stderr.write("[%s.%s:%d] git stderr : '%s'\n" %
                                     (self.__class__.__name__, 
                                      inspect.currentframe().f_code.co_name,
                                      inspect.currentframe().f_lineno, gitcmdio.stderr)) 

    def manage_env(self, args:argparse.Namespace, rest:list=[]):

        subcmd      = args.subcommand if hasattr(args, 'subcommand') else 'unknown'

        self.set_python_path(python_cmd=(args.python if (hasattr(args, 'python') and
                                                         args.python is not None) else self.python_select),
                             pip_cmd=(args.pip if (hasattr(args, 'pip') and
                                                   args.pip is not None) else str(self.pip_use)),
                             prefix_cmd=( args.prefix if (hasattr(args, 'prefix') and
                                                          args.prefix  is not None) else self.prefix))

        if hasattr(args, 'git') and (args.git is not None):
            self.set_git_path(git_cmd=args.git)

        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_dry_run = args.dry_run if hasattr(args, 'dry_run') else False

        flg_move   = args.move   if hasattr(args, 'move')   else False
        flg_git    = args.git    if hasattr(args, 'git')    else False
        flg_readme = args.readme if hasattr(args, 'readme') else False
        title      = args.title  if hasattr(args, 'title')  else str(pathlib.Path(self.prefix).name)
        
        modules   = args.module      if hasattr(args, 'module')     else []
        scrptlibs = args.script_lib  if hasattr(args, 'script_lib') else []
        scripts   = args.scriptnames if hasattr(args, 'scriptnames') else []


        git_user   = args.git_user               if hasattr(args, 'git_user')         else None
        git_email  = args.git_email              if hasattr(args, 'git_email')        else None
        git_url    = args.git_remote_url         if hasattr(args, 'git_remote_url')   else None
        git_origin = (not args.git_set_upstream) if hasattr(args, 'git_set_upstream') else True

        if hasattr(args, 'std_script_lib') and args.std_script_lib:
            for _scrlib in self.__class__.SCRIPT_STD_LIB.keys():
                if _scrlib in scrptlibs or (_scrlib+'.py') in scrptlibs:
                    continue
                scrptlibs.append(_scrlib)

        for _scrlib in scrptlibs:
            _scrlib_info = self.__class__.SCRIPT_STD_LIB.get(_scrlib)
            if _scrlib_info is None:
                continue
            for _dep in _scrlib_info.get('depends', []):
                if _dep in scrptlibs:
                    continue
                scrptlibs.append(_dep)

        for _scrlib in scrptlibs:
            _scrlib_info = self.__class__.SCRIPT_STD_LIB.get(_scrlib)
            if _scrlib_info is None:
                continue
            for _m in _scrlib_info.get('pip_module', []):
                if _m in modules:
                    continue
                modules.append(_m)

        keyword_buf = {}
        keyword_buf.update(self.__class__.FILENAME_DEFAULT)
        keyword_buf.update({
            '____TITLE____':              title,
            '____MNGSCRIPT_NAME____':     self.__class__.MNG_SCRIPT,
            '____AUTHOR_NAME____':        self.__class__.guess_git_username(),
            '____AUTHOR_EMAIL____':       self.__class__.guess_git_useremail(),
            '____py_shebang_pattern____': self.python_shebang,
        })

        if subcmd == 'init':

            self.make_directory_structure(dry_run=flg_dry_run, verbose=flg_verbose)

            self.put_this_into_structure(flg_move=flg_move, dry_run=flg_dry_run, verbose=flg_verbose)

            self.mksymlink_this_in_structure(self.__class__.MNG_SCRIPT, strip_py=True,
                                             dry_run=flg_dry_run, verbose=flg_verbose)

            if flg_git:

                self.make_gitignore_contents(os.path.join(self.prefix, '.gitignore'),
                                             encoding=self.encoding, dry_run=flg_dry_run, verbose=flg_verbose)
            
                self.put_gitkeep(dry_run=flg_dry_run, verbose=flg_verbose)
                self.setup_git(git_user=git_user, git_email=git_email, git_url=git_url,
                               verbose=flg_verbose, dry_run=flg_dry_run, origin=git_origin)


        if flg_readme:

            readme_path = self.update_readme(keywords=keyword_buf,
                                             bin_basenames=[x.removesuffix('.py') for x in scripts],
                                             lib_basenames=[x.removesuffix('.py') for x in scrptlibs],
                                             flg_git=flg_git, backup=False,
                                             verbose=flg_verbose, dry_run=flg_dry_run)

        self.add_pyscr(basename=[x.removesuffix('.py') for x in scripts],
                       keywords=keyword_buf, verbose=flg_verbose, dry_run=flg_dry_run)
                
        self.add_pylib(basename=[x.removesuffix('.py') for x in scrptlibs],
                       keywords=keyword_buf, verbose=flg_verbose, dry_run=flg_dry_run)

        if len(modules)>0:
            self.run_pip(subcmd='install', args=modules, verbose=flg_verbose, dry_run=flg_dry_run)

    def update_readme(self, keywords={}, bin_basenames=[], lib_basenames=[],
                      flg_git=False, backup=False, verbose=False, dry_run=False):

        readme_path = os.path.join(self.prefix,
                                   self.__class__.FILENAME_DEFAULT.get('____README_NAME____', 'README.md'))

        readme_updater = self.ReadMeUpdater(ref_pycan=self,
                                            keywords=keywords, 
                                            bin_basenames=bin_basenames, 
                                            lib_basenames=lib_basenames,
                                            flg_git=flg_git)
        if os.path.exists(readme_path):
            readme_bkup = self.__class__.rename_with_mtime_suffix(readme_path,
                                                                  dest_dir=self.tmpdir,
                                                                  verbose=verbose,
                                                                  dry_run=dry_run)
            if readme_bkup is None:
                if verbose or dry_run:
                    sys.stderr.write("[%s.%s:%d] : Save Readme file : '%s'\n" %
                                     (self.__class__.__name__, 
                                      inspect.currentframe().f_code.co_name,
                                      inspect.currentframe().f_lineno, readme_path))
                if not dry_run:
                    readme_updater.save_readme_contents(output=readme_path, format_alist=keywords)
            else:
                buf = readme_updater.proc_file(in_file=readme_bkup, 
                                               out_file=readme_path, encoding=self.encoding,
                                               verbose=verbose, dry_run=dry_run)
        else:
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] : Save Readme file : '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, readme_path))
            if not dry_run:
                readme_updater.save_readme_contents(output=readme_path, format_alist=keywords)


    def add_pyscr(self, basename, keywords={}, verbose=False, dry_run=False):
        if isinstance(basename, list):
            for bn in basename:
                self.add_pyscr(bn, keywords=keywords, verbose=verbose, dry_run=dry_run)
            return

        scr_path = os.path.join(self.python_path, basename+'.py')
        if os.path.exists(scr_path):
            sys.stderr.write("[%s.%s:%d] : Warning: File already exists (Skipped) : '%s'\n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, scr_path))
        else:
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] : Preparing python library file from template : '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, scr_path))
                
            if not dry_run:
                str_format={'____SCRIPT_NAME____': basename if basename.endswith('.py') else basename+'.py'}
                str_format.update(keywords)

                code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=str_format)

                self.__class__.EmbeddedText.extract_to_file(outfile=scr_path,infile=None,
                                                            s_marker=r'\s*#{5,}\s*____PY_MAIN_TEMPLATE_START____\s*#{5,}',
                                                            e_marker=r'\s*#{5,}\s*____PY_MAIN_TEMPLATE_END____\s*#{5,}',
                                                            include_markers=False, multi_match=False,dedent=True, 
                                                            skip_head_emptyline=True, skip_tail_emptyline=True,
                                                            dequote=False, format_filter=code_filter, 
                                                            open_mode='w', encoding=self.encoding)
                os.chmod(scr_path, mode=0o755)


        bin_path = os.path.join(self.bindir, basename)
        if os.path.exists(bin_path):
            sys.stderr.write("[%s.%s:%d] : Warning: File already exists (Skipped) : '%s'\n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, bin_path))
        else:
            self.mksymlink_this_in_structure(basename, strip_py=True,
                                             dry_run=dry_run, verbose=verbose)


    def add_pylib(self, basename, keywords={}, verbose=False, dry_run=False):
        if isinstance(basename, list):
            for bn in basename:
                self.add_pylib(bn, keywords=keywords, verbose=verbose, dry_run=dry_run)
            return

        scr_path = os.path.join(self.python_path, basename+'.py')
        if os.path.exists(scr_path):
            sys.stderr.write("[%s.%s:%d] : Warning: File already exists (Skipped) : '%s'\n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, scr_path))
        else:
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] : Preparing python library file from template : '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, scr_path))
                
            gen_fuction = self.__class__.SCRIPT_STD_LIB.get(basename,{}).get('creator')

            
            if not dry_run:
                if callable(gen_fuction):
                    gen_fuction(scr_path, keywords=keywords, shebang=self.python_shebang)
                else:
                    str_format = {'____NEW_CLS_NAME____': basename}
                    str_format.update(keywords)
                    code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=str_format)

                    self.__class__.EmbeddedText.extract_to_file(outfile=scr_path, infile=None,
                                                                s_marker=r'\s*#{5,}\s*____PY_LIB_SCRIPT_TEMPLATE_START____\s*#{5,}',
                                                                e_marker=r'\s*#{5,}\s*____PY_LIB_SCRIPT_TEMPLATE_END____\s*#{5,}',
                                                                include_markers=False, multi_match=False,dedent=True, 
                                                                skip_head_emptyline=True, skip_tail_emptyline=True,
                                                                dequote=False, format_filter=code_filter, 
                                                                open_mode='w', encoding=self.encoding)

    def make_gitignore_contents(self, output_path,
                                dry_run=False, verbose=False, format_alist={}, **format_args):

        if os.path.exists(output_path):
            if verbose:
                sys.stderr.write("[%s.%s:%d] Warning File exists : skip : '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, output_path))
            return

        if verbose or dry_run:
            sys.stderr.write("[%s.%s:%d] .gitignore : '%s'\n" %
                             (self.__class__.__name__, 
                              inspect.currentframe().f_code.co_name,
                              inspect.currentframe().f_lineno, output_path))
        if not dry_run:
            str_format={'____GIT_DUMMYFILE____': 
                        self.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'] }

            str_format['____GIT_INGORE_DIRS____'] = ""
            for _gitkpdir in self.git_keepdirs:
                str_format['____GIT_INGORE_DIRS____'] += ("%s/*\n" % (_gitkpdir, ))
            str_format['____GIT_INGORE_DIRS____'].rstrip()
            str_format.update(format_alist)
            str_format.update(**format_args)
            
            text_filter = self.__class__.EmbeddedText.FormatFilter(format_variables=str_format)

            self.__class__.EmbeddedText.extract_to_file(outfile=output_path, infile=None,
                                                        s_marker=r'\s*#{5,}\s*____GITIGNORE_TEMPLATE_START____\s*#{5,}',
                                                        e_marker=r'\s*#{5,}\s*____GITIGNORE_TEMPLATE_END____\s*#{5,}',
                                                        include_markers=False, multi_match=False,dedent=True, 
                                                        skip_head_emptyline=True, skip_tail_emptyline=True,
                                                        dequote=True, format_filter=text_filter, 
                                                        open_mode='w', encoding=self.encoding)
            os.chmod(output_path, mode=0o644)


    def put_gitkeep(self, dry_run=False, verbose=False):
        for d in self.git_keepdirs: # not self.pip_dir_list():
            dp = os.path.join(d, self.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'])
            
            if os.path.exists(dp):
                if verbose:
                    sys.stderr.write("[%s.%s:%d] Warning File exists : skip : '%s'\n" %
                                     (self.__class__.__name__, 
                                      inspect.currentframe().f_code.co_name,
                                      inspect.currentframe().f_lineno, dp))
                continue
            if verbose or dry_run:
                sys.stderr.write("[%s.%s:%d] put %s in '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno,
                                  self.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'], d))
            if not dry_run:
                pathlib.Path(dp).touch(mode=0o644, exist_ok=True)

    @classmethod
    def guess_git_username(cls):
        gitcmd = os.environ.get('GIT', 'git')
        
        gitcmdio = subprocess.run([gitcmd, 'config', '--local', '--get', 'user.name'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        gitcmdio = subprocess.run([gitcmd, 'config', '--global', '--get', 'user.name'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        return getpass.getuser().rstrip(os.linesep)

    @classmethod
    def guess_git_useremail(cls):
        gitcmd = os.environ.get('GIT', 'git')
        
        gitcmdio = subprocess.run([gitcmd, 'config', '--local', '--get', 'user.email'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        gitcmdio = subprocess.run([gitcmd, 'config', '--global', '--get', 'user.email'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        return (getpass.getuser()+'@'+socket.gethostname()).rstrip(os.linesep)


    class ReadMeUpdater(object):
        CNTNTS_HD_MRKR  = re.compile(r"^ *- *Contents:")
        CNTNTS_TL_MRKR  = re.compile(r"^ *- *Usage.*:")
        CNTNTS_IDX_MRKR = re.compile(r"^ +(?P<index>[0-9]+)\. +(?P<file_path>[^\b][^:]+) *: *(?P<desc>\S.*)$")
        GITIGNORE_RE    = re.compile(r"\.gitignore")
        USAGE_RE        = CNTNTS_TL_MRKR
        
        def __init__(self, ref_pycan, keywords={}, bin_basenames=[], lib_basenames=[], flg_git:bool=False):
            self.ref_pycan = ref_pycan
            self.keywords=keywords
            self.bin_basenames=bin_basenames
            self.lib_basenames=lib_basenames

            self.bin_subdir       = self.ref_pycan.bindir.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.python_subdir    = self.ref_pycan.python_path.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_subdir       = self.ref_pycan.python_pip_path.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_cache_subdir = self.ref_pycan.python_pip_cache.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_src_subdir   = self.ref_pycan.python_pip_src.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_log_subdir   = self.ref_pycan.python_pip_logdir.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.gitkeep_subdirs  = [ x.removeprefix(self.ref_pycan.prefix).removeprefix('/') for x in self.ref_pycan.git_keepdirs ]

            self.flg_git=flg_git

        def update_keywords(self, text):
            for k,v in self.keywords.items():
                text = text.replace(k, v)
            return text

        def proc_file(self, in_file=None, in_text='', out_file=None, encoding="utf-8", verbose=False, dry_run=False):
            if verbose or dry_run:
                if in_file is None:
                    msg = "Read from text: '%s%s'" % (in_text[:20], "..." if len(in_text)>20 else '')
                else:
                    msg = "Read from file: '%s'"   % (in_file)

                sys.stderr.write("[%s.%s:%d] Read from text: '%s'\n" %
                                 (self.__class__.__name__, 
                                  inspect.currentframe().f_code.co_name,
                                  inspect.currentframe().f_lineno, msg))
            fin = (io.StringIO(initial_value=in_text, encoding=encoding) 
                   if in_file is None else open(in_file, encoding=encoding) )
            fout = (io.StringIO(encoding=encoding)
                    if (dry_run or out_file is None)
                    else open(out_file, "w", encoding=encoding))

            for line in self.process_lines(fin):
                if (dry_run) and (out_file is not None):
                    continue
                fout.write(line)
            fin.close()
            if out_file is None:
                return fout.getvalue()
            else:
                fout.close()
                        
        def process_lines(self, lines: typing.Iterator[str]) -> typing.Iterator[str]:
            fidx, flg_added, flg_in_range = (0, False, False)
            file_listed = {}

            for raw in lines:
                line = self.update_keywords(raw.rstrip("\n"))

                if self.__class__.CNTNTS_HD_MRKR.match(line):
                    flg_in_range = True
                if self.__class__.CNTNTS_TL_MRKR.match(line):
                    if ( (not flg_added) and (self.__class__.USAGE_RE.match(line))):
                        block, fidx = self.make_additional_block(fidx, file_listed)
                        for b in block:
                            yield b
                        yield "\n"
                        added = True
        
                    flg_in_range = False
        
                if flg_in_range:
                    f_match=self.__class__.CNTNTS_IDX_MRKR.match(line)
                    if f_match:
                        fidx += 1
                        line = "  %-3s %-42s %s" % ( ("%d." % (fidx,)),
                                                     f_match.group('file_path')+":",
                                                     f_match.group('desc'))
                        file_listed[f_match.group('file_path')] = f_match.group('index')
        
                if flg_in_range and self.__class__.CNTNTS_TL_MRKR.match(line):
                    in_range = False
        
                yield line + "\n"

        def make_additional_block(self, start_idx:int, file_listed:dict) -> tuple[list[str], int]:
            buf = []
            f = start_idx

            for bn in self.bin_basenames:
                scr_subpath = os.path.join(self.python_subdir,bn+'.py')
                if not scr_subpath in file_listed.keys():
                    f += 1
                    buf.append("  %-3s %-42s Example Python script that use modules\n" % ("%d." % (f,), scr_subpath+':'))

                bin_subpath = os.path.join(self.bin_subdir, bn)
                if not bin_subpath in file_listed.keys():
                    f += 1
                    # buf.append("  %-3s %-42s Symbolic link to %s to invoke %s.py.\n" % ("%d." % (f,), bin_subpath+':', 
                    #                                                                     os.path.basename(__file__), bn))
                    buf.append("  %-3s %-42s Symbolic link to %s to invoke %s.py.\n"
                               % ("%d." % (f,), bin_subpath+':', 
                                  pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name, bn))

            for bn in self.lib_basenames:
                scr_subpath = os.path.join(self.python_subdir, bn+'.py')
                if scr_subpath in file_listed.keys():
                    continue
                f += 1
                buf.append("  %-3s %-42s Python Library script used in this package\n" % ("%d." % (f,), scr_subpath+':'))

            return buf, f

        def save_readme_contents(self, output, bin_basenames=None, lib_basenames=None, gitkeepdirs=None, format_alist={}, **format_args):

            str_format={'____GIT_DUMMYFILE____':        self.ref_pycan.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'],
                        '____TITLE____' :               'Project Title',
                        '____README_NAME____':          self.ref_pycan.__class__.FILENAME_DEFAULT.get('____README_NAME____', 'README.md'),
                        '____MNGSCRIPT_NAME____':       self.ref_pycan.__class__.FILENAME_DEFAULT.get('MNG_SCRIPT',          'pycan_mng'),
                        '____BIN_PATH____':             str(self.bin_subdir),
                        '____PYLIB_PATH____':           str(self.python_subdir),
                        '____PIP_PATH____':             str(self.pip_subdir),
                        '____PIP_CACHE____':            str(self.pip_cache_subdir),
                        '____PIP_SRC____':              str(self.pip_src_subdir),
                        '____PIP_LOG____':              str(self.pip_log_subdir),
                        '____SHSCRIPT_ENTITY_NAME____':
                        pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name, # os.path.basename(__file__),
                        '____AUTHOR_NAME____':          'Auther Name',
                        '____AUTHOR_EMAIL____':         'Auther-email-address',
                        '____GIT_DUMMY_LISTS____':      "\n",
                        '____SCRIPT_DESC____':          "\n",
                        '____LIBFILE_DESC____':         "\n"
                        }
            str_format.update(format_alist)
            str_format.update(**format_args)

            bin_bns = bin_basenames if isinstance(bin_basenames, list) else self.bin_basenames
            lib_bns = lib_basenames if isinstance(lib_basenames, list) else self.lib_basenames
            git_kds = gitkeepdirs   if isinstance(gitkeepdirs, list)   else self.gitkeep_subdirs

            dummy_desc   = str_format.get('____GIT_DUMMY_LISTS____', "\n")
            script_desc  = str_format.get('____SCRIPT_DESC____', "\n")
            libfile_desc = str_format.get('____LIBFILE_DESC____', "\n")

            contents_list = []
            contents_list.append([str_format['____README_NAME____'],
                                  "This file"])
            contents_list.append([os.path.join(str_format['____BIN_PATH____'],
                                               str_format['____MNGSCRIPT_NAME____']),
                                  "Symblic link to '"
                                  +str_format['____SHSCRIPT_ENTITY_NAME____']
                                  +" for installing Python modules by pip locally."])
            contents_list.append([os.path.join(str_format['____BIN_PATH____'],
                                               str_format['____SHSCRIPT_ENTITY_NAME____']),
                                  "Wrapper python script to invoke Python script. (Entity)"])
            contents_list.append([str_format['____PIP_PATH____'],  "Directory where python modules are stored"])
            contents_list.append([str_format['____PIP_CACHE____'], "Cache directory for module installation by pip"])
            contents_list.append([str_format['____PIP_SRC____'],   "Source directory for module installation for pip"])
            contents_list.append([str_format['____PIP_LOG____'],   "Log directory for module installation for pip"])
            contents_list.append("\n")

            if self.flg_git:
                contents_list.append([".gitignore", "Git-related file"])
                git_keepdir_desc = "Git-related file to keep modules directory in repository."
                for _gitkd in git_kds:
                    contents_list.append([os.path.join(_gitkd, str_format['____GIT_DUMMYFILE____']),
                                          git_keepdir_desc])
                    git_keepdir_desc = 'a ditto'
                contents_list.append("\n")

            for _scr in bin_bns:
                _scr_bn = _scr.removesuffix('.py')
                contents_list.append([os.path.join(self.python_subdir, _scr_bn+'.py'),
                                      "Example Python script that use modules"])
                contents_list.append([os.path.join(self.bin_subdir, _scr_bn),
                                      ( "Symbolic link to '%s' to invoke %s.py." 
                                        % (str_format['____SHSCRIPT_ENTITY_NAME____'], _scr_bn))])
                #contents_list.append("\n")

            lib_desc_default = 'Example Python module file by template'
            for _lib in lib_bns:
                _lib_bn   = _lib.removesuffix('.py')
                _lib_desc = ( self.ref_pycan.__class__.SCRIPT_STD_LIB.get(_lib_bn,{'description': lib_desc_default}).get('description') 
                              if _lib_bn in self.ref_pycan.__class__.SCRIPT_STD_LIB.keys() else None)
                if _lib_desc is None:
                    _lib_desc = lib_desc_default
                contents_list.append([("%s.py" % (os.path.join(self.python_subdir,_lib_bn),)),
                                      _lib_desc])

            contents_lines = ""
            desc_idx=0
            for descinfo in contents_list:
                if (isinstance(descinfo,(list, tuple)) and 
                    isinstance(descinfo[0], str) and descinfo[0]):
                    contents_lines += "  %-3s %-42s %s\n" % (("%d." % (desc_idx+1,)),
                                                             ("%s:" % (descinfo[0],)),
                                                             (str(descinfo[1]) if len(descinfo)>1 else '' ))
                    desc_idx += 1
                else:
                    contents_lines += (descinfo if isinstance(descinfo,str) else "")

            str_format.update({'____contents_lines____': contents_lines.rstrip(os.linesep)})

            text_filter = self.ref_pycan.__class__.EmbeddedText.FormatFilter(format_variables=str_format)

            self.ref_pycan.__class__.EmbeddedText.extract_to_file(outfile=output, infile=None,
                                                                  s_marker=r'\s*#{5,}\s*____README_TEMPLATE_START____\s*#{5,}',
                                                                  e_marker=r'\s*#{5,}\s*____README_TEMPLATE_END____\s*#{5,}',
                                                                  include_markers=False, multi_match=False,dedent=True, 
                                                                  skip_head_emptyline=True, skip_tail_emptyline=True,
                                                                  dequote=True, format_filter=text_filter, 
                                                                  open_mode='w', encoding=self.ref_pycan.encoding)
            os.chmod(output, mode=0o644)

    class PyCodeFilter(object):

        SHEBANG_PATTERN = re.compile(r'^\s*#+ *____py_shebang_pattern____ *#+ *(?=[\n\r]+)')
            
        def __init__(self, 
                     shebang,
                     keyword_table:dict=None, 
                     **cmd_args):
            self.shebang=shebang
            self.keyword_table  = keyword_table
            self.valid_keywords = (keyword_table is not None)
            if self.valid_keywords:
                self.keyword_table.update(cmd_args)
    
        def __call__(self, line:str)->str:
            if isinstance(self.shebang, str) and self.shebang:
                line = self.__class__.SHEBANG_PATTERN.sub(self.shebang, line, 1)
            if self.valid_keywords:
                for k,v in self.keyword_table.items():
                    line = line.replace(str(k), str(v))
            return line

    def python_pkg_cache_template_save(self, outputfile, keywords:dict={}, shebang:str=None):

        code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=keywords)

        self.__class__.EmbeddedText.extract_to_file(outfile=outputfile, infile=None,
                                                    s_marker=r'\s*#{5,}\s*____PKG_CACHE_TEMPLATE_START____\s*#{5,}',
                                                    e_marker=r'\s*#{5,}\s*____PKG_CACHE_TEMPLATE_END____\s*#{5,}',
                                                    include_markers=False, multi_match=False,dedent=True, 
                                                    skip_head_emptyline=True, skip_tail_emptyline=True,
                                                    dequote=False, format_filter=code_filter, 
                                                    open_mode='w', encoding=self.encoding)
        os.chmod(outputfile, mode=0o644)

    def python_intrinsic_format_template_save(self, outputfile, keywords:dict={}, shebang:str=None):

        code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=keywords)

        self.__class__.EmbeddedText.extract_to_file(outfile=outputfile, infile=None,
                                                    s_marker=r'\s*#{5,}\s*____INTRINSIC_FORMATTER_TEMPLATE_START____\s*#{5,}',
                                                    e_marker=r'\s*#{5,}\s*____INTRINSIC_FORMATTER_TEMPLATE_END____\s*#{5,}',
                                                    include_markers=False, multi_match=False,dedent=True, 
                                                    skip_head_emptyline=True, skip_tail_emptyline=True,
                                                    dequote=False, format_filter=code_filter, 
                                                    open_mode='w', encoding=self.encoding)
        os.chmod(outputfile, mode=0o644)

    class EmbeddedText(object):
    
        HEADSPACE   = re.compile(r'^(?P<indent>\s*).*')
        EMPTYLINE   = re.compile(r'^\s*$')
        TRIPLEQUATE = re.compile(r"^\s*(?P<triplequote>'{3}|\"{3})(?P<rest>.*)$")
    
        class FormatFilter(object):
            
            def __init__(self, 
                         keyword_table:dict=None, 
                         format_variables:dict=None,
                         **cmd_args):
                self.keyword_table    = keyword_table
                self.format_variables = format_variables
                self.flg_filters      = (isinstance(self.keyword_table,dict),
                                         isinstance(self.format_variables,dict))
                if self.flg_filters[0]:
                    self.keyword_table.update(cmd_args)
                if self.flg_filters[1]:
                    self.format_variables.update(cmd_args)
    
            def __call__(self, line:str)->str:
                if self.flg_filters[1]:
                    line = line.format(**self.format_variables)
                if self.flg_filters[0]:
                    for k,v in self.keyword_table.items():
                        line = line.replace(k, v)
                return line
    
        @classmethod
        def extract_raw(cls, lines: typing.Iterable[str],
                        s_marker:str=None, e_marker:str=None,
                        include_markers:bool=True, multi_match:bool=False,
                        dedent:bool=False, format_filter=None) -> typing.Iterator[str]:
    
            s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                        else ( re.compile(s_marker) 
                               if isinstance(s_marker, str) and s_marker else None))
            e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                         else ( re.compile(e_marker) 
                                if isinstance(e_marker, str) and e_marker else None))
    
            indent     = ''
            in_range = True if s_pttrn is None else False

            for line in lines:
                if not in_range:
                    if s_pttrn is None or s_pttrn.match(line):
                        if dedent:
                            m_indent = cls.HEADSPACE.match(line)
                            if m_indent:
                                indent = m_indent.group('indent')
                                line = line.removeprefix(indent)
                        in_range = True
                        if include_markers:
                            yield format_filter(line) if callable(format_filter) else line
                else:
                    line = line.removeprefix(indent)
                    if e_pttrn is None:
                        yield format_filter(line) if callable(format_filter) else line
                    elif e_pttrn.match(line):
                        if include_markers:
                            yield format_filter(line) if callable(format_filter) else line
                        if multi_match and s_pttrn is not None:
                            in_range   = False
                            indent     = ''
                        else:
                            return
                    else:
                        yield format_filter(line) if callable(format_filter) else line
    
        @classmethod
        def extract_dequote(cls, lines: typing.Iterable[str],
                            s_marker:str=None, e_marker:str=None,
                            include_markers:bool=True, multi_match:bool=False,
                            dedent:bool=False, dequote:bool=True, 
                            format_filter=None) -> typing.Iterator[str]:
    
            s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                        else ( re.compile(s_marker) 
                               if isinstance(s_marker, str) and s_marker else None))
            e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                         else ( re.compile(e_marker) 
                                if isinstance(e_marker, str) and e_marker else None))
    
            quote_mrkr = ''
            for line in cls.extract_raw(lines=lines,
                                        s_marker=s_pttrn,
                                        e_marker=e_pttrn,
                                        include_markers=include_markers,
                                        multi_match=multi_match,
                                        dedent=dedent,
                                        format_filter=format_filter):
                if dequote:
                    if quote_mrkr:
                        pos = line.find(quote_mrkr)
                        if pos>=0:
                            line = line[0:pos] + line[pos+len(quote_mrkr):]
                            quote_mrkr = ''
    
                    m_triquote = cls.TRIPLEQUATE.match(line)
                    while m_triquote:
                        quote_mrkr = m_triquote.group('triplequote')
                        line = m_triquote.group('rest')+os.linesep
                        
                        pos = line.find(quote_mrkr)
                        if pos>=0:
                            line = line[0:pos]+line[pos+len(quote_mrkr):]
                            quote_mrkr = ''
                        else:
                            break
                        m_triquote = cls.TRIPLEQUATE.match(line)
                        
                yield line
    
        @classmethod
        def extract(cls,lines: typing.Iterable[str],
                    s_marker:str=None,
                    e_marker:str=None,
                    include_markers:bool=True,
                    multi_match:bool=False,
                    dedent:bool=False,
                    dequote:bool=False,
                    skip_head_emptyline:bool=False,
                    skip_tail_emptyline:bool=False, 
                    format_filter=None) -> typing.Iterator[str]:
    
            s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                        else ( re.compile(s_marker) 
                               if isinstance(s_marker, str) and s_marker else None))
            e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                         else ( re.compile(e_marker) 
                                if isinstance(e_marker, str) and e_marker else None))
            el_buf     = []
            el_bfr_hdr = True
            in_range = True if s_pttrn is None else False
            for line in cls.extract_dequote(lines=lines,
                                            s_marker=s_pttrn, e_marker=e_pttrn,
                                            include_markers=True,
                                            multi_match=multi_match,
                                            dedent=dedent, dequote=dequote,
                                            format_filter=format_filter):
                if not in_range:
                    if s_pttrn is None or s_pttrn.match(line):
                        in_range = True
                        if include_markers:
                            yield line
                else:
                    m_el = cls.EMPTYLINE.match(line)
                    if m_el:
                        el_buf.append(line)
                    else:
                        if el_bfr_hdr and skip_head_emptyline:
                            el_bfr_hdr = False
                            el_buf=[]
    
                    if e_pttrn is not None and e_pttrn.match(line):
                        if not skip_tail_emptyline:
                            yield from el_buf
                            el_buf = []
                        if include_markers:
                            yield line
                        if multi_match or (s_pttrn is not None):
                            el_buf     = []
                            el_bfr_hdr = True
                            in_range   = False
                        else:
                            return
                    elif not m_el:
                        yield from el_buf
                        el_buf = []
                        yield line
    
            if e_pttrn is None and (not skip_tail_emptyline):
                yield from el_buf
                el_buf = []
    
        @classmethod
        def extract_from_file(cls, infile:str=None, s_marker:str=None, e_marker:str=None,
                              include_markers:bool=True, multi_match:bool=False,
                              dedent:bool=False, skip_head_emptyline:bool=False,
                              skip_tail_emptyline:bool=False, dequote:bool=False,
                              format_filter=None, encoding:str='utf-8') -> typing.Iterator[str]:
    
            input_path = pathlib.Path( infile if isinstance(infile,str) and infile
                                       else inspect.getsourcefile(inspect.currentframe())).resolve()
            with open(input_path, encoding=encoding) as fin:
                for line in cls.extract(fin, 
                                        s_marker=s_marker,
                                        e_marker=e_marker,
                                        include_markers=include_markers,
                                        multi_match=multi_match,
                                        dedent=dedent, dequote=dequote,
                                        format_filter=format_filter,
                                        skip_head_emptyline=skip_head_emptyline,
                                        skip_tail_emptyline=skip_tail_emptyline):
                    yield line
    
        @classmethod
        def extract_to_file(cls, outfile, infile:str=None, s_marker:str=None, e_marker:str=None,
                            include_markers:bool=True, multi_match:bool=False,
                            dedent:bool=False, skip_head_emptyline:bool=False,
                            skip_tail_emptyline:bool=False, dequote:bool=False,
                            format_filter=None, open_mode='w', encoding:str='utf-8'):
            
            fout = sys.stdout if outfile is None else open(outfile, mode=open_mode, encoding=encoding)
            for line in cls.extract_from_file(infile=infile, 
                                              s_marker=s_marker, e_marker=e_marker,
                                              include_markers=include_markers,
                                              multi_match=multi_match, dedent=dedent, 
                                              skip_head_emptyline=skip_head_emptyline,
                                              skip_tail_emptyline=skip_tail_emptyline,
                                              dequote=dequote, format_filter=format_filter, encoding=encoding):
                fout.write(line)
            if outfile is not None:
                fout.close()

def main():
    import sys
    return PyEncase(sys.argv).main()

if __name__=='__main__':
    main()

    if False:

        ############# ____GITIGNORE_TEMPLATE_START____ #######################

        """
        # .gitignore
        *.py[cod]
        *$py.class
        # For emacs backup file
        *~
        {____GIT_INGORE_DIRS____}
        !{____GIT_DUMMYFILE____}
        """

        ############# ____GITIGNORE_TEMPLATE_END____ #######################



        ############# ____README_TEMPLATE_START____ #######################
    
        """
        #
        # {____TITLE____}
        #
        
        Skeleton for small portable tools by python script
        
        - Contents:

        {____contents_lines____}
         
        - Usage (Procedure for adding new script):
        
          1. Put new script under '{____PYLIB_PATH____}'.
        
             Example: '{____PYLIB_PATH____}/{{newscriptname}}.py'
        
          2. Make symbolic link to '{____BIN_PATH____}/{____SHSCRIPT_ENTITY_NAME____}' with same basename as the
             basename of new script.
        
              Example: '{____BIN_PATH____}/{{newscriptname}}' --> {____SHSCRIPT_ENTITY_NAME____}
        
          3. Download external python module by './{____BIN_PATH____}/{____MNGSCRIPT_NAME____}'
        
              Example: '{____PYLIB_PATH____}/{{newscriptname}}.py' uses modules, pytz and tzlocal.
        
              % ./{____BIN_PATH____}/{____MNGSCRIPT_NAME____} install pytz tzlocal
        
          4. Invoke the symbolic link made in step.2 for execute the script.
        
              % ./{____BIN_PATH____}/{{newscriptname}}
        
        - Caution:
        
          - Do not put python scripts/modules that are not managed by pip
            under '{____PIP_PATH____}'.
        
            Otherwise those scripts/modules will be removed by
            `./{____BIN_PATH____}/{____MNGSCRIPT_NAME____} distclean`
        
        - Note:
        
          - Python executable is seeked by the following order.
        
            1. Environmental variable: PYTHON
            2. Shebang in called python script
            3. python3 in PATH
            4. python  in PATH
        
          - pip command is seeked by the following order.
        
            1. Environmental variable: PIP
            2. pip3 in PATH for "{____MNGSCRIPT_NAME____}"
            3. pip3 in PATH
        
        - Requirements (Tools used in "{____SHSCRIPT_ENTITY_NAME____}")
        
          - Python, PIP
        
        - Author
        
          - {____AUTHOR_NAME____} ({____AUTHOR_EMAIL____})
    
        --
        """

        ############# ____README_TEMPLATE_END____ #######################


        ############# ____PY_MAIN_TEMPLATE_START____ #######################
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
            
        import argparse
        import datetime
        import sys
            
        import pytz
        import tzlocal
        
        #import pkgstruct
        
        def main():
            """
            ____SCRIPT_NAME____
            Example code skeleton: Just greeting
            """
            argpsr = argparse.ArgumentParser(description='Example: showing greeting words')
            argpsr.add_argument('name', nargs='*', type=str, default=['World'],  help='your name')
            argpsr.add_argument('-d', '--date', action='store_true', help='Show current date & time')
            args = argpsr.parse_args()
            if args.date:
                tz_local = tzlocal.get_localzone()
                datestr  = datetime.datetime.now(tz=tz_local).strftime(" It is \"%c.\"")
            else:
                datestr = ''
        
            print("Hello, %s!%s" % (' '.join(args.name), datestr))
            print("Python : %d.%d.%d " % sys.version_info[0:3]+ "(%s)" % sys.executable)
            hdr_str = "Python path: "
            for i,p in enumerate(sys.path):
                print("%-2d : %s" % (i+1, p))
                hdr_str = ""
        
            #pkg_info   = pkgstruct.PkgStructure(script_path=sys.argv[0])
            #pkg_info.dump(relpath=False, with_seperator=True)
        
        if __name__ == '__main__':
            main()

        ########## ____PY_MAIN_TEMPLATE_END____ ##########

        
        ########## ____PY_LIB_SCRIPT_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
        
        import json
        
        class ____NEW_CLS_NAME____(object):
            """
            ____NEW_CLS_NAME____
            Example class code skeleton: 
            """
            def __init__(self):
                self.contents = {}  
        
            def __repr__(self):
                return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
        
            def __str__(self):
                return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
        
        if __name__ == '__main__':
            help(____NEW_CLS_NAME____)

        ########## ____PY_LIB_SCRIPT_TEMPLATE_END____ ##########

        ########## ____PKG_CACHE_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
        import gzip
        import bz2
        import re
        import os
        import sys
        import json
        import filecmp
        
        import yaml
        
        import intrinsic_format
        import pkgstruct
        
        class PkgCache(pkgstruct.PkgStruct):
            """
            Class for Data cache for packaged directory
            """
            def __init__(self, subdirkey='pkg_cachedir', subdir=None, 
                         dir_perm=0o755, perm=0o644, keep_oldfile=False, backup_ext='.bak',
                         timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True,
                         script_path=None, env_input=None, prefix=None, pkg_name=None,
                         flg_realpath=False, remove_tail_digits=True, remove_head_dots=True, 
                         basename=None, tzinfo=None, unnecessary_exts=['.sh', '.py', '.tar.gz'],
                         namespece=globals(), yaml_register=True, **args):
        
                super().__init__(script_path=script_path, env_input=env_input, prefix=prefix, pkg_name=pkg_name,
                                 flg_realpath=flg_realpath, remove_tail_digits=remove_tail_digits, remove_head_dots=remove_head_dots, 
                                 unnecessary_exts=unnecessary_exts, **args)
        
                self.config = { 'dir_perm':                 dir_perm,
                                'perm':                     perm,
                                'keep_oldfile':             keep_oldfile,
                                'backup_ext':               backup_ext,
                                'timestampformat':          timestampformat,
                                'avoid_duplicate':          avoid_duplicate,
                                'json:skipkeys':            False,
                                'json:ensure_ascii':        False, # True,
                                'json:check_circular':      True, 
                                'json:allow_nan':           True,
                                'json:indent':              4, # None,
                                'json:separators':          None,
                                'json:default':             None,
                                'json:sort_keys':           True, # False,
                                'json:parse_float':         None,
                                'json:parse_int':           None,
                                'json:parse_constant':      None,
                                'json:object_pairs_hook':   None,
                                'yaml:stream':              None,
                                'yaml:default_style':       None,
                                'yaml:default_flow_style':  None,
                                'yaml:encoding':            None,
                                'yaml:explicit_start':      True, # None,
                                'yaml:explicit_end':        True, # None,
                                'yaml:version':             None,
                                'yaml:tags':                None,
                                'yaml:canonical':           True, # None,
                                'yaml:indent':              4, # None,
                                'yaml:width':               None,
                                'yaml:allow_unicode':       None,
                                'yaml:line_break':          None
                               }
        
                if isinstance(subdir,list) or isinstance(subdir,tuple):
                    _subdir = [ str(sd) for sd in subdir]
                    self.cache_dir = self.concat_path(skey, *_subdir)
                elif subdir is not None:
                    self.cache_dir = self.concat_path(skey, str(subdir))
                else:
                    self.cache_dir = self.concat_path(skey)
        
                self.intrinsic_formatter = intrinsic_format.intrinsic_formatter(namespace=namespace,
                                                                                register=yaml_register)
        
            def read(self, fname, default=''):
                return self.read_cache(fname, default='', directory=self.cache_dir)
        
            def save(self, fname, data):
                return self.save_cache(fname, data, directory=self.cache_dir, **self.config)
        
            @classmethod
            def save_cache(cls, fname, data, directory='./cache', dir_perm=0o755,
                           keep_oldfile=False, backup_ext='.bak', 
                           timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
                """ function to save data to cache file
                fname     : filename
                data      : Data to be stored
                directory : directory where the cache is stored. (default: './cache')
            
                Return value : file path of cache file
                               None when fail to make cache file
                """
                data_empty = True if (((isinstance(data, str) or isinstance(data, bytes) or
                                        isinstance(data, dict) or isinstance(data, list) or
                                        isinstance(data, tuple) ) and len(data)==0)
                                      or isinstance(data, NoneType) ) else False
                if data_empty:
                    return None
                if not os.path.isdir(directory):
                    os.makedirs(directory, mode=dir_perm, exist_ok=True)
                o_path = os.path.join(directory, fname)
                ext1, ext2, fobj = cls.open_autoassess(o_path, 'w',
                                                       keep_oldfile=keep_oldfile,
                                                       backup_ext=backup_ext, 
                                                       timestampformat=timestampformat,
                                                       avoid_duplicate=avoid_duplicate)
                if fobj is None:
                    return None
        
                if ext2 == 'yaml':
                    #f.write(yaml.dump(data))
                    f.write(self.intrinsic_formatter.dump_json(data, 
                                                               skipkeys=self.config['json:skipkeys'],
                                                               ensure_ascii=self.config['json:ensure_ascii'],
                                                               check_circular=self.config['json:check_circular'],
                                                               allow_nan=self.config['json:allow_nan'],
                                                               indent=self.config['json:indent'],
                                                               separators=self.config['json:separators'],
                                                               default=self.config['json:default'],
                                                               sort_keys=self.config['json:sort_keys']))
                elif ext2 == 'json':
                    #f.write(json.dumps(data, ensure_ascii=False))
                    f.write(self.intrinsic_formatter.dump_yaml(data,
                                                               stream=self.config['yaml:stream'],
                                                               default_style=self.config['yaml:default_style'],
                                                               default_flow_style=self.config['yaml:default_flow_style'],
                                                               encoding=self.config['yaml:encoding'],
                                                               explicit_start=self.config['yaml:explicit_start'],
                                                               explicit_end=self.config['yaml:explicit_end'],
                                                               version=self.config['yaml:version'],
                                                               tags=self.config['yaml:tags'],
                                                               canonical=self.config['yaml:canonical'],
                                                               indent=self.config['yaml:indent'],
                                                               width=self.config['yaml:width'],
                                                               allow_unicode=self.config['yaml:allow_unicode'],
                                                               line_break=self.config['yaml:line_break']))
                else:
                    f.write(data)
                f.close()
        
                os.path.chmod(o_path, mode=perm)
                return o_path
        
            @classmethod
            def backup_by_rename(cls, orig_path, backup_ext='.bak',
                                 timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
                if not os.path.lexists(orig_path):
                    return
                path_base, path_ext2 = os.path.splitext(orig_path)
                if path_ext2 in ['.bz2', '.gz']:
                    path_base, path_ext = os.path.splitext(path_base)
                else:
                    path_ext2, path_ext = ('', path_ext2)
                if path_ext == backup_ext and len(path_base)>0:
                    path_base, path_ext = os.path.splitext(path_base)
                if isinstance(timestampformat, str) and len(timestampformat)>0:
                    mtime_txt = '.' + datetime.datetime.fromtimestamp(os.lstat(orig_path).st_mtime).strftime(timestampformat)
                else:
                    mtime_txt = ''
        
                i=0
                while(True):
                    idx_txt = ( ".%d" % (i) ) if i>0 else ''
                    bak_path = path_base + mtime_txt + idx_txt + path_ext  + backup_ext + path_ext2
                    if os.path.lexists(bak_path):
                        if avoid_duplicate and filecmp.cmp(orig_path, bak_path, shallow=False):
                            os.unlink(bak_path)
                        else:
                            continue
                    os.rename(orig_path, bak_path)
                    break
        
                    
            @classmethod
            def open_autoassess(cls, path, mode, 
                                keep_oldfile=False, backup_ext='.bak', 
                                timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
        
                """ function to open normal file or file compressed by gzip/bzip2
                    path : file path
                    mode : file open mode 'r' or 'w'
            
                    Return value: (1st_extension: bz2/gz/None,
                                   2nd_extension: yaml/json/...,
                                   opend file-io object or None)
                """
                if 'w' in mode or 'W' in mode:
                    modestr = 'w'
                    if keep_oldfile:
                        cls.backup_by_rename(path, backup_ext=backup_ext,
                                             timestampformat=timestampformat,
                                             avoid_duplicate=avoid_duplicate)
                elif 'r' in mode  or 'R' in mode:
                    modestr = 'r'
                    if not os.path.isfile(path):
                        return (None, None, None)
                else:
                    raise ValueError("mode should be 'r' or 'w'")
        
                base, ext2 = os.path.splitext(path)
                if ext2 in ['.bz2', '.gz']:
                    base, ext1 = os.path.splitext(path_base)
                else:
                    ext1, ext2 = (ext2, '')
        
                if ext2 == 'bz2':
                    return (ext2, ext1, bz2.BZ2File(path, modestr+'b'))
                elif ext2 == 'gz':
                    return (ext2, ext1, gzip.open(path, modestr+'b'))
                return (ext2, ext1, open(path, mode))
        
            @classmethod
            def read_cache(cls, fname, default='', directory='./cache'):
                """ function to read data from cache file
                fname      : filename
                default   : Data when file is empty (default: empty string)
                directory : directory where the cache is stored. (default: ./cache)
            
                Return value : data    when cache file is exist and not empty,
                               default otherwise
                """
                if not os.path.isdir(directory):
                    return default
                in_path = os.path.join(directory, fname)
                ext1, ext2, fobj = cls.open_autoassess(in_path, 'r')
                if fobj is None:
                    return default
                f_size = os.path.getsize(in_path)
        
                data = default
                if ((ext1 == 'bz2' and f_size > 14) or
                    (ext1 == 'gz'  and f_size > 14) or
                    (ext1 != 'bz2' and ext1 != 'gz' and f_size > 0)):
                    if ext2 == 'yaml' or ext2 == 'YAML':
                        #data = yaml.load(fobj)
                        data = self.intrinsic_formatter.load_json(fobj,
                                                                  parse_float=self.config['json:parse_float'],
                                                                  parse_int=self.config['json:parse_int'],
                                                                  parse_constant=self.config['json:parse_constant'],
                                                                  object_pairs_hook=self.config['json:object_pairs_hook'])
                    elif ext2 == 'json'or ext2 == 'JSON':
                        # data = json.load(fobj)
                        data = self.intrinsic_formatter.load_yaml(fobj)
                    else:
                        data = fobj.read()
                f.close()
                return data
            
        
        if __name__ == '__main__':
            help(PkgCache)

        ########## ____PKG_CACHE_TEMPLATE_END____ ##########

        ########## ____INTRINSIC_FORMATTER_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
        import os
        import sys
        import io
        
        import datetime
        import copy
        import inspect
        
        import json
        import yaml
        
        class intrinsic_formatter(object):
            """
            Utility for intrinsic format to store/restore class instanse data.
                    w/  interface for PyYAML and json
            """
            def __init__(self, namespace=globals(), register=True, proc=None):
                self.pyyaml_dumper  = yaml.SafeDumper
                self.pyyaml_loader  = yaml.SafeLoader
                self.namespace      = namespace
                self.proc           = proc
                if register:
                    self.pyyaml_register(namespace=self.namespace)
        
            @classmethod
            def decode(cls, data, proc=None, namespace=globals()):
                """
                Restore object from intrinsic data expression as much as possible
                """
                untouch_type  = (int, float, complex, bool, str, bytes, bytearray)
                sequence_type = (list, tuple, set, frozenset)
            
                if isinstance(data, dict):
                    meta_data_tag = ('____class____', '____name____', '____tag____')
                    _cls_, _clsname, _clstag = ( data.get(k) for k in meta_data_tag )
                    if _cls_ == 'datetime.datetime':
                        # return datetime.datetime.fromisoformat(data.get('timestamp'))
                        return datetime.datetime.strptime(data.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%f%z')
            
                    if _cls_ is not None and _clsname is not None and _clstag is not None:
                        if isinstance(namespace, dict):
                            cls_ref = namespace.get(_cls_)
                            if cls_ref is None:
                                cls_ref = namespace.get(_clsname)
                        if cls_ref is None:
                            cls_ref = locals().get(_cls_)
                        if cls_ref is None:
                            cls_ref = locals().get(_clsname)
                        if cls_ref is None:
                            cls_ref = globals().get(_cls_)
                        if cls_ref is None:
                            cls_ref = globals().get(_clsname)
                        if cls_ref is not None and inspect.isclass(cls_ref):
                            if hasattr(cls_ref, 'from_intrinsic') and callable(cls_ref.from_intrinsic):
                                return proc(cls_ref.from_intrinsic(data)) if callable(proc) else cls_ref.from_intrinsic(data)
                            if hasattr(cls_ref, 'from_dict') and callable(cls_ref.from_dict):
                                return proc(cls_ref.from_dict(data)) if callable(proc) else cls_ref.from_dict(data)
            
                            cnstrctr_args={k: cls.decode(d, proc=proc, namespace=namespace) for k, d in data.items() if k not in meta_data_tag }
                            try:
                                new_obj=cls_ref()
                                for k,d in cnstrctr_args.items():
                                    new_obj.__dict__[k] = copy.deepcopy(d)
                                return new_obj
                            except:
                                pass
                    return {k: cls.decode(d, proc=proc, namespace=namespace) for k, d in data.items() }
            
                for _seqtype in sequence_type:
                    if isinstance(data, _seqtype):
                        return _seqtype( cls.decode(d, proc=proc) for d in data )
            
                if isinstance(data, untouch_type):
                    return proc(data) if callable(proc) else data
            
                #if data is None:
                #    return None
            
                return proc(data) if callable(proc) else data
            
            @classmethod
            def encode(cls, data, proc=None):
                """
                Convert object to intrinsic data expression as much as possible
                """
            
                untouch_type  = (int, float, complex, bool, str, bytes, bytearray)
                sequence_type = (list, tuple, set, frozenset)
                undump_keys   = ('__init__', '__doc__' )
                # undump_keys   = ('__module__', '__init__', '__doc__' )
            
                if data is None:
                    return None
            
                if isinstance(data, untouch_type):
                    return proc(data) if callable(proc) else data
            
                if isinstance(data, datetime.datetime):
                    return {'____class____': data.__class__.__module__+'.'+data.__class__.__name__,
                            '____name____':  data.__class__.__name__,
                            '____tag____':  '!!'+data.__class__.__name__,
                            #'timestamp': data.isoformat(timespec='microseconds'),
                            'timestamp': data.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),  }
            
                if isinstance(data, dict):
                    return {k: cls.encode(d, proc=proc) for k,d in data.items() }
            
                for _seqtype in sequence_type:
                    if isinstance(data, _seqtype):
                        return _seqtype( cls.encode(d, proc=proc) for d in data )
            
                if ( isinstance(data,object) and
                     ( not inspect.ismethod(data) ) and 
                     ( not inspect.isfunction(data) ) ):
                    try:
                        meta_data = {'____class____': data.__class__.__module__+'.'+data.__class__.__name__,
                                     '____name____':  data.__class__.__name__,
                                     '____tag____':  '!!'+data.__class__.__name__}
                        if hasattr(data, 'intrinsic_form') and callable(data.intrinsic_form):
                            return { **meta_data, **(data.intrinsic_form()) }
                        elif hasattr(data, 'to_dict') and callable(data.to_dict):
                            return { **meta_data, **(data.to_dict()) }
                        elif hasattr(data, 'asdict') and callable(data.asdict):
                            return { **meta_data, **(data.asdict()) }
            
                        _data_dict_=data.__dict__
                        return { **meta_data,
                                 **{ k: cls.encode(d, proc=proc) 
                                     for k, d in _data_dict_.items()
                                     if ( ( k not in undump_keys ) and
                                          ( isinstance(d,object) and
                                            ( not inspect.ismethod(d) ) and 
                                            ( not inspect.isfunction(d) ) ) ) } }
                    except:
                        return proc(data) if callable(proc) else data
            
                return None
        
            @classmethod
            def pyyaml_extended_representer(cls, dumper, obj):
                cnved = cls.encode(obj)
                node = dumper.represent_mapping(cnved.get('____tag____'), cnved)
                return node
        
            def pyyaml_register_presenter(self, namespace=globals()):
                apathic_keys = ('__name__', '__doc__', '__package__', '__loader__', '__spec__',
                                '__annotations__', '__builtins__', '__module__', '__init__')
                if isinstance(namespace, dict):
                    glbs = {clskey: cls for clskey, cls in namespace.items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ str(cls.__name__) for key,cls in glbs.items() ]
                    for i_tag in tag_tbd:
                        self.pyyaml_dumper.add_representer(namespace.get(i_tag), intrinsic_formatter.pyyaml_extended_representer)
                else:            
                    glbs = {clskey: cls for clskey, cls in globals().items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ str(cls.__name__) for key,cls in glbs.items() ]
                    for i_tag in tag_tbd:
                        self.pyyaml_dumper.add_representer(globals()[i_tag], intrinsic_formatter.pyyaml_extended_representer)
        
            @classmethod
            def pyyaml_node_to_dict(cls, loader, node):
                if isinstance(node, yaml.nodes.SequenceNode):
                    ret = loader.construct_sequence(node)
                    for idx, sub_node in enumerate(node.value):
                        if isinstance(sub_node, yaml.nodes.CollectionNode):
                            ret[idx] = cls.pyyaml_node_to_dict(loader, sub_node)
                elif isinstance(node, yaml.nodes.MappingNode):
                    ret = loader.construct_mapping(node)
                    for sub_key, sub_node in node.value:
                        if isinstance(sub_node, yaml.nodes.CollectionNode):
                            ret[sub_key.value] = cls.pyyaml_node_to_dict(loader, sub_node)
                else:
                    ret = loader.construct_scalar(node)
                return ret
        
            @classmethod
            def pyyaml_extended_constructor(cls, loader, node, proc=None, namespace=globals()):
                deced = cls.pyyaml_node_to_dict(loader, node)
                obj = cls.decode(deced, proc=proc, namespace=namespace)
                return obj
        
            def pyyaml_register_constructor(self, namespace=globals()):
                apathic_keys = ('__name__', '__doc__', '__package__', '__loader__', '__spec__',
                                '__annotations__', '__builtins__', '__module__', '__init__')
                if namespace is None:
                    glbs = {clskey: cls for clskey, cls in globals().items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ '!!'+str(cls.__name__) for key,cls in glbs.items() ]
                elif isinstance(namespace, (list, tuple, set, frozenset)):
                    tag_tbd = namespace
                elif isinstance(namespace, dict):
                    glbs = {clskey: cls for clskey, cls in namespace.items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ '!!'+str(cls.__name__) for key,cls in glbs.items() ]
                else:
                    tag_tbd = [ namespace ]
        
                for i_tag in tag_tbd:
                    self.pyyaml_loader.add_constructor(i_tag,
                                                       lambda l, n : intrinsic_formatter.pyyaml_extended_constructor(l, n,
                                                                                                                     proc=self.proc,
                                                                                                                     namespace=self.namespace))
        
            def pyyaml_register(self, namespace=globals()):
                self.pyyaml_register_constructor(namespace=namespace)
                self.pyyaml_register_presenter(namespace=namespace)
        
            class json_encoder(json.JSONEncoder):
                def default(self, obj):
                    ret = intrinsic_formatter.encode(obj)
                    if type(obj)!=type(ret):
                        return ret
                    return super().default(obj)
        
            @classmethod
            def dump_json_bulk(cls, obj, fp=None, skipkeys=False, ensure_ascii=True, check_circular=True, 
                               allow_nan=True, indent=None, separators=None, default=None, sort_keys=False, **kw):
        
                if fp is not None:
                    return json.dump(obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                     allow_nan=allow_nan, cls=cls.json_encoder, indent=indent, separators=separators,
                                     default=default, sort_keys=sort_keys, **kw)
                else:
                    return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                      allow_nan=allow_nan, cls=cls.json_encoder, indent=indent, separators=separators,
                                      default=default, sort_keys=sort_keys, **kw)
        
        
            def dump_json(self, obj, fp=None, skipkeys=False, ensure_ascii=False, check_circular=True, 
                          allow_nan=True, indent=4, separators=None, default=None, sort_keys=False, **kw):
                return self.dump_json_bulk(obj, fp=fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, 
                                           allow_nan=allow_nan, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kw)
        
            @classmethod
            def load_json_bulk(cls, obj, parse_float=None, parse_int=None,
                               parse_constant=None, object_pairs_hook=None, namespace=globals(), **kw):
                if isinstance(obj, io.IOBase):
                    return json.load(obj, object_hook=lambda x : cls.decode(x, namespace=namespace),
                                     parse_float=parse_float, parse_int=parse_int, 
                                     parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
                return json.loads(obj, object_hook=lambda x : cls.decode(x, namespace=namespace),
                                  parse_float=parse_float, parse_int=parse_int,
                                  parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
        
            def load_json(self, obj, parse_float=None, parse_int=None,
                          parse_constant=None, object_pairs_hook=None, namespace=globals(), **kw):
                return self.load_json_bulk(obj=obj, parse_float=parse_float, parse_int=parse_int,
                                           parse_constant=parse_constant, object_pairs_hook=object_pairs_hook,
                                           namespace=self.namespace, **kw)
        
            def dump_yaml(self, obj, stream=None, default_style=None, default_flow_style=None, encoding=None,
                          #indent=None, explicit_start=None, explicit_end=None, canonical=None,
                          indent=4, explicit_start=True, explicit_end=True, canonical=True,
                          version=None, tags=None, width=None, allow_unicode=None, line_break=None):
                return yaml.dump(obj, stream=stream, Dumper=self.pyyaml_dumper, default_style=default_style,
                                 default_flow_style=default_flow_style, encoding=encoding, explicit_end=explicit_end,
                                 version=version, tags=tags, canonical=canonical, indent=indent, width=width,
                                 allow_unicode=allow_unicode, line_break=line_break)
        
            def load_yaml(self, obj):
                return yaml.load(obj, Loader=self.pyyaml_loader)
        
        if __name__ == '__main__':
            help(intrinsic_formatter)
                    
        ########## ____INTRINSIC_FORMATTER_TEMPLATE_END____ ##########
