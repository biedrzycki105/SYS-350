$name = Read-Host "Would you like to set a hostname? (y/N)"
if ($name -eq 'y'-or $name -eq 'Y'){
    $hostname = Read-Host "Set a hostname for this box:"
    
    Rename-Computer -NewName $hostname
}

$network = Read-Host "Would you like to configure a network interface with an IP Address? (y/N)"
if ($network -eq 'y'-or $network -eq 'Y'){
    Get-NetIPInterface
    $NetIPInterface = Read-Host "Select the Interface Index you want to configure an IP Address for:"
    $IPv4Address = Read-Host "Enter the IP address you want to assign to the interface (ex. 192.168.1.100)"
    $PrefixLength = Read-Host "Configure the Prefix Length (ex. 24)"
    $DefaultGateway = Read-Host "Configure the default gateway"
    $DNSServer = Read-Host "Configure a DNS Server"

    New-NetIPAddress -InterfaceIndex $NetIPInterface -IPAddress $IPv4Address -PrefixLength $PrefixLength -DefaultGateway $DefaultGateway
    Set-DnsClientServerAddress -InterfaceIndex $NetIPInterface -ServerAddresses $DNSServer
}

$adds = Read-Host "Would you like to install Active Directory Domain Services? (y/N)"
if ($adds -eq 'y'-or $adds -eq 'Y'){
    Add-WindowsFeature AD-Domain-Services
}


$domain = Read-Host "Would you like to create a new domain? (y/N)"
if ($domain -eq 'y' -or $domain -eq 'Y'){
    $domainname = Read-Host "What would you like to call your domain? ex. spacejam.local"
    Install-ADDSForest -DomainName $domainname -InstallDNS
}

$dns = Read-Host "Would you like to update DNS records using the DNSEntries.csv configuration file?"
if ($dns -eq 'y'-or $dns -eq 'Y'){
    $entries = Import-Csv -Path "./configs/DNSEntries.csv"
    Add-DnsServerPrimaryZone -NetworkID $Network -ReplicationScope "Domain"
    foreach ($entry in $entries){
        Add-DnsServerResourceRecordA -Name $entry.Name -ZoneName $entry.ZoneName -AllowUpdateAny -IPv4Address $entry.IPv4Address -CreatePtr
    }
}

