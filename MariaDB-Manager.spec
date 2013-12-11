%define _topdir	 	%(echo $PWD)/
%define name		MariaDB-Manager
%define release		##RELEASE_TAG##
%define version 	##VERSION_TAG##
%define buildroot 	%{_topdir}/%{name}-%{version}-%{release}root
%define install_path	/usr/local/skysql/

BuildRoot:		%{buildroot}
BuildArch:              noarch
Summary: 		MariaDB Manager
License: 		GPL
Name: 			%{name}
Version: 		%{version}
Release: 		%{release}
Source: 		%{name}-%{version}-%{release}.tar.gz
Prefix: 		/
Group: 			Development/Tools
Requires:		MariaDB-Manager-WebUI sqlite MariaDB-Manager-API MariaDB-Manager-Monitor tomcat7 = 7.0.39-1 gawk grep
#BuildRequires:		

%description
MariaDB Manager is a tool to manage and monitor a set of MariaDB
servers using the Galera multi-master replication form Codership.

%prep

%setup -q

%build

%post
mkdir -p /usr/local/skysql/SQLite/AdminConsole
chown -R apache:apache %{install_path}SQLite
mkdir -p /usr/local/skysql/config

sed -i 's/# chkconfig: -/# chkconfig: 2345/' /etc/init.d/httpd
rm -f /etc/rc{2,3,4,5}.d/K*httpd*
chkconfig --add httpd
/etc/init.d/httpd restart

# Not overwriting existing WebUI configurations
if [ ! -f /usr/local/skysql/config/manager.json ] ; then
	# Generating API key for WebUI
	newKey=$(echo $RANDOM$(date)$RANDOM | md5sum | cut -f1 -d" ")

	componentID=2
  keyString="${componentID} = \"${newKey}\""

	# Registering key on components.ini
	componentFile=/usr/local/skysql/config/components.ini
	grep "^${componentID} = \"" ${componentFile} &>/dev/null
	if [ "$?" != "0" ] ; then
		echo $keyString >> $componentFile
	fi

	# Registering key on api.ini
	grep "^${componentID} = \"" /etc/skysqlmgr/api.ini &>/dev/null
	if [ "$?" != "0" ] ; then
		sed -i "/^\[apikeys\]$/a $keyString" /etc/skysqlmgr/api.ini
	fi
	
	# Creating manager.json file
	sed -e "s/###ID###/$componentID/" \
		-e "s/###CODE###/$newKey/" \
		%{install_path}config/manager.json.template \
		> %{install_path}config/manager.json
fi

# Not overwriting existing monitor key
grep -q "^3 =" components.ini
if [ $? -ne 0 ]; then
	# Generating API key for Monitor
	newKey=$(echo $RANDOM$(date)$RANDOM | md5sum | cut -f1 -d" ")

	componentID=3

	# Registering key on components.ini
	componentFile=/usr/local/skysql/config/components.ini
	keyString="${componentID} = \"${newKey}\""
	grep "^${componentID} = \"" ${componentFile} &>/dev/null
	if [ "$?" != "0" ] ; then
		echo $keyString >> $componentFile
	fi

	# Registering key on api.ini
	grep "^${componentID} = \"" /etc/skysqlmgr/api.ini &>/dev/null
	if [ "$?" != "0" ] ; then
		sed -i "/^\[apikeys\]$/a $keyString" /etc/skysqlmgr/api.ini
	fi

fi

%install

mkdir -p $RPM_BUILD_ROOT%{install_path}
mkdir $RPM_BUILD_ROOT%{install_path}config
mkdir $RPM_BUILD_ROOT%{install_path}skysql_aws/

cp manager.json $RPM_BUILD_ROOT%{install_path}config/manager.json.template
cp skysql.config $RPM_BUILD_ROOT%{install_path}skysql_aws/

%clean

%files
%defattr(-,root,root)
%{install_path}config/manager.json
%{install_path}skysql_aws/skysql.config

%changelog