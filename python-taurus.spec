
# pure python modules goes in python_sitelib
# platform-specific modules goes in python_sitearch

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           python-taurus
Version:        4.1.0
Release:        1%{?dist}.maxiv
Summary:        Taurus framework
Group:          Development/Languages
License:        GPL
URL:            http://www.tango-controls.org/static/taurus
Source:         taurus-%{version}.tar.gz
BuildRequires:  python-setuptools
BuildRequires:  PyQt4-devel
BuildRequires:  python-ply
BuildRequires:  python-pytango
Requires:       python-pytango
Requires:       python-lxml
Requires:       python-ply
Requires:       python-guiqwt
Requires:       python-qub
Requires:       PyQt4-devel
Requires:       PyMca
Requires:       spyder
Requires:       sardana >= 2.2

Obsoletes:      taurus < %{version}-%{release}
Provides:       taurus = %{version}-%{release}

BuildArch:      noarch

%description
Taurus is a python framework for both CLI and GUI tango applications. It is
build on top of PyTango and PyQt. Taurus stands for TAngo User interface ‘R’ Us.

%prep
%setup -q -n taurus-%{version}

%build
%{__python} setup.py build
#%{__python} setup.py build_doc --external-img-tools

%install
python setup.py install --single-version-externally-managed \
                        -O1 --skip-build --prefix=%{_prefix}\
                        --root=%{buildroot} --record=INSTALLED_FILES

# rm -rf %{buildroot}

# %{__python} setup.py install \
#     -O1 \
#     --skip-build \
#     --prefix=%{_prefix} \
#     --root=%{buildroot}

# move html documentation to temporary location
#mv %{buildroot}%{_docdir}/taurus/html .
#rmdir %{buildroot}%{_docdir}/taurus

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)
#%doc html
#%{_bindir}/*
#%{python_sitelib}/taurus*
#%attr(-,root,man) %{_mandir}/man1/*

%changelog

* Mon Jul 24 2017 Antonio Milan Otero <antonio.milan_otero@maxiv.lu.se> - 4.0.0
- Update to version 4.0.0 from upstream.

* Fri Sep 04 2015 Johan Forsberg <johan.forsberg@maxlab.lu.se> - 3.6.0
- Update to version 3.6.0 from upstream (split from Sardana)

* Tue Sep 30 2014 Johan Forsberg <johan.forsberg@maxlab.lu.se> - 3.3.0
- Update to version 3.3.0 from upstream
- Depend on Sardana 1.4 because some files have been moved from Taurus to Sardana

* Mon Jun 10 2013 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.1-6.20130610git
- new git commits

* Wed May 08 2013 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.1-5.20130508git
- new git commits

* Mon May 06 2013 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.1-4.20130506git
- new git commits

* Fri Apr 12 2013 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.1-3.20130411git
- depend on python-qub

* Fri Apr 12 2013 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.1-2.20130411git
- fix conflict with filesystem package
- skip doc generation

* Thu Apr 11 2013 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.1-1.20130411git
- use default installation prefix
- build from git snapshot. no patches

* Wed Nov 21 2012 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.0-3
- add patch: scripts-use-python2.6.patch

* Thu Jun 21 2012 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.0-2
- rebuild for new repository layout

* Mon May 14 2012 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 3.0.0-1
- svn revision 18517
- drop patch: install-taurus.core.tauv1-module.patch (module removed upstream)
- add patch: install-taurus.qt.qtgui.shell-module.patch
- add patch: add-build_doc-use-inkscape-option.patch
- add patch: add-no-doc-option-to-install-target.patch

* Wed Nov 30 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-12.20111130svn18517
- svn revision 18517
- move to PRE_PYPOOL branch (trunk requires development PyTango)

* Wed Aug 31 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-11.20110831svn17704
- apply patch: install-taurus.core.tauv1-module.patch
- apply patch: taurusplot-qwt-5.1-compatibility.patch

* Wed Aug 31 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-10.20110831svn17704
- svn revision 17704
- apply patch: install-taurus.core.utils-module.patch

* Fri Aug 26 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-9.20110824svn17658
- rename python26 package: python26-taurus
- apply patch: spyderlib-translation-fix.patch

* Thu Aug 25 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-8.20110824svn17658
- svn revision 17658
- requires python-guiqwt

* Tue Jul 05 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-7.20110705svn17131
- svn revision 17131

* Mon Jun 27 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-6.20110627svn17095
- svn revision 17095

* Tue Jun 07 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-5.20110607svn17046
- svn revision 17046
- requires PyMca

* Tue May 31 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-4.20110531svn16967
- svn revision 16967

* Fri May 20 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-3.20110520svn16918
- svn revision 16918

* Thu May 12 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-2.20110512svn16856
- svn revision 16856

* Wed Apr 06 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.1.1-1
- update to version 2.1.1

* Tue Apr 05 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.0.0-2
- depend on python-lxml and python-ply
- generate and install documentation on fedora and el6

* Tue Mar 08 2011 Andreas Persson <andreas_g.persson@maxlab.lu.se> - 2.0.0-2
- initial package

