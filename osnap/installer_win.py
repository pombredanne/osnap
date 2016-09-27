import os
import shutil
import collections
import subprocess

import osnap.const
import osnap.make_nsis
import osnap.installer_base


class OsnapInstallerWin(osnap.installer_base.OsnapInstaller):

    def make_installer(self):

        self.copy_app(os.path.join(osnap.const.dist_dir, osnap.const.windows_app_dir), self.application_name,
                      self.verbose)

        # application .exe
        exe_name = self.application_name + '.exe'
        orig_launch_exe_path = os.path.join(osnap.const.dist_dir, 'launch.exe')
        dist_exe_path = os.path.join(osnap.const.dist_dir, exe_name)
        if self.verbose:
            print('moving %s to %s' % (orig_launch_exe_path, dist_exe_path))
        os.rename(orig_launch_exe_path, dist_exe_path)

        # support files
        for f in [self.application_name + '.ico', 'LICENSE']:
            shutil.copy2(f, osnap.const.dist_dir)

        # write NSIS script
        nsis_file_name = self.application_name + '.nsis'

        nsis_defines = collections.OrderedDict()
        nsis_defines['COMPANYNAME'] = self.author
        nsis_defines['APPNAME'] = self.application_name
        nsis_defines['EXENAME'] = exe_name
        nsis_defines['DESCRIPTION'] = '"' + self.description + '"'  # the description must be in quotes

        v = self.python_version.split('.')
        nsis_defines['VERSIONMAJOR'] = v[0]
        nsis_defines['VERSIONMINOR'] = v[1]
        nsis_defines['VERSIONBUILD'] = v[2]

        # These will be displayed by the "Click here for support information" link in "Add/Remove Programs"
        # It is possible to use "mailto:" links in here to open the email client
        nsis_defines['HELPURL'] = self.url  # "Support Information" link
        nsis_defines['UPDATEURL'] = self.url  # "Product Updates" link
        nsis_defines['ABOUTURL'] = self.url  # "Publisher" link

        if self.verbose:
            print('writing %s' % nsis_file_name)
        nsis = osnap.make_nsis.MakeNSIS(nsis_defines, nsis_file_name, project_packages)
        nsis.write_all()

        shutil.copy(nsis_file_name, osnap.const.dist_dir)

        os.chdir(osnap.const.dist_dir)

        nsis_path = os.path.join('c:', os.sep, 'Program Files (x86)', 'NSIS', 'makensis.exe')
        if os.path.exists(nsis_path):
            pkgproj_command = [nsis_path, nsis_file_name]
            if self.verbose:
                print('%s' % str(pkgproj_command))
            subprocess.check_call(pkgproj_command)
        else:
            print('error: NSIS tool could not be found (expected at %s)' % nsis_path)
            print('See http://nsis.sourceforge.net for information on how to obtain the NSIS '
                  '(Nullsoft Scriptable Install System) tool.')
