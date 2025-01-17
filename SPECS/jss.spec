################################################################################
Name:           jss
################################################################################

Summary:        Java Security Services (JSS)
URL:            http://www.dogtagpki.org/wiki/JSS
License:        MPLv1.1 or GPLv2+ or LGPLv2+

Version:        4.4.9
Release:        4%{?dist}

# To generate the source tarball:
# $ git clone https://github.com/dogtagpki/jss.git
# $ cd jss
# $ git tag v4.4.<z>
# $ git push origin v4.4.<z>
# Then go to https://github.com/dogtagpki/jss/releases and download the source
# tarball.
Source:         https://github.com/dogtagpki/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

# To create a patch for all changes since a version tag:
# $ git format-patch \
#     --stdout \
#     <version tag> \
#     > jss-VERSION-RELEASE.patch
Patch0: 0001-Remove-space-from-AlgorithmId.toString.patch
Patch1: 0002-Fix-SHA512withRSA-PSS-identifier.patch
Patch2: 0003-Add-AlgorithmId.toStringWithParams-fix-toString.patch
Patch3: 0004-More-SHA256withRSA-PSS-algorithm-fixes.-Various-typo.patch
Patch4: 0005-Related-Bug-1710105-JSS-add-RSA-PSS-support.patch
Patch5: 0006-Update-.gitignore.patch
Patch6: 0007-Update-CI-tests.patch
Patch7: 0008-Add-GitLab-synchronization-job.patch
Patch8: 0009-Fix-Bug-2180920-add-AES-support-for-TMS-server-side-.patch
#Patch9: 0010-Fix-Issue-RHCS-4675.patch
Patch10: 0011-Bug2184930_Fix-AIA-externsion-print.patch
Patch11: 0012-Bug2209624_Fix-SIA-extension.patch


Conflicts:      idm-console-framework < 1.1.17-4
Conflicts:      pki-base < 10.4.0
Conflicts:      tomcatjss < 7.2.1

# autosetup
BuildRequires:  git

BuildRequires:  nss-devel >= 3.90.0-2
BuildRequires:  nspr-devel >= 4.35.0-1
BuildRequires:  java-1.8.0-openjdk-devel
BuildRequires:  jpackage-utils
%if 0%{?fedora} >= 25 || 0%{?rhel} > 7
BuildRequires:  perl-interpreter
%endif
BuildRequires:  apache-commons-lang
BuildRequires:  apache-commons-codec

Requires:       nss >= 3.90.0-2
Requires:       java-1.8.0-openjdk-headless
Requires:       jpackage-utils
Requires:       apache-commons-lang
Requires:       apache-commons-codec

%description
Java Security Services (JSS) is a java native interface which provides a bridge
for java-based applications to use native Network Security Services (NSS).
This only works with gcj. Other JREs require that JCE providers be signed.

################################################################################
%package javadoc
################################################################################

Summary:        Java Security Services (JSS) Javadocs
Group:          Documentation
Requires:       jss = %{version}-%{release}

%description javadoc
This package contains the API documentation for JSS.

################################################################################
%prep

%autosetup -n %{name}-%{version} -p 1 -S git

# Prior to version 4.4.5, the source code were stored under "jss-<version>/jss"
# path in the source tarball. Starting from version 4.4.5, the files will be
# stored under "jss-<version>" path. However, since the build system is still
# using the old path (introduced via sandboxing), the unpacked source code has
# to be moved to the old path with the following commands. Otherwise, even
# though we're linking against system libraries, the build will complain about
# a missing sandbox.

cd ..
mv %{name}-%{version} jss
mkdir %{name}-%{version}
mv jss %{name}-%{version}

################################################################################
%build

%if 0%{?fedora} >= 27
%set_build_flags
%endif

[ -z "$JAVA_HOME" ] && export JAVA_HOME=%{_jvmdir}/java
[ -z "$USE_INSTALLED_NSPR" ] && export USE_INSTALLED_NSPR=1
[ -z "$USE_INSTALLED_NSS" ] && export USE_INSTALLED_NSS=1

# Enable compiler optimizations and disable debugging code
# NOTE: If you ever need to create a debug build with optimizations disabled
# just comment out this line and change in the %%install section below the
# line that copies jars xpclass.jar to be xpclass_dbg.jar
export BUILD_OPT=1

# Generate symbolic info for debuggers
XCFLAGS="-g $RPM_OPT_FLAGS"
export XCFLAGS

PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1

export PKG_CONFIG_ALLOW_SYSTEM_LIBS
export PKG_CONFIG_ALLOW_SYSTEM_CFLAGS

NSPR_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nspr | sed 's/-I//'`
NSPR_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nspr | sed 's/-L//'`

NSS_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nss | sed 's/-I//'`
NSS_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nss | sed 's/-L//'`

export NSPR_INCLUDE_DIR
export NSPR_LIB_DIR
export NSS_INCLUDE_DIR
export NSS_LIB_DIR

%if 0%{?__isa_bits} == 64
USE_64=1
export USE_64
%endif

# The Makefile is not thread-safe
make -C jss/coreconf
make -C jss
make -C jss javadoc

################################################################################
%install

# Copy the license files here so we can include them in %%doc
cp -p jss/MPL-1.1.txt .
cp -p jss/gpl.txt .
cp -p jss/lgpl.txt .

