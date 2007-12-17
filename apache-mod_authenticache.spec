#Module-Specific definitions
%define mod_name mod_authenticache
%define mod_conf 28_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	A generic credential caching module for the apache Web server
Name:		apache-%{mod_name}
Version:	2.0.8
Release:	%mkrel 6
Group:		System/Servers
License:	Apache License
URL:		http://killa.net/infosec/mod_authenticache/
Source0:	http://killa.net/infosec/mod_authenticache/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Source2:	%{mod_name}-example_files.tar.bz2
Patch0:		mod_authenticache-2.0.8-apache220.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1

%description
%{mod_name} provides a simple and generic method for caching
authentication information on the client side in order to enhance
performance. It has been tested with several Basic HTTP
authentication modules, and has an Apache 2.0.x optional function
exporter for caching credentials from any custom authentication module. 

%prep

%setup -q -n %{mod_name}-%{version} -a2
%patch0 -p0

# fix version string
#perl -pi -e "s|^#define VERSION.*|#define VERSION \"%{version}\"|g" defines.h

# fix strange attribs
chmod 644 *

# fix version string
echo "#define VERSION \"%{version}\"" >> defines.h

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%{_sbindir}/apxs -c %{mod_name}.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# make the example work... (ugly, but it works...)
NEW_URL=%{_docdir}/%{name}-%{version}/
perl -pi -e "s|_REPLACE_ME_|$NEW_URL|g" %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}
perl -pi -e "s|_REPLACE_ME_|$NEW_URL|g" .htaccess

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc .htaccess .htpasswd index.html
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*
