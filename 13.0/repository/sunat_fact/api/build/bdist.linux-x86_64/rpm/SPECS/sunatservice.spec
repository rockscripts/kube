%define name sunatservice
%define version 1.0.133
%define unmangled_version 1.0.133
%define unmangled_version 1.0.133
%define release 1

Summary: SUNAT - sign and verify xml
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: @rockscripts <rockscripts@gmail.com>
Url: https://instagram.com/rockscripts/

%description
Generate signatures for Sunat e-documents

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
