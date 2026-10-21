# modules/xrealInterfaceLibrary
%global commit1 61ecd4ccccdce06cd7f38561cc3b9743231a694f
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})
# modules/xrealInterfaceLibrary/interface_lib/modules/hidapi
%global commit2 9904cbea94b9f7268a4bb526a1d32ac36e699aee
%global shortcommit2 %(c=%{commit2}; echo ${c:0:7})
# modules/xrDeviceKit
%global commit3 586520b4b45790076e9f96f3507409dcf56fd913
%global shortcommit3 %(c=%{commit3}; echo ${c:0:7})
# modules/xrDeviceKit/modules/Fusion
%global commit4 b607fc32d2d8dd1ac5fb9f81ca8244dda6e58ddf
%global shortcommit4 %(c=%{commit4}; echo ${c:0:7})
# modules/xrealAirDeviceKit
%global commit5 f4a24be31bd17cbed72aea9c7cef9349a8cfd3f0
%global shortcommit5 %(c=%{commit5}; echo ${c:0:7})
# modules/xrealOneDeviceKit
%global commit6 f5833f611265f418b1ea549da20dc4764d86a4ec
%global shortcommit6 %(c=%{commit6}; echo ${c:0:7})
# modules/xrealOneDeviceKit/modules/xreal_one_driver
%global commit7 3e912315ec16e94e9a47688770d649cfef293624
%global shortcommit7 %(c=%{commit7}; echo ${c:0:7})

# Prebuilt vendor SDKs and their dependencies are private to the driver
%global __provides_exclude_from ^%{_libdir}/%{name}/.*$
%global __requires_exclude ^lib(carina_vio|glasses|GlassSDK|RayNeoXRMiniSDK|opencv_[a-z0-9]+)\\.so.*$

Name:           xr-driver
Version:        2.11.9
Release:        1%{?dist}
Summary:        User space driver for XR glasses
# The VITURE, Rokid and TCL/RayNeo SDKs are prebuilt binaries, each under its
# own proprietary license.
License:        GPL-3.0-or-later AND MIT AND (BSD-3-Clause OR GPL-3.0-only OR HIDAPI)
URL:            https://github.com/wheaney/XRLinuxDriver
# Vendor SDKs are only available for these architectures:
ExclusiveArch:  x86_64 aarch64

Source0:        %{url}/archive/v%{version}/XRLinuxDriver-%{version}.tar.gz
Source1:        https://gitlab.com/wheaney/nrealAirLinuxDriver/-/archive/%{commit1}/nrealAirLinuxDriver-%{shortcommit1}.tar.gz
Source2:        https://github.com/libusb/hidapi/archive/%{commit2}.tar.gz#/hidapi-%{shortcommit2}.tar.gz
Source3:        https://github.com/wheaney/xrDeviceKit/archive/%{commit3}.tar.gz#/xrDeviceKit-%{shortcommit3}.tar.gz
Source4:        https://github.com/xioTechnologies/Fusion/archive/%{commit4}.tar.gz#/Fusion-%{shortcommit4}.tar.gz
Source5:        https://github.com/wheaney/xrealAirDeviceKit/archive/%{commit5}.tar.gz#/xrealAirDeviceKit-%{shortcommit5}.tar.gz
Source6:        https://github.com/wheaney/xrealOneDeviceKit/archive/%{commit6}.tar.gz#/xrealOneDeviceKit-%{shortcommit6}.tar.gz
Source7:        https://github.com/rohitsangwan01/xreal_one_driver/archive/%{commit7}.tar.gz#/xreal_one_driver-%{shortcommit7}.tar.gz
Patch0:         %{name}-no-submodule-update.patch

BuildRequires:  cargo
BuildRequires:  cargo-rpm-macros
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  libatomic
BuildRequires:  patchelf
BuildRequires:  python3
BuildRequires:  python3-pyyaml
BuildRequires:  rust
BuildRequires:  systemd-rpm-macros
BuildRequires:  (crate(byteorder/default) >= 1.4 with crate(byteorder/default) < 2)
BuildRequires:  pkgconfig(json-c)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libevdev)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(wayland-client)

Requires:       /usr/bin/curl
Requires:       jq

Provides:       bundled(fusion) = 1.2.8
Provides:       bundled(hidapi) = 0.16.0

%description
User space driver for XR glasses from VITURE, XREAL, Rokid and TCL/RayNeo. It
reads the head tracking data from the glasses and makes it available to the
Breezy Desktop GNOME Shell extension and KWin effect, and can also output it as
mouse or joystick movements.

The VITURE, Rokid and TCL/RayNeo support relies on the proprietary SDKs from
the respective vendors. Rokid and TCL/RayNeo glasses are supported only on
x86_64.

