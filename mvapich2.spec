%{!?python3_sitearch: %global python3_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:            mvapich2
Version:         2.3
Release:         8
Summary:         OSU MVAPICH2 MPI package
License:         BSD and MIT
URL:             http://mvapich.cse.ohio-state.edu
Source:          http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-%{version}.tar.gz
Source1:         mvapich2.module.in
Source2:         mvapich2.macros.in
Patch0001:       0001-mvapich23-unbundle-contrib-hwloc.patch
Patch0002:       0002-mvapich23-unbundle-osu_benchmarks.patch
BuildRequires:   gcc-gfortran python3-devel
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

%prep
%autosetup -n %{name}-%{version} -p1
rm -r contrib/ limic2-0.5.6/ osu_benchmarks/

find . -name configure -exec \
    sed -i -r 's/(hardcode_into_libs)=.*$/\1=no/' '{}' ';'

mkdir .default
mv * .default
mv .default default

%ifarch x86_64
cp -pr default psm2
%endif


%build
%set_build_flags
export AR=ar

%ifarch x86_64
cd psm2
%configure --prefix=%{_libdir}/mvapich2-psm2 --exec-prefix=%{_libdir}/mvapich2-psm2 \
    --bindir=%{_libdir}/mvapich2-psm2/bin --sbindir=%{_libdir}/mvapich2-psm2/bin \
    --libdir=%{_libdir}/mvapich2-psm2/lib --mandir=%{_mandir}/mvapich2-psm2-x86_64 \
    --includedir=%{_includedir}/mvapich2-psm2-x86_64 \
    --sysconfdir=%{_sysconfdir}/mvapich2-psm2-x86_64 --datarootdir=%{_datadir}/mvapich2-psm2 \
    --docdir=%{_docdir}/mvapich2 --enable-error-checking=runtime --enable-timing=none \
    --enable-g=mem,dbg,meminit --enable-fast=all --enable-shared --enable-static \
    --enable-fortran=all --enable-cxx --with-fuse=no --disable-silent-rules --disable-wrapper-rpath \
    --with-hwloc-prefix=system --with-device=ch3:psm --with-ftb=no --with-blcr=no \
    CC=gcc CFLAGS="-m64 -O3 -fno-strict-aliasing %{build_cflags} $XFLAGS" CXX=g++ \
    CXXFLAGS="-m64 -O3 %{build_cflags} $XFLAGS" FC=gfortran FCFLAGS="-m64 %{build_cflags} \
    $XFLAGS" F77=gfortran FFLAGS="-m64 %{build_cflags} $XFLAGS" LDFLAGS="%{build_ldflags}"

find . -name libtool -exec \
    sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g;
            s|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' '{}' ';'
%make_build
cd ..
%endif

%global namearch mvapich2-%{_arch}
cd default
%configure --prefix=%{_libdir}/mvapich2 --exec-prefix=%{_libdir}/mvapich2 \
    --bindir=%{_libdir}/mvapich2/bin --sbindir=%{_libdir}/mvapich2/bin \
    --libdir=%{_libdir}/mvapich2/lib --mandir=%{_mandir}/%{namearch} \
    --includedir=%{_includedir}/%{namearch} --sysconfdir=%{_sysconfdir}/%{namearch} \
    --datarootdir=%{_datadir}/mvapich2 --docdir=%{_docdir}/mvapich2 \
    --enable-error-checking=runtime --enable-timing=none --enable-g=mem,dbg,meminit \
    --enable-fast=all --enable-shared --enable-static --enable-fortran=all --enable-cxx \
    --disable-silent-rules --disable-wrapper-rpath --with-hwloc-prefix=system --with-ftb=no \
    --with-blcr=no --with-fuse=no \
    CC=gcc CFLAGS="-O3 -fno-strict-aliasing %{build_cflags} $XFLAGS" CXX=g++  \
    CXXFLAGS="-O3 %{build_cflags} $XFLAGS" FC=gfortran FCFLAGS="%{build_cflags} $XFLAGS" \
    F77=gfortran  FFLAGS="%{build_cflags} $XFLAGS" LDFLAGS="%{build_ldflags}"

find . -name libtool -exec \
    sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g;
            s|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' '{}' ';'
%make_build
cd ..

%install
finish_install() {
        local LIBNAME="$1"
        local NAMEARCH="$1-%{_arch}"
        %delete_la
        install -d %{buildroot}%{_mandir}/$NAMEARCH/man{2,4,5,6,7,8,9,n}
        install -d %{buildroot}/%{_fmoddir}/$1$4
        install -d %{buildroot}/%{python3_sitearch}/$1
        install -d %{buildroot}%{_sysconfdir}/modulefiles/mpi
        sed "s#@LIBDIR@#%{_libdir}/$1#g;
             s#@ETCDIR@#%{_sysconfdir}/$NAMEARCH#g;
             s#@FMODDIR@#%{_fmoddir}/$1$4#g;
             s#@INCDIR@#%{_includedir}/$NAMEARCH#g;
             s#@MANDIR@#%{_mandir}/$NAMEARCH#g;
             s#@PYSITEARCH@#%{python3_sitearch}/$1#g;
             s#@COMPILER@#$NAMEARCH#g;
             s#@SUFFIX@#_$1#g" < $2 \
                > %{buildroot}%{_sysconfdir}/modulefiles/mpi/$NAMEARCH

        install -d %{buildroot}%{_sysconfdir}/rpm
        sed "s#@MACRONAME@#${LIBNAME//[-.]/_}#g;
             s#@MODULENAME@#$NAMEARCH#" < $3 \
                > %{buildroot}/%{_sysconfdir}/rpm/macros.$NAMEARCH
}

install -d %{buildroot}%{_docdir}/mvapich2

%ifarch x86_64
cd psm2
%make_install
finish_install mvapich2-psm2 %SOURCE1 %SOURCE2 ""
cd ..
%endif

cd default
%make_install
finish_install mvapich2 %SOURCE1 %SOURCE2 ""
cd ..

%global namearch mvapich2-%{_arch}
%files
%dir %{_libdir}/mvapich2
%dir %{_libdir}/mvapich2/bin
%dir %{_libdir}/mvapich2/lib
%dir %{_fmoddir}/mvapich2
%dir %{python3_sitearch}/mvapich2

%{_libdir}/mvapich2/bin/hydra_*
%{_libdir}/mvapich2/bin/mpichversion
%{_libdir}/mvapich2/bin/mpiexec*
%{_libdir}/mvapich2/bin/mpiname
%{_libdir}/mvapich2/bin/mpirun*
%{_libdir}/mvapich2/bin/mpispawn
%{_libdir}/mvapich2/bin/mpivars
%{_libdir}/mvapich2/bin/parkill
%{_libdir}/mvapich2/lib/*.so.*
%{_sysconfdir}/modulefiles/mpi/%{namearch}

%files devel
%dir %{_includedir}/%{namearch}
%{_sysconfdir}/rpm/macros.%{namearch}
%{_includedir}/%{namearch}/*
%{_libdir}/mvapich2/bin/mpic++
%{_libdir}/mvapich2/bin/mpicc
%{_libdir}/mvapich2/bin/mpicxx
%{_libdir}/mvapich2/bin/mpif77
%{_libdir}/mvapich2/bin/mpif90
%{_libdir}/mvapich2/bin/mpifort
%{_libdir}/mvapich2/lib/pkgconfig
%{_libdir}/mvapich2/lib/*.a
%{_libdir}/mvapich2/lib/*.so

%files help
%{_docdir}/mvapich2
%dir %{_mandir}/%{namearch}
%dir %{_mandir}/%{namearch}/man*
%{_mandir}/%{namearch}/man1/*
%{_mandir}/%{namearch}/man3/*


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
* Tue Jul 28 2020 lingsheng <lingsheng@huawei.com> - 2.3-8
- Synchronize buildrequire.

* Sat Mar 14 2020 sunguoshuai <sunguoshuai@huawei.com> - 2.3-7
- del rpm-mpi-hooks deps.

* Fri Nov 22 2019 sunguoshuai <sunguoshuai@huawei.com> - 2.3-6
- Package init.