# There is no install target so we'll do it by hand

# jars
install -d -m 0755 $RPM_BUILD_ROOT%{_jnidir}
# NOTE: if doing a debug no opt build change xpclass.jar to xpclass_dbg.jar
install -m 644 dist/xpclass.jar ${RPM_BUILD_ROOT}%{_jnidir}/jss4.jar

# We have to use the name libjss4.so because this is dynamically
# loaded by the jar file.
install -d -m 0755 $RPM_BUILD_ROOT%{_libdir}/jss
install -m 0755 dist/Linux*.OBJ/lib/libjss4.so ${RPM_BUILD_ROOT}%{_libdir}/jss/
pushd  ${RPM_BUILD_ROOT}%{_libdir}/jss
    ln -fs %{_jnidir}/jss4.jar jss4.jar
popd

# javadoc
install -d -m 0755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -rp dist/jssdoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -p jss/jss.html $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -p jss/*.txt $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

# No ldconfig is required since this library is loaded by Java itself.
################################################################################
%files

%defattr(-,root,root,-)
%doc jss/jss.html jss/MPL-1.1.txt jss/gpl.txt jss/lgpl.txt
%{_libdir}/jss/*
%{_jnidir}/*
%{_libdir}/jss/lib*.so

################################################################################
%files javadoc

%defattr(-,root,root,-)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*

################################################################################
%changelog
* Tue Mar 5 2024 Dogtag PKI Team <pki-devel@redhat.com> 4.4.9-4
- Updated nspr-devel and nss-devel build requirements as well as nss runtime
  requirements [mharmsen]
- RHEL-18401 - JSS - add AES support for TMS server-side keygen on latest
  HSM / FIPS environment [RHEL 7.9.z] [jmagne]
- JSS: add RSA PSS support
  Add PSS cases to algorithm name translating method [jmagne]
- Add GitLab synchronization job [edewata]
- Add AES support for TMS server-side keygen on latest
  HSM / FIPS environment [RHCS 9.7.z]
  Back port AES KWP wrap alg support only for JSS in this branch to allow for
  the TMS bug referenced above to work. [jmagne]
- Empty commit to fix commit msg from previous commit
  JSS- add AES support for TMS server-side keygen on latest HSM / FIPS
  environment [RHCS 9.7.z]
  Back port AES KWP wrap alg support only for JSS in this branch to allow for
  the TMS bug referenced above to work. [jmagne]
- RHEL-23935 - JSS - PrettyPrintCert does not properly translate AIA
  information into a readable format [RHEL 7.9.z] [mfargett]
- Fix AIA extension print
  The "Authority Info Access" extension was not included in the oid
  extension  map so it was not correctly printed.
  This add AIA extension to the oid map. [mfargett]
- Fix SIA extension
  The "Subject Info Access" extension was not included in the oid
  extension  map so it was not correctly printed.
  This add SIA extension to the oid map. [mfargett]

* Thu May 7 2020 Dogtag PKI Team <pki-devel@redhat.com> 4.4.9-3
- Fix issue with RSA/PSS and SHA-512
  Bugzilla #1710105

* Fri Apr 3 2020 Dogtag PKI Team <pki-devel@redhat.com> 4.4.9-2
- Update v4.4.9 to match upstream

* Fri Apr 3 2020 Dogtag PKI Team <pki-devel@redhat.com> 4.4.9-1
- Rebase to JSS v4.4.9
  Bugzilla #1818631 - Rebase JSS to v4.4.9 in RHEL 7.9

* Sun Mar 29 2020 Dogtag PKI Team <pki-devel@redhat.com> 4.4.7-3
- Bugzilla #1710105 - JSS: add RSA PSS support (jmagne)
- Bugzilla #1796642 - JSS -- remove hardcoded native library
  /usr/lib{64}/jss/libjss4.so (ascheel)

* Wed Sep 11 2019 Dogtag PKI Team <pki-devel@redhat.com> 4.4.7-2
- Bugzilla #1747967 - CVE 2019-14823 jss: OCSP policy "Leaf and Chain" implicitly trusts the root certificate

* Mon Aug  5 2019 Dogtag PKI Team <pki-devel@redhat.com> 4.4.7-1
- Bugzilla #1733590 - Rebase JSS in RHEL 7.8 (ascheel)

* Fri Mar 15 2019 Dogtag PKI Team <pki-devel@redhat.com> 4.4.6-1
- Bugzilla #1659527 - Rebase JSS in RHEL 7.7 (ascheel)

* Thu Jul  5 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-3
- Bugzilla #1534772 - org.mozilla.jss.pkix.primitive.AlgorithmIdentifier
  decode/encode process alters original data (cfu)
- Bugzilla #1554056 - JSS: Add support for TLS_*_SHA384 ciphers (cfu)

* Thu Jun 21 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-2
- Red Hat Bugzilla #1560682 - (RFE) Migrate RHCS x509 cert and crl
  functionality to JSS (jmagne)

* Tue May 29 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-1
- Rebased to JSS 4.4.4

* Thu Apr 05 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.3-1
- Rebased to JSS 4.4.3
#- Red Hat Bugzilla #1548548 - Partial Fedora build flags injection
