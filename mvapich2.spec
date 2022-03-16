%{!?python3_sitearch: %global python3_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:            mvapich2
Version:         2.3.6
Release:         1
Summary:         OSU MVAPICH2 MPI package
License:         BSD and MIT
URL:             http://mvapich.cse.ohio-state.edu
Source:          http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-%{version}.tar.gz
Source1:         mvapich2.module.in
Source2:         mvapich2.macros.in
Patch0010:       add-riscv-support.patch
BuildRequires:   gcc-gfortran python3-devel gcc-c++
BuildRequires:   bison flex autoconf automake libtool
BuildRequires:   perl-Digest-MD5 hwloc-devel rdma-core-devel

%ifarch x86_64
BuildRequires:   libpsm2-devel >= 10.3.58
%endif
Provides:        mpi
Requires:        environment-modules

%description
MVAPICH2 is a Message Passing Interface (MPI 3.0) ,over InfiniBand,
Omni-Path, Ethernet/iWARP, RoCE.

%package devel
Summary:         Development files for mvapich2
Provides:        mpi-devel
Requires:        rdma-core-devel
Requires:        mvapich2 = %{version}-%{release} gcc-gfortran

%description devel
Provides development headers and libraries for mvapich2.

%package help
Summary:         Documentation files for mvapich2
BuildArch:       noarch
Provides:        mvapich2-doc = %{version}-%{release}
Obsoletes:       mvapich2-doc < %{version}-%{release}

%description help
Help and additional documentation for mvapich2.

%ifarch x86_64
%package psm2
Summary:         OSU MVAPICH2 MPI package 2.3 for Omni-Path adapters
Provides:        mpi
Requires:        environment-modules

%description psm2
MVAPICH2 is a Message Passing Interface (MPI 3.0) ,over InfiniBand, Omni-Path,
Ethernet/iWARP, RoCE. And mvapich2-psm2 is a version of mvapich2 2.3 transport
for Omni-Path adapters.

%package psm2-devel
Summary:         Development files for mvapich2-psm2
Provides:        mpi-devel
Requires:        rdma-core-devel
Requires:        mvapich2-psm2 = %{version}-%{release} gcc-gfortran

%description psm2-devel
Provides development headers and libraries for mvapich2-psm2.

%package psm2-help
Summary:         Documentation files for mvapich2-psm2

%description psm2-help
Help and additional documentation for mvapich2-psm2.
%endif

%define module_name mvapich2%{?pack_suff}
%define p_prefix /usr/%_lib/mpi/gcc/%{module_name}
%define p_bindir  %{p_prefix}/bin
%define p_datadir %{p_prefix}/share
%define p_includedir %{p_prefix}/include
%define p_mandir  %{p_datadir}/man
%define p_libdir  %{p_prefix}/%{_lib}
%define p_libexecdir %{p_prefix}/%{_lib}
%define _moduledir /usr/share/modules/gnu-%{module_name}
%define package_name mvapich2%{?pack_suff}

%prep
%setup -q -n mvapich2-%{version}%{?rc_ver}
cp /usr/share/automake*/config.* .

%patch10 -p1

%build
%set_build_flags
PERL_USE_UNSAFE_INC=1 ./autogen.sh

%configure \
    --prefix=%{p_prefix} \
    --exec-prefix=%{p_prefix} \
    --datadir=%{p_datadir} \
    --bindir=%{p_bindir} \
    --includedir=%{p_includedir} \
    --libdir=%{p_libdir} \
    --libexecdir=%{p_libexecdir} \
    --mandir=%{p_mandir} \
   --docdir=%{_datadir}/doc/%{name} \
   --disable-wrapper-rpath \
   --enable-yield=sched_yield \
%ifarch x86_64
   --with-device=ch3:psm \
   --with-psm2=/usr \
%endif
  --without-mpe

make %{?_smp_mflags} V=1

%install
make DESTDIR=%{buildroot} V=1 install

rm -f %{buildroot}%{p_libdir}/libfmpich.la \
      %{buildroot}%{p_libdir}/libmpich.la \
      %{buildroot}%{p_libdir}/libmpichcxx.la \
      %{buildroot}%{p_libdir}/libmpichf90.la \
      %{buildroot}%{p_libdir}/libmpl.la \
      %{buildroot}%{p_libdir}/libopa.la \
      %{buildroot}%{p_libdir}/libmpi.la \
      %{buildroot}%{p_libdir}/libmpicxx.la \
      %{buildroot}%{p_libdir}/libmpifort.la
install -m 0755 -d %{buildroot}%{_datadir}/doc/%{name}
install -m 0644 COPYRIGHT* %{buildroot}%{_datadir}/doc/%{name}
install -m 0644 CHANGE* %{buildroot}%{_datadir}/doc/%{name}

install -m 0755 -d %{buildroot}%{_bindir}
sed -e 's,prefix,%p_prefix,g' -e 's,libdir,%{p_libdir},g' %{S:1} > %{buildroot}%{p_bindir}/mpivars.sh
sed -e 's,prefix,%p_prefix,g' -e 's,libdir,%{p_libdir},g' %{S:2} > %{buildroot}%{p_bindir}/mpivars.csh

mkdir -p %{buildroot}%{_moduledir}

cat << EOF > %{buildroot}%{_moduledir}/%{version}
#%%Module
proc ModulesHelp { } {
        global dotversion
        puts stderr "\tLoads the gnu - mvapich2 %{version}  Environment"
}

module-whatis  "Loads the gnu mvapich2 %{version} Environment."
conflict gnu-mvapich2
prepend-path PATH %{%p_bindir}
prepend-path INCLUDE %{p_includedir}
prepend-path INCLUDE %{p_libdir}
prepend-path MANPATH %{p_mandir}
prepend-path LD_LIBRARY_PATH %{p_libdir}

EOF

cat << EOF > %{buildroot}%{_moduledir}/.version
#%%Module1.0
set ModulesVersion "%{version}"

EOF

%global namearch mvapich2-%{_arch}
%files
%defattr(-, root, root)
%dir /usr/%_lib/mpi
%dir /usr/%_lib/mpi/gcc
%dir /usr/share/modules
%dir %{_moduledir}
%{_moduledir}
%doc %{_datadir}/doc/%{name}/COPYRIGHT*
%doc %{_datadir}/doc/%{name}/CHANGE*
%dir %{p_prefix}
%dir %{p_bindir}
%dir %{p_datadir}
%dir %{p_includedir}
%dir %{p_mandir}
%dir %{p_mandir}/man1
%dir %{p_mandir}/man3
%dir %{p_libdir}
%dir %{p_libexecdir}
%{p_bindir}/*
%{p_libexecdir}/osu-micro-benchmarks
%{p_mandir}/man1/*
%{p_libdir}/*.so.*

%files devel
%defattr(-,root,root)
%dir %{p_libdir}/pkgconfig
%{p_mandir}/man3/*
%{p_includedir}
%{p_libdir}/*.so
%{p_libdir}/pkgconfig/mvapich2.pc
%{p_libdir}/pkgconfig/openpa.pc
%{p_libdir}/*.a

%files help
%defattr(-, root, root)
%doc %{_datadir}/doc/%{name}
%exclude /%{_datadir}/doc/%{name}/COPYRIGHT*
%exclude /%{_datadir}/doc/%{name}/CHANGE*


%ifarch x86_64
%files psm2
%dir %{_libdir}/mvapich2-psm2
%dir %{_libdir}/mvapich2-psm2/bin
%dir %{_libdir}/mvapich2-psm2/lib
%dir %{_fmoddir}/mvapich2-psm2
%dir %{python3_sitearch}/mvapich2-psm2

%{_libdir}/mvapich2-psm2/bin/hydra*
%{_libdir}/mvapich2-psm2/bin/mpichversion
%{_libdir}/mvapich2-psm2/bin/mpiexec*
%{_libdir}/mvapich2-psm2/bin/mpiname
%{_libdir}/mvapich2-psm2/bin/mpirun*
%{_libdir}/mvapich2-psm2/bin/mpispawn
%{_libdir}/mvapich2-psm2/bin/mpivars
%{_libdir}/mvapich2-psm2/bin/parkill
%{_libdir}/mvapich2-psm2/lib/*.so.*
%{_sysconfdir}/modulefiles/mpi/mvapich2-psm2-x86_64

%files psm2-devel
%dir %{_includedir}/mvapich2-psm2-x86_64
%{_sysconfdir}/rpm/macros.mvapich2-psm2-x86_64
%{_includedir}/mvapich2-psm2-x86_64/*
%{_libdir}/mvapich2-psm2/bin/mpic++
%{_libdir}/mvapich2-psm2/bin/mpicc
%{_libdir}/mvapich2-psm2/bin/mpicxx
%{_libdir}/mvapich2-psm2/bin/mpif*
%{_libdir}/mvapich2-psm2/lib/pkgconfig
%{_libdir}/mvapich2-psm2/lib/*.a
%{_libdir}/mvapich2-psm2/lib/*.so

%files psm2-help
%dir %{_mandir}/mvapich2-psm2-x86_64
%dir %{_mandir}/mvapich2-psm2-x86_64/man*
%{_mandir}/mvapich2-psm2-x86_64/man1/*
%{_mandir}/mvapich2-psm2-x86_64/man3/*
%endif


%changelog
* Tue 15 Mar 2022 misaka00251 <misaka00251@misakanet.cn> 2.3.6-1
- Add RISC-V support (patch by Andreas Schwab)
- Upgrade package version

* Sat 07 Aug 2021 sunguoshuai <sunguoshuai@huawei.com> - 2.3-11
- fix build error with gcc 10,include allow mismatched arguement and multiple definition

* Wed July 9 2021 zhaoyao <zhaoyao32@huawei.com> - 2.3-10
- fix build error: Abording because C++ compiler does not work.

* Sat Mar 27 2021 zhanghua <zhanghua40@huawei.com> - 2.3-9
- fix build error, replace deprecated sys_siglist with strsignal

* Tue Jul 28 2020 lingsheng <lingsheng@huawei.com> - 2.3-8
- Synchronize buildrequire.

* Sat Mar 14 2020 sunguoshuai <sunguoshuai@huawei.com> - 2.3-7
- del rpm-mpi-hooks deps.

* Fri Nov 22 2019 sunguoshuai <sunguoshuai@huawei.com> - 2.3-6
- Package init.