%prep
%autosetup -p1 -n XRLinuxDriver-%{version}

mkdir -p modules/xrealInterfaceLibrary/interface_lib/modules/hidapi \
    modules/xrDeviceKit/modules/Fusion \
    modules/xrealAirDeviceKit \
    modules/xrealOneDeviceKit/modules/xreal_one_driver
tar -xzf %{SOURCE1} --strip-components=1 -C modules/xrealInterfaceLibrary
tar -xzf %{SOURCE2} --strip-components=1 -C modules/xrealInterfaceLibrary/interface_lib/modules/hidapi
tar -xzf %{SOURCE3} --strip-components=1 -C modules/xrDeviceKit
tar -xzf %{SOURCE4} --strip-components=1 -C modules/xrDeviceKit/modules/Fusion
tar -xzf %{SOURCE5} --strip-components=1 -C modules/xrealAirDeviceKit
tar -xzf %{SOURCE6} --strip-components=1 -C modules/xrealOneDeviceKit
tar -xzf %{SOURCE7} --strip-components=1 -C modules/xrealOneDeviceKit/modules/xreal_one_driver

cp modules/xrealInterfaceLibrary/LICENSE.md LICENSE.xrealInterfaceLibrary.md
cp modules/xrealInterfaceLibrary/interface_lib/modules/hidapi/LICENSE.txt LICENSE.hidapi.txt
cp modules/xrDeviceKit/modules/Fusion/LICENSE.md LICENSE.Fusion.md
cp modules/xrealOneDeviceKit/modules/xreal_one_driver/LICENSE LICENSE.xreal_one_driver

pushd modules/xrealOneDeviceKit/modules/xreal_one_driver
%cargo_prep
popd

# Use system libusb
rm -f lib/x86_64/viture/libusb-1.0.so*
# OpenCV is used only by the x86_64 VITURE SDK, and it does not need videoio
rm -f lib/x86_64/viture/libopencv_*.so.4.2.0 lib/x86_64/viture/libopencv_videoio.so*
rm -f lib/aarch64/viture/libopencv_*

%build
export RUSTFLAGS="%{build_rustflags}"
%cmake
%cmake_build

%install
install -p -m 0755 -D %{_vpath_builddir}/xrDriver %{buildroot}%{_bindir}/xrDriver
patchelf --set-rpath %{_libdir}/%{name} %{buildroot}%{_bindir}/xrDriver
install -p -m 0755 bin/xr_driver_cli bin/xr_driver_logs %{buildroot}%{_bindir}/

mkdir -p %{buildroot}%{_libdir}/%{name}
install -p -m 0755 lib/%{_target_cpu}/viture/lib{carina_vio,glasses}.so %{buildroot}%{_libdir}/%{name}/
%ifarch x86_64
install -p -m 0755 lib/x86_64/lib{GlassSDK,RayNeoXRMiniSDK}.so lib/x86_64/viture/libopencv_*.so.4.2 \
    %{buildroot}%{_libdir}/%{name}/
%endif
for lib in %{buildroot}%{_libdir}/%{name}/*; do
    patchelf --set-rpath '$ORIGIN' $lib
done

mkdir -p %{buildroot}%{_udevrulesdir}
install -p -m 0644 udev/*.rules %{buildroot}%{_udevrulesdir}/

mkdir -p %{buildroot}%{_modulesloaddir}
echo uinput > %{buildroot}%{_modulesloaddir}/%{name}.conf

sed -i -e '/^Environment=/d' -e 's|{bin_dir}|%{_bindir}|g' systemd/%{name}.service
install -p -m 0644 -D systemd/%{name}.service %{buildroot}%{_userunitdir}/%{name}.service

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%postun
%systemd_user_postun_with_restart %{name}.service

%files
%license LICENSE LICENSE.xrealInterfaceLibrary.md LICENSE.hidapi.txt LICENSE.Fusion.md LICENSE.xreal_one_driver
%doc README.md
%{_bindir}/xrDriver
%{_bindir}/xr_driver_cli
%{_bindir}/xr_driver_logs
%{_libdir}/%{name}
%{_modulesloaddir}/%{name}.conf
%{_udevrulesdir}/70-rayneo-xr.rules
%{_udevrulesdir}/70-rokid-xr.rules
%{_udevrulesdir}/70-uinput-xr.rules
%{_udevrulesdir}/70-viture-xr.rules
%{_udevrulesdir}/70-xreal-xr.rules
%{_userunitdir}/%{name}.service

%changelog
* Wed Oct 21 2026 Simone Caronni <negativo17@gmail.com> - 2.11.9-1
- First build.
