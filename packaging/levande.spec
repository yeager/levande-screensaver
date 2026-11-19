Name:           levande-screensaver
Version:        0.1.1
Release:        1%{?dist}
Summary:        Animated screensavers for GNOME
License:        GPL-3.0-or-later
URL:            https://github.com/yeager/levande-screensaver
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3, python3-gobject, python3-cairo, gtk4

%description
Nine animated scenes with GNOME idle monitoring and lock integration.

%prep
%setup -q

%install
install -d %{buildroot}%{_datadir}/levande/assets %{buildroot}%{_datadir}/applications %{buildroot}%{_sysconfdir}/xdg/autostart
install -m 755 levande.py idle.py %{buildroot}%{_datadir}/levande/
install -m 644 assets/*.png %{buildroot}%{_datadir}/levande/assets/
install -d %{buildroot}%{_datadir}/levande/locale/sv/LC_MESSAGES
install -m 644 locale/sv/LC_MESSAGES/*.mo %{buildroot}%{_datadir}/levande/locale/sv/LC_MESSAGES/
install -m 644 packaging/levande.desktop %{buildroot}%{_datadir}/applications/
install -m 644 packaging/levande-idle.desktop %{buildroot}%{_sysconfdir}/xdg/autostart/

%files
%{_datadir}/levande
%{_datadir}/applications/levande.desktop
%{_sysconfdir}/xdg/autostart/levande-idle.desktop
