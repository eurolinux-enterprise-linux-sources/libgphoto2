%bcond_with gp2ddb

%global udevdir %(pkg-config --variable=udevdir udev)
%global port_version 0.12.0

Name:           libgphoto2
Version:        2.5.15
Release:        3%{?dist}
Summary:        Library for accessing digital cameras
Group:          Development/Libraries
# GPLV2+ for the main lib (due to exif.c) and most plugins, some plugins GPLv2
License:        GPLv2+ and GPLv2
URL:            http://www.gphoto.org/

Source0:        http://downloads.sourceforge.net/gphoto/%{name}-%{version}.tar.bz2
Patch1:         gphoto2-pkgcfg.patch
Patch2:         gphoto2-storage.patch
Patch3:         gphoto2-ixany.patch
Patch4:         gphoto2-device-return.patch
Patch5:         gphoto2-ptp.patch
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  systemd
%if %{with gp2ddb}
BuildRequires:  flex
BuildRequires:  bison
%endif
BuildRequires:  libtool-ltdl-devel
BuildRequires:  libjpeg-devel
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  gd-devel
BuildRequires:  pkgconfig(libexif)
# -----------------------------------
# libgphoto2_port
# -----------------------------------
BuildRequires:  lockdev-devel
BuildRequires:  pkgconfig(libusb-1.0)
Requires:       lockdev
# -----------------------------------
Obsoletes:      gphoto2 < 2.4.0-11

%description
libgphoto2 is a library that can be used by applications to access
various digital cameras. libgphoto2 itself is not a GUI application,
opposed to gphoto. There are GUI frontends for the gphoto2 library,
however, such as gtkam for example.


%package devel
Summary:        Headers and links to compile against the libgphoto2 library
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libexif-devel
Obsoletes:      gphoto2-devel < 2.4.0-11
Provides:       gphoto2-devel = %{version}-%{release}

%description devel
libgphoto2 is a library that can be used by applications to access
various digital cameras. libgphoto2 itself is not a GUI application,
opposed to gphoto. There are GUI frontends for the gphoto2 library,
however, such as gtkam for example.

This package contains files needed to compile applications that
use libgphoto2.


%prep
%autosetup -p1
for f in AUTHORS ChangeLog COPYING libgphoto2_port/AUTHORS libgphoto2_port/COPYING.LIB `find -name 'README.*'`; do
    iconv -f ISO-8859-1 -t UTF-8 $f > $f.conv && mv -f $f.conv $f
done

%build
CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
CXXFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"

%configure \
    udevscriptdir='%{udevdir}'   \
    --with-drivers=all           \
    --with-doc-dir=%{_pkgdocdir} \
%if %{with gp2ddb}
    --enable-gp2ddb              \
%endif
    --disable-static             \
    --disable-rpath              \
    %{nil}

# Don't use rpath!
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool libgphoto2_port/libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool libgphoto2_port/libtool


%make_build

%install
%make_install INSTALL="install -p" mandir=%{_mandir}

pushd packaging/linux-hotplug/
  export LIBDIR=%{buildroot}%{_libdir}
  export CAMLIBS=%{buildroot}%{_libdir}/%{name}/%{version}
  export LD_LIBRARY_PATH=%{buildroot}%{_libdir}

  # Output udev rules for device identification; this is used by GVfs gphoto2
  # backend and others.
  mkdir -p %{buildroot}%{_udevrulesdir}
  %{buildroot}%{_libdir}/%{name}/print-camera-list udev-rules version 136 > %{buildroot}%{_udevrulesdir}/40-libgphoto2.rules
popd

# remove circular symlink in /usr/include/gphoto2 (#460807)
rm -f %{buildroot}%{_includedir}/gphoto2/gphoto2

# remove unneeded print-camera-list from libdir (#745081)
rm -f %{buildroot}%{_libdir}/libgphoto2/print-camera-list

find %{buildroot} -type f -name "*.la" -print -delete

%find_lang %{name}-6
%find_lang %{name}_port-12
cat libgphoto2*.lang >> %{name}.lang

# https://fedoraproject.org/wiki/Packaging_tricks#With_.25doc
mkdir __doc
mv %{buildroot}%{_pkgdocdir}/* __doc
rm -rf %{buildroot}%{_pkgdocdir}
rm -rf %{buildroot}%{_datadir}/libgphoto2_port/*/vcamera/

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


