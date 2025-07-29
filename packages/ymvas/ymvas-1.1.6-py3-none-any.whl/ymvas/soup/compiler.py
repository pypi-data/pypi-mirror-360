from os.path import join, exists, dirname, basename, isdir
from pathlib import Path
import os, json, shutil, yaml

from .references import Ref
from ..settings  import Settings

class Compiler:
    info  = []

    valid_formats = [
        "pdf",
        "html",
        'png'
    ]

    def __init__(self, stg:Settings ):
        self.settings = stg

        self._p_repo              = self.settings.root
        self._p_repo_dot_git      = self.settings.git

        # settings
        self._is_account          = self.settings.is_main

        self.f_settings_endpoints = self.settings.f_settings_endpoints
        self.d_compile_prefix     = self.settings.d_compile_prefix
 

    def _get_cache(self):
        self._cache = {}
        self.cache_info_file = join(self._p_compiled_dir,'config.json')
        self._has_cache      = False

        if exists( self.cache_info_file ):
            try:
                f = open(self.cache_info_file,'r')
                self._cache = json.loads(f.read())
                f.close()
                self._has_cache = True
            except Exception:
                pass

    def _tracked_settings(self):
        tracked = " ".join([
            self.settings.d_settings ,
        ])

        commited = os.popen(
            f"git --git-dir={self._p_repo_dot_git} "
            f"--work-tree={self.settings.root} diff "
            f"--name-only HEAD~1 HEAD "
            f"-- {tracked} "
        ).read().strip().split("\n")

        modified = os.popen(
            f"git --git-dir={self._p_repo_dot_git} "
            f"--work-tree={self.settings.root} status "
            f"-s {tracked} "
        ).read().strip().split("\n")

        files = []
        for f in modified:
            mtype = f[:3]
            file  = f[3:].strip()
            if '"' in f or "'" in f:
                continue
            if "R" in mtype:
                fxf  = file.split('->')
                file = fxf[-1].strip()
            files.append(file)

        return [f for f in list(set(commited + files)) if f.strip() != '']

    def _tracked_files(self):
        if not self._has_cache:
            _files = []
            for r,_,files in os.walk( self.settings.d_endpoints ):
                for f in files:
                    original = Path(join( r , f ))
                    _files.append(str(original.relative_to(
                        Path( self.settings.root )
                    )))
            return [f for f in _files if f.strip() != '']


        tracked = " ".join([
          self.settings.d_endpoints ,
        ])

        commited = os.popen(
            f"git --git-dir={self._p_repo_dot_git} "
            f"--work-tree={self.settings.root} diff "
            f"--name-only HEAD~1 HEAD "
            f"-- {tracked} "
        ).read().strip().split("\n")

        modified = os.popen(
            f"git --git-dir={self._p_repo_dot_git} "
            f"--work-tree={self.settings.root} status "
            f"-s {tracked} "
        ).read().strip().split("\n")

        files = []
        for f in modified:
            mtype = f[:3]
            file  = f[3:].strip()

            if '"' in f or "'" in f:
                # skip strange files
                self.info.append({
                    "operation" : "file-skip-compile",
                    "file"      : file
                })
                continue
            if "R" in mtype:
                fxf  = file.split('->')
                file = fxf[-1].strip()

                self.info.append({
                    "operation" : "file-renamed",
                    "file"      : fxf[0].strip()
                })

            if "D" in mtype:
                self.info.append({
                    "operation" : "file-removed",
                    "file"      : file
                })

                continue

            files.append(file)
        return [f for f in list(set(commited + files)) if f.strip() != '']

    def _make_pdf(self, file, content, conf = {} ):
        try:
            import pdfkit

            file.write(pdfkit.from_string(
                content,
                False,
                options = {
                    'margin-top'    : str(conf.get( 'margin-top'    , '0.0in' )),
                    'margin-right'  : str(conf.get( 'margin-right'  , '0.0in' )),
                    'margin-bottom' : str(conf.get( 'margin-bottom' , '0.0in' )),
                    'margin-left'   : str(conf.get( 'margin-left'   , '0.0in' )),
                }
            ))

        except OSError as e:
            file.write(content.encode('utf-8'))
            print('[pdfkit] failed to create file, please install all the depedencies required!')

    def _make_svg_png(self,file,content,conf = {}):
        _content = content.encode('utf-8')
        try:
            from cairosvg import svg2png
            file.write(svg2png(bytestring=_content))
        except Exception as e:
            file.write(_content)
            print('[cairosvg] failed to create file, please install all the depedencies required!')

    def _make_md_html(self,file,content,conf = {}):
        _content = content.encode('utf-8')
        try:
            import markdown
            file.write(markdown.markdown(content).encode('utf-8'))
        except Exception as e:
            file.write(_content)
            print('[markdown] failed to create file, please install all the depedencies required!')


    def get_endpoints(self):
        if exists(self.f_settings_endpoints):
            with open(self.f_settings_endpoints,'r') as f:
                data = yaml.safe_load(f.read())
                if isinstance(data,dict):
                    return data
        return {}

    def run(self, compile_dir ):
        if not exists(self.settings.d_endpoints):
            return
        
        self._p_compiled_dir = compile_dir 

        self._get_cache()
        os.makedirs( self._p_compiled_dir ,exist_ok =True)

        config = {
            "files"   : {},
        }

        # for traquing files
        if self.settings.is_main:
            config['modules'] = [
                m.name for m in self.settings.get_modules().values() \
                if not m.root
            ]

        old_config = self._cache
        old_files  = old_config.get('files',{})

        files     = self._tracked_files()
        settings  = self._tracked_settings()

        self.settings.log("Old     Files    :  " + json.dumps(old_files, indent=2) )
        if len(settings) == 0 and len(files) == 0:
            self.settings.log(f"No changes detected!")
            return

        self.settings.log("Tracked Files    : \n" + '\n'.join(files) )
        self.settings.log("Tracked settings : \n" + '\n'.join(settings) )

        # settings modified in last commit
        _modified_settings = len(settings) != 0
        for f in files:
            ff = join(self._p_repo, f)
            if ff.startswith(self.settings.d_settings):
                _modified_settings = True
                break

        self.settings.log(f"Are settings modified? : {_modified_settings}")

        # get endpoints data
        endpoints = self.get_endpoints()

        # track modifications
        if _modified_settings:
            for mf, mf_info in old_files.items():

                # check current settings
                _curr_conf = endpoints.get(mf,{})
                _prev_conf = mf_info.get('conf',{})

                if json.dumps( _curr_conf ) == json.dumps( _prev_conf ):
                    # no changes
                    continue

                # add this file to be compiled again
                # because settings have changed
                origin = mf_info.get('origin',None)
                if origin != None:
                    files = list(set(files + [origin]))

                # remove previous compiled filefile
                _prev_compiled = mf_info.get( 'compiled' , None )
                if _prev_compiled != None:
                    _prev_compiled = join(self._p_compiled_dir, _prev_compiled)
                    if exists(_prev_compiled):
                        os.remove(_prev_compiled)

                self.info.append({
                    "operation" : "file-removed",
                    "file"      : _prev_compiled
                })

        for f in files:
            ff = join(self._p_repo, f)
            if isdir(ff):
                continue

            origin = str(Path( ff ).relative_to(self._p_repo))
            name   = str(Path( ff ).relative_to(self.settings.d_endpoints))
            conf   = endpoints.get(name,{})

            format = conf.get('format',None)
            format = format if format in self.valid_formats else None

            e = Ref( ff, self.settings )

            nnamet = name
            if format != None:
                fname   = e.basename.split('.')[0] if '.' in e.basename else e.basename
                fname  += f'.{format}'
                nnamet  = name.strip(e.basename)
                nnamet += fname

            ntarget = join(self._p_compiled_dir, nnamet)
            vnam    = ntarget.replace(basename(ntarget),'')

            os.makedirs( vnam , exist_ok = True )

            self.settings.log(f"Creating file: {ntarget}")

            if e.justy_copy:
                shutil.copy2( e.fpath , ntarget )
            else:
                file = open(ntarget,'wb')

                if format   == 'pdf':
                    self._make_pdf(file,e.content,conf)
                elif format == 'png':
                    self._make_svg_png(file,e.content,conf)
                elif format == 'html':
                    self._make_md_html(file,e.content,conf)
                else:
                    file.write(e.content.encode('utf-8'))

                file.close()

            config['files'][name] = {
                "origin"   : origin,
                "compiled" : nnamet,
                "conf"     : conf
            }


        for f in self.info:
            # remove compiled if file was renamed
            if f.get('operation',None) != 'file-renamed':
                continue

            for mf, mf_info in self._cache.get('files',{}).items():
                origin = mf_info.get('origin',None)
                if origin != f:
                    continue

                _prev_compiled = mf_info.get('compiled',None)
                if _prev_compiled == None:
                    continue

                _prev_compiled = join(self._p_compiled_dir, _prev_compiled)
                if exists(_prev_compiled):
                    os.remove(_prev_compiled)
                    break

        _pre_avatar = self._cache.get('avatar',None) == None
        _get_avatar = (( len(settings) != 0 or _pre_avatar) and self._is_account)

        self.settings.log(f"Copy avatar : {_get_avatar}")

        if _get_avatar:
            posible_avatars = ["png","jpeg","jpg"]

            for a in posible_avatars:
                af = f"avatar.{a}"
                ap = join( '.ymvas', 'settings', af )

                config['avatar'] = {
                    "origin"  : ap ,
                    "display" : af ,
                }

                a_origin = join(self._p_repo , ap )

                if not exists(a_origin):
                    continue

                if (ap in settings or _pre_avatar):
                    shutil.copy2( a_origin , join(self._p_compiled_dir, af ))
                    break

        with open(self.cache_info_file,'w') as f:
            from ..__init__ import __version__
            config['version'] = __version__

            f.write(json.dumps(config, indent = 10))

        # print complie data
        self.settings.log(f"Final config : {json.dumps(config,indent = 2)}")
        url = self.settings.get_global_settings().get('ymvas-compile-url',None)
        if url is not None:
            for k,v in config["files"].items():
                c = v.get('compiled',None)
                if c is None: continue
                print( f"[COMPILER] : {url}/{self.d_compile_prefix}/{c}" )


        # end