%files -f %{name}.lang
%license COPYING
%doc AUTHORS README NEWS
%{_libdir}/%{name}.so.*
%{_libdir}/%{name}_port.so.*
%dir %{_libdir}/%{name}/
%dir %{_libdir}/%{name}/%{version}/
%dir %{_libdir}/%{name}_port/
%dir %{_libdir}/%{name}_port/%{port_version}/
%{_libdir}/%{name}/%{version}/*.so
%{_libdir}/%{name}_port/%{port_version}/*.so
%{_udevrulesdir}/40-libgphoto2.rules
%{udevdir}/check-ptp-camera
%{_datadir}/libgphoto2/

%files devel
%doc __doc/*
%{_bindir}/gphoto2-config
%{_bindir}/gphoto2-port-config
%{_includedir}/gphoto2/
%{_libdir}/%{name}.so
%{_libdir}/%{name}_port.so
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/pkgconfig/%{name}_port.pc
%{_mandir}/man3/%{name}.3*
%{_mandir}/man3/%{name}_port.3*

%changelog
* Wed Mar 06 2019 Josef Ridky <jridky@redhat.com> - 2.5.15-3
- fix CFLAGS and CXXFLAGS content

* Wed Mar 06 2019 Josef Ridky <jridky@redhat.com> - 2.5.15-2
- Resolves: #1551747 - fix issue with get folder list

* Wed Oct 04 2017 Josef Ridky <jridky@redhat.com> - 2.5.15-1
- Resolves: #1463585 - rebase to the latest upstream version

* Wed Jun 21 2017 Debarshi Ray <rishi@fedoraproject.org> - 2.5.2-4
- BuildRequire libusbx-devel, not libusbx
Resolves: #1365875

* Tue Jun 20 2017 Debarshi Ray <rishi@fedoraproject.org> - 2.5.2-4
- Use only libusbx and drop libusb
Resolves: #1365875

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 2.5.2-3
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.5.2-2
- Mass rebuild 2013-12-27

* Mon May  6 2013 Hans de Goede <hdegoede@redhat.com> - 2.5.2-1
- New upstream release bugfix 2.5.2
- Drop bugfix patches (merged upstream)

* Sat May  4 2013 Hans de Goede <hdegoede@redhat.com> - 2.5.1.1-4
- Fix crash when dealing with PTP devices without a memory card (rhbz#915688)

* Thu May  2 2013 Hans de Goede <hdegoede@redhat.com> - 2.5.1.1-3
- Fix PTP devices not working in USB-3 ports (rhbz#819918)
- Cleanup spec-file

* Tue Apr 23 2013 Tim Waugh <twaugh@redhat.com> 2.5.1.1-2
- Use _udevrulesdir macro.

* Tue Feb 19 2013 Jindrich Novy <jnovy@redhat.com> 2.5.1.1-1
- update to 2.5.1.1

* Sun Feb 17 2013 Jindrich Novy <jnovy@redhat.com> 2.5.0-8
- fix camera detection - thanks to Panu Matilainen (#912040)

* Wed Jan 30 2013 Jindrich Novy <jnovy@redhat.com> 2.5.0-7
- move /lib files to /usr/lib
- fix changelog

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 2.5.0-6
- rebuild due to "jpeg8-ABI" feature drop

* Sun Jan 13 2013 Jindrich Novy <jnovy@redhat.com> 2.5.0-5
- remove deprecated HAL file (#894527)

* Sat Dec 01 2012 Jindrich Novy <jnovy@redhat.com> 2.5.0-4
- compile with -fno-strict-aliasing (because of ptp.c)

* Wed Sep 19 2012 Hans de Goede <hdegoede@redhat.com> 2.5.0-3
- Fix the usbscsi port driver not working, this fixes many miniature
  (keychain) photo frames no longer being accessible

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 Jindrich Novy <jnovy@redhat.com> 2.5.0-1
- update to 2.5.0

* Mon Apr 16 2012 Jindrich Novy <jnovy@redhat.com> 2.4.14-1
- update to 2.4.14

* Wed Mar 21 2012 Jindrich Novy <jnovy@redhat.com> 2.4.13-1
- update to 2.4.13

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.11-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 12 2011 Jindrich Novy <jnovy@redhat.com> 2.4.11-2
- remove unneeded print-camera-list from libdir (#745081)

* Mon Apr 18 2011 Jindrich Novy <jnovy@redhat.com> 2.4.11-1
- update to 2.4.11

* Wed Feb 09 2011 Jindrich Novy <jnovy@redhat.com> 2.4.10.1-1
- update to 2.4.10.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.10-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jan 26 2011 Caolán McNamara <caolanm@redhat.com> 2.4.10-4
- rebuild for dependencies

* Wed Oct 20 2010 Jindrich Novy <jnovy@redhat.com> 2.4.10-3
- move udev helper scripts to /lib/udev (#644552)

* Mon Sep 06 2010 Jindrich Novy <jnovy@redhat.com> 2.4.10-2
- BR: gd-devel because of ax203 and st2205 camlibs (#630570)

* Tue Aug 17 2010 Jindrich Novy <jnovy@redhat.com> 2.4.10-1
- update to 2.4.10

* Mon Jul 12 2010 Dan Horák <dan[at]danny.cz> 2.4.9-2
- remove the need to call autoreconf

* Mon Apr 12 2010 Jindrich Novy <jnovy@redhat.com> 2.4.9-1
- update to 2.4.9

* Mon Jan 25 2010 Jindrich Novy <jnovy@redhat.com> 2.4.8-1
- update to 2.4.8

* Fri Dec 18 2009 Jindrich Novy <jnovy@redhat.com> 2.4.7-3
- remove circular symlink in /usr/include/gphoto2 (#460807)

* Fri Oct 23 2009 Jindrich Novy <jnovy@redhat.com> 2.4.7-2
- return the dual-mode device to kernel once we don't use it (#530545)

* Tue Aug 18 2009 Jindrich Novy <jnovy@redhat.com> 2.4.7-1
- update to 2.4.7
- drop udev patch, applied upstream
- update storage patch

* Sun Aug 09 2009 David Zeuthen <davidz@redhat.com> 2.4.6-3
- Add patch from http://sourceforge.net/tracker/?func=detail&aid=2801117&group_id=8874&atid=308874
  and generate generic udev rules for device identification (ID_GPHOTO2* properties)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon May 18 2009 Jindrich Novy <jnovy@redhat.com> 2.4.6-1
- update to 2.4.6
- new IDs for Kodak V803, M1063, Canon PowerShot A650IS, SD990 (aka IXUS 980IS),
  SD880IS, A480, Canon EOS 50D, Fuji FinePix S1000fd
- many Canon related fixes

* Wed Apr 08 2009 Jindrich Novy <jnovy@redhat.com> 2.4.5-1
- update to 2.4.5
- remove .canontimeout patch, applied upstream

* Wed Apr 01 2009 Jindrich Novy <jnovy@redhat.com> 2.4.4-4
- increase timeouts for Canon cameras (#476355), thanks to
  Andrzej Nowak and Russell Harrison

* Thu Mar 05 2009 Caolán McNamara <caolanm@redhat.com> - 2.4.4-3
- tweak BR to get to build

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 22 2009 Jindrich Novy <jnovy@redhat.com> 2.4.4-1
- update to 2.4.4
- many fixes and improvements to Nikon and Canon cameras
- translation updates

* Thu Nov 13 2008 Rex Dieter <rdieter@fedoraproject.org> 2.4.3-2
- respin (libtool)

* Mon Oct 20 2008 Jindrich Novy <jnovy@redhat.com> 2.4.3-1
- update to libgphoto2-2.4.3

* Tue Sep 23 2008 Jindrich Novy <jnovy@redhat.com> 2.4.2-2
- convert all shipped docs to UTF-8

* Fri Aug 01 2008 Jindrich Novy <jnovy@redhat.com> 2.4.2-1
- update to 2.4.2
- contains many fixes in the Canon camera communication interface
- drop build patch, no more needed

* Mon Jul 07 2008 Jindrich Novy <jnovy@redhat.com> 2.4.1-6
- increase maximal number of entries in the camera list (#454245)

* Fri Jun 20 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 2.4.1-5
- fix pkgcfg patch to match actual .pc file names (fixes kdegraphics build)

* Thu Jun 12 2008 Jindrich Novy <jnovy@redhat.com> 2.4.1-3
- libgphoto2-devel requires libusb-devel and libexif-devel for
  pkgconfig

* Wed Jun 04 2008 Jindrich Novy <jnovy@redhat.com> 2.4.1-2
- fix obsoletes
- workaround problem with coreutils-6.12 and RHEL5-xen kernels
  what prevents libgphoto2 koji build

* Mon Jun 02 2008 Jindrich Novy <jnovy@redhat.com> 2.4.1-1
- update to 2.4.1 (#443515, #436138)

* Thu May 29 2008 Stepan Kasal <skasal@redhat.com> 2.4.0-3
- drop gphoto2-norpath.patch
- use quoted here-document in %%prep
- fix some typos in m4 sources
- run autoreconf to get autotools right

* Mon Apr 21 2008 Jindrich Novy <jnovy@redhat.com> 2.4.0-2
- apply patch to fix build with libusb

* Fri Apr 18 2008 Jindrich Novy <jnovy@redhat.com> 2.4.0-1
- backport patch from upstream to avoid segfault when
  data phase is skipped for certain devices (#435413)
- initial build

* Mon Apr 14 2008 Jindrich Novy <jnovy@redhat.com> 2.4.0-0.2
- review fixes, thanks to Hans de Goede: (#437285)
  - remove unused macro
  - don't exclude s390/s390x
  - preserve timestamps
  - fix license

* Thu Mar 13 2008 Jindrich Novy <jnovy@redhat.com> 2.4.0-0.1
- initial libgphoto2 packaging
